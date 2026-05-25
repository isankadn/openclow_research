#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[1]
PAPER = WORKSPACE / "paper_draft"
TABLES = PAPER / "tables"
TABLES.mkdir(parents=True, exist_ok=True)


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(str(c) for c in row) + " |" for row in rows)
    return "\n".join(out) + "\n"


def nfmt(n):
    return f"{int(n):,}"


def main():
    clean = read_csv(ROOT / "outputs" / "clean_score_grain_local_only.csv")
    matrix = read_csv(ROOT / "outputs" / "score_xapi_same_course_sufficiency_local_only.csv")
    candidates = {
        (r["grade_level"], r["course_subject"], r["test_family"])
        for r in read_csv(ROOT / "outputs" / "candidate_analysis_cells_v2.csv")
        if r["paper_candidate_flag"] == "strong_candidate"
    }
    strong = [
        r for r in matrix
        if (r["grade_level"], r["course_subject"], r["test_family"]) in candidates
        and r["score_validity_flag"] == "valid"
    ]
    course_embedded = [r for r in strong if r["test_family"] in {"school_regular_exam", "unit_or_chapter_test"}]
    benesse = [r for r in strong if r["test_family"] == "external_benesse"]

    def assessments(rows):
        return {"|".join([r["course_id"], r["name"], r["test_date"]]) for r in rows}

    def events(rows, prefix):
        return sum(int(float(r.get(prefix, 0) or 0)) for r in rows)

    profile = (ROOT / "outputs" / "grade_test_profile_report.md").read_text(encoding="utf-8")
    raw_total = raw_missing_date = None
    for line in profile.splitlines():
        if line.startswith("- total_rows:"):
            raw_total = nfmt(line.split(":", 1)[1].strip())
        if line.startswith("- missing_date_rows:"):
            raw_missing_date = nfmt(line.split(":", 1)[1].strip())

    global_fe = [
        r for r in read_csv(ROOT / "outputs" / "model_window_robustness_v1.csv")
        if r["window"] == "m3" and r["feature"] == "log_active_days"
    ][0]
    strict_fe = [
        r for r in read_csv(ROOT / "outputs" / "student_course_fe_robustness_v1.csv")
        if r["scope"] == "course_embedded"
        and r["window"] == "m3"
        and r["model"] == "student_course_assessment_fe_adjusted"
        and r["feature"] == "log_active_days"
    ][0]
    course_embedded_student_fe = [
        r for r in read_csv(ROOT / "outputs" / "student_course_fe_robustness_v1.csv")
        if r["scope"] == "course_embedded"
        and r["window"] == "m3"
        and r["model"] == "student_assessment_fe_adjusted"
        and r["feature"] == "log_active_days"
    ][0]
    break_after = [r for r in strong if r["test_family"] == "break_after_test"]
    evidence_rows = [
        ["Raw score records", raw_total or "", "Initial assessment-score table"],
        ["Clean dated assessment records", nfmt(len(clean)), "Rows with test date available for temporal ordering"],
        ["Valid normalized outcomes", nfmt(sum(1 for r in clean if r["score_validity_flag"] == "valid")), "Rows with usable normalized score"],
        ["Strong-cell valid rows", nfmt(len(strong)), "Rows in cells meeting the strong-cell rule"],
        ["Course-embedded rows", nfmt(len(course_embedded)), "Regular exams and unit/chapter tests"],
        ["External Benesse contrast rows", nfmt(len(benesse)), "External assessment comparison"],
        ["Break-after-test rows", nfmt(len(break_after)), "Retained in diagnostics but not the main course-embedded claim"],
        ["Global fixed-effect rows", nfmt(global_fe["n_rows_after_fe"]), "Strong-cell rows after student and assessment FE filtering"],
        ["Course-embedded student+assessment FE rows", nfmt(course_embedded_student_fe["identified_rows"]), "Main course-aligned fixed-effect comparison"],
        ["Course-embedded student-course+assessment FE rows", nfmt(strict_fe["identified_rows"]), "Stricter robustness comparison"],
        ["Same-course pre-test ebook events in strong cells", nfmt(events(strong, "events_m3")), "Trace richness in 3-month pre-test window"],
    ]
    (TABLES / "table1_sample_construction.md").write_text(
        md_table(["Stage", "Records", "Role in analysis"], evidence_rows),
        encoding="utf-8",
    )

    quality_rows = [
        ["Raw score records", raw_total or "", "Initial score table"],
        ["Excluded: missing test conduct date", raw_missing_date or "", "Cannot establish behavior-before-outcome ordering"],
        ["Retained: dated score records", nfmt(len(clean)), "Eligible for temporal outcome analysis"],
        ["Excluded from modeling: invalid/missing quiz score", nfmt(sum(1 for r in clean if r["score_validity_flag"] != "valid")), "Cannot compute normalized outcome"],
        ["Retained: valid normalized outcomes", nfmt(sum(1 for r in clean if r["score_validity_flag"] == "valid")), "Outcome-valid records"],
        ["Retained for strong-cell modeling", nfmt(len(strong)), "Sufficient same-course xAPI linkage and valid outcome"],
    ]
    (TABLES / "table_data_quality_flow.md").write_text(
        md_table(["Stage", "Records", "Reason"], quality_rows),
        encoding="utf-8",
    )

    print("Wrote table1_sample_construction.md and table_data_quality_flow.md")


if __name__ == "__main__":
    main()
