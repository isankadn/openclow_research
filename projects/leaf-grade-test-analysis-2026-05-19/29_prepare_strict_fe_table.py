#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[1]
OUT = ROOT / "outputs"
PAPER_TABLES = WORKSPACE / "paper_draft" / "tables"
PAPER_TABLES.mkdir(parents=True, exist_ok=True)


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(value):
    return f"{float(value):+.3f}"


def pnum(value):
    value = float(value)
    return "<0.001" if value < 0.001 else f"{value:.3f}"


def nfmt(value):
    return f"{int(float(value)):,}"


def find(rows, scope, window, model):
    for row in rows:
        if (
            row["scope"] == scope
            and row["window"] == window
            and row["model"] == model
            and row["feature"] == "log_active_days"
        ):
            return row
    raise KeyError((scope, window, model))


def main():
    rows = read_csv(OUT / "student_course_fe_robustness_v1.csv")
    selected = [
        ("Course-embedded", "course_embedded", "m3"),
        ("Course-embedded", "course_embedded", "m6"),
        ("Course-embedded", "course_embedded", "m12"),
        ("Regular exams", "school_regular_exam", "m3"),
        ("Unit/chapter tests", "unit_or_chapter_test", "m3"),
        ("External Benesse", "external_benesse", "m3"),
    ]
    table = [
        "| Scope | Window | Student FE beta | Student-course FE beta | Student-course 95% CI | p | Rows | Student-courses |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for label, scope, window in selected:
        baseline = find(rows, scope, window, "student_assessment_fe_adjusted")
        strict = find(rows, scope, window, "student_course_assessment_fe_adjusted")
        table.append(
            "| "
            + " | ".join([
                label,
                window,
                fnum(baseline["beta_std"]),
                fnum(strict["beta_std"]),
                f"[{fnum(strict['ci_low'])}, {fnum(strict['ci_high'])}]",
                pnum(strict["p_cluster"]),
                nfmt(strict["identified_rows"]),
                nfmt(strict["student_courses"]),
            ])
            + " |"
        )
    path = PAPER_TABLES / "table4_student_course_fe_robustness.md"
    path.write_text("\n".join(table) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
