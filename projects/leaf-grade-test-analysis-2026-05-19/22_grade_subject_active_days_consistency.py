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

TARGET_FAMILIES = {"school_regular_exam", "unit_or_chapter_test"}
WINDOWS = ["m3", "m6", "m12"]
FEATURES = ["log_events", "log_active_days", "navigation_rate", "memo_rate", "marker_rate", "content_session_rate"]
MIN_IDENTIFIED_ROWS = 180
MIN_STUDENTS = 80
MIN_ASSESSMENTS = 6


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


def fmt(value, digits=5):
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def normal_p(beta, se):
    if se <= 0:
        return 1.0
    return math.erfc(abs(beta / se) / math.sqrt(2))


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


def add_features(row, window):
    events = to_int(row.get(f"events_{window}"))
    active_days = to_int(row.get(f"active_days_{window}"))
    navigation = to_int(row.get(f"navigation_{window}"))
    memo = to_int(row.get(f"memo_{window}"))
    marker = to_int(row.get(f"marker_{window}"))
    content_session = to_int(row.get(f"content_session_{window}"))
    denom = events if events > 0 else 1
    out = dict(row)
    out["y"] = to_float(row["score_normalized_0_1"])
    out["assessment_id"] = "|".join([row["course_id"], row["name"], row["test_date"]])
    out["log_events"] = math.log1p(events)
    out["log_active_days"] = math.log1p(active_days)
    out["navigation_rate"] = navigation / denom
    out["memo_rate"] = memo / denom
    out["marker_rate"] = marker / denom
    out["content_session_rate"] = content_session / denom
    return out


def filter_identified(rows):
    by_student = defaultdict(list)
    by_assessment = defaultdict(list)
    for row in rows:
        by_student[row["student_id"]].append(row)
        by_assessment[row["assessment_id"]].append(row)
    kept = [
        row for row in rows
        if len(by_student[row["student_id"]]) >= 2 and len(by_assessment[row["assessment_id"]]) >= 20
    ]
    by_student = defaultdict(list)
    for row in kept:
        by_student[row["student_id"]].append(row)
    variable_students = set()
    for sid, srows in by_student.items():
        if max(r["log_active_days"] for r in srows) - min(r["log_active_days"] for r in srows) > 1e-12:
            variable_students.add(sid)
    return [row for row in kept if row["student_id"] in variable_students]


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


def fit_twfe(rows):
    rows = filter_identified(rows)
    if len(rows) < MIN_IDENTIFIED_ROWS:
        raise ValueError("too few rows")
    if len({r["student_id"] for r in rows}) < MIN_STUDENTS:
        raise ValueError("too few students")
    if len({r["assessment_id"] for r in rows}) < MIN_ASSESSMENTS:
        raise ValueError("too few assessments")
    residuals = two_way_residuals(rows, ["y"] + FEATURES)
    y = standardize(residuals["y"])
    if y is None:
        raise ValueError("no outcome variance")
    x_cols = []
    used = []
    for feature in FEATURES:
        z = standardize(residuals[feature])
        if z is not None:
            x_cols.append(z)
            used.append(feature)
    x_matrix = [list(vals) for vals in zip(*x_cols)]
    betas, xtx = ols(y, x_matrix)
    inv_xtx = mat_inverse(xtx)
    residual = [yi - sum(beta * xi for beta, xi in zip(betas, xs)) for yi, xs in zip(y, x_matrix)]
    cluster_scores = defaultdict(lambda: [0.0] * len(betas))
    for row, xs, u in zip(rows, x_matrix, residual):
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
    ses = dict(zip(used, [math.sqrt(max(vcov[i][i], 0.0)) for i in range(len(betas))]))
    return dict(zip(used, betas)), ses, rows


def main():
    candidate_keys = {
        (r["grade_level"], r["course_subject"], r["test_family"])
        for r in read_csv(CANDIDATE_PATH)
        if r.get("paper_candidate_flag") == "strong_candidate"
    }
    base = []
    for row in read_csv(MATRIX_PATH):
        key = (row["grade_level"], row["course_subject"], row["test_family"])
        if key not in candidate_keys:
            continue
        if row["test_family"] not in TARGET_FAMILIES:
            continue
        if row.get("score_validity_flag") != "valid" or row.get("classification_confidence") == "low":
            continue
        base.append(row)

    group_keys = sorted({(r["grade_level"], r["course_subject"], r["test_family"]) for r in base})
    out = []
    for grade, subject, family in group_keys:
        for window in WINDOWS:
            rows = [
                add_features(row, window)
                for row in base
                if row["grade_level"] == grade and row["course_subject"] == subject and row["test_family"] == family
            ]
            rows = [r for r in rows if r["y"] is not None]
            try:
                betas, ses, identified = fit_twfe(rows)
            except ValueError as exc:
                out.append({
                    "grade_level": grade, "course_subject": subject, "test_family": family,
                    "window": window, "status": f"skipped:{exc}", "feature": "log_active_days",
                    "beta_std": "", "se_cluster_student": "", "ci_low": "", "ci_high": "", "p_cluster": "",
                    "identified_rows": 0, "students": 0, "assessments": 0,
                })
                continue
            beta = betas["log_active_days"]
            se = ses["log_active_days"]
            out.append({
                "grade_level": grade, "course_subject": subject, "test_family": family,
                "window": window, "status": "estimated", "feature": "log_active_days",
                "beta_std": fmt(beta), "se_cluster_student": fmt(se),
                "ci_low": fmt(beta - 1.96 * se), "ci_high": fmt(beta + 1.96 * se),
                "p_cluster": fmt(normal_p(beta, se)),
                "identified_rows": len(identified),
                "students": len({r["student_id"] for r in identified}),
                "assessments": len({r["assessment_id"] for r in identified}),
            })
    write_csv(OUT / "grade_subject_active_days_consistency_v1.csv", list(out[0].keys()), out)

    estimated = [r for r in out if r["status"] == "estimated"]
    report = []
    report.append("# Grade/Subject Active-Days Consistency V1")
    report.append("")
    report.append("## Design")
    report.append("- Course-embedded assessments only: regular exams and unit/chapter tests.")
    report.append("- Separate two-way fixed-effect models by grade + subject + test family.")
    report.append("- Each model adjusts for event volume and behavior composition; reported coefficient is log active days.")
    report.append("- This tests whether the mechanism is grade-, subject-, or assessment-family-local rather than uniform across all cells.")
    report.append("")
    report.append("## Estimated Cells")
    for row in estimated:
        report.append(
            f"- {row['grade_level']} {row['course_subject']} {row['test_family']} {row['window']}: "
            f"beta={float(row['beta_std']):+.3f}, CI [{float(row['ci_low']):+.3f}, {float(row['ci_high']):+.3f}], "
            f"p={float(row['p_cluster']):.3f}"
        )
    report.append("")
    report.append("## Interpretation")
    pos = [r for r in estimated if float(r["beta_std"]) > 0]
    sig_pos = [r for r in estimated if float(r["ci_low"]) > 0]
    report.append(f"- Positive estimated cells: {len(pos)} / {len(estimated)}.")
    report.append(f"- Clearly positive cells with CI above zero: {len(sig_pos)} / {len(estimated)}.")
    report.append("- If 中1/中2/中3 mathematics are consistently positive, the result is not driven by one grade.")
    (REPORTS / "grade_subject_active_days_consistency_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
