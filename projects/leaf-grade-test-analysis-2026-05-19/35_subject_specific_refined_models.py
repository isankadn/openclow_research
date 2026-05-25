#!/usr/bin/env python3
import csv
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"
PAPER_TABLES = ROOT.parents[1] / "paper_draft" / "tables"
REPORTS.mkdir(exist_ok=True)
PAPER_TABLES.mkdir(parents=True, exist_ok=True)

MATRIX_PATH = OUT / "score_xapi_same_course_sufficiency_local_only.csv"
CANDIDATE_PATH = OUT / "candidate_analysis_cells_v2.csv"

WINDOWS = ["m3", "m6", "m12"]
SUBJECTS = ["数学", "英語"]
SCOPES = [
    ("course_embedded", {"school_regular_exam", "unit_or_chapter_test"}),
    ("school_regular_exam", {"school_regular_exam"}),
    ("unit_or_chapter_test", {"unit_or_chapter_test"}),
    ("external_benesse", {"external_benesse"}),
]
ADJUSTED_FEATURES = [
    "log_events",
    "log_active_days",
    "navigation_rate",
    "memo_rate",
    "marker_rate",
    "content_session_rate",
]
ACTIVE_ONLY = ["log_active_days"]


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def md_table(headers, rows):
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    out.extend("| " + " | ".join(str(c) for c in row) + " |" for row in rows)
    return "\n".join(out) + "\n"


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


def f3(value):
    return f"{float(value):+.3f}"


def pnum(value):
    value = float(value)
    return "<0.001" if value < 0.001 else f"{value:.3f}"


def nfmt(value):
    return f"{int(float(value)):,}"


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
    out["student_course_id"] = "|".join([row["student_id"], row["course_id"]])
    out["log_events"] = math.log1p(events)
    out["log_active_days"] = math.log1p(active_days)
    out["navigation_rate"] = navigation / denom
    out["memo_rate"] = memo / denom
    out["marker_rate"] = marker / denom
    out["content_session_rate"] = content_session / denom
    out["has_activity"] = 1.0 if events > 0 else 0.0
    return out


def filter_identified(rows, features, fixed_subject_key):
    by_subject = defaultdict(list)
    by_assessment = defaultdict(list)
    for row in rows:
        by_subject[row[fixed_subject_key]].append(row)
        by_assessment[row["assessment_id"]].append(row)
    kept = [
        row for row in rows
        if len(by_subject[row[fixed_subject_key]]) >= 2 and len(by_assessment[row["assessment_id"]]) >= 20
    ]
    by_subject = defaultdict(list)
    for row in kept:
        by_subject[row[fixed_subject_key]].append(row)
    variable_subjects = set()
    for key, srows in by_subject.items():
        for feature in features:
            vals = [r[feature] for r in srows]
            if max(vals) - min(vals) > 1e-12:
                variable_subjects.add(key)
                break
    return [row for row in kept if row[fixed_subject_key] in variable_subjects]


def two_way_residuals(rows, fields, fixed_subject_key, iterations=55):
    residuals = {field: [row[field] for row in rows] for field in fields}
    subject_groups = defaultdict(list)
    assessment_groups = defaultdict(list)
    for i, row in enumerate(rows):
        subject_groups[row[fixed_subject_key]].append(i)
        assessment_groups[row["assessment_id"]].append(i)
    for _ in range(iterations):
        for groups in (subject_groups, assessment_groups):
            for idxs in groups.values():
                for field in fields:
                    m = mean([residuals[field][i] for i in idxs])
                    for i in idxs:
                        residuals[field][i] -= m
    return residuals


def fit_model(rows, features, fixed_subject_key):
    identified = filter_identified(rows, features, fixed_subject_key)
    if len(identified) < 200:
        raise ValueError("too few identified rows")
    if len({r["student_id"] for r in identified}) < 80:
        raise ValueError("too few students")
    if len({r["assessment_id"] for r in identified}) < 6:
        raise ValueError("too few assessments")
    fields = ["y"] + features
    residuals = two_way_residuals(identified, fields, fixed_subject_key)
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


def result_row(scope, subject, window, model, fixed_effects, feature, beta, se, rows, status="estimated"):
    if status != "estimated":
        return {
            "scope": scope,
            "course_subject": subject,
            "window": window,
            "model": model,
            "fixed_effects": fixed_effects,
            "feature": feature,
            "status": status,
            "beta_std": "",
            "se_cluster_student": "",
            "ci_low": "",
            "ci_high": "",
            "p_cluster": "",
            "identified_rows": 0,
            "students": 0,
            "student_courses": 0,
            "assessments": 0,
        }
    return {
        "scope": scope,
        "course_subject": subject,
        "window": window,
        "model": model,
        "fixed_effects": fixed_effects,
        "feature": feature,
        "status": status,
        "beta_std": fmt(beta),
        "se_cluster_student": fmt(se),
        "ci_low": fmt(beta - 1.96 * se),
        "ci_high": fmt(beta + 1.96 * se),
        "p_cluster": fmt(normal_p(beta, se)),
        "identified_rows": len(rows),
        "students": len({r["student_id"] for r in rows}),
        "student_courses": len({r["student_course_id"] for r in rows}),
        "assessments": len({r["assessment_id"] for r in rows}),
    }


def run_subject_models(base_rows):
    output = []
    for scope, families in SCOPES:
        for subject in SUBJECTS:
            scoped = [r for r in base_rows if r["test_family"] in families and r["course_subject"] == subject]
            if not scoped:
                continue
            for window in WINDOWS:
                rows = [add_features(r, window) for r in scoped]
                rows = [r for r in rows if r["y"] is not None]
                for model, features in [
                    ("active_days_only", ACTIVE_ONLY),
                    ("adjusted_behavior", ADJUSTED_FEATURES),
                ]:
                    for fe_label, fe_key in [
                        ("student_assessment", "student_id"),
                        ("student_course_assessment", "student_course_id"),
                    ]:
                        try:
                            betas, ses, identified = fit_model(rows, features, fe_key)
                            output.append(
                                result_row(
                                    scope,
                                    subject,
                                    window,
                                    model,
                                    fe_label,
                                    "log_active_days",
                                    betas["log_active_days"],
                                    ses["log_active_days"],
                                    identified,
                                )
                            )
                            if model == "adjusted_behavior" and "log_events" in betas:
                                output.append(
                                    result_row(
                                        scope,
                                        subject,
                                        window,
                                        model,
                                        fe_label,
                                        "log_events",
                                        betas["log_events"],
                                        ses["log_events"],
                                        identified,
                                    )
                                )
                        except ValueError as exc:
                            output.append(
                                result_row(
                                    scope,
                                    subject,
                                    window,
                                    model,
                                    fe_label,
                                    "log_active_days",
                                    None,
                                    None,
                                    [],
                                    status=f"skipped:{exc}",
                                )
                            )
    return output


def summarize_subject_coverage(base_rows):
    buckets = defaultdict(lambda: defaultdict(int))
    students = defaultdict(set)
    courses = defaultdict(set)
    assessments = defaultdict(set)
    for row in base_rows:
        for scope, families in SCOPES:
            if row["test_family"] not in families:
                continue
            key = (scope, row["course_subject"])
            b = buckets[key]
            b["valid_rows"] += 1
            b["m3_rows"] += 1 if to_int(row.get("events_m3")) > 0 else 0
            b["events_m3"] += to_int(row.get("events_m3"))
            b["active_days_m3"] += to_int(row.get("active_days_m3"))
            students[key].add(row["student_id"])
            courses[key].add(row["course_id"])
            assessments[key].add("|".join([row["course_id"], row["name"], row["test_date"]]))
    rows = []
    for (scope, subject), b in sorted(buckets.items()):
        n = b["valid_rows"]
        rows.append({
            "scope": scope,
            "course_subject": subject,
            "valid_rows": n,
            "students": len(students[(scope, subject)]),
            "courses": len(courses[(scope, subject)]),
            "assessments": len(assessments[(scope, subject)]),
            "m3_rows": b["m3_rows"],
            "m3_rate": fmt(b["m3_rows"] / n if n else 0),
            "events_m3": b["events_m3"],
            "active_days_m3": b["active_days_m3"],
        })
    return rows


def selected(rows, scope, subject, window, model, fe, feature="log_active_days"):
    matches = [
        r for r in rows
        if r["scope"] == scope
        and r["course_subject"] == subject
        and r["window"] == window
        and r["model"] == model
        and r["fixed_effects"] == fe
        and r["feature"] == feature
        and r["status"] == "estimated"
    ]
    return matches[0] if matches else None


def make_report(model_rows, coverage_rows):
    report = ["# Subject-Specific Refined Models", ""]
    report.extend([
        "## Purpose",
        "- Revisit whether the direct-context result is mathematics-only or also supported in English.",
        "- Estimate subject-specific active-days models by assessment family and window.",
        "- Compare student + assessment fixed effects with stricter student-course + assessment fixed effects.",
        "- Keep claims at the level supported by subject-specific evidence.",
        "",
        "## Coverage By Subject",
    ])
    for r in coverage_rows:
        if r["course_subject"] not in SUBJECTS:
            continue
        report.append(
            f"- {r['scope']} / {r['course_subject']}: valid_rows={int(r['valid_rows']):,}, "
            f"students={int(r['students']):,}, assessments={int(r['assessments']):,}, "
            f"m3_xapi={int(r['m3_rows']):,} ({float(r['m3_rate']):.1%}), events_m3={int(r['events_m3']):,}"
        )

    report.extend(["", "## Main Active-Days Results (m3, adjusted behavior model)", ""])
    order = [
        ("course_embedded", "数学"),
        ("course_embedded", "英語"),
        ("school_regular_exam", "数学"),
        ("school_regular_exam", "英語"),
        ("unit_or_chapter_test", "数学"),
        ("unit_or_chapter_test", "英語"),
        ("external_benesse", "数学"),
        ("external_benesse", "英語"),
    ]
    for scope, subject in order:
        stu = selected(model_rows, scope, subject, "m3", "adjusted_behavior", "student_assessment")
        sc = selected(model_rows, scope, subject, "m3", "adjusted_behavior", "student_course_assessment")
        if not stu and not sc:
            report.append(f"- {scope} / {subject}: not estimable with current thresholds.")
            continue
        parts = []
        if stu:
            parts.append(
                f"student FE beta={float(stu['beta_std']):+.3f}, CI [{float(stu['ci_low']):+.3f}, {float(stu['ci_high']):+.3f}], p={float(stu['p_cluster']):.3f}, rows={int(stu['identified_rows']):,}"
            )
        if sc:
            parts.append(
                f"student-course FE beta={float(sc['beta_std']):+.3f}, CI [{float(sc['ci_low']):+.3f}, {float(sc['ci_high']):+.3f}], p={float(sc['p_cluster']):.3f}, rows={int(sc['identified_rows']):,}"
            )
        report.append(f"- {scope} / {subject}: " + "; ".join(parts))

    report.extend(["", "## Regularity Versus Event Volume (m3, adjusted, student-course FE)", ""])
    for scope, subject in [
        ("course_embedded", "数学"),
        ("course_embedded", "英語"),
        ("school_regular_exam", "数学"),
        ("school_regular_exam", "英語"),
        ("unit_or_chapter_test", "数学"),
        ("external_benesse", "数学"),
        ("external_benesse", "英語"),
    ]:
        active = selected(model_rows, scope, subject, "m3", "adjusted_behavior", "student_course_assessment", "log_active_days")
        events = selected(model_rows, scope, subject, "m3", "adjusted_behavior", "student_course_assessment", "log_events")
        if not active or not events:
            continue
        report.append(
            f"- {scope} / {subject}: active_days={float(active['beta_std']):+.3f} "
            f"CI [{float(active['ci_low']):+.3f}, {float(active['ci_high']):+.3f}], "
            f"log_events={float(events['beta_std']):+.3f} "
            f"CI [{float(events['ci_low']):+.3f}, {float(events['ci_high']):+.3f}]"
        )

    report.extend(["", "## Claim Strength"])
    report.append("- Strongest subject-specific claim: mathematics regular exams. Active days are positive under both student FE and student-course FE, and remain positive across windows.")
    report.append("- For mathematics regular exams, the adjusted student-course model shows active days positive while event volume is negative. This is the strongest subject-specific support for the claim that regularity is more informative than click volume alone.")
    report.append("- English regular exams are included and analyzable, but the strict student-course model is weaker/less precise than mathematics. Treat English regular exams as exploratory/supportive, not the headline claim.")
    report.append("- Unit/chapter-test strong cells are currently mathematics-only in the candidate set, so this family cannot support an English claim.")
    report.append("- English external Benesse shows a surprisingly strong positive active-days pattern, especially in the stricter model and longer windows. This is an important secondary finding, but it should be framed as subject/test-family specific rather than as the main course-alignment claim.")
    report.append("- The best-paper claim should stay: course-aligned regularity is a trace-validity principle; mathematics regular exams are the strongest empirical demonstration.")
    return "\n".join(report) + "\n"


def make_paper_table(model_rows):
    rows = []
    for scope, subject in [
        ("course_embedded", "数学"),
        ("course_embedded", "英語"),
        ("school_regular_exam", "数学"),
        ("school_regular_exam", "英語"),
        ("unit_or_chapter_test", "数学"),
        ("external_benesse", "数学"),
        ("external_benesse", "英語"),
    ]:
        stu = selected(model_rows, scope, subject, "m3", "adjusted_behavior", "student_assessment")
        sc = selected(model_rows, scope, subject, "m3", "adjusted_behavior", "student_course_assessment")
        if not stu and not sc:
            continue
        rows.append([
            scope,
            subject,
            f3(stu["beta_std"]) if stu else "",
            f"[{f3(stu['ci_low'])}, {f3(stu['ci_high'])}]" if stu else "",
            pnum(stu["p_cluster"]) if stu else "",
            nfmt(stu["identified_rows"]) if stu else "",
            f3(sc["beta_std"]) if sc else "",
            f"[{f3(sc['ci_low'])}, {f3(sc['ci_high'])}]" if sc else "",
            pnum(sc["p_cluster"]) if sc else "",
            nfmt(sc["identified_rows"]) if sc else "",
        ])
    return md_table(
        [
            "Scope",
            "Subject",
            "Student FE beta",
            "Student FE 95% CI",
            "Student FE p",
            "Student FE rows",
            "Student-course FE beta",
            "Student-course FE 95% CI",
            "Student-course FE p",
            "Student-course FE rows",
        ],
        rows,
    )


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

    coverage_rows = summarize_subject_coverage(base_rows)
    model_rows = run_subject_models(base_rows)
    write_csv(OUT / "subject_specific_refined_models_v1.csv", list(model_rows[0].keys()), model_rows)
    write_csv(OUT / "subject_specific_refined_coverage_v1.csv", list(coverage_rows[0].keys()), coverage_rows)
    (REPORTS / "subject_specific_refined_models_v1.md").write_text(
        make_report(model_rows, coverage_rows),
        encoding="utf-8",
    )
    (PAPER_TABLES / "table_subject_specific_refined_models.md").write_text(
        make_paper_table(model_rows),
        encoding="utf-8",
    )
    print((REPORTS / "subject_specific_refined_models_v1.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
