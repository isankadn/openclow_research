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

TARGET_FAMILIES = ["course_embedded", "school_regular_exam", "unit_or_chapter_test", "external_benesse"]
WINDOWS = ["m3", "m6", "m12"]
FEATURES = ["log_events", "log_active_days", "navigation_rate", "memo_rate", "marker_rate", "content_session_rate"]


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


def add_window_features(row, window):
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
    out["student_course_id"] = "|".join([row["student_id"], row["course_id"]])
    out["log_events"] = math.log1p(events)
    out["log_active_days"] = math.log1p(active_days)
    out["navigation_rate"] = navigation / denom
    out["memo_rate"] = memo / denom
    out["marker_rate"] = marker / denom
    out["content_session_rate"] = content_session / denom
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

    variable_subjects = set()
    for sid, srows in by_subject.items():
        for feature in features:
            if max(r[feature] for r in srows) - min(r[feature] for r in srows) > 1e-12:
                variable_subjects.add(sid)
                break
    return [row for row in kept if row[subject_key] in variable_subjects]


def two_way_residuals(rows, fields, subject_key, iterations=45):
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


def fit_model(rows, features, subject_key):
    identified = filter_identified(rows, features, subject_key)
    if len(identified) < 200:
        raise ValueError("too few identified rows")
    fields = ["y"] + features
    residuals = two_way_residuals(identified, fields, subject_key)
    y = standardize(residuals["y"])
    if y is None:
        raise ValueError("no outcome variance")
    x_cols = []
    used = []
    for feature in features:
        z = standardize(residuals[feature])
        if z is not None:
            x_cols.append(z)
            used.append(feature)
    if not x_cols:
        raise ValueError("no predictor variance")
    x_matrix = [list(vals) for vals in zip(*x_cols)]
    betas, xtx = ols(y, x_matrix)
    inv_xtx = mat_inverse(xtx)
    resid = [yi - sum(b * xi for b, xi in zip(betas, xs)) for yi, xs in zip(y, x_matrix)]

    # Keep student-level clustering for comparability with earlier models.
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
            vcov[i][j] = sum(
                inv_xtx[i][k] * meat[k][l] * inv_xtx[l][j]
                for k in range(len(betas)) for l in range(len(betas))
            )
    g = len(cluster_scores)
    n = len(identified)
    p = len(betas)
    if g > 1 and n > p:
        factor = (g / (g - 1)) * ((n - 1) / (n - p))
        vcov = [[v * factor for v in row] for row in vcov]
    ses = [math.sqrt(max(vcov[i][i], 0.0)) for i in range(len(betas))]
    return dict(zip(used, betas)), dict(zip(used, ses)), identified


def family_filter(rows, family):
    if family == "course_embedded":
        return [r for r in rows if r["test_family"] in {"school_regular_exam", "unit_or_chapter_test"}]
    return [r for r in rows if r["test_family"] == family]


def main():
    candidate_keys = {
        (r["grade_level"], r["course_subject"], r["test_family"])
        for r in read_csv(CANDIDATE_PATH)
        if r.get("paper_candidate_flag") == "strong_candidate"
    }
    source = []
    for row in read_csv(MATRIX_PATH):
        key = (row["grade_level"], row["course_subject"], row["test_family"])
        if key not in candidate_keys:
            continue
        if row.get("score_validity_flag") != "valid" or row.get("classification_confidence") == "low":
            continue
        source.append(row)

    output = []
    for family in TARGET_FAMILIES:
        for window in WINDOWS:
            rows = [add_window_features(row, window) for row in family_filter(source, family)]
            rows = [row for row in rows if row["y"] is not None]
            for model, subject_key, features in [
                ("student_assessment_fe_active_days", "student_id", ["log_active_days"]),
                ("student_assessment_fe_adjusted", "student_id", FEATURES),
                ("student_course_assessment_fe_active_days", "student_course_id", ["log_active_days"]),
                ("student_course_assessment_fe_adjusted", "student_course_id", FEATURES),
            ]:
                try:
                    betas, ses, identified = fit_model(rows, features, subject_key)
                except ValueError:
                    continue
                for feature in features:
                    if feature not in betas:
                        continue
                    beta = betas[feature]
                    se = ses[feature]
                    output.append({
                        "scope": family,
                        "window": window,
                        "model": model,
                        "feature": feature,
                        "beta_std": fmt(beta),
                        "se_cluster_student": fmt(se),
                        "ci_low": fmt(beta - 1.96 * se),
                        "ci_high": fmt(beta + 1.96 * se),
                        "p_cluster": fmt(normal_p(beta, se)),
                        "identified_rows": len(identified),
                        "students": len({r["student_id"] for r in identified}),
                        "student_courses": len({r["student_course_id"] for r in identified}),
                        "assessments": len({r["assessment_id"] for r in identified}),
                    })

    out_path = OUT / "student_course_fe_robustness_v1.csv"
    write_csv(out_path, list(output[0].keys()), output)

    report = []
    report.append("# Student-Course Fixed-Effect Robustness V1")
    report.append("")
    report.append("## Purpose")
    report.append("- Tests the main active-days mechanism under a stricter fixed-effect structure.")
    report.append("- Baseline model: student fixed effects + assessment-occasion fixed effects.")
    report.append("- Stricter model: student-course fixed effects + assessment-occasion fixed effects.")
    report.append("- Coefficients are standardized residual associations; standard errors are clustered by student.")
    report.append("")
    report.append("## Main Active-Days Comparison")
    for scope in TARGET_FAMILIES:
        report.append(f"### {scope}")
        for window in WINDOWS:
            rows = [
                r for r in output
                if r["scope"] == scope and r["window"] == window and r["feature"] == "log_active_days"
                and r["model"] in {"student_assessment_fe_adjusted", "student_course_assessment_fe_adjusted"}
            ]
            for r in rows:
                label = "student FE" if r["model"] == "student_assessment_fe_adjusted" else "student-course FE"
                report.append(
                    f"- {window} / {label}: beta={float(r['beta_std']):+.3f}, "
                    f"CI [{float(r['ci_low']):+.3f}, {float(r['ci_high']):+.3f}], "
                    f"p={float(r['p_cluster']):.3f}, rows={int(r['identified_rows']):,}, "
                    f"students={int(r['students']):,}, student-courses={int(r['student_courses']):,}, "
                    f"assessments={int(r['assessments']):,}"
                )
        report.append("")
    report.append("## Interpretation")
    report.append("- Student-course fixed effects remove stable student-by-course differences, such as a learner's persistent strength or engagement in a particular course.")
    report.append("- A positive active-days coefficient under this stricter model supports the interpretation that within-student-course changes in regular pre-test Bookroll activity align with outcome changes.")
    report.append("- The model remains observational: it does not remove time-varying preparation, teacher support, offline study, or exam-specific effort.")
    (REPORTS / "student_course_fe_robustness_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
