#!/usr/bin/env python3
import csv
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

MATRIX_PATH = OUT / "score_xapi_same_course_sufficiency_local_only.csv"
CANDIDATE_PATH = OUT / "candidate_analysis_cells_v2.csv"
OLD_MONTHLY_PATH = OUT / "xapi_old_context_monthly_local_only.csv"

SEED = 20260519
BOOTSTRAPS = 300


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


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
    if not values:
        return None
    xs = sorted(values)
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


def month_index(ym):
    y, m = ym.split("-")
    return int(y) * 12 + int(m)


def ym_from_index(idx):
    y = idx // 12
    m = idx % 12
    if m == 0:
        y -= 1
        m = 12
    return f"{y:04d}-{m:02d}"


FIELDS = [
    "events_total", "active_days", "navigation_events", "memo_events", "marker_events",
    "quiz_events", "timer_events", "content_session_events",
]


def build_course_month_index(target_students, target_courses):
    index = defaultdict(lambda: defaultdict(int))
    represented_events = 0
    for row in read_csv(OLD_MONTHLY_PATH):
        sid = row["student_id"]
        if sid not in target_students:
            continue
        course_id = row["course_id"]
        if course_id not in target_courses:
            continue
        key = (sid, course_id, row["event_month"])
        for field in FIELDS:
            index[key][field] += to_int(row[field])
        represented_events += to_int(row["events_total"])
    return index, represented_events


def assessment_residuals(rows):
    groups = defaultdict(list)
    for row in rows:
        row["assessment_id"] = "|".join([row["course_id"], row["name"], row["test_date"]])
        groups[row["assessment_id"]].append(row)
    out = []
    for group in groups.values():
        if len(group) < 20:
            continue
        y_mean = mean([r["score"] for r in group])
        for row in group:
            rr = dict(row)
            rr["score_resid"] = row["score"] - y_mean
            out.append(rr)
    scale = sd([r["score_resid"] for r in out])
    for row in out:
        row["score_resid_std"] = row["score_resid"] / scale if scale > 0 else 0.0
    return out


def entropy(shares):
    vals = [s for s in shares if s > 0]
    if not vals:
        return 0.0
    return -sum(s * math.log(s) for s in vals) / math.log(3)


def classify_phase(row):
    active = [row["early_active_days"], row["middle_active_days"], row["late_active_days"]]
    events = [row["early_events"], row["middle_events"], row["late_events"]]
    total_active = sum(active)
    total_events = sum(events)
    active_months = sum(1 for v in active if v > 0)
    if total_events == 0:
        return "no_same_course_activity"
    if active_months == 3 and max(active) / total_active < 0.50:
        if row["navigation_share"] >= 0.35:
            return "distributed_navigation"
        return "distributed_sustained"
    if active[2] / total_active >= 0.60:
        return "late_intensive"
    if active[0] / total_active >= 0.60:
        return "early_declining"
    if active_months == 1:
        return "single_month_activity"
    return "intermittent_activity"


def bootstrap_ci(rows, group_field, value_field):
    by_student = defaultdict(list)
    for row in rows:
        by_student[row["student_id"]].append(row)
    students = list(by_student)
    rng = random.Random(SEED)
    estimates = defaultdict(list)
    for _ in range(BOOTSTRAPS):
        sample = []
        for _ in students:
            sample.extend(by_student[rng.choice(students)])
        buckets = defaultdict(list)
        for row in sample:
            buckets[row[group_field]].append(row[value_field])
        for key, vals in buckets.items():
            estimates[key].append(mean(vals))
    return {
        key: {
            "ci_low": fmt(percentile(vals, 0.025)),
            "ci_high": fmt(percentile(vals, 0.975)),
            "bootstraps": len(vals),
        }
        for key, vals in estimates.items()
    }


def main():
    candidate_keys = {
        (r["grade_level"], r["course_subject"], r["test_family"])
        for r in read_csv(CANDIDATE_PATH)
        if r.get("paper_candidate_flag") == "strong_candidate"
    }
    score_rows = []
    for row in read_csv(MATRIX_PATH):
        key = (row["grade_level"], row["course_subject"], row["test_family"])
        if key not in candidate_keys:
            continue
        if row.get("score_validity_flag") != "valid" or row.get("classification_confidence") == "low":
            continue
        score = to_float(row.get("score_normalized_0_1"))
        if score is None:
            continue
        rr = dict(row)
        rr["score"] = score
        score_rows.append(rr)

    target_students = {r["student_id"] for r in score_rows}
    target_courses = {r["course_id"] for r in score_rows}
    month_indexed, represented_events = build_course_month_index(target_students, target_courses)

    phase_rows = []
    for row in score_rows:
        test_m = month_index(row["test_month"])
        phase_months = {
            "early": ym_from_index(test_m - 3),
            "middle": ym_from_index(test_m - 2),
            "late": ym_from_index(test_m - 1),
        }
        phase_vals = {}
        totals = defaultdict(int)
        for phase, ym in phase_months.items():
            vals = month_indexed.get((row["student_id"], row["course_id"], ym), {})
            for field in FIELDS:
                value = to_int(vals.get(field, 0))
                totals[field] += value
                if field == "events_total":
                    phase_vals[f"{phase}_events"] = value
                elif field == "active_days":
                    phase_vals[f"{phase}_active_days"] = value
        total_events = totals["events_total"]
        denom = total_events if total_events > 0 else 1
        active = [phase_vals["early_active_days"], phase_vals["middle_active_days"], phase_vals["late_active_days"]]
        event_phase = [phase_vals["early_events"], phase_vals["middle_events"], phase_vals["late_events"]]
        shares = [v / sum(event_phase) for v in event_phase] if sum(event_phase) > 0 else [0, 0, 0]
        rr = {
            "student_id": row["student_id"],
            "course_id": row["course_id"],
            "name": row["name"],
            "test_date": row["test_date"],
            "test_family": row["test_family"],
            "grade_level": row["grade_level"],
            "course_subject": row["course_subject"],
            "score": row["score"],
            **phase_vals,
            "total_events": total_events,
            "total_active_days": totals["active_days"],
            "active_month_count": sum(1 for v in active if v > 0),
            "phase_entropy": entropy(shares),
            "late_event_share": shares[2],
            "early_event_share": shares[0],
            "active_day_slope": phase_vals["late_active_days"] - phase_vals["early_active_days"],
            "navigation_share": totals["navigation_events"] / denom,
            "memo_share": totals["memo_events"] / denom,
            "marker_share": totals["marker_events"] / denom,
            "content_session_share": totals["content_session_events"] / denom,
        }
        rr["phase_strategy"] = classify_phase(rr)
        phase_rows.append(rr)

    phase_rows = assessment_residuals(phase_rows)
    local_fields = [
        "student_id", "course_id", "name", "test_date", "test_family", "grade_level", "course_subject",
        "phase_strategy", "score_resid_std", "early_events", "middle_events", "late_events",
        "early_active_days", "middle_active_days", "late_active_days", "active_month_count",
        "phase_entropy", "late_event_share", "active_day_slope", "navigation_share", "memo_share", "marker_share",
    ]
    write_csv(
        OUT / "temporal_phase_assignments_local_only.csv",
        local_fields,
        [{k: fmt(v) if isinstance(v, float) else v for k, v in row.items() if k in local_fields} for row in phase_rows],
    )

    buckets = defaultdict(list)
    for row in phase_rows:
        buckets[row["phase_strategy"]].append(row)
    cis = bootstrap_ci(phase_rows, "phase_strategy", "score_resid_std")
    summary = []
    for strategy, rows in buckets.items():
        summary.append({
            "phase_strategy": strategy,
            "rows": len(rows),
            "students": len({r["student_id"] for r in rows}),
            "assessments": len({"|".join([r["course_id"], r["name"], r["test_date"]]) for r in rows}),
            "score_resid_std_mean": fmt(mean([r["score_resid_std"] for r in rows])),
            "score_resid_std_sd": fmt(sd([r["score_resid_std"] for r in rows])),
            "score_resid_ci_low": cis.get(strategy, {}).get("ci_low", ""),
            "score_resid_ci_high": cis.get(strategy, {}).get("ci_high", ""),
            "active_month_count_mean": fmt(mean([r["active_month_count"] for r in rows])),
            "phase_entropy_mean": fmt(mean([r["phase_entropy"] for r in rows])),
            "late_event_share_mean": fmt(mean([r["late_event_share"] for r in rows])),
            "active_day_slope_mean": fmt(mean([r["active_day_slope"] for r in rows])),
            "navigation_share_mean": fmt(mean([r["navigation_share"] for r in rows])),
            "memo_share_mean": fmt(mean([r["memo_share"] for r in rows])),
            "marker_share_mean": fmt(mean([r["marker_share"] for r in rows])),
            "top_test_families": "; ".join(f"{k}:{v}" for k, v in Counter(r["test_family"] for r in rows).most_common(4)),
        })
    summary.sort(key=lambda r: float(r["score_resid_std_mean"]), reverse=True)
    write_csv(OUT / "temporal_phase_strategy_summary_v1.csv", list(summary[0].keys()), summary)

    report = []
    report.append("# Temporal Phase Strategy Analysis V1")
    report.append("")
    report.append("## Design")
    report.append("- Strong candidate cells only, valid outcomes only.")
    report.append("- Three pre-test phases: early = test month minus 3, middle = minus 2, late = minus 1.")
    report.append("- Same-course old BookRoll monthly features use direct ClickHouse context_id after the saikyo_old reimport.")
    report.append("- Outcome comparison uses assessment fixed-effect residuals.")
    report.append("- Row-level phase assignments remain local only.")
    report.append("")
    report.append("## Aggregate Scope")
    report.append(f"- rows after assessment fixed-effect filtering: {len(phase_rows):,}")
    report.append(f"- unique students: {len({r['student_id'] for r in phase_rows}):,}")
    report.append(f"- represented old same-course events in these rows/windows: {represented_events:,}")
    report.append("")
    report.append("## Strategy Summary")
    for row in summary:
        report.append(
            f"- {row['phase_strategy']}: rows={int(row['rows']):,}, students={int(row['students']):,}, "
            f"score_resid={float(row['score_resid_std_mean']):+.3f} "
            f"CI [{float(row['score_resid_ci_low']):+.3f}, {float(row['score_resid_ci_high']):+.3f}], "
            f"active_months={float(row['active_month_count_mean']):.2f}, "
            f"entropy={float(row['phase_entropy_mean']):.2f}, "
            f"late_share={float(row['late_event_share_mean']):.2f}, "
            f"navigation_share={float(row['navigation_share_mean']):.2f}, "
            f"memo_share={float(row['memo_share_mean']):.2f}"
        )
    report.append("")
    report.append("## Interpretation")
    report.append("- This is the first direct temporal-strategy layer: it separates sustained, late-intensive, early-declining, intermittent, and no-activity patterns.")
    report.append("- Strategies with stable positive residuals are better paper candidates than simple behavior totals.")
    report.append("- The next check should combine phase strategy with behavior profile to see whether distributed navigation remains positive after separating late cramming from sustained use.")
    (REPORTS / "temporal_phase_strategy_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
