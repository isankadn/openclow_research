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
PHASE_PATH = OUT / "temporal_phase_assignments_local_only.csv"

BOOTSTRAPS = 0
SEED = 20260519
BASELINE_STRATEGY = "no_same_course_activity"
CONTINUOUS_FEATURES = [
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


def key(row):
    return "|".join([row["student_id"], row["course_id"], row["name"], row["test_date"]])


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
    return solve_linear(xtx, xty), xtx


def mat_inverse(a):
    n = len(a)
    inv = []
    for col in range(n):
        b = [0.0] * n
        b[col] = 1.0
        inv.append(solve_linear(a, b))
    return [[inv[col][row] for col in range(n)] for row in range(n)]


def mat_vec_mul(a, v):
    return [sum(aij * vj for aij, vj in zip(row, v)) for row in a]


def normal_p(beta, se):
    if se <= 0:
        return 1.0
    z = abs(beta / se)
    return math.erfc(z / math.sqrt(2))


def standardize(values):
    s = sd(values)
    if s <= 1e-12:
        return None
    m = mean(values)
    return [(v - m) / s for v in values]


def add_features(row):
    events = to_int(row.get("events_m3"))
    active_days = to_int(row.get("active_days_m3"))
    navigation = to_int(row.get("navigation_m3"))
    memo = to_int(row.get("memo_m3"))
    marker = to_int(row.get("marker_m3"))
    content_session = to_int(row.get("content_session_m3"))
    denom = events if events > 0 else 1
    row["y"] = to_float(row["score_normalized_0_1"])
    row["assessment_id"] = "|".join([row["course_id"], row["name"], row["test_date"]])
    row["log_events_m3"] = math.log1p(events)
    row["log_active_days_m3"] = math.log1p(active_days)
    row["navigation_rate_m3"] = navigation / denom
    row["memo_rate_m3"] = memo / denom
    row["marker_rate_m3"] = marker / denom
    row["content_session_rate_m3"] = content_session / denom


def two_way_residuals(rows, fields, iterations=15):
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


def identified_rows(rows, features):
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
        for feature in features:
            if max(r[feature] for r in srows) - min(r[feature] for r in srows) > 1e-12:
                variable_students.add(sid)
                break
    return [row for row in kept if row["student_id"] in variable_students]


def fit_model(rows, features):
    rows = identified_rows(rows, features)
    fields = ["y"] + features
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
        raise ValueError("no feature variance")
    x_matrix = [list(vals) for vals in zip(*x_cols)]
    coefs, xtx = ols(y, x_matrix)
    inv_xtx = mat_inverse(xtx)
    residual = [yi - sum(beta * xi for beta, xi in zip(coefs, xs)) for yi, xs in zip(y, x_matrix)]
    cluster_scores = defaultdict(lambda: [0.0] * len(coefs))
    for row, xs, u in zip(rows, x_matrix, residual):
        score = cluster_scores[row["student_id"]]
        for j, x in enumerate(xs):
            score[j] += x * u
    meat = [[0.0 for _ in coefs] for _ in coefs]
    for score in cluster_scores.values():
        for i in range(len(coefs)):
            for j in range(len(coefs)):
                meat[i][j] += score[i] * score[j]
    vcov = [[0.0 for _ in coefs] for _ in coefs]
    for i in range(len(coefs)):
        for j in range(len(coefs)):
            vcov[i][j] = sum(inv_xtx[i][k] * meat[k][l] * inv_xtx[l][j] for k in range(len(coefs)) for l in range(len(coefs)))
    g = len(cluster_scores)
    n = len(rows)
    p = len(coefs)
    if g > 1 and n > p:
        factor = (g / (g - 1)) * ((n - 1) / (n - p))
        vcov = [[v * factor for v in row] for row in vcov]
    se = [math.sqrt(max(vcov[i][i], 0.0)) for i in range(len(coefs))]
    return dict(zip(used, coefs)), dict(zip(used, se)), rows


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
    if BOOTSTRAPS <= 0:
        return estimates
    for _ in range(BOOTSTRAPS):
        try:
            coefs, _, _ = fit_model(bootstrap_rows(rows, rng), features)
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
    phase_by_key = {key(row): row["phase_strategy"] for row in read_csv(PHASE_PATH)}
    rows = []
    for row in read_csv(MATRIX_PATH):
        phase = phase_by_key.get(key(row))
        if not phase:
            continue
        if row.get("score_validity_flag") != "valid" or row.get("classification_confidence") == "low":
            continue
        add_features(row)
        if row["y"] is None:
            continue
        row["phase_strategy"] = phase
        rows.append(row)

    strategies = sorted({row["phase_strategy"] for row in rows})
    strategy_features = []
    for strategy in strategies:
        if strategy == BASELINE_STRATEGY:
            continue
        feature = "strategy_" + strategy
        strategy_features.append(feature)
        for row in rows:
            row[feature] = 1.0 if row["phase_strategy"] == strategy else 0.0

    model_specs = [
        ("strategy_total_twfe", strategy_features),
        ("strategy_adjusted_for_behavior_twfe", strategy_features + CONTINUOUS_FEATURES),
    ]
    out = []
    for model_name, features in model_specs:
        coefs, ses, identified = fit_model(rows, features)
        boot = bootstrap_model(rows, features, SEED + len(model_name))
        for feature in features:
            if feature not in coefs:
                continue
            out.append({
                "model": model_name,
                "feature": feature,
                "baseline": BASELINE_STRATEGY if feature.startswith("strategy_") else "",
                "beta_std": fmt(coefs[feature]),
                "se_cluster_student": fmt(ses[feature]),
                "ci_low": fmt(coefs[feature] - 1.96 * ses[feature]),
                "ci_high": fmt(coefs[feature] + 1.96 * ses[feature]),
                "p_boot": fmt(normal_p(coefs[feature], ses[feature])),
                "bootstraps": "cluster_se",
                "identified_rows": len(identified),
                "students": len({r["student_id"] for r in identified}),
                "assessments": len({r["assessment_id"] for r in identified}),
            })
    write_csv(OUT / "strategy_feature_adjusted_twfe_v1.csv", list(out[0].keys()), out)

    report = []
    report.append("# Strategy Categories Plus Behavior Features: Two-Way Fixed Effects V1")
    report.append("")
    report.append("## Design")
    report.append("- Observational, causal-cautious model.")
    report.append("- Fixed effects: student and assessment occasion.")
    report.append("- Strategy baseline: no_same_course_activity.")
    report.append("- Model 1 estimates the within-student total strategy contrast against the no-activity baseline.")
    report.append("- Model 2 adds measured behavior features, so strategy coefficients become residual/direct contrasts beyond active days, navigation, memo, marker, and content-session composition.")
    report.append("- This adjustment may control away part of the strategy mechanism; therefore Model 1 and Model 2 answer different questions.")
    report.append("")
    for model_name, title in [
        ("strategy_total_twfe", "Model 1: Strategy Categories Only"),
        ("strategy_adjusted_for_behavior_twfe", "Model 2: Strategy Categories Plus Behavior Features"),
    ]:
        report.append(f"## {title}")
        for row in [r for r in out if r["model"] == model_name and r["feature"].startswith("strategy_")]:
            label = row["feature"].replace("strategy_", "")
            report.append(
                f"- {label}: beta={float(row['beta_std']):+.3f}, "
                f"CI [{float(row['ci_low']):+.3f}, {float(row['ci_high']):+.3f}], "
                f"p_boot={float(row['p_boot']):.3f}"
            )
        if model_name.endswith("behavior_twfe"):
            report.append("")
            report.append("Behavior-feature covariates in adjusted model:")
            for row in [r for r in out if r["model"] == model_name and not r["feature"].startswith("strategy_")]:
                report.append(
                    f"- {row['feature']}: beta={float(row['beta_std']):+.3f}, "
                    f"CI [{float(row['ci_low']):+.3f}, {float(row['ci_high']):+.3f}], "
                    f"p_boot={float(row['p_boot']):.3f}"
                )
        report.append("")
    report.append("## Causal Interpretation")
    report.append("- Student fixed effects remove stable ability/background differences; assessment fixed effects remove test/course/date difficulty.")
    report.append("- The remaining comparison is within-student variation across assessments.")
    report.append("- Time-varying confounding remains possible, especially changing effort, offline study, teacher support, and preparation cycles.")
    report.append("- Use language such as 'consistent with' or 'supports a causal-cautious interpretation', not definitive causal claims.")
    (REPORTS / "strategy_feature_adjusted_twfe_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
