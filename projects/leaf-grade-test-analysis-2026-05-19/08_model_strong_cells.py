#!/usr/bin/env python3
import csv
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

MATRIX_PATH = OUT / "score_xapi_same_course_sufficiency_local_only.csv"
CANDIDATE_PATH = OUT / "candidate_analysis_cells_v2.csv"

GLOBAL_BOOTSTRAPS = 200
CELL_BOOTSTRAPS = 50
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
        if pivot != col:
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
    if not y or not x_matrix:
        raise ValueError("empty model")
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


def residualize(rows, fields, group_field="assessment_id", min_group_n=20):
    groups = defaultdict(list)
    for row in rows:
        groups[row[group_field]].append(row)
    out = []
    for group_rows in groups.values():
        if len(group_rows) < min_group_n:
            continue
        means = {field: mean([r[field] for r in group_rows]) for field in fields}
        for row in group_rows:
            rr = dict(row)
            for field in fields:
                rr[field + "_resid"] = row[field] - means[field]
            out.append(rr)
    return out


def add_features(row):
    events = to_int(row.get("events_m3"))
    active_days = to_int(row.get("active_days_m3"))
    navigation = to_int(row.get("navigation_m3"))
    memo = to_int(row.get("memo_m3"))
    marker = to_int(row.get("marker_m3"))
    content_session = to_int(row.get("content_session_m3"))
    denom = events if events > 0 else 1
    row["y"] = to_float(row.get("score_normalized_0_1"))
    row["log_events_m3"] = math.log1p(events)
    row["log_active_days_m3"] = math.log1p(active_days)
    row["navigation_rate_m3"] = navigation / denom
    row["memo_rate_m3"] = memo / denom
    row["marker_rate_m3"] = marker / denom
    row["content_session_rate_m3"] = content_session / denom
    row["assessment_id"] = "|".join([row["course_id"], row["name"], row["test_date"]])


FEATURES = [
    "log_events_m3",
    "log_active_days_m3",
    "navigation_rate_m3",
    "memo_rate_m3",
    "marker_rate_m3",
    "content_session_rate_m3",
]


def fit_multivariable(rows, features=FEATURES):
    fields = ["y"] + features
    resid = residualize(rows, fields)
    if len(resid) < 100:
        raise ValueError("too few rows after assessment fixed effects")
    y = standardize([r["y_resid"] for r in resid])
    if y is None:
        raise ValueError("no outcome variance")
    x_cols = []
    used_features = []
    for feature in features:
        z = standardize([r[feature + "_resid"] for r in resid])
        if z is not None:
            x_cols.append(z)
            used_features.append(feature)
    if not x_cols:
        raise ValueError("no feature variance")
    x_matrix = [list(vals) for vals in zip(*x_cols)]
    coefs = ols(y, x_matrix)
    return dict(zip(used_features, coefs)), len(resid), len({r["student_id"] for r in resid}), len({r["assessment_id"] for r in resid})


def fit_univariate(rows, feature):
    resid = residualize(rows, ["y", feature])
    if len(resid) < 100:
        raise ValueError("too few rows after assessment fixed effects")
    y = standardize([r["y_resid"] for r in resid])
    x = standardize([r[feature + "_resid"] for r in resid])
    if y is None or x is None:
        raise ValueError("no variance")
    beta = sum(xi * yi for xi, yi in zip(x, y)) / sum(xi * xi for xi in x)
    return beta, len(resid), len({r["student_id"] for r in resid}), len({r["assessment_id"] for r in resid})


def bootstrap_rows(rows, rng):
    by_student = defaultdict(list)
    for row in rows:
        by_student[row["student_id"]].append(row)
    students = list(by_student.keys())
    sampled = []
    for _ in students:
        sid = rng.choice(students)
        sampled.extend(by_student[sid])
    return sampled


def bootstrap_multivariable(rows):
    rng = random.Random(SEED)
    estimates = defaultdict(list)
    for _ in range(GLOBAL_BOOTSTRAPS):
        sample = bootstrap_rows(rows, rng)
        try:
            coefs, _, _, _ = fit_multivariable(sample)
        except ValueError:
            continue
        for feature, coef in coefs.items():
            estimates[feature].append(coef)
    return estimates


def bootstrap_univariate(rows, feature):
    rng = random.Random(SEED + sum(ord(c) for c in feature))
    estimates = []
    for _ in range(CELL_BOOTSTRAPS):
        sample = bootstrap_rows(rows, rng)
        try:
            beta, _, _, _ = fit_univariate(sample, feature)
        except ValueError:
            continue
        estimates.append(beta)
    return estimates


def summarize_estimates(estimates):
    if not estimates:
        return {"ci_low": "", "ci_high": "", "p_boot": "", "bootstraps": 0}
    le_zero = sum(1 for x in estimates if x <= 0) / len(estimates)
    ge_zero = sum(1 for x in estimates if x >= 0) / len(estimates)
    p_boot = min(1.0, 2 * min(le_zero, ge_zero))
    return {
        "ci_low": fmt(percentile(estimates, 0.025)),
        "ci_high": fmt(percentile(estimates, 0.975)),
        "p_boot": fmt(p_boot),
        "bootstraps": len(estimates),
    }


def main():
    candidates = {
        (r["grade_level"], r["course_subject"], r["test_family"])
        for r in read_csv(CANDIDATE_PATH)
        if r.get("paper_candidate_flag") == "strong_candidate"
    }
    rows = []
    excluded_low_conf = 0
    for r in read_csv(MATRIX_PATH):
        key = (r["grade_level"], r["course_subject"], r["test_family"])
        if key not in candidates:
            continue
        if r.get("score_validity_flag") != "valid":
            continue
        if r.get("classification_confidence") == "low":
            excluded_low_conf += 1
            continue
        add_features(r)
        if r["y"] is None:
            continue
        rows.append(r)

    global_coefs, n_rows, n_students, n_assessments = fit_multivariable(rows)
    boot = bootstrap_multivariable(rows)
    global_out = []
    for feature in FEATURES:
        if feature not in global_coefs:
            continue
        global_out.append({
            "model": "assessment_fixed_effects_multivariable",
            "feature": feature,
            "beta_std": fmt(global_coefs[feature]),
            **summarize_estimates(boot.get(feature, [])),
            "n_rows": n_rows,
            "n_students": n_students,
            "n_assessments": n_assessments,
        })
    write_csv(OUT / "model_global_fixed_effects_v1.csv", list(global_out[0].keys()), global_out)

    cell_out = []
    for cell in sorted(candidates):
        cell_rows = [r for r in rows if (r["grade_level"], r["course_subject"], r["test_family"]) == cell]
        for feature in FEATURES:
            try:
                beta, cr, cs, ca = fit_univariate(cell_rows, feature)
                estimates = bootstrap_univariate(cell_rows, feature)
            except ValueError:
                continue
            cell_out.append({
                "grade_level": cell[0],
                "course_subject": cell[1],
                "test_family": cell[2],
                "feature": feature,
                "beta_std": fmt(beta),
                **summarize_estimates(estimates),
                "n_rows": cr,
                "n_students": cs,
                "n_assessments": ca,
            })
    write_csv(OUT / "model_cell_fixed_effects_v1.csv", list(cell_out[0].keys()), cell_out)

    strongest = sorted(cell_out, key=lambda r: abs(float(r["beta_std"])), reverse=True)[:20]
    report = []
    report.append("# Strong-Cell Assessment-Fixed-Effects Modeling V1")
    report.append("")
    report.append("## Model Scope")
    report.append("- Uses only strong candidate grade/subject/test-family cells from candidate_analysis_cells_v2.csv.")
    report.append("- Uses only valid normalized quiz-score outcomes.")
    report.append("- Excludes low-confidence test-name classifications.")
    report.append("- Outcome and predictors are residualized by assessment_id = course_id + test name + test date.")
    report.append("- Coefficients are standardized effects: SD change in score residual per 1 SD change in behavior residual.")
    report.append("- Uncertainty uses student-cluster bootstrap resampling; only aggregate coefficients are exported.")
    report.append("")
    report.append("## Analysis Rows")
    report.append(f"- rows entering candidate-cell model filter: {len(rows):,}")
    report.append(f"- excluded low-confidence rows: {excluded_low_conf:,}")
    report.append(f"- rows after assessment fixed-effect filtering in global model: {n_rows:,}")
    report.append(f"- students in global model: {n_students:,}")
    report.append(f"- assessment occasions in global model: {n_assessments:,}")
    report.append("")
    report.append("## Global Multivariable Model")
    for row in global_out:
        report.append(
            f"- {row['feature']}: beta={float(row['beta_std']):+.3f}, "
            f"95% bootstrap CI [{float(row['ci_low']):+.3f}, {float(row['ci_high']):+.3f}], "
            f"p_boot={float(row['p_boot']):.3f}"
        )
    report.append("")
    report.append("## Largest Cell-Level Univariate Signals")
    for row in strongest:
        report.append(
            f"- {row['grade_level']} {row['course_subject']} {row['test_family']} / {row['feature']}: "
            f"beta={float(row['beta_std']):+.3f}, CI [{float(row['ci_low']):+.3f}, {float(row['ci_high']):+.3f}], "
            f"n={int(row['n_rows']):,}, students={int(row['n_students']):,}, assessments={int(row['n_assessments']):,}"
        )
    report.append("")
    report.append("## Interpretation Guardrails")
    report.append("- These are associational models, not causal estimates.")
    report.append("- Assessment fixed effects mean the estimates compare students taking the same course/test/date, reducing test-difficulty confounding.")
    report.append("- Strong signals should be checked with alternate windows, exclusion of ambiguous old mappings, and sequence/profile features before paper claims.")
    (REPORTS / "modeling_results_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
