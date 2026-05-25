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


def mean(vals):
    return sum(vals) / len(vals) if vals else 0.0


def sd(vals):
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))


def fit(rows, outcome_label):
    identified = subject_models.filter_identified(rows, FEATURES, "student_course_id")
    fields = ["y"] + FEATURES
    residuals = subject_models.two_way_residuals(identified, fields, "student_course_id")
    y = subject_models.standardize(residuals["y"])
    x_cols = []
    used = []
    for f in FEATURES:
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
    out = []
    for feature in ["log_active_days", "log_events"]:
        idx = used.index(feature)
        beta = betas[idx]
        se = math.sqrt(max(vcov[idx][idx], 0.0))
        out.append({
            "outcome": outcome_label,
            "feature": feature,
            "beta_std": f"{beta:.6f}",
            "se_cluster_student": f"{se:.6f}",
            "ci_low": f"{beta - 1.96 * se:.6f}",
            "ci_high": f"{beta + 1.96 * se:.6f}",
            "p_cluster": f"{math.erfc(abs(beta / se) / math.sqrt(2)) if se > 0 else 1.0:.6f}",
            "rows": len(identified),
            "students": len({r["student_id"] for r in identified}),
            "student_courses": len({r["student_course_id"] for r in identified}),
            "assessments": len({r["assessment_id"] for r in identified}),
        })
    return out


def main():
    candidate_keys = {
        (r["grade_level"], r["course_subject"], r["test_family"])
        for r in read_csv(OUT / "candidate_analysis_cells_v2.csv")
        if r.get("paper_candidate_flag") == "strong_candidate"
    }
    scoped = []
    for row in read_csv(OUT / "score_xapi_same_course_sufficiency_local_only.csv"):
        key = (row["grade_level"], row["course_subject"], row["test_family"])
        if key not in candidate_keys:
            continue
        if row.get("score_validity_flag") != "valid" or row.get("classification_confidence") == "low":
            continue
        if row["test_family"] == "school_regular_exam" and row["course_subject"] == "数学":
            scoped.append(subject_models.add_features(row, "m3"))

    by_assessment = defaultdict(list)
    for row in scoped:
        by_assessment[row["assessment_id"]].append(row["y"])
    stats = {aid: (mean(vals), sd(vals)) for aid, vals in by_assessment.items()}

    z_rows = []
    for row in scoped:
        m, s = stats[row["assessment_id"]]
        if s <= 1e-12:
            continue
        nr = dict(row)
        nr["y"] = (row["y"] - m) / s
        z_rows.append(nr)

    out = fit(scoped, "normalized_score") + fit(z_rows, "within_assessment_z_score")
    write_csv(OUT / "outcome_scaling_sensitivity_v1.csv", list(out[0].keys()), out)

    active_norm = next(r for r in out if r["outcome"] == "normalized_score" and r["feature"] == "log_active_days")
    active_z = next(r for r in out if r["outcome"] == "within_assessment_z_score" and r["feature"] == "log_active_days")
    report = [
        "# Outcome Scaling Sensitivity V1",
        "",
        "## Scope",
        "- Mathematics regular exams.",
        "- Adjusted 3-month student-course + assessment fixed-effect model.",
        "- Compares the main normalized-score outcome with a within-assessment z-score outcome.",
        "",
        "## Key Result",
        f"- Normalized score: active-days beta={float(active_norm['beta_std']):+.3f}, CI [{float(active_norm['ci_low']):+.3f}, {float(active_norm['ci_high']):+.3f}], rows={int(active_norm['rows']):,}.",
        f"- Within-assessment z-score: active-days beta={float(active_z['beta_std']):+.3f}, CI [{float(active_z['ci_low']):+.3f}, {float(active_z['ci_high']):+.3f}], rows={int(active_z['rows']):,}.",
        "",
        "## Interpretation",
        "- The active-days result remains positive under within-assessment z-score outcome scaling.",
    ]
    (REPORTS / "outcome_scaling_sensitivity_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
