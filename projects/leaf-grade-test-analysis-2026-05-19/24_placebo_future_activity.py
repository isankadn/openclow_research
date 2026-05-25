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
CANDIDATE_PATH = OUT / "candidate_analysis_cells_v2.csv"
OLD_MONTHLY_PATH = OUT / "xapi_old_content_monthly_local_only.csv"
NEW_MONTHLY_PATH = OUT / "xapi_new_context_monthly_local_only.csv"
OLD_BRIDGE_PATH = OUT / "old_bookroll_content_course_bridge_unique.csv"

TARGET_FAMILIES = {"school_regular_exam", "unit_or_chapter_test"}
FEATURES = ["log_events", "log_active_days", "navigation_rate", "memo_rate", "marker_rate", "content_session_rate"]


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


def fmt(value, digits=5):
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def normal_p(beta, se):
    if se <= 0:
        return 1.0
    return math.erfc(abs(beta / se) / math.sqrt(2))


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


def standardize(values):
    s = sd(values)
    if s <= 1e-12:
        return None
    m = mean(values)
    return [(v - m) / s for v in values]


def build_course_month_index(target_students, target_courses):
    idx = defaultdict(lambda: defaultdict(int))
    content_to_course = {
        r["contents_id"]: r["mapped_course_id"]
        for r in read_csv(OLD_BRIDGE_PATH)
        if r.get("mapped_course_id") in target_courses
    }
    for r in read_csv(OLD_MONTHLY_PATH):
        sid = r["student_id"]
        if sid not in target_students:
            continue
        course_id = content_to_course.get(r["contents_id"])
        if course_id not in target_courses:
            continue
        key = (sid, course_id, r["event_month"])
        for src, dst in [
            ("events_total", "events"), ("active_days", "active_days"),
            ("navigation_events", "navigation"), ("memo_events", "memo"),
            ("marker_events", "marker"), ("content_session_events", "content_session"),
        ]:
            idx[key][dst] += to_int(r[src])
    if NEW_MONTHLY_PATH.exists():
        for r in read_csv(NEW_MONTHLY_PATH):
            sid = r["student_id"]
            course_id = r["course_id"]
            if sid not in target_students or course_id not in target_courses:
                continue
            key = (sid, course_id, r["event_month"])
            for src, dst in [
                ("events_total", "events"), ("active_days", "active_days"),
                ("navigation_events", "navigation"), ("memo_events", "memo"),
                ("marker_events", "marker"), ("content_session_events", "content_session"),
            ]:
                idx[key][dst] += to_int(r[src])
    return idx


def window_sum(index, sid, course_id, test_month, offsets):
    base = month_index(test_month)
    out = defaultdict(int)
    for offset in offsets:
        vals = index.get((sid, course_id, ym_from_index(base + offset)), {})
        for k, v in vals.items():
            out[k] += int(v)
    return out


def add_window_features(row, vals, label):
    events = vals.get("events", 0)
    denom = events if events > 0 else 1
    out = dict(row)
    out["window_type"] = label
    out["y"] = to_float(row["score_normalized_0_1"])
    out["assessment_id"] = "|".join([row["course_id"], row["name"], row["test_date"]])
    out["log_events"] = math.log1p(events)
    out["log_active_days"] = math.log1p(vals.get("active_days", 0))
    out["navigation_rate"] = vals.get("navigation", 0) / denom
    out["memo_rate"] = vals.get("memo", 0) / denom
    out["marker_rate"] = vals.get("marker", 0) / denom
    out["content_session_rate"] = vals.get("content_session", 0) / denom
    out["has_activity"] = 1 if events > 0 else 0
    return out


def filter_identified(rows):
    by_student = defaultdict(list)
    by_assessment = defaultdict(list)
    for row in rows:
        by_student[row["student_id"]].append(row)
        by_assessment[row["assessment_id"]].append(row)
    kept = [r for r in rows if len(by_student[r["student_id"]]) >= 2 and len(by_assessment[r["assessment_id"]]) >= 20]
    by_student = defaultdict(list)
    for row in kept:
        by_student[row["student_id"]].append(row)
    variable = set()
    for sid, srows in by_student.items():
        if max(r["log_active_days"] for r in srows) - min(r["log_active_days"] for r in srows) > 1e-12:
            variable.add(sid)
    return [r for r in kept if r["student_id"] in variable]


def two_way_residuals(rows, fields, iterations=25):
    residuals = {field: [row[field] for row in rows] for field in fields}
    student_groups = defaultdict(list)
    assessment_groups = defaultdict(list)
    for i, row in enumerate(rows):
        student_groups[row["student_id"]].append(i)
        assessment_groups[row["assessment_id"]].append(i)
    for _ in range(iterations):
        for groups in (student_groups, assessment_groups):
            for idxs in groups.values():
                for field in fields:
                    m = mean([residuals[field][i] for i in idxs])
                    for i in idxs:
                        residuals[field][i] -= m
    return residuals


def fit_twfe(rows, features=FEATURES):
    rows = filter_identified(rows)
    fields = ["y"] + features
    residuals = two_way_residuals(rows, fields)
    y = standardize(residuals["y"])
    x_cols = []
    used = []
    for feature in features:
        z = standardize(residuals[feature])
        if z is not None:
            x_cols.append(z)
            used.append(feature)
    x_matrix = [list(vals) for vals in zip(*x_cols)]
    betas, xtx = ols(y, x_matrix)
    inv_xtx = mat_inverse(xtx)
    resid = [yi - sum(b * xi for b, xi in zip(betas, xs)) for yi, xs in zip(y, x_matrix)]
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
    g, n, p = len(cluster_scores), len(rows), len(betas)
    if g > 1 and n > p:
        factor = (g / (g - 1)) * ((n - 1) / (n - p))
        vcov = [[v * factor for v in row] for row in vcov]
    ses = [math.sqrt(max(vcov[i][i], 0.0)) for i in range(len(betas))]
    return dict(zip(used, betas)), dict(zip(used, ses)), rows


def main():
    candidate_keys = {
        (r["grade_level"], r["course_subject"], r["test_family"])
        for r in read_csv(CANDIDATE_PATH)
        if r.get("paper_candidate_flag") == "strong_candidate"
    }
    base = []
    for row in read_csv(MATRIX_PATH):
        key = (row["grade_level"], row["course_subject"], row["test_family"])
        if key not in candidate_keys or row["test_family"] not in TARGET_FAMILIES:
            continue
        if row.get("score_validity_flag") != "valid" or row.get("classification_confidence") == "low":
            continue
        base.append(row)
    idx = build_course_month_index({r["student_id"] for r in base}, {r["course_id"] for r in base})
    rows_by_family_window = defaultdict(list)
    for row in base:
        pre = window_sum(idx, row["student_id"], row["course_id"], row["test_month"], [-3, -2, -1])
        post = window_sum(idx, row["student_id"], row["course_id"], row["test_month"], [1, 2, 3])
        rows_by_family_window[(row["test_family"], "pre_m3")].append(add_window_features(row, pre, "pre_m3"))
        rows_by_family_window[(row["test_family"], "future_m3_placebo")].append(add_window_features(row, post, "future_m3_placebo"))

    out = []
    for (family, window_type), rows in sorted(rows_by_family_window.items()):
        betas, ses, identified = fit_twfe([r for r in rows if r["y"] is not None])
        for feature in FEATURES:
            if feature not in betas:
                continue
            beta, se = betas[feature], ses[feature]
            out.append({
                "test_family": family,
                "window_type": window_type,
                "feature": feature,
                "beta_std": fmt(beta),
                "se_cluster_student": fmt(se),
                "ci_low": fmt(beta - 1.96 * se),
                "ci_high": fmt(beta + 1.96 * se),
                "p_cluster": fmt(normal_p(beta, se)),
                "identified_rows": len(identified),
                "students": len({r["student_id"] for r in identified}),
                "assessments": len({r["assessment_id"] for r in identified}),
                "activity_rows": sum(1 for r in identified if r["has_activity"]),
            })
    write_csv(OUT / "future_activity_placebo_v1.csv", list(out[0].keys()), out)

    report = []
    report.append("# Future-Activity Placebo Check V1")
    report.append("")
    report.append("## Design")
    report.append("- Tests whether future same-course activity after the test predicts the earlier score.")
    report.append("- Pre window: months -3, -2, -1 before test month.")
    report.append("- Future placebo window: months +1, +2, +3 after test month; test month excluded to avoid mixed before/after contamination.")
    report.append("- Student fixed effects + assessment fixed effects, adjusted for behavior composition.")
    report.append("- If future active days resembles the pre-test effect, temporal interpretation is weaker.")
    report.append("")
    for family in sorted(TARGET_FAMILIES):
        report.append(f"## {family}")
        for row in [r for r in out if r["test_family"] == family and r["feature"] == "log_active_days"]:
            report.append(
                f"- {row['window_type']}: beta={float(row['beta_std']):+.3f}, "
                f"CI [{float(row['ci_low']):+.3f}, {float(row['ci_high']):+.3f}], "
                f"p={float(row['p_cluster']):.3f}"
            )
        report.append("")
    report.append("## Interpretation")
    report.append("- The strongest temporal pattern would be positive pre-test active days with weak/null future-placebo active days.")
    report.append("- A positive future-placebo signal would suggest persistent time-varying motivation or post-test continuation rather than a clean pre-test mechanism.")
    (REPORTS / "future_activity_placebo_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
