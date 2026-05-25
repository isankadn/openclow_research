#!/usr/bin/env python3
import csv
import importlib.util
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"

spec = importlib.util.spec_from_file_location("subject_models", ROOT / "35_subject_specific_refined_models.py")
subject_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject_models)

FEATURES = subject_models.ADJUSTED_FEATURES


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def fnum(value):
    return f"{value:.6f}"


def p_value(beta, se):
    if se <= 0:
        return 1.0
    return math.erfc(abs(beta / se) / math.sqrt(2))


def vcov_for_cluster(identified, x_matrix, resid, inv_xtx, cluster_key):
    p = len(inv_xtx)
    cluster_scores = defaultdict(lambda: [0.0] * p)
    for row, xs, u in zip(identified, x_matrix, resid):
        if cluster_key == "student":
            key = row["student_id"]
        elif cluster_key == "assessment":
            key = row["assessment_id"]
        elif cluster_key == "student_assessment":
            key = row["student_id"] + "|" + row["assessment_id"]
        else:
            raise ValueError(cluster_key)
        score = cluster_scores[key]
        for j, x in enumerate(xs):
            score[j] += x * u

    meat = [[0.0 for _ in range(p)] for _ in range(p)]
    for score in cluster_scores.values():
        for i in range(p):
            for j in range(p):
                meat[i][j] += score[i] * score[j]

    vcov = [[0.0 for _ in range(p)] for _ in range(p)]
    for i in range(p):
        for j in range(p):
            vcov[i][j] = sum(
                inv_xtx[i][k] * meat[k][l] * inv_xtx[l][j]
                for k in range(p) for l in range(p)
            )

    g = len(cluster_scores)
    n = len(identified)
    if g > 1 and n > p:
        factor = (g / (g - 1)) * ((n - 1) / (n - p))
        vcov = [[v * factor for v in row] for row in vcov]
    return vcov, g


def add_vcov(a, b, sign=1.0):
    return [[a[i][j] + sign * b[i][j] for j in range(len(a))] for i in range(len(a))]


def fit_with_cluster_sensitivity(base_rows, scope, subject):
    rows = [
        subject_models.add_features(r, "m3")
        for r in base_rows
        if r["test_family"] == "school_regular_exam" and r["course_subject"] == subject
    ]
    rows = [r for r in rows if r["y"] is not None]
    identified = subject_models.filter_identified(rows, FEATURES, "student_course_id")
    fields = ["y"] + FEATURES
    residuals = subject_models.two_way_residuals(identified, fields, "student_course_id")
    y = subject_models.standardize(residuals["y"])
    x_cols = []
    used = []
    for feature in FEATURES:
        z = subject_models.standardize(residuals[feature])
        if z is not None:
            x_cols.append(z)
            used.append(feature)
    x_matrix = [list(vals) for vals in zip(*x_cols)]
    betas, xtx = subject_models.ols(y, x_matrix)
    inv_xtx = subject_models.mat_inverse(xtx)
    resid = [yi - sum(b * xi for b, xi in zip(betas, xs)) for yi, xs in zip(y, x_matrix)]

    v_student, g_student = vcov_for_cluster(identified, x_matrix, resid, inv_xtx, "student")
    v_assessment, g_assessment = vcov_for_cluster(identified, x_matrix, resid, inv_xtx, "assessment")
    v_pair, g_pair = vcov_for_cluster(identified, x_matrix, resid, inv_xtx, "student_assessment")
    v_two_way = add_vcov(add_vcov(v_student, v_assessment, 1.0), v_pair, -1.0)

    out = []
    for i, feature in enumerate(used):
        beta = betas[i]
        se_student = math.sqrt(max(v_student[i][i], 0.0))
        se_assessment = math.sqrt(max(v_assessment[i][i], 0.0))
        se_two_way = math.sqrt(max(v_two_way[i][i], 0.0))
        out.append({
            "scope": scope,
            "subject": subject,
            "feature": feature,
            "beta_std": fnum(beta),
            "se_cluster_student": fnum(se_student),
            "p_cluster_student": fnum(p_value(beta, se_student)),
            "se_cluster_assessment": fnum(se_assessment),
            "p_cluster_assessment": fnum(p_value(beta, se_assessment)),
            "se_two_way_student_assessment": fnum(se_two_way),
            "p_two_way_student_assessment": fnum(p_value(beta, se_two_way)),
            "rows": len(identified),
            "students": len({r["student_id"] for r in identified}),
            "student_courses": len({r["student_course_id"] for r in identified}),
            "assessments": len({r["assessment_id"] for r in identified}),
            "student_clusters": g_student,
            "assessment_clusters": g_assessment,
            "student_assessment_clusters": g_pair,
        })
    return out


def main():
    candidate_keys = {
        (r["grade_level"], r["course_subject"], r["test_family"])
        for r in read_csv(OUT / "candidate_analysis_cells_v2.csv")
        if r.get("paper_candidate_flag") == "strong_candidate"
    }
    base_rows = []
    for row in read_csv(OUT / "score_xapi_same_course_sufficiency_local_only.csv"):
        key = (row["grade_level"], row["course_subject"], row["test_family"])
        if key not in candidate_keys:
            continue
        if row.get("score_validity_flag") != "valid" or row.get("classification_confidence") == "low":
            continue
        base_rows.append(row)

    rows = fit_with_cluster_sensitivity(base_rows, "school_regular_exam", "数学")
    out_path = OUT / "key_cluster_sensitivity_v1.csv"
    write_csv(out_path, list(rows[0].keys()), rows)

    active = next(r for r in rows if r["feature"] == "log_active_days")
    events = next(r for r in rows if r["feature"] == "log_events")
    report = [
        "# Key Cluster Sensitivity V1",
        "",
        "## Design",
        "- Scope: mathematics regular exams.",
        "- Model: adjusted 3-month student-course + assessment fixed effects.",
        "- Sensitivity compares student-clustered, assessment-clustered, and two-way student + assessment clustered standard errors.",
        "",
        "## Key Results",
        f"- log_active_days beta={float(active['beta_std']):+.3f}; student-cluster SE={float(active['se_cluster_student']):.3f}, p={float(active['p_cluster_student']):.3f}; two-way SE={float(active['se_two_way_student_assessment']):.3f}, p={float(active['p_two_way_student_assessment']):.3f}.",
        f"- log_events beta={float(events['beta_std']):+.3f}; student-cluster SE={float(events['se_cluster_student']):.3f}, p={float(events['p_cluster_student']):.3f}; two-way SE={float(events['se_two_way_student_assessment']):.3f}, p={float(events['p_two_way_student_assessment']):.3f}.",
        "",
        "## Interpretation",
        "- The main active-days result remains positive under two-way student + assessment clustered standard errors.",
        "- Event volume remains negative under the same sensitivity, but should be interpreted as event intensity conditional on regularity and behavior composition.",
    ]
    (REPORTS / "key_cluster_sensitivity_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
