#!/usr/bin/env python3
import csv
import os
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ANALYSIS_HOST = os.environ.get("ANALYSIS_MYSQL_HOST", "10.236.173.145")
ANALYSIS_PORT = os.environ.get("ANALYSIS_MYSQL_PORT", "33308")
ANALYSIS_USER = os.environ.get("ANALYSIS_MYSQL_USER", "reader")
ANALYSIS_DB = os.environ.get("ANALYSIS_MYSQL_DB", "analysis_development")

MOODLE_HOST = os.environ.get("MOODLE_MYSQL_HOST", "10.236.173.145")
MOODLE_PORT = os.environ.get("MOODLE_MYSQL_PORT", "33307")
MOODLE_USER = os.environ.get("MOODLE_MYSQL_USER", "reader")
MOODLE_DB = os.environ.get("MOODLE_MYSQL_DB", "moodle")


def mysql_query(host, port, user, database, password, sql):
    env = os.environ.copy()
    if password:
        env["MYSQL_PWD"] = password
    cmd = [
        "mysql",
        "-N",
        "-B",
        "-h",
        host,
        "-P",
        str(port),
        "-u",
        user,
        "-D",
        database,
        "-e",
        sql,
    ]
    proc = subprocess.run(cmd, env=env, text=True, capture_output=True, check=True)
    rows = []
    for line in proc.stdout.splitlines():
        rows.append(line.split("\t"))
    return rows


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def norm_subject(value):
    if not value:
        return ""
    if value in {"数学", "英語", "国語", "理科", "社会", "保健体育", "技術・家庭", "美術", "音楽", "道徳", "HR"}:
        return value
    return ""


def infer_subject(course_name, path_names):
    for name in path_names:
        subject = norm_subject(name)
        if subject:
            return subject, "moodle_category"
    checks = [
        ("数学", "数学"),
        ("英語", "英語"),
        ("国語", "国語"),
        ("理科", "理科"),
        ("社会", "社会"),
        ("保健体育", "保健体育"),
        ("技術・家庭", "技術・家庭"),
        ("美術", "美術"),
        ("音楽", "音楽"),
        ("道徳", "道徳"),
    ]
    for needle, subject in checks:
        if needle in course_name:
            return subject, "course_name"
    if re.search(r"(?:^|[^A-Za-z])(?:IEC|EEC)[0-9ⅠⅡⅢI]+", course_name):
        return "英語", "course_name_program_code"
    return "", "unclassified"


def infer_grade(course_name, path_names):
    for name in path_names:
        if re.fullmatch(r"[中高][123]", name):
            return name, "moodle_category"
    if "中学共通" in path_names:
        return "中学共通", "moodle_category"
    if "高校" in path_names:
        broad = ("高校", "moodle_category_broad")
    else:
        broad = ("", "unclassified")

    patterns = [
        (r"高校\s*1\s*年|高\s*1|\[高1\]|IEC1|EEC1|IECI|EECI", "高1"),
        (r"高校\s*2\s*年|高\s*2|\[高2\]|IEC2|EEC2|IECII|EECII|IECⅡ|EECⅡ", "高2"),
        (r"高校\s*3\s*年|高\s*3|\[高3\]|IEC3|EEC3|IECIII|EECIII", "高3"),
        (r"中学\s*1\s*年|中\s*1|\[中1\]|1年.*\[中学\]", "中1"),
        (r"中学\s*2\s*年|中\s*2|\[中2\]|2年.*\[中学\]", "中2"),
        (r"中学\s*3\s*年|中\s*3|\[中3\]|3年.*\[中学\]", "中3"),
    ]
    for pattern, grade in patterns:
        if re.search(pattern, course_name):
            return grade, "course_name"
    return broad


def school_level(grade):
    if grade.startswith("中"):
        return "junior_high"
    if grade.startswith("高") or grade == "高校":
        return "senior_high"
    return ""


def infer_class_group(course_name):
    matches = re.findall(r"(?:[A-ZＡ-Ｚ]\s*組|\d+\s*-\s*\d+\s*組)", course_name)
    if matches:
        return ",".join(m.replace(" ", "") for m in matches)
    return ""


def main():
    analysis_pwd = os.environ.get("ANALYSIS_MYSQL_PWD", os.environ.get("MYSQL_PWD", ""))
    moodle_pwd = os.environ.get("MOODLE_MYSQL_PWD", os.environ.get("MYSQL_PWD", ""))

    score_rows = mysql_query(
        ANALYSIS_HOST,
        ANALYSIS_PORT,
        ANALYSIS_USER,
        ANALYSIS_DB,
        analysis_pwd,
        """
        SELECT
          course_id,
          course_name,
          COUNT(*) AS score_rows,
          COUNT(DISTINCT student_id) AS students,
          COUNT(DISTINCT name) AS tests,
          COALESCE(DATE_FORMAT(MIN(date_at), '%Y-%m-%d'), '') AS min_date,
          COALESCE(DATE_FORMAT(MAX(date_at), '%Y-%m-%d'), '') AS max_date
        FROM course_student_scores
        GROUP BY course_id, course_name
        ORDER BY course_id
        """,
    )

    courses = mysql_query(
        MOODLE_HOST,
        MOODLE_PORT,
        MOODLE_USER,
        MOODLE_DB,
        moodle_pwd,
        """
        SELECT id, fullname, shortname, category
        FROM mdl_course
        ORDER BY id
        """,
    )
    categories = mysql_query(
        MOODLE_HOST,
        MOODLE_PORT,
        MOODLE_USER,
        MOODLE_DB,
        moodle_pwd,
        """
        SELECT id, name, parent, depth, path
        FROM mdl_course_categories
        ORDER BY id
        """,
    )

    course_by_id = {
        row[0]: {
            "moodle_course_id": row[0],
            "moodle_course_name": row[1],
            "shortname": row[2],
            "category_id": row[3],
        }
        for row in courses
    }
    category_by_id = {
        row[0]: {"id": row[0], "name": row[1], "parent": row[2], "depth": row[3], "path": row[4]}
        for row in categories
    }

    enriched = []
    for course_id, course_name, score_count, student_count, test_count, min_date, max_date in score_rows:
        moodle = course_by_id.get(course_id, {})
        category_id = moodle.get("category_id", "")
        cat = category_by_id.get(category_id, {})
        path_ids = [part for part in cat.get("path", "").split("/") if part]
        path_names = [category_by_id.get(pid, {}).get("name", "") for pid in path_ids]
        year_category = path_names[0] if path_names else ""
        grade, grade_source = infer_grade(course_name, path_names)
        subject, subject_source = infer_subject(course_name, path_names)
        enriched.append(
            {
                "course_id": course_id,
                "score_course_name": course_name,
                "moodle_course_name": moodle.get("moodle_course_name", ""),
                "score_rows": int(score_count),
                "students": int(student_count),
                "tests": int(test_count),
                "min_date": min_date,
                "max_date": max_date,
                "moodle_category_path": " > ".join(path_names),
                "year_category": year_category,
                "grade_level": grade,
                "grade_source": grade_source,
                "school_level": school_level(grade),
                "subject": subject,
                "subject_source": subject_source,
                "class_group": infer_class_group(course_name),
            }
        )

    fields = [
        "course_id",
        "score_course_name",
        "moodle_course_name",
        "score_rows",
        "students",
        "tests",
        "min_date",
        "max_date",
        "moodle_category_path",
        "year_category",
        "grade_level",
        "grade_source",
        "school_level",
        "subject",
        "subject_source",
        "class_group",
    ]
    write_csv(OUT_DIR / "score_course_context.csv", fields, enriched)

    def aggregate(keys):
        buckets = defaultdict(lambda: {"courses": 0, "score_rows": 0, "students_course_sum": 0, "tests_course_sum": 0})
        for row in enriched:
            key = tuple(row[k] or "(unclassified)" for k in keys)
            b = buckets[key]
            b["courses"] += 1
            b["score_rows"] += row["score_rows"]
            b["students_course_sum"] += row["students"]
            b["tests_course_sum"] += row["tests"]
        return [
            {**{keys[i]: key[i] for i in range(len(keys))}, **value}
            for key, value in sorted(buckets.items(), key=lambda item: (-item[1]["score_rows"], item[0]))
        ]

    summary_rows = []
    for label, keys in [
        ("by_grade_subject", ["grade_level", "subject"]),
        ("by_year_grade_subject", ["year_category", "grade_level", "subject"]),
        ("by_subject", ["subject"]),
        ("by_grade", ["grade_level"]),
        ("by_source", ["grade_source", "subject_source"]),
    ]:
        rows = aggregate(keys)
        write_csv(OUT_DIR / f"{label}.csv", keys + ["courses", "score_rows", "students_course_sum", "tests_course_sum"], rows)
        summary_rows.append((label, rows[:12]))

    source_counts = Counter((row["grade_source"], row["subject_source"]) for row in enriched)
    unclassified = [row for row in enriched if not row["grade_level"] or not row["subject"]]

    report = []
    report.append("# Course Context Mapping - Score Table to Moodle")
    report.append("")
    report.append("## Scope")
    report.append(f"- Score courses checked: {len(enriched)}")
    report.append(f"- Score rows covered: {sum(row['score_rows'] for row in enriched):,}")
    report.append(f"- Courses found in Moodle: {sum(1 for row in enriched if row['moodle_course_name'])}")
    report.append(f"- Courses missing from Moodle: {sum(1 for row in enriched if not row['moodle_course_name'])}")
    report.append(f"- Courses with grade/level classified: {sum(1 for row in enriched if row['grade_level'])}")
    report.append(f"- Courses with subject classified: {sum(1 for row in enriched if row['subject'])}")
    report.append("")
    report.append("## Classification Source Counts")
    for (grade_src, subject_src), count in sorted(source_counts.items(), key=lambda item: (-item[1], item[0])):
        report.append(f"- grade={grade_src}, subject={subject_src}: {count} courses")
    report.append("")

    for label, rows in summary_rows:
        report.append(f"## {label}")
        for row in rows:
            dims = ", ".join(f"{k}={row[k]}" for k in row.keys() if k not in {"courses", "score_rows", "students_course_sum", "tests_course_sum"})
            report.append(
                f"- {dims}: {row['courses']} courses, {row['score_rows']:,} score rows, "
                f"{row['students_course_sum']:,} course-student counts, {row['tests_course_sum']:,} course-test counts"
            )
        report.append("")

    if unclassified:
        report.append("## Unclassified Courses")
        for row in unclassified[:40]:
            report.append(
                f"- {row['course_id']} {row['score_course_name']} | path={row['moodle_category_path']} | "
                f"grade={row['grade_level'] or '?'} subject={row['subject'] or '?'}"
            )
        if len(unclassified) > 40:
            report.append(f"- ... {len(unclassified) - 40} more")
        report.append("")

    report.append("## Interpretation")
    report.append("- Moodle category paths are strong enough to recover year/grade/subject for many older courses.")
    report.append("- Newer courses often sit directly under grade categories, so subject must be inferred from course names.")
    report.append("- This supports grade/level and subject stratification, but classification should be stored with source flags.")
    report.append("- For cross-subject papers, treat subject as a covariate/stratum; avoid pooling math, Japanese, and English as equivalent content.")
    (OUT_DIR / "course_context_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print("\n".join(report))


if __name__ == "__main__":
    main()
