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

SEED = 20260519
K = 4
N_INIT = 12
MAX_ITER = 40
BOOTSTRAPS = 150

FEATURES = [
    "log_events_m3",
    "log_active_days_m3",
    "navigation_rate_m3",
    "memo_rate_m3",
    "marker_rate_m3",
    "content_session_rate_m3",
]


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


def add_features(row):
    events = to_int(row.get("events_m3"))
    active_days = to_int(row.get("active_days_m3"))
    navigation = to_int(row.get("navigation_m3"))
    memo = to_int(row.get("memo_m3"))
    marker = to_int(row.get("marker_m3"))
    content_session = to_int(row.get("content_session_m3"))
    denom = events if events > 0 else 1
    row["y"] = to_float(row.get("score_normalized_0_1"))
    row["assessment_id"] = "|".join([row["course_id"], row["name"], row["test_date"]])
    row["log_events_m3"] = math.log1p(events)
    row["log_active_days_m3"] = math.log1p(active_days)
    row["navigation_rate_m3"] = navigation / denom
    row["memo_rate_m3"] = memo / denom
    row["marker_rate_m3"] = marker / denom
    row["content_session_rate_m3"] = content_session / denom
    row["has_xapi_m3"] = events > 0


def assessment_residualize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["assessment_id"]].append(row)
    kept = []
    for group_rows in groups.values():
        if len(group_rows) < 20:
            continue
        y_mean = mean([r["y"] for r in group_rows])
        for row in group_rows:
            rr = dict(row)
            rr["score_resid"] = row["y"] - y_mean
            kept.append(rr)
    scale = sd([r["score_resid"] for r in kept])
    for row in kept:
        row["score_resid_std"] = row["score_resid"] / scale if scale > 0 else 0.0
    return kept


def standardize_matrix(rows, features):
    stats = {}
    matrix = []
    for feature in features:
        vals = [r[feature] for r in rows]
        stats[feature] = (mean(vals), sd(vals))
    for row in rows:
        matrix.append([
            (row[feature] - stats[feature][0]) / stats[feature][1] if stats[feature][1] > 1e-12 else 0.0
            for feature in features
        ])
    return matrix, stats


def dist2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def kmeans(matrix, k, rng):
    centers = [matrix[i][:] for i in rng.sample(range(len(matrix)), k)]
    assignments = [-1] * len(matrix)
    for _ in range(MAX_ITER):
        changed = False
        for i, point in enumerate(matrix):
            cluster = min(range(k), key=lambda c: dist2(point, centers[c]))
            if assignments[i] != cluster:
                assignments[i] = cluster
                changed = True
        new_centers = [[0.0 for _ in matrix[0]] for _ in range(k)]
        counts = [0] * k
        for point, cluster in zip(matrix, assignments):
            counts[cluster] += 1
            for j, value in enumerate(point):
                new_centers[cluster][j] += value
        for c in range(k):
            if counts[c] == 0:
                new_centers[c] = matrix[rng.randrange(len(matrix))][:]
            else:
                new_centers[c] = [v / counts[c] for v in new_centers[c]]
        centers = new_centers
        if not changed:
            break
    sse = sum(dist2(point, centers[cluster]) for point, cluster in zip(matrix, assignments))
    return assignments, centers, sse


def best_kmeans(matrix):
    best = None
    rng = random.Random(SEED)
    for _ in range(N_INIT):
        result = kmeans(matrix, K, rng)
        if best is None or result[2] < best[2]:
            best = result
    return best


def profile_names(rows, assignments, centers):
    cluster_rows = defaultdict(list)
    for row, cluster in zip(rows, assignments):
        cluster_rows[cluster].append(row)
    profile = {}
    remaining = set(cluster_rows)

    marker_cluster = max(remaining, key=lambda c: mean([r["marker_rate_m3"] for r in cluster_rows[c]]))
    profile[marker_cluster] = "high_volume_marker_intensive"
    remaining.remove(marker_cluster)

    memo_cluster = max(remaining, key=lambda c: mean([r["memo_rate_m3"] for r in cluster_rows[c]]))
    profile[memo_cluster] = "memo_intensive"
    remaining.remove(memo_cluster)

    nav_cluster = max(remaining, key=lambda c: mean([r["navigation_rate_m3"] for r in cluster_rows[c]]))
    profile[nav_cluster] = "distributed_navigation"
    remaining.remove(nav_cluster)

    for c in remaining:
        profile[c] = "low_regular_activity"
    return profile


def summarize_profiles(rows):
    buckets = defaultdict(list)
    for row in rows:
        buckets[row["profile"]].append(row)
    out = []
    for profile, group in buckets.items():
        out.append({
            "profile": profile,
            "rows": len(group),
            "students": len({r["student_id"] for r in group}),
            "assessments": len({r["assessment_id"] for r in group}),
            "score_resid_std_mean": fmt(mean([r["score_resid_std"] for r in group])),
            "score_resid_std_sd": fmt(sd([r["score_resid_std"] for r in group])),
            "score_norm_mean": fmt(mean([r["y"] for r in group])),
            "events_m3_mean": fmt(mean([to_int(r["events_m3"]) for r in group]), 2),
            "active_days_m3_mean": fmt(mean([to_int(r["active_days_m3"]) for r in group]), 2),
            "navigation_rate_m3_mean": fmt(mean([r["navigation_rate_m3"] for r in group])),
            "memo_rate_m3_mean": fmt(mean([r["memo_rate_m3"] for r in group])),
            "marker_rate_m3_mean": fmt(mean([r["marker_rate_m3"] for r in group])),
            "content_session_rate_m3_mean": fmt(mean([r["content_session_rate_m3"] for r in group])),
            "top_test_families": "; ".join(f"{k}:{v}" for k, v in Counter(r["test_family"] for r in group).most_common(4)),
            "top_grades": "; ".join(f"{k}:{v}" for k, v in Counter(r["grade_level"] for r in group).most_common(4)),
        })
    return sorted(out, key=lambda r: float(r["score_resid_std_mean"]), reverse=True)


def bootstrap_profile_means(rows):
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
            buckets[row["profile"]].append(row["score_resid_std"])
        for profile, vals in buckets.items():
            estimates[profile].append(mean(vals))
    out = {}
    for profile, vals in estimates.items():
        out[profile] = {
            "score_resid_ci_low": fmt(percentile(vals, 0.025)),
            "score_resid_ci_high": fmt(percentile(vals, 0.975)),
            "bootstraps": len(vals),
        }
    return out


def main():
    candidates = {
        (r["grade_level"], r["course_subject"], r["test_family"])
        for r in read_csv(CANDIDATE_PATH)
        if r.get("paper_candidate_flag") == "strong_candidate"
    }
    rows = []
    for row in read_csv(MATRIX_PATH):
        key = (row["grade_level"], row["course_subject"], row["test_family"])
        if key not in candidates:
            continue
        if row.get("score_validity_flag") != "valid" or row.get("classification_confidence") == "low":
            continue
        add_features(row)
        if row["y"] is not None:
            rows.append(row)

    residual_rows = assessment_residualize(rows)
    xapi_rows = [r for r in residual_rows if r["has_xapi_m3"]]
    no_xapi_rows = [r for r in residual_rows if not r["has_xapi_m3"]]
    matrix, stats = standardize_matrix(xapi_rows, FEATURES)
    assignments, centers, sse = best_kmeans(matrix)
    names = profile_names(xapi_rows, assignments, centers)
    for row, cluster in zip(xapi_rows, assignments):
        row["cluster"] = cluster
        row["profile"] = names[cluster]
    for row in no_xapi_rows:
        row["cluster"] = ""
        row["profile"] = "no_same_course_xapi"

    profile_rows = xapi_rows + no_xapi_rows
    summaries = summarize_profiles(profile_rows)
    cis = bootstrap_profile_means(profile_rows)
    for row in summaries:
        row.update(cis.get(row["profile"], {"score_resid_ci_low": "", "score_resid_ci_high": "", "bootstraps": 0}))
    write_csv(OUT / "behavior_profile_summary_v1.csv", list(summaries[0].keys()), summaries)

    assigned_local = []
    for row in profile_rows:
        assigned_local.append({
            "student_id": row["student_id"],
            "course_id": row["course_id"],
            "test_date": row["test_date"],
            "name": row["name"],
            "grade_level": row["grade_level"],
            "course_subject": row["course_subject"],
            "test_family": row["test_family"],
            "profile": row["profile"],
            "score_resid_std": fmt(row["score_resid_std"]),
            "events_m3": row["events_m3"],
            "active_days_m3": row["active_days_m3"],
        })
    write_csv(OUT / "behavior_profile_assignments_local_only.csv", list(assigned_local[0].keys()), assigned_local)

    report = []
    report.append("# Behavior Profiles V1")
    report.append("")
    report.append("## Scope")
    report.append("- Strong candidate cells only, valid outcomes only.")
    report.append("- Profiles use 3-month same-course xAPI features.")
    report.append("- Outcome comparison uses assessment fixed-effect residuals, so profiles are compared within the same course/test/date.")
    report.append("- Row-level profile assignments remain local only.")
    report.append("")
    report.append("## Coverage")
    report.append(f"- rows after assessment fixed-effect filtering: {len(profile_rows):,}")
    report.append(f"- rows with same-course xAPI used in k-means: {len(xapi_rows):,}")
    report.append(f"- rows without same-course xAPI kept as separate profile: {len(no_xapi_rows):,}")
    report.append(f"- k-means clusters: {K}, starts: {N_INIT}, SSE: {sse:.2f}")
    report.append("")
    report.append("## Profile Summary")
    for row in summaries:
        report.append(
            f"- {row['profile']}: rows={int(row['rows']):,}, students={int(row['students']):,}, "
            f"score_resid={float(row['score_resid_std_mean']):+.3f} "
            f"CI [{float(row['score_resid_ci_low']):+.3f}, {float(row['score_resid_ci_high']):+.3f}], "
            f"active_days_mean={float(row['active_days_m3_mean']):.2f}, "
            f"events_mean={float(row['events_m3_mean']):.1f}, "
            f"memo_rate={float(row['memo_rate_m3_mean']):.3f}, "
            f"navigation_rate={float(row['navigation_rate_m3_mean']):.3f}"
        )
    report.append("")
    report.append("## Interpretation")
    report.append("- Profiles are descriptive strategy groups, not causal mechanisms.")
    report.append("- A profile is paper-relevant only if it is interpretable, common enough, and has a stable assessment-residual score difference.")
    report.append("- This profile layer can support a stronger narrative than coefficients alone: regular/distributed engagement appears more valuable than raw click volume.")
    (REPORTS / "behavior_profiles_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
