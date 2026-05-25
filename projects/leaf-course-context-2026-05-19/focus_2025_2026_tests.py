#!/usr/bin/env python3
import csv
import os
import subprocess
from collections import defaultdict
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
OUT_DIR = PROJECT_DIR / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
COURSE_CONTEXT = OUT_DIR / "score_course_context.csv"

ANALYSIS_HOST = os.environ.get("ANALYSIS_MYSQL_HOST", "10.236.173.145")
ANALYSIS_PORT = os.environ.get("ANALYSIS_MYSQL_PORT", "33308")
ANALYSIS_USER = os.environ.get("ANALYSIS_MYSQL_USER", "reader")
ANALYSIS_DB = os.environ.get("ANALYSIS_MYSQL_DB", "analysis_development")


def mysql_query(sql):
    env = os.environ.copy()
    password = os.environ.get("ANALYSIS_MYSQL_PWD", os.environ.get("MYSQL_PWD", ""))
    if password:
        env["MYSQL_PWD"] = password
    cmd = [
        "mysql",
        "-N",
        "-B",
        "-h",
        ANALYSIS_HOST,
        "-P",
        str(ANALYSIS_PORT),
        "-u",
        ANALYSIS_USER,
        "-D",
        ANALYSIS_DB,
        "-e",
        sql,
    ]
    proc = subprocess.run(cmd, env=env, text=True, capture_output=True, check=True)
    return [line.split("\t") for line in proc.stdout.splitlines()]


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_context():
    with COURSE_CONTEXT.open(encoding="utf-8") as f:
        return {row["course_id"]: row for row in csv.DictReader(f)}


def aggregate(rows, dims):
    buckets = defaultdict(lambda: {"score_rows": 0, "students": set(), "tests": set(), "courses": set()})
    for row in rows:
        key = tuple(row.get(dim) or "(unclassified)" for dim in dims)
        bucket = buckets[key]
        bucket["score_rows"] += int(row["score_rows"])
        bucket["students"].add(row["student_id"])
        bucket["tests"].add(row["test_name"])
        bucket["courses"].add(row["course_id"])
    out = []
    for key, value in buckets.items():
        out.append(
            {
                **{dims[i]: key[i] for i in range(len(dims))},
                "score_rows": value["score_rows"],
                "students": len(value["students"]),
                "tests": len(value["tests"]),
                "courses": len(value["courses"]),
            }
        )
    return sorted(out, key=lambda r: (-r["score_rows"], tuple(r[d] for d in dims)))


def main():
    context = load_context()
    raw = mysql_query(
        """
        SELECT
          course_id,
          course_name,
          name AS test_name,
          DATE_FORMAT(date_at, '%Y-%m-%d') AS test_date,
          DATE_FORMAT(date_at, '%Y') AS test_year,
          DATE_FORMAT(date_at, '%Y-%m') AS test_month,
          student_id,
          COUNT(*) AS score_rows
        FROM course_student_scores
        WHERE date_at >= '2025-01-01'
          AND date_at < '2027-01-01'
        GROUP BY course_id, course_name, name, test_date, test_year, test_month, student_id
        ORDER BY test_date, course_id, name, student_id
        """
    )

    rows = []
    for course_id, course_name, test_name, test_date, test_year, test_month, student_id, score_rows in raw:
        ctx = context.get(course_id, {})
        rows.append(
            {
                "test_year": test_year,
                "test_month": test_month,
                "test_date": test_date,
                "course_id": course_id,
                "course_name": course_name,
                "grade_level": ctx.get("grade_level", ""),
                "school_level": ctx.get("school_level", ""),
                "subject": ctx.get("subject", ""),
                "class_group": ctx.get("class_group", ""),
                "grade_source": ctx.get("grade_source", ""),
                "subject_source": ctx.get("subject_source", ""),
                "test_name": test_name,
                "student_id": student_id,
                "score_rows": score_rows,
            }
        )

    detail_fields = [
        "test_year",
        "test_month",
        "test_date",
        "course_id",
        "course_name",
        "grade_level",
        "school_level",
        "subject",
        "class_group",
        "grade_source",
        "subject_source",
        "test_name",
        "student_id",
        "score_rows",
    ]
    write_csv(OUT_DIR / "tests_2025_2026_detail.csv", detail_fields, rows)

    summaries = {
        "tests_2025_2026_by_year.csv": ["test_year"],
        "tests_2025_2026_by_month.csv": ["test_month"],
        "tests_2025_2026_by_grade_subject.csv": ["grade_level", "subject"],
        "tests_2025_2026_by_year_grade_subject.csv": ["test_year", "grade_level", "subject"],
        "tests_2025_2026_by_course.csv": ["course_id", "course_name", "grade_level", "subject"],
        "tests_2025_2026_by_test_name.csv": ["test_name", "grade_level", "subject"],
    }

    summary_outputs = {}
    for filename, dims in summaries.items():
        agg = aggregate(rows, dims)
        summary_outputs[filename] = (dims, agg)
        write_csv(OUT_DIR / filename, dims + ["score_rows", "students", "tests", "courses"], agg)

    years_present = {row["test_year"] for row in rows}
    total_rows = sum(int(row["score_rows"]) for row in rows)
    total_students = len({row["student_id"] for row in rows})
    total_tests = len({row["test_name"] for row in rows})
    total_courses = len({row["course_id"] for row in rows})

    report = []
    report.append("# 2025-2026 Test Conduct Date Focus")
    report.append("")
    report.append("## Scope")
    report.append("- Date filter: date_at >= 2025-01-01 and date_at < 2027-01-01")
    report.append("- Interpretation: date_at is the test conduct date.")
    report.append(f"- Test years present in filtered rows: {', '.join(sorted(years_present)) if years_present else 'none'}")
    report.append(f"- 2026 rows present: {'yes' if '2026' in years_present else 'no'}")
    report.append(f"- Score rows: {total_rows:,}")
    report.append(f"- Distinct students: {total_students:,}")
    report.append(f"- Distinct test names: {total_tests:,}")
    report.append(f"- Distinct courses: {total_courses:,}")
    report.append("")

    for title, filename, max_rows in [
        ("By Month", "tests_2025_2026_by_month.csv", 12),
        ("By Grade And Subject", "tests_2025_2026_by_grade_subject.csv", 20),
        ("Top Courses", "tests_2025_2026_by_course.csv", 20),
        ("Top Test Names", "tests_2025_2026_by_test_name.csv", 20),
    ]:
        dims, agg = summary_outputs[filename]
        report.append(f"## {title}")
        for row in agg[:max_rows]:
            label = ", ".join(f"{dim}={row[dim]}" for dim in dims)
            report.append(
                f"- {label}: {row['score_rows']:,} score rows, "
                f"{row['students']:,} students, {row['tests']:,} tests, {row['courses']:,} courses"
            )
        report.append("")

    report.append("## Working Interpretation")
    report.append("- The current 2025-2026 conduct-date window is really a 2025-only test window in the available score table.")
    report.append("- It is still useful for recent-course analysis, especially 2024年度 courses whose tests were conducted in Jan-Mar 2025.")
    report.append("- For a strong paper, use this as a recent-test subset and avoid saying we analyzed 2026 unless new 2026 rows are added later.")
    report.append("- Grade/subject comparisons are feasible, but Japanese/国語 remains sparse compared with math and English.")
    (OUT_DIR / "tests_2025_2026_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
