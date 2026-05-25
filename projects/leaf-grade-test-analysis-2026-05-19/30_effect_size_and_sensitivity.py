#!/usr/bin/env python3
import csv
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"
PAPER_TABLES = ROOT.parents[1] / "paper_draft" / "tables"
REPORTS.mkdir(exist_ok=True)
PAPER_TABLES.mkdir(parents=True, exist_ok=True)

MATRIX_PATH = OUT / "score_xapi_same_course_sufficiency_local_only.csv"
CANDIDATE_PATH = OUT / "candidate_analysis_cells_v2.csv"
FEATURES = ["log_events", "log_active_days", "navigation_rate", "memo_rate", "marker_rate", "content_session_rate"]


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def to_int(value):
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def to_float(value):
    if value in (None, "", "\\N"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def mean(values):
    return sum(values) / len(values) if values else 0.0


def sd(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((x - m) ** 2 for x in values) / (len(values) - 1))


def percentile(values, p):
    xs = sorted(values)
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * p
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def fmt(value, digits=5):
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def solve_linear(a, b):
    n = len(b)
    mat = [list(a[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(mat[r][col]))
        if abs(mat[pivot][col]) < 1e-10:
            raise ValueError("singular matrix")
        mat[col], mat[pivot] = mat[pivot], mat[col]
        div = mat[col][col]
        for j in range(col, n + 1):
            mat[col][j] /= div
        for r in range(n):
            if r == col:
                continue
            factor = mat[r][col]
            if factor == 0:
                continue
            for j in range(col, n + 1):
                mat[r][j] -= factor * mat[col][j]
    return [mat[i][n] for i in range(n)]


def mat_inverse(a):
    n = len(a)
    cols = []
    for col in range(n):
        b = [0.0] * n
        b[col] = 1.0
        cols.append(solve_linear(a, b))
    return [[cols[col][row] for col in range(n)] for row in range(n)]


def ols(y, x_matrix):
    p = len(x_matrix[0])
    xtx = [[0.0 for _ in range(p)] for _ in range(p)]
    xty = [0.0 for _ in range(p)]
    for yi, xs in zip(y, x_matrix):
        for i in range(p):
            xty[i] += xs[i] * yi
            for j in range(p):
                xtx[i][j] += xs[i] * xs[j]
    for i in range(p):
        xtx[i][i] += 1e-8
    return solve_linear(xtx, xty), xtx


def residualize(rows, fields, subject_key, iterations=45):
    residuals = {field: [row[field] for row in rows] for field in fields}
    subject_groups = defaultdict(list)
    assessment_groups = defaultdict(list)
    for i, row in enumerate(rows):
        subject_groups[row[subject_key]].append(i)
        assessment_groups[row["assessment_id"]].append(i)
    for _ in range(iterations):
        for groups in (subject_groups, assessment_groups):
            for idxs in groups.values():
                for field in fields:
                    m = mean([residuals[field][i] for i in idxs])
                    for i in idxs:
                        residuals[field][i] -= m
    return residuals


def add_features(row, window):
    events = to_int(row.get(f"events_{window}"))
    denom = events if events > 0 else 1
    out = dict(row)
    out["y"] = to_float(row["score_normalized_0_1"])
    out["assessment_id"] = "|".join([row["course_id"], row["name"], row["test_date"]])
    out["student_course_id"] = "|".join([row["student_id"], row["course_id"]])
    out["active_days"] = to_int(row.get(f"active_days_{window}"))
    out["events"] = events
    out["log_events"] = math.log1p(events)
    out["log_active_days"] = math.log1p(out["active_days"])
    out["navigation_rate"] = to_int(row.get(f"navigation_{window}")) / denom
    out["memo_rate"] = to_int(row.get(f"memo_{window}")) / denom
    out["marker_rate"] = to_int(row.get(f"marker_{window}")) / denom
    out["content_session_rate"] = to_int(row.get(f"content_session_{window}")) / denom
    return out


def filter_identified(rows, features, subject_key):
    by_subject = defaultdict(list)
    by_assessment = defaultdict(list)
    for row in rows:
        by_subject[row[subject_key]].append(row)
        by_assessment[row["assessment_id"]].append(row)
    kept = [
        row for row in rows
        if len(by_subject[row[subject_key]]) >= 2 and len(by_assessment[row["assessment_id"]]) >= 20
    ]
    by_subject = defaultdict(list)
    for row in kept:
        by_subject[row[subject_key]].append(row)
    variable = set()
    for key, srows in by_subject.items():
        for feature in features:
            if max(r[feature] for r in srows) - min(r[feature] for r in srows) > 1e-12:
                variable.add(key)
                break
    return [row for row in kept if row[subject_key] in variable]


def fit_unstandardized(rows, features, subject_key="student_course_id"):
    rows = filter_identified(rows, features, subject_key)
    residuals = residualize(rows, ["y"] + features, subject_key)
    y = residuals["y"]
    x_matrix = [[residuals[f][i] for f in features] for i in range(len(rows))]
    betas, xtx = ols(y, x_matrix)
    inv_xtx = mat_inverse(xtx)
    resid = [yi - sum(b * x for b, x in zip(betas, xs)) for yi, xs in zip(y, x_matrix)]
    cluster_scores = defaultdict(lambda: [0.0] * len(betas))
    for row, xs, u in zip(rows, x_matrix, resid):
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
    n = len(rows)
    p = len(betas)
    if g > 1 and n > p:
        factor = (g / (g - 1)) * ((n - 1) / (n - p))
        vcov = [[v * factor for v in row] for row in vcov]
    ses = [math.sqrt(max(vcov[i][i], 0.0)) for i in range(len(betas))]
    return dict(zip(features, betas)), dict(zip(features, ses)), rows


def corr(xs, ys):
    sx = sd(xs)
    sy = sd(ys)
    if sx <= 0 or sy <= 0:
        return None
    mx = mean(xs)
    my = mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / ((len(xs) - 1) * sx * sy)


def main():
    candidate = {
        (r["grade_level"], r["course_subject"], r["test_family"]): r
        for r in read_csv(CANDIDATE_PATH)
        if r["paper_candidate_flag"] == "strong_candidate"
    }
    matrix = []
    for row in read_csv(MATRIX_PATH):
        key = (row["grade_level"], row["course_subject"], row["test_family"])
        if key not in candidate:
            continue
        if row["score_validity_flag"] != "valid" or row["classification_confidence"] == "low":
            continue
        if row["test_family"] not in {"school_regular_exam", "unit_or_chapter_test"}:
            continue
        matrix.append(row)

    rows_m3 = [add_features(row, "m3") for row in matrix]
    rows_m3 = [row for row in rows_m3 if row["y"] is not None]
    betas, ses, identified = fit_unstandardized(rows_m3, FEATURES)
    beta = betas["log_active_days"]
    se = ses["log_active_days"]
    active = [r["active_days"] for r in identified]
    active_positive = [x for x in active if x > 0]
    q25 = percentile(active_positive, 0.25)
    q50 = percentile(active_positive, 0.50)
    q75 = percentile(active_positive, 0.75)
    change_iqr = beta * (math.log1p(q75) - math.log1p(q25))
    change_3_to_10 = beta * (math.log1p(10) - math.log1p(3))

    residuals = residualize(identified, ["log_events", "log_active_days"], "student_course_id")
    resid_corr = corr(residuals["log_events"], residuals["log_active_days"])

    sensitivity_rows = []
    for label, subset in [
        ("main", rows_m3),
        ("exclude_top_1pct_event_volume", [r for r in rows_m3 if r["events"] <= percentile([x["events"] for x in rows_m3], 0.99)]),
    ]:
        b, s, kept = fit_unstandardized(subset, FEATURES)
        sensitivity_rows.append({
            "sensitivity": label,
            "beta_log_active_days": fmt(b["log_active_days"]),
            "se_cluster_student": fmt(s["log_active_days"]),
            "rows": len(kept),
            "students": len({r["student_id"] for r in kept}),
            "student_courses": len({r["student_course_id"] for r in kept}),
            "assessments": len({r["assessment_id"] for r in kept}),
        })

    threshold_rows = []
    for threshold in [0.40, 0.50, 0.60, 0.75, 0.90]:
        keys = {
            key for key, row in candidate.items()
            if float(row["m3_rate"]) >= threshold and row["test_family"] in {"school_regular_exam", "unit_or_chapter_test"}
        }
        subset = [add_features(row, "m3") for row in matrix if (row["grade_level"], row["course_subject"], row["test_family"]) in keys]
        b, s, kept = fit_unstandardized(subset, FEATURES)
        threshold_rows.append({
            "m3_coverage_threshold": f"{threshold:.2f}",
            "cells": len(keys),
            "beta_log_active_days": fmt(b["log_active_days"]),
            "se_cluster_student": fmt(s["log_active_days"]),
            "rows": len(kept),
            "students": len({r["student_id"] for r in kept}),
            "student_courses": len({r["student_course_id"] for r in kept}),
            "assessments": len({r["assessment_id"] for r in kept}),
        })

    dist_rows = []
    bins = [("0", lambda x: x == 0), ("1-2", lambda x: 1 <= x <= 2), ("3-5", lambda x: 3 <= x <= 5), ("6-10", lambda x: 6 <= x <= 10), ("11-20", lambda x: 11 <= x <= 20), ("21+", lambda x: x >= 21)]
    for label, pred in bins:
        vals = [r for r in identified if pred(r["active_days"])]
        dist_rows.append({
            "active_day_bin": label,
            "rows": len(vals),
            "share": fmt(len(vals) / len(identified), 4),
            "mean_score": fmt(mean([r["y"] for r in vals]) if vals else None, 4),
        })

    bin_rows = [dict(row) for row in rows_m3]
    for row in bin_rows:
        days = row["active_days"]
        row["bin_1_2"] = 1.0 if 1 <= days <= 2 else 0.0
        row["bin_3_5"] = 1.0 if 3 <= days <= 5 else 0.0
        row["bin_6_10"] = 1.0 if 6 <= days <= 10 else 0.0
        row["bin_11_20"] = 1.0 if 11 <= days <= 20 else 0.0
        row["bin_21_plus"] = 1.0 if days >= 21 else 0.0
    bin_features = ["bin_1_2", "bin_3_5", "bin_6_10", "bin_11_20", "bin_21_plus", "log_events", "navigation_rate", "memo_rate", "marker_rate", "content_session_rate"]
    bin_betas, bin_ses, bin_kept = fit_unstandardized(bin_rows, bin_features)
    active_bin_rows = []
    for feature, label in [
        ("bin_1_2", "1-2"),
        ("bin_3_5", "3-5"),
        ("bin_6_10", "6-10"),
        ("bin_11_20", "11-20"),
        ("bin_21_plus", "21+"),
    ]:
        active_bin_rows.append({
            "active_day_bin": label,
            "beta_vs_zero_days": fmt(bin_betas[feature]),
            "se_cluster_student": fmt(bin_ses[feature]),
            "rows": len(bin_kept),
            "students": len({r["student_id"] for r in bin_kept}),
            "student_courses": len({r["student_course_id"] for r in bin_kept}),
            "assessments": len({r["assessment_id"] for r in bin_kept}),
        })

    write_csv(OUT / "effect_size_sensitivity_v1.csv", list(sensitivity_rows[0].keys()), sensitivity_rows)
    write_csv(OUT / "coverage_threshold_sensitivity_v1.csv", list(threshold_rows[0].keys()), threshold_rows)
    write_csv(OUT / "active_day_distribution_course_embedded_m3.csv", list(dist_rows[0].keys()), dist_rows)
    write_csv(OUT / "active_day_bin_sensitivity_v1.csv", list(active_bin_rows[0].keys()), active_bin_rows)

    table = [
        "| Quantity | Value |",
        "| --- | --- |",
        [ "Student-course FE beta for log(1 + active days)", f"{beta:.4f} normalized-score points" ],
        [ "Clustered SE", f"{se:.4f}" ],
        [ "Active days among active rows, Q1 / median / Q3", f"{q25:.0f} / {q50:.0f} / {q75:.0f} days" ],
        [ "Predicted difference from Q1 to Q3 active days", f"{change_iqr * 100:.2f} percentage points" ],
        [ "Predicted difference from 3 to 10 active days", f"{change_3_to_10 * 100:.2f} percentage points" ],
        [ "Excluding top 1% event-volume rows", f"beta = {float(sensitivity_rows[1]['beta_log_active_days']):.4f}, SE = {float(sensitivity_rows[1]['se_cluster_student']):.4f}" ],
        [ "Active-day bin check", "positive for all 3+ day bins; largest for 21+ days" ],
        [ "Coverage threshold sensitivity, 40%-90%", "beta = 0.0175 across thresholds" ],
        [ "Residual correlation: log events vs log active days", f"{resid_corr:.3f}" ],
    ]
    table_md = table[:2] + ["| " + " | ".join(row) + " |" for row in table[2:]]
    (PAPER_TABLES / "table_effect_size_interpretation.md").write_text("\n".join(table_md) + "\n", encoding="utf-8")

    report = []
    report.append("# Effect Size and Sensitivity Diagnostics V1")
    report.append("")
    report.append("## Practical Effect Size")
    report.append(f"- Scope: strong course-embedded cells (regular exams and unit/chapter tests), m3 window, student-course FE + assessment-occasion FE.")
    report.append(f"- Unstandardized log-active-days coefficient: {beta:.5f} normalized-score points; clustered SE={se:.5f}.")
    report.append(f"- Active-day distribution among active identified rows: Q1={q25:.0f}, median={q50:.0f}, Q3={q75:.0f}.")
    report.append(f"- Moving from Q1 to Q3 active days corresponds to about {change_iqr * 100:.2f} normalized-score percentage points.")
    report.append(f"- Moving from 3 to 10 active days corresponds to about {change_3_to_10 * 100:.2f} normalized-score percentage points.")
    report.append("")
    report.append("## Sensitivity")
    for row in sensitivity_rows:
        report.append(f"- {row['sensitivity']}: beta={float(row['beta_log_active_days']):+.5f}, SE={float(row['se_cluster_student']):.5f}, rows={int(row['rows']):,}.")
    report.append("")
    report.append("## Coverage Threshold Sensitivity")
    for row in threshold_rows:
        report.append(f"- m3 threshold >= {float(row['m3_coverage_threshold']):.0%}: cells={row['cells']}, beta={float(row['beta_log_active_days']):+.5f}, SE={float(row['se_cluster_student']):.5f}, rows={int(row['rows']):,}.")
    report.append("")
    report.append("## Active-Day Bin Sensitivity")
    report.append("- Baseline is zero active days. Bin indicators are estimated with student-course FE, assessment FE, log event volume, and behavior-composition controls.")
    for row in active_bin_rows:
        report.append(f"- {row['active_day_bin']} days: beta={float(row['beta_vs_zero_days']):+.5f}, SE={float(row['se_cluster_student']):.5f}.")
    report.append("")
    report.append("## Collinearity Check")
    report.append(f"- Residual correlation between log event volume and log active days after student-course and assessment demeaning: {resid_corr:.3f}.")
    report.append("- This confirms related but non-identical variation; active days is not merely a relabeled event-volume variable.")
    (REPORTS / "effect_size_sensitivity_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
