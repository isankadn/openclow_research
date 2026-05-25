#!/usr/bin/env python3
import csv
import math
import os
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

MATRIX_PATH = OUT / "score_xapi_same_course_sufficiency_local_only.csv"
CANDIDATE_PATH = OUT / "candidate_analysis_cells_v2.csv"

WINDOWS = ["m3", "m6", "m12"]
BASE_FEATURES = ["log_events", "log_active_days", "navigation_rate", "memo_rate", "marker_rate", "content_session_rate"]
BOOTSTRAPS = int(os.environ.get("LEAF_TWFE_BOOTSTRAPS", "80"))
SEED = 20260519


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
    return solve_linear(xtx, xty)


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
    out["log_events"] = math.log1p(events)
    out["log_active_days"] = math.log1p(active_days)
    out["navigation_rate"] = navigation / denom
    out["memo_rate"] = memo / denom
    out["marker_rate"] = marker / denom
    out["content_session_rate"] = content_session / denom
    out["has_activity"] = 1.0 if events > 0 else 0.0
    return out


def filter_identified_rows(rows, fields):
    by_student = defaultdict(list)
    by_assessment = defaultdict(list)
    for row in rows:
        by_student[row["student_id"]].append(row)
        by_assessment[row["assessment_id"]].append(row)
    kept = []
    for row in rows:
        if len(by_student[row["student_id"]]) < 2:
            continue
        if len(by_assessment[row["assessment_id"]]) < 20:
            continue
        kept.append(row)
    # Need within-student variation in at least one treatment feature.
    variable_students = set()
    by_student = defaultdict(list)
    for row in kept:
        by_student[row["student_id"]].append(row)
    for sid, srows in by_student.items():
        for field in fields:
            if max(r[field] for r in srows) - min(r[field] for r in srows) > 1e-12:
                variable_students.add(sid)
                break
    return [r for r in kept if r["student_id"] in variable_students]


def two_way_residuals(rows, fields, iterations=40):
    values = {field: [row[field] for row in rows] for field in fields}
    student_groups = defaultdict(list)
    assessment_groups = defaultdict(list)
    for i, row in enumerate(rows):
        student_groups[row["student_id"]].append(i)
        assessment_groups[row["assessment_id"]].append(i)
    residuals = {field: vals[:] for field, vals in values.items()}
    for _ in range(iterations):
        for groups in (student_groups, assessment_groups):
            for idxs in groups.values():
                for field in fields:
                    m = mean([residuals[field][i] for i in idxs])
                    for i in idxs:
                        residuals[field][i] -= m
    return residuals


def fit_twfe(rows, features):
    fields = ["y"] + features
    rows = filter_identified_rows(rows, features)
    if len(rows) < 200:
        raise ValueError("too few identified rows")
    residuals = two_way_residuals(rows, fields)
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
    coefs = ols(y, [list(vals) for vals in zip(*x_cols)])
    return dict(zip(used, coefs)), rows


def bootstrap_rows(rows, rng):
    by_student = defaultdict(list)
    for row in rows:
        by_student[row["student_id"]].append(row)
    students = list(by_student)
    out = []
    for _ in students:
        out.extend(by_student[rng.choice(students)])
    return out


def bootstrap_model(rows, features, seed):
    rng = random.Random(seed)
    estimates = defaultdict(list)
    for _ in range(BOOTSTRAPS):
        try:
            coefs, _ = fit_twfe(bootstrap_rows(rows, rng), features)
        except ValueError:
            continue
        for feature, beta in coefs.items():
            estimates[feature].append(beta)
    return estimates


def estimate_summary(estimates):
    if not estimates:
        return {"ci_low": "", "ci_high": "", "p_boot": "", "bootstraps": 0}
    le_zero = sum(1 for x in estimates if x <= 0) / len(estimates)
    ge_zero = sum(1 for x in estimates if x >= 0) / len(estimates)
    return {
        "ci_low": fmt(percentile(estimates, 0.025)),
        "ci_high": fmt(percentile(estimates, 0.975)),
        "p_boot": fmt(min(1.0, 2 * min(le_zero, ge_zero))),
        "bootstraps": len(estimates),
    }


def main():
    candidate_keys = {
        (r["grade_level"], r["course_subject"], r["test_family"])
        for r in read_csv(CANDIDATE_PATH)
        if r.get("paper_candidate_flag") == "strong_candidate"
    }
    source_rows = []
    for row in read_csv(MATRIX_PATH):
        key = (row["grade_level"], row["course_subject"], row["test_family"])
        if key not in candidate_keys:
            continue
        if row.get("score_validity_flag") != "valid" or row.get("classification_confidence") == "low":
            continue
        source_rows.append(row)

    out = []
    for window in WINDOWS:
        rows = [add_window_features(row, window) for row in source_rows]
        rows = [row for row in rows if row["y"] is not None]
        coefs, identified = fit_twfe(rows, BASE_FEATURES)
        boot = bootstrap_model(rows, BASE_FEATURES, SEED + len(window))
        for feature in BASE_FEATURES:
            if feature not in coefs:
                continue
            out.append({
                "window": window,
                "model": "student_and_assessment_twfe",
                "feature": feature,
                "beta_std": fmt(coefs[feature]),
                **estimate_summary(boot.get(feature, [])),
                "identified_rows": len(identified),
                "students": len({r["student_id"] for r in identified}),
                "assessments": len({r["assessment_id"] for r in identified}),
            })

    # Separate binary activity model: interpretable as within-student difference
    # between assessment occasions with versus without same-course activity.
    for window in WINDOWS:
        rows = [add_window_features(row, window) for row in source_rows]
        rows = [row for row in rows if row["y"] is not None]
        coefs, identified = fit_twfe(rows, ["has_activity"])
        boot = bootstrap_model(rows, ["has_activity"], SEED + 99 + len(window))
        out.append({
            "window": window,
            "model": "student_and_assessment_twfe_binary_activity",
            "feature": "has_activity",
            "beta_std": fmt(coefs["has_activity"]),
            **estimate_summary(boot.get("has_activity", [])),
            "identified_rows": len(identified),
            "students": len({r["student_id"] for r in identified}),
            "assessments": len({r["assessment_id"] for r in identified}),
        })

    write_csv(OUT / "causal_twfe_models_v1.csv", list(out[0].keys()), out)

    report = []
    report.append("# Causal-Cautious Two-Way Fixed-Effects Models V1")
    report.append("")
    report.append("## Design")
    report.append("- Observational design, not randomized causal identification.")
    report.append("- Adds student fixed effects to assessment fixed effects.")
    report.append("- Interpretation: within the same student, whether changes in pre-test behavior across assessments align with changes in normalized score, while controlling for assessment difficulty/date/course/test.")
    report.append("- This reduces confounding from stable student ability, motivation, and background, but not from time-varying unobserved factors.")
    report.append("- Coefficients are standardized residual associations after two-way demeaning.")
    report.append("")
    report.append("## Multivariable Two-Way Fixed-Effects Results")
    for window in WINDOWS:
        report.append(f"### {window}")
        for row in [r for r in out if r["window"] == window and r["model"] == "student_and_assessment_twfe"]:
            report.append(
                f"- {row['feature']}: beta={float(row['beta_std']):+.3f}, "
                f"CI [{float(row['ci_low']):+.3f}, {float(row['ci_high']):+.3f}], "
                f"p_boot={float(row['p_boot']):.3f}"
            )
        report.append("")
    report.append("## Binary Same-Course Activity Models")
    for row in [r for r in out if r["model"] == "student_and_assessment_twfe_binary_activity"]:
        report.append(
            f"- {row['window']}: has_activity beta={float(row['beta_std']):+.3f}, "
            f"CI [{float(row['ci_low']):+.3f}, {float(row['ci_high']):+.3f}], "
            f"p_boot={float(row['p_boot']):.3f}"
        )
    report.append("")
    report.append("## Causal Interpretation")
    report.append("- If active-days remains positive here, it is less likely to be only a between-student ability artifact.")
    report.append("- Remaining threats: time-varying effort, teacher assignment, assessment preparation, unmeasured offline study, and reverse causality from motivated students choosing to read more.")
    report.append("- Paper language should use causal-cautious terms unless a stronger quasi-experimental design is added.")
    (REPORTS / "causal_twfe_results_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
