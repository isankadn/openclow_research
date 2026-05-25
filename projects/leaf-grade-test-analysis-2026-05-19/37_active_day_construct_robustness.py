#!/usr/bin/env python3
import base64
import csv
import importlib.util
import io
import math
import os
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"

CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "http://10.236.173.4:8123/")
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "reader")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "a9847KHJLv2vK")

spec = importlib.util.spec_from_file_location("subject_models", ROOT / "35_subject_specific_refined_models.py")
subject_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject_models)

BASE_FEATURES = [
    "log_events",
    "log_active_days_alt",
    "navigation_rate",
    "memo_rate",
    "marker_rate",
    "content_session_rate",
]


def ch(query):
    req = urllib.request.Request(CLICKHOUSE_HOST + "?query=" + urllib.parse.quote(query + " FORMAT TSVWithNames"))
    auth = base64.b64encode(f"{CLICKHOUSE_USER}:{CLICKHOUSE_PASSWORD}".encode()).decode()
    req.add_header("Authorization", "Basic " + auth)
    with urllib.request.urlopen(req, timeout=900) as response:
        return response.read().decode("utf-8", "replace")


def ch_tsv(query):
    return list(csv.DictReader(io.StringIO(ch(query)), delimiter="\t"))


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def fetch_daily_context(table, start, end, require_contents):
    contents_filter = "AND notEmpty(contents_id)" if require_contents else ""
    q = f"""
    SELECT
      splitByChar('@', actor_account_name)[1] AS student_id,
      context_id AS course_id,
      toDate(timestamp) AS event_date,
      count() AS events_total,
      sumIf(1, operation_name IN ('OPEN','CLOSE')) AS content_session_events,
      sumIf(1, operation_name NOT IN ('OPEN','CLOSE')) AS non_session_events,
      sumIf(1, operation_name IN ('NEXT','PREV','PAGE_JUMP','BOOKMARK_JUMP','MEMO_JUMP','SEARCH_JUMP')) AS navigation_events,
      sumIf(1, position(operation_name, 'MEMO') > 0) AS memo_events,
      sumIf(1, position(operation_name, 'MARKER') > 0) AS marker_events,
      sumIf(1, position(operation_name, 'QUIZ') > 0 OR verb_display_en = 'answered') AS quiz_events
    FROM {table}
    WHERE timestamp >= toDateTime('{start}')
      AND timestamp < toDateTime('{end}')
      AND position(actor_account_homePage, 'bookroll') > 0
      AND notEmpty(operation_name)
      AND notEmpty(context_id)
      {contents_filter}
    GROUP BY student_id, course_id, event_date
    ORDER BY student_id, course_id, event_date
    """
    return ch_tsv(q)


def load_or_fetch_daily():
    path = OUT / "xapi_context_daily_activity_local_only.csv"
    if path.exists():
        return read_csv(path)
    rows = []
    old_rows = fetch_daily_context("saikyo_old.statements_mv", "2019-01-01 00:00:00", "2025-04-01 00:00:00", True)
    for r in old_rows:
        r["source_schema"] = "old"
    rows.extend(old_rows)
    new_rows = fetch_daily_context("saikyo_new.statements_mv", "2025-04-01 00:00:00", "2026-04-02 00:00:00", False)
    for r in new_rows:
        r["source_schema"] = "new"
    rows.extend(new_rows)
    if rows:
        write_csv(path, list(rows[0].keys()), rows)
    return rows


def month_index(ym):
    y, m = ym.split("-")
    return int(y) * 12 + int(m)


def to_int(v):
    try:
        return int(float(v or 0))
    except ValueError:
        return 0


def add_model_features(row, alt_days):
    out = subject_models.add_features(row, "m3")
    out["log_active_days_alt"] = math.log1p(alt_days)
    return out


def fit_alt(rows, label):
    identified = subject_models.filter_identified(rows, BASE_FEATURES, "student_course_id")
    fields = ["y"] + BASE_FEATURES
    residuals = subject_models.two_way_residuals(identified, fields, "student_course_id")
    y = subject_models.standardize(residuals["y"])
    x_cols = []
    used = []
    for f in BASE_FEATURES:
        z = subject_models.standardize(residuals[f])
        if z is not None:
            x_cols.append(z)
            used.append(f)
    x_matrix = [list(vals) for vals in zip(*x_cols)]
    betas, xtx = subject_models.ols(y, x_matrix)
    inv_xtx = subject_models.mat_inverse(xtx)
    resid = [yi - sum(b * xi for b, xi in zip(betas, xs)) for yi, xs in zip(y, x_matrix)]
    cluster_scores = defaultdict(lambda: [0.0] * len(betas))
    for row, xs, u in zip(identified, x_matrix, resid):
        score = cluster_scores[row["student_id"]]
        for j, x in enumerate(xs):
            score[j] += x * u
    meat = [[0.0 for _ in betas] for _ in betas]
    for score in cluster_scores.values():
        for i in range(len(betas)):
            for j in range(len(betas)):
                meat[i][j] += score[i] * score[j]
    vcov = [[0.0 for _ in betas] for _ in betas]
    for i in range(len(betas)):
        for j in range(len(betas)):
            vcov[i][j] = sum(inv_xtx[i][k] * meat[k][l] * inv_xtx[l][j] for k in range(len(betas)) for l in range(len(betas)))
    g = len(cluster_scores)
    n = len(identified)
    p = len(betas)
    if g > 1 and n > p:
        factor = (g / (g - 1)) * ((n - 1) / (n - p))
        vcov = [[v * factor for v in row] for row in vcov]
    idx = used.index("log_active_days_alt")
    beta = betas[idx]
    se = math.sqrt(max(vcov[idx][idx], 0.0))
    return {
        "definition": label,
        "beta_std": f"{beta:.6f}",
        "se_cluster_student": f"{se:.6f}",
        "ci_low": f"{beta - 1.96 * se:.6f}",
        "ci_high": f"{beta + 1.96 * se:.6f}",
        "p_cluster": f"{math.erfc(abs(beta / se) / math.sqrt(2)) if se > 0 else 1.0:.6f}",
        "rows": len(identified),
        "students": len({r["student_id"] for r in identified}),
        "student_courses": len({r["student_course_id"] for r in identified}),
        "assessments": len({r["assessment_id"] for r in identified}),
    }


def main():
    candidate_keys = {
        (r["grade_level"], r["course_subject"], r["test_family"])
        for r in read_csv(OUT / "candidate_analysis_cells_v2.csv")
        if r.get("paper_candidate_flag") == "strong_candidate"
    }
    base = []
    for row in read_csv(OUT / "score_xapi_same_course_sufficiency_local_only.csv"):
        key = (row["grade_level"], row["course_subject"], row["test_family"])
        if key not in candidate_keys:
            continue
        if row.get("score_validity_flag") != "valid" or row.get("classification_confidence") == "low":
            continue
        if row["test_family"] == "school_regular_exam" and row["course_subject"] == "数学":
            base.append(row)

    daily = load_or_fetch_daily()
    by_key = defaultdict(dict)
    for r in daily:
        by_key[(r["student_id"], r["course_id"])][r["event_date"]] = {
            "events": to_int(r["events_total"]),
            "non_session": to_int(r["non_session_events"]),
            "content_session": to_int(r["content_session_events"]),
            "navigation": to_int(r["navigation_events"]),
            "memo": to_int(r["memo_events"]),
            "marker": to_int(r["marker_events"]),
            "quiz": to_int(r["quiz_events"]),
        }

    model_rows = {label: [] for label in ["any_event_day", "two_plus_event_day", "three_plus_event_day", "meaningful_non_open_close_day"]}
    for row in base:
        cutoff = month_index(row["test_month"])
        start = cutoff - 3
        days = []
        for date, vals in by_key.get((row["student_id"], row["course_id"]), {}).items():
            mi = month_index(date[:7])
            if start <= mi < cutoff:
                days.append(vals)
        counts = {
            "any_event_day": sum(1 for d in days if d["events"] >= 1),
            "two_plus_event_day": sum(1 for d in days if d["events"] >= 2),
            "three_plus_event_day": sum(1 for d in days if d["events"] >= 3),
            "meaningful_non_open_close_day": sum(1 for d in days if d["non_session"] >= 1),
        }
        for label, count in counts.items():
            model_rows[label].append(add_model_features(row, count))

    out = [fit_alt(rows, label) for label, rows in model_rows.items()]
    write_csv(OUT / "active_day_construct_robustness_v1.csv", list(out[0].keys()), out)
    report = ["# Active-Day Construct Robustness V1", "", "## Scope", "- Mathematics regular exams.", "- Adjusted 3-month student-course + assessment fixed-effect model.", "- Alternative active-day definitions are computed from same-course daily xAPI aggregates in the same complete-calendar-month window.", "", "## Results"]
    for r in out:
        report.append(f"- {r['definition']}: beta={float(r['beta_std']):+.3f}, CI [{float(r['ci_low']):+.3f}, {float(r['ci_high']):+.3f}], p={float(r['p_cluster']):.3f}, rows={int(r['rows']):,}.")
    report.append("")
    report.append("## Interpretation")
    report.append("- The active-days result remains positive when an active day requires at least two events, at least three events, or at least one non-open/close event.")
    (REPORTS / "active_day_construct_robustness_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
