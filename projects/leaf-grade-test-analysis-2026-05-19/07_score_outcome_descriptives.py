#!/usr/bin/env python3
import csv
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
MATRIX_PATH = OUT / "score_xapi_same_course_sufficiency_local_only.csv"


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_float(value):
    if value in (None, "", "\\N"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def to_int(value):
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


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


def mean(values):
    return sum(values) / len(values) if values else None


def sd(values):
    if len(values) < 2:
        return None
    m = mean(values)
    return math.sqrt(sum((x - m) ** 2 for x in values) / (len(values) - 1))


def fmt(value, digits=4):
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def summarize(rows, dims):
    buckets = {}
    for r in rows:
        key = tuple(r.get(dim) or "(missing)" for dim in dims)
        b = buckets.setdefault(key, {
            "score_rows": 0,
            "valid_score_rows": 0,
            "m3_rows": 0,
            "m6_rows": 0,
            "m12_rows": 0,
            "old_m3_rows": 0,
            "new_m3_rows": 0,
            "no_xapi_m3_rows": 0,
            "students": set(),
            "courses": set(),
            "test_names": set(),
            "scores": [],
            "events_m3": 0,
            "active_days_m3": 0,
            "navigation_m3": 0,
            "memo_m3": 0,
            "marker_m3": 0,
            "quiz_m3": 0,
            "timer_m3": 0,
            "content_session_m3": 0,
        })
        b["score_rows"] += 1
        b["students"].add(r["student_id"])
        b["courses"].add(r["course_id"])
        b["test_names"].add(r["name"])
        events_m3 = to_int(r.get("events_m3"))
        events_m6 = to_int(r.get("events_m6"))
        events_m12 = to_int(r.get("events_m12"))
        old_m3 = to_int(r.get("old_events_m3"))
        new_m3 = to_int(r.get("new_events_m3"))
        b["m3_rows"] += 1 if events_m3 > 0 else 0
        b["m6_rows"] += 1 if events_m6 > 0 else 0
        b["m12_rows"] += 1 if events_m12 > 0 else 0
        b["old_m3_rows"] += 1 if old_m3 > 0 else 0
        b["new_m3_rows"] += 1 if new_m3 > 0 else 0
        b["no_xapi_m3_rows"] += 1 if events_m3 == 0 else 0
        for field in [
            "events_m3", "active_days_m3", "navigation_m3", "memo_m3", "marker_m3",
            "quiz_m3", "timer_m3", "content_session_m3",
        ]:
            b[field] += to_int(r.get(field))
        if r.get("score_validity_flag") == "valid":
            score = to_float(r.get("score_normalized_0_1"))
            if score is not None:
                b["valid_score_rows"] += 1
                b["scores"].append(score)

    out = []
    for key, b in buckets.items():
        n = b["score_rows"]
        scores = b["scores"]
        row = {dims[i]: key[i] for i in range(len(dims))}
        row.update({
            "score_rows": n,
            "valid_score_rows": b["valid_score_rows"],
            "valid_score_rate": fmt(b["valid_score_rows"] / n if n else None),
            "students": len(b["students"]),
            "courses": len(b["courses"]),
            "test_names": len(b["test_names"]),
            "m3_rows": b["m3_rows"],
            "m3_rate": fmt(b["m3_rows"] / n if n else None),
            "m6_rows": b["m6_rows"],
            "m6_rate": fmt(b["m6_rows"] / n if n else None),
            "m12_rows": b["m12_rows"],
            "m12_rate": fmt(b["m12_rows"] / n if n else None),
            "old_m3_rows": b["old_m3_rows"],
            "new_m3_rows": b["new_m3_rows"],
            "no_xapi_m3_rows": b["no_xapi_m3_rows"],
            "events_m3": b["events_m3"],
            "active_days_m3": b["active_days_m3"],
            "navigation_m3": b["navigation_m3"],
            "memo_m3": b["memo_m3"],
            "marker_m3": b["marker_m3"],
            "quiz_m3": b["quiz_m3"],
            "timer_m3": b["timer_m3"],
            "content_session_m3": b["content_session_m3"],
            "score_norm_mean": fmt(mean(scores)),
            "score_norm_sd": fmt(sd(scores)),
            "score_norm_q1": fmt(percentile(scores, 0.25)),
            "score_norm_median": fmt(percentile(scores, 0.50)),
            "score_norm_q3": fmt(percentile(scores, 0.75)),
            "score_norm_min": fmt(min(scores) if scores else None),
            "score_norm_max": fmt(max(scores) if scores else None),
        })
        if b["valid_score_rows"] >= 100 and len(b["students"]) >= 100 and b["m3_rows"] >= 100:
            row["paper_candidate_flag"] = "strong_candidate" if (b["m3_rows"] / n) >= 0.50 else "limited_xapi_coverage"
        else:
            row["paper_candidate_flag"] = "insufficient"
        out.append(row)
    return sorted(out, key=lambda r: (
        r["paper_candidate_flag"] != "candidate",
        -int(r["m3_rows"]),
        -int(r["valid_score_rows"]),
        tuple(r[d] for d in dims),
    ))


def main():
    rows = read_csv(MATRIX_PATH)
    total = len(rows)
    valid = sum(1 for r in rows if r.get("score_validity_flag") == "valid")
    has_m3 = sum(1 for r in rows if to_int(r.get("events_m3")) > 0)
    old_m3 = sum(1 for r in rows if to_int(r.get("old_events_m3")) > 0)
    new_m3 = sum(1 for r in rows if to_int(r.get("new_events_m3")) > 0)

    outputs = {
        "outcome_by_year_family.csv": ["test_year", "test_family"],
        "outcome_by_grade_subject_family.csv": ["grade_level", "course_subject", "test_family"],
        "outcome_by_year_grade_subject_family.csv": ["test_year", "grade_level", "course_subject", "test_family"],
    }
    summary_data = {}
    fields = None
    for filename, dims in outputs.items():
        data = summarize(rows, dims)
        summary_data[filename] = (dims, data)
        if data:
            fields = list(data[0].keys())
            write_csv(OUT / filename, fields, data)

    candidate_rows = [
        r for r in summary_data["outcome_by_grade_subject_family.csv"][1]
        if r["paper_candidate_flag"] == "strong_candidate"
    ]
    candidate_source = summary_data["outcome_by_grade_subject_family.csv"][1]
    candidate_fields = list(candidate_source[0].keys()) if candidate_source else (fields or [])
    write_csv(OUT / "candidate_analysis_cells_v2.csv", candidate_fields, candidate_rows)

    report = []
    report.append("# Paper-Ready Outcome And Harmonized XAPI Diagnostics V2")
    report.append("")
    report.append("## Analysis Matrix")
    report.append("- Grain: one row per student_id + course_id + test name + test date.")
    report.append("- Outcome: normalized quiz score from (quiz - min) / (max - min) in course_student_scores.")
    report.append("- xAPI features: old and new BookRoll events harmonized to student_id + course_id + event_month, then rolled up in pre-test windows.")
    report.append("- Privacy rule: row-level matrix remains local only; this report contains aggregate diagnostics.")
    report.append("")
    report.append("## Overall Quality")
    report.append(f"- total clean score rows: {total:,}")
    report.append(f"- rows with valid normalized score: {valid:,} ({valid / total:.1%})")
    report.append(f"- rows with any same-course xAPI in 3-month pre-test window: {has_m3:,} ({has_m3 / total:.1%})")
    report.append(f"- rows with old-source same-course xAPI in 3-month window: {old_m3:,} ({old_m3 / total:.1%})")
    report.append(f"- rows with new-source same-course xAPI in 3-month window: {new_m3:,} ({new_m3 / total:.1%})")
    report.append("")

    for title, filename, max_rows in [
        ("Candidate Grade/Subject/Test Cells", "outcome_by_grade_subject_family.csv", 25),
        ("Year/Test Family Outcome Coverage", "outcome_by_year_family.csv", 20),
        ("Year Grade/Subject/Test Cells", "outcome_by_year_grade_subject_family.csv", 25),
    ]:
        dims, data = summary_data[filename]
        report.append(f"## {title}")
        shown = 0
        for r in data:
            if title.startswith("Candidate") and r["paper_candidate_flag"] != "strong_candidate":
                continue
            label = ", ".join(f"{d}={r[d]}" for d in dims)
            report.append(
                f"- {label}: valid_scores={int(r['valid_score_rows']):,}/{int(r['score_rows']):,}, "
                f"students={int(r['students']):,}, courses={int(r['courses']):,}, "
                f"m3_xapi={int(r['m3_rows']):,} ({float(r['m3_rate']):.1%}), "
                f"old_m3_rows={int(r['old_m3_rows']):,}, new_m3_rows={int(r['new_m3_rows']):,}, "
                f"score_mean={float(r['score_norm_mean'] or 0):.3f}, "
                f"score_median={float(r['score_norm_median'] or 0):.3f}, flag={r['paper_candidate_flag']}"
            )
            shown += 1
            if shown >= max_rows:
                break
        if shown == 0:
            report.append("- No cells met the current candidate threshold.")
        report.append("")

    report.append("## Interpretation")
    report.append("- The combined matrix is suitable for selecting defensible analysis cells, not yet for making causal claims.")
    report.append("- Strong candidate cells require at least 100 valid outcomes, at least 100 students, at least 100 pre-test same-course xAPI-linked rows, and at least 50% 3-month same-course xAPI coverage.")
    report.append("- Strong candidate cells should be modeled with fixed effects for test family/grade/subject and random or clustered effects for student/course where feasible.")
    report.append("- Old-source same-course linkage now uses direct context_id after the saikyo_old reimport; sensitivity checks should focus on alternate xAPI windows and the small residual set with missing context_id.")
    report.append("- Because scaled is zero in the source table, normalized quiz score should be the primary numeric outcome unless the score table semantics are revised.")
    (REPORTS / "paper_ready_result_set_v2.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
