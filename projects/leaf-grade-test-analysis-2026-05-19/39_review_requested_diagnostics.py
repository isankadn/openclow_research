#!/usr/bin/env python3
import csv
import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"

spec = importlib.util.spec_from_file_location("subject_models", ROOT / "35_subject_specific_refined_models.py")
subject_models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject_models)


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt_p(value):
    value = float(value)
    return "<0.001" if value < 0.001 else f"{value:.3f}"


def add_review_features(row):
    out = subject_models.add_features(row, "m3")
    events = subject_models.to_int(row.get("events_m3"))
    active_days = subject_models.to_int(row.get("active_days_m3"))
    out["any_activity"] = 1.0 if events > 0 else 0.0
    out["log_active_days_given_activity"] = math.log1p(active_days) if events > 0 else 0.0
    out["log_event_intensity"] = math.log1p(events) - math.log1p(active_days)
    out["log_events_per_active_day"] = math.log1p(events / active_days) if active_days > 0 else 0.0
    return out


def coefficient_rows(rows, model_label, features, fe_key="student_course_id"):
    betas, ses, identified = subject_models.fit_model(rows, features, fe_key)
    output = []
    for feature in features:
        if feature not in betas:
            continue
        beta = betas[feature]
        se = ses[feature]
        output.append({
            "model": model_label,
            "fixed_effects": "student_course_assessment",
            "feature": feature,
            "beta_std": f"{beta:.6f}",
            "se_cluster_student": f"{se:.6f}",
            "ci_low": f"{beta - 1.96 * se:.6f}",
            "ci_high": f"{beta + 1.96 * se:.6f}",
            "p_cluster": f"{subject_models.normal_p(beta, se):.6f}",
            "identified_rows": len(identified),
            "students": len({r["student_id"] for r in identified}),
            "student_courses": len({r["student_course_id"] for r in identified}),
            "assessments": len({r["assessment_id"] for r in identified}),
        })
    return output


def main():
    candidate_keys = {
        (r["grade_level"], r["course_subject"], r["test_family"])
        for r in read_csv(OUT / "candidate_analysis_cells_v2.csv")
        if r.get("paper_candidate_flag") == "strong_candidate"
    }
    base = []
    for row in read_csv(OUT / "score_xapi_same_course_sufficiency_local_only.csv"):
        key = (row["grade_level"], row["course_subject"], row["test_family"])
        if key not in candidate_keys:
            continue
        if row.get("score_validity_flag") != "valid" or row.get("classification_confidence") == "low":
            continue
        if row["test_family"] == "school_regular_exam" and row["course_subject"] == "数学":
            base.append(add_review_features(row))

    any_activity_features = [
        "any_activity",
        "log_active_days_given_activity",
        "navigation_rate",
        "memo_rate",
        "marker_rate",
        "content_session_rate",
    ]
    intensity_features = [
        "log_active_days",
        "log_event_intensity",
        "navigation_rate",
        "memo_rate",
        "marker_rate",
        "content_session_rate",
    ]
    active_only_intensity_features = [
        "log_active_days",
        "log_events_per_active_day",
        "navigation_rate",
        "memo_rate",
        "marker_rate",
        "content_session_rate",
    ]

    rows = []
    rows.extend(coefficient_rows(base, "any_activity_plus_active_days", any_activity_features))
    rows.extend(coefficient_rows(base, "log_event_intensity_reparameterized", intensity_features))
    active_rows = [r for r in base if r["any_activity"] > 0]
    rows.extend(coefficient_rows(active_rows, "active_rows_event_intensity", active_only_intensity_features))

    write_csv(OUT / "review_requested_diagnostics_v1.csv", list(rows[0].keys()), rows)

    report = [
        "# Review-Requested Diagnostics V1",
        "",
        "## Scope",
        "- Mathematics regular exams.",
        "- 3-month pre-assessment window.",
        "- Student-course and assessment fixed effects.",
        "- Student-clustered standard errors.",
        "",
        "## Results",
    ]
    for row in rows:
        if row["feature"] not in {
            "any_activity",
            "log_active_days_given_activity",
            "log_active_days",
            "log_event_intensity",
            "log_events_per_active_day",
        }:
            continue
        report.append(
            f"- {row['model']} / {row['feature']}: beta={float(row['beta_std']):+.3f}, "
            f"CI [{float(row['ci_low']):+.3f}, {float(row['ci_high']):+.3f}], "
            f"p={fmt_p(row['p_cluster'])}, rows={int(row['identified_rows']):,}."
        )
    report.extend([
        "",
        "## Interpretation",
        "- The any-activity split checks whether the active-days signal is only an access/no-access contrast.",
        "- The event-intensity models check whether concentrated activity remains negative after regularity is separated from event volume.",
    ])
    (REPORTS / "review_requested_diagnostics_v1.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
