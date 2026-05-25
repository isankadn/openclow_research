#!/usr/bin/env python3
import csv
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

PROFILE_PATH = OUT / "behavior_profile_assignments_local_only.csv"
PHASE_PATH = OUT / "temporal_phase_assignments_local_only.csv"

BOOTSTRAPS = 300
SEED = 20260519
MIN_ROWS = 100


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def mean(values):
    return sum(values) / len(values) if values else 0.0


def sd(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return (sum((x - m) ** 2 for x in values) / (len(values) - 1)) ** 0.5


def percentile(values, p):
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    frac = pos - lo
    return xs[lo] + (xs[hi] - xs[lo]) * frac


def fmt(value, digits=5):
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def key(row):
    return "|".join([row["student_id"], row["course_id"], row["name"], row["test_date"]])


def bootstrap(rows, group_field):
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
            buckets[row[group_field]].append(row["score_resid_std"])
        for group, vals in buckets.items():
            estimates[group].append(mean(vals))
    return {
        group: {
            "ci_low": fmt(percentile(vals, 0.025)),
            "ci_high": fmt(percentile(vals, 0.975)),
            "bootstraps": len(vals),
        }
        for group, vals in estimates.items()
    }


def main():
    profile_by_key = {key(row): row for row in read_csv(PROFILE_PATH)}
    merged = []
    for row in read_csv(PHASE_PATH):
        p = profile_by_key.get(key(row))
        if not p:
            continue
        score = to_float(row["score_resid_std"])
        if score is None:
            continue
        merged.append({
            "student_id": row["student_id"],
            "course_id": row["course_id"],
            "name": row["name"],
            "test_date": row["test_date"],
            "grade_level": row["grade_level"],
            "test_family": row["test_family"],
            "phase_strategy": row["phase_strategy"],
            "behavior_profile": p["profile"],
            "combined_strategy": row["phase_strategy"] + " + " + p["profile"],
            "score_resid_std": score,
        })

    buckets = defaultdict(list)
    for row in merged:
        buckets[row["combined_strategy"]].append(row)
    cis = bootstrap(merged, "combined_strategy")
    out = []
    for strategy, rows in buckets.items():
        if len(rows) < MIN_ROWS:
            continue
        out.append({
            "combined_strategy": strategy,
            "rows": len(rows),
            "students": len({r["student_id"] for r in rows}),
            "assessments": len({"|".join([r["course_id"], r["name"], r["test_date"]]) for r in rows}),
            "score_resid_std_mean": fmt(mean([r["score_resid_std"] for r in rows])),
            "score_resid_std_sd": fmt(sd([r["score_resid_std"] for r in rows])),
            "score_resid_ci_low": cis.get(strategy, {}).get("ci_low", ""),
            "score_resid_ci_high": cis.get(strategy, {}).get("ci_high", ""),
            "top_test_families": "; ".join(f"{k}:{v}" for k, v in Counter(r["test_family"] for r in rows).most_common(4)),
            "top_grades": "; ".join(f"{k}:{v}" for k, v in Counter(r["grade_level"] for r in rows).most_common(4)),
        })
    out.sort(key=lambda r: float(r["score_resid_std_mean"]), reverse=True)
    write_csv(OUT / "combined_strategy_profile_summary_v1.csv", list(out[0].keys()), out)

    report = []
    report.append("# Combined Temporal Strategy And Behavior Profile V1")
    report.append("")
    report.append("## Design")
    report.append("- Merges temporal phase strategies with behavior-profile clusters at the local row level.")
    report.append("- Reports only aggregate combinations with at least 100 rows.")
    report.append("- Outcome is assessment fixed-effect residual score in SD units.")
    report.append("")
    report.append("## Strongest Combined Strategies")
    for row in out[:20]:
        report.append(
            f"- {row['combined_strategy']}: rows={int(row['rows']):,}, students={int(row['students']):,}, "
            f"score_resid={float(row['score_resid_std_mean']):+.3f} "
            f"CI [{float(row['score_resid_ci_low']):+.3f}, {float(row['score_resid_ci_high']):+.3f}]"
        )
    report.append("")
    report.append("## Interpretation")
    report.append("- This table helps separate sustained strategy from behavior-type composition.")
    report.append("- Combinations with positive residuals and enough rows are candidates for the paper's strategy typology figure.")
    report.append("- Small high-performing combinations should be treated as hypothesis-generating only.")
    (REPORTS / "combined_strategy_profiles_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
