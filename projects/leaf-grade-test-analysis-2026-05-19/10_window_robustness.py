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
BOOTSTRAPS = 60
SEED = 20260519
WINDOWS = ["m3", "m6", "m12"]
BASE_FEATURES = ["log_events", "log_active_days", "navigation_rate", "memo_rate", "marker_rate", "content_session_rate"]


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


def residualize(rows, fields, min_group_n=20):
    groups = defaultdict(list)
    for row in rows:
        groups[row["assessment_id"]].append(row)
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


def add_window_features(row, window):
    events = to_int(row.get(f"events_{window}"))
    active_days = to_int(row.get(f"active_days_{window}"))
    navigation = to_int(row.get(f"navigation_{window}"))
    memo = to_int(row.get(f"memo_{window}"))
    marker = to_int(row.get(f"marker_{window}"))
    content_session = to_int(row.get(f"content_session_{window}"))
    denom = events if events > 0 else 1
    out = dict(row)
    out["y"] = to_float(row.get("score_normalized_0_1"))
    out["assessment_id"] = "|".join([row["course_id"], row["name"], row["test_date"]])
    out["log_events"] = math.log1p(events)
    out["log_active_days"] = math.log1p(active_days)
    out["navigation_rate"] = navigation / denom
    out["memo_rate"] = memo / denom
    out["marker_rate"] = marker / denom
    out["content_session_rate"] = content_session / denom
    out["has_xapi"] = 1 if events > 0 else 0
    return out


def fit_multivariable(rows):
    fields = ["y"] + BASE_FEATURES
    resid = residualize(rows, fields)
    if len(resid) < 100:
        raise ValueError("too few rows")
    y = standardize([r["y_resid"] for r in resid])
    if y is None:
        raise ValueError("no outcome variance")
    x_cols = []
    used = []
    for feature in BASE_FEATURES:
        z = standardize([r[feature + "_resid"] for r in resid])
        if z is not None:
            x_cols.append(z)
            used.append(feature)
    if not x_cols:
        raise ValueError("no feature variance")
    coefs = ols(y, [list(vals) for vals in zip(*x_cols)])
    return dict(zip(used, coefs)), len(resid), len({r["student_id"] for r in resid}), len({r["assessment_id"] for r in resid})


def bootstrap_rows(rows, rng):
    by_student = defaultdict(list)
    for row in rows:
        by_student[row["student_id"]].append(row)
    students = list(by_student.keys())
    out = []
    for _ in students:
        out.extend(by_student[rng.choice(students)])
    return out


def bootstrap_model(rows, seed):
    rng = random.Random(seed)
    estimates = defaultdict(list)
    for _ in range(BOOTSTRAPS):
        try:
            coefs, _, _, _ = fit_multivariable(bootstrap_rows(rows, rng))
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
    base_rows = []
    for row in read_csv(MATRIX_PATH):
        key = (row["grade_level"], row["course_subject"], row["test_family"])
        if key not in candidate_keys:
            continue
        if row.get("score_validity_flag") != "valid" or row.get("classification_confidence") == "low":
            continue
        base_rows.append(row)

    # First robustness gate: the all-strong-cells model across windows.
    # Family-specific bootstrapped models are useful later, but slow enough that
    # they should run after the global window pattern is established.
    scopes = [("all_strong_cells", None)]

    out = []
    for window in WINDOWS:
        window_rows = [add_window_features(r, window) for r in base_rows]
        for scope_name, family in scopes:
            rows = [r for r in window_rows if family is None or r["test_family"] == family]
            if len(rows) < 150:
                continue
            try:
                coefs, n_rows, n_students, n_assessments = fit_multivariable(rows)
                boot = bootstrap_model(rows, SEED + len(out) + len(window))
            except ValueError:
                continue
            xapi_rows = sum(1 for r in rows if r["has_xapi"])
            for feature in BASE_FEATURES:
                if feature not in coefs:
                    continue
                out.append({
                    "window": window,
                    "scope": scope_name,
                    "feature": feature,
                    "beta_std": fmt(coefs[feature]),
                    **estimate_summary(boot.get(feature, [])),
                    "n_rows_after_fe": n_rows,
                    "n_students": n_students,
                    "n_assessments": n_assessments,
                    "source_rows": len(rows),
                    "xapi_rows": xapi_rows,
                    "xapi_rate": fmt(xapi_rows / len(rows) if rows else None),
                })

    write_csv(OUT / "model_window_robustness_v1.csv", list(out[0].keys()), out)

    report = []
    report.append("# Window Robustness Modeling V1")
    report.append("")
    report.append("## Scope")
    report.append("- Same strong candidate cells and assessment fixed-effect design as modeling V1.")
    report.append("- Repeats the global multivariable model for 3-, 6-, and 12-month pre-test xAPI windows.")
    report.append("- This first pass uses the all-strong-cells model; family-specific robustness should be run after this global pattern is reviewed.")
    report.append("")
    report.append("## Main Strong-Cell Model Across Windows")
    for window in WINDOWS:
        report.append(f"### {window}")
        for row in [r for r in out if r["window"] == window and r["scope"] == "all_strong_cells"]:
            report.append(
                f"- {row['feature']}: beta={float(row['beta_std']):+.3f}, "
                f"CI [{float(row['ci_low']):+.3f}, {float(row['ci_high']):+.3f}], "
                f"p_boot={float(row['p_boot']):.3f}, xapi_rate={float(row['xapi_rate']):.1%}"
            )
        report.append("")
    report.append("## Interpretation")
    report.append("- A result is more credible if sign and magnitude are stable across windows, not only significant in one arbitrary window.")
    report.append("- Active-days stability would support a distributed-engagement interpretation.")
    report.append("- If raw event volume weakens while active days remains positive, the paper should frame behavior quality/regularity rather than click quantity.")
    (REPORTS / "window_robustness_results_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
