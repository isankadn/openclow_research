#!/usr/bin/env python3
import csv
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

ANALYSIS_HOST = os.environ.get("ANALYSIS_MYSQL_HOST", "10.236.173.145")
ANALYSIS_PORT = os.environ.get("ANALYSIS_MYSQL_PORT", "33308")
ANALYSIS_USER = os.environ.get("ANALYSIS_MYSQL_USER", "reader")
ANALYSIS_DB = os.environ.get("ANALYSIS_MYSQL_DB", "analysis_development")

COURSE_CONTEXT = Path("/home/ubuntu/.openclaw/workspace/projects/leaf-course-context-2026-05-19/outputs/score_course_context.csv")


def mysql_query(sql):
    env = os.environ.copy()
    pwd = os.environ.get("ANALYSIS_MYSQL_PWD", os.environ.get("MYSQL_PWD", ""))
    if pwd:
        env["MYSQL_PWD"] = pwd
    cmd = [
        "mysql", "-N", "-B", "-h", ANALYSIS_HOST, "-P", str(ANALYSIS_PORT),
        "-u", ANALYSIS_USER, "-D", ANALYSIS_DB, "-e", sql,
    ]
    proc = subprocess.run(cmd, env=env, text=True, capture_output=True, check=True)
    return [line.split("\t") for line in proc.stdout.splitlines()]


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_float(value):
    if value in (None, "", "\\N"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def fmt_number(value):
    if value is None:
        return ""
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.6g}"


def score_fields_from_group(
    quiz_min_value,
    quiz_max_value,
    quiz_mean_value,
    quiz_missing_rows,
    score_min_value,
    score_max_value,
    scaled_min_value,
    scaled_max_value,
    original_rows,
):
    quiz_min = parse_float(quiz_min_value)
    quiz_max = parse_float(quiz_max_value)
    quiz_mean = parse_float(quiz_mean_value)
    quiz_missing = int(quiz_missing_rows or 0)
    score_min = parse_float(score_min_value)
    score_max = parse_float(score_max_value)
    scaled_min = parse_float(scaled_min_value)
    scaled_max = parse_float(scaled_max_value)
    original_count = int(original_rows)

    flags = []
    if quiz_missing >= original_count or quiz_mean is None:
        flags.append("missing_quiz")
    if score_min is None or score_max is None or score_max <= score_min:
        flags.append("invalid_score_range")
    if quiz_min is not None and quiz_max is not None and abs(quiz_min - quiz_max) > 1e-9:
        flags.append("duplicate_score_conflict")
    if quiz_min is not None and score_min is not None and quiz_min < score_min:
        flags.append("score_below_min")
    if quiz_max is not None and score_max is not None and quiz_max > score_max:
        flags.append("score_above_max")

    normalized = None
    if not flags and quiz_mean is not None and score_min is not None and score_max is not None:
        normalized = (quiz_mean - score_min) / (score_max - score_min)

    return {
        "quiz_score": fmt_number(quiz_mean),
        "score_min": fmt_number(score_min),
        "score_max": fmt_number(score_max),
        "scaled_score": fmt_number(scaled_min) if scaled_min == scaled_max else "",
        "score_normalized_0_1": fmt_number(normalized),
        "score_validity_flag": "|".join(flags) if flags else "valid",
    }


def normalize_name(name):
    text = (name or "").strip().replace("　", " ")
    return re.sub(r"\s+", " ", text)


def classify_test_name(name):
    text = normalize_name(name)
    lower = text.lower()
    if "benesse" in lower or "ベネッセ" in text:
        family = "external_benesse"
    elif "模試" in text:
        family = "external_mock_exam"
    elif "中間" in text or "期末" in text or "学年末" in text:
        family = "school_regular_exam"
    elif "章" in text:
        family = "unit_or_chapter_test"
    elif "夏休み明け" in text or "冬明け" in text or "春休み明け" in text:
        family = "break_after_test"
    elif "小テスト" in text or "確認" in text or "quiz" in lower or "クイズ" in text:
        family = "quiz_or_check"
    elif "test" in lower or "テスト" in text:
        family = "generic_test"
    else:
        family = "unclear"

    if "学年末" in text:
        term = "academic_year_end"
    elif "前期" in text:
        term = "first_term"
    elif "後期" in text:
        term = "second_term"
    elif "1学期" in text or "一学期" in text:
        term = "term_1"
    elif "2学期" in text or "二学期" in text:
        term = "term_2"
    elif "3学期" in text or "三学期" in text:
        term = "term_3"
    else:
        term = "unknown"

    if "学年末" in text:
        timing = "year_end_final"
    elif "中間" in text:
        timing = "midterm"
    elif "期末" in text:
        timing = "final"
    elif "模試" in text:
        timing = "mock_exam"
    elif "実力" in text:
        timing = "achievement_or_proficiency"
    elif "章" in text:
        timing = "unit_or_chapter"
    elif "夏休み明け" in text or "冬明け" in text or "春休み明け" in text:
        timing = "after_break"
    else:
        timing = "unknown"

    if re.search(r"英語|IEC|EEC|英\b", text):
        subject_hint = "英語"
    elif re.search(r"数学|数S|数①|数②|数I|数Ⅰ|数A|数Ａ|数Ⅱ|数II|数B|数Ｂ|数", text):
        subject_hint = "数学"
    elif "国語" in text:
        subject_hint = "国語"
    elif "理科" in text:
        subject_hint = "理科"
    elif "社会" in text:
        subject_hint = "社会"
    else:
        subject_hint = "unknown"

    if re.search(r"total|合計|総合", lower):
        score_component = "total"
    elif "技能" in text:
        score_component = "skill"
    elif "見方" in text or "考え方" in text:
        score_component = "thinking_judgement_expression"
    elif re.search(r"\[S\]|\bS\b", text):
        score_component = "subscore_s"
    elif re.search(r"\[R\]|\bR\b", text):
        score_component = "subscore_r"
    elif re.search(r"\[W\]|\bW\b", text):
        score_component = "subscore_w"
    elif re.search(r"数[①1]", text):
        score_component = "math_part_1"
    elif re.search(r"数[②2]", text):
        score_component = "math_part_2"
    else:
        score_component = "unspecified_or_single_score"

    confidence = "high"
    if family == "external_benesse" and timing == "mock_exam" and subject_hint != "unknown":
        confidence = "high"
    elif family in {"unclear", "generic_test"}:
        confidence = "low"
    elif subject_hint == "unknown" or term == "unknown":
        confidence = "medium"

    return {
        "test_name_normalized": text,
        "test_family": family,
        "term": term,
        "timing": timing,
        "subject_hint_from_name": subject_hint,
        "score_component": score_component,
        "classification_confidence": confidence,
    }


def load_course_context():
    if not COURSE_CONTEXT.exists():
        return {}
    with COURSE_CONTEXT.open(encoding="utf-8") as f:
        return {row["course_id"]: row for row in csv.DictReader(f)}


def aggregate(rows, dims):
    buckets = defaultdict(lambda: {
        "clean_score_rows": 0, "duplicate_extra_rows": 0,
        "students": set(), "courses": set(), "test_names": set(),
    })
    for row in rows:
        key = tuple(row.get(dim) or "(missing)" for dim in dims)
        b = buckets[key]
        b["clean_score_rows"] += int(row["clean_score_rows"])
        b["duplicate_extra_rows"] += int(row["duplicate_extra_rows"])
        b["students"].add(row["student_id"])
        b["courses"].add(row["course_id"])
        b["test_names"].add(row["name"])
    out = []
    for key, b in buckets.items():
        out.append({
            **{dims[i]: key[i] for i in range(len(dims))},
            "clean_score_rows": b["clean_score_rows"],
            "duplicate_extra_rows": b["duplicate_extra_rows"],
            "students": len(b["students"]),
            "courses": len(b["courses"]),
            "test_names": len(b["test_names"]),
        })
    return sorted(out, key=lambda r: (-r["clean_score_rows"], tuple(r[d] for d in dims)))


def main():
    context = load_course_context()
    overview_rows = mysql_query("""
        SELECT COUNT(*) AS total_rows,
               SUM(CASE WHEN date_at IS NULL THEN 1 ELSE 0 END) AS missing_date_rows,
               SUM(CASE WHEN date_at IS NOT NULL THEN 1 ELSE 0 END) AS dated_rows,
               COUNT(DISTINCT student_id) AS students,
               COUNT(DISTINCT course_id) AS courses,
               COUNT(DISTINCT name) AS test_names,
               MIN(date_at) AS min_date,
               MAX(date_at) AS max_date
        FROM course_student_scores
    """)[0]

    duplicate_rows = mysql_query("""
        SELECT COUNT(*) AS duplicate_groups, COALESCE(SUM(row_count - 1), 0) AS duplicate_extra_rows
        FROM (
          SELECT student_id, course_id, name, date_at, COUNT(*) AS row_count
          FROM course_student_scores
          WHERE date_at IS NOT NULL
          GROUP BY student_id, course_id, name, date_at
          HAVING COUNT(*) > 1
        ) d
    """)[0]

    clean_grain_raw = mysql_query("""
        SELECT student_id, course_id, course_name, name,
               DATE_FORMAT(date_at, '%Y-%m-%d') AS test_date,
               DATE_FORMAT(date_at, '%Y') AS test_year,
               MIN(quiz) AS quiz_min_value,
               MAX(quiz) AS quiz_max_value,
               AVG(quiz) AS quiz_mean_value,
               SUM(CASE WHEN quiz IS NULL THEN 1 ELSE 0 END) AS quiz_missing_rows,
               MIN(`min`) AS score_min_value,
               MAX(`max`) AS score_max_value,
               MIN(scaled) AS scaled_min_value,
               MAX(scaled) AS scaled_max_value,
               COUNT(*) AS original_rows
        FROM course_student_scores
        WHERE date_at IS NOT NULL
        GROUP BY student_id, course_id, course_name, name, date_at
        ORDER BY test_date, course_id, name, student_id
    """)

    clean_rows = []
    test_name_rows = {}
    for (
        student_id, course_id, course_name, name, test_date, test_year,
        quiz_min_value, quiz_max_value, quiz_mean_value, quiz_missing_rows,
        score_min_value, score_max_value, scaled_min_value, scaled_max_value,
        original_rows,
    ) in clean_grain_raw:
        ctx = context.get(course_id, {})
        cls = classify_test_name(name)
        duplicate_extra = max(int(original_rows) - 1, 0)
        score_fields = score_fields_from_group(
            quiz_min_value, quiz_max_value, quiz_mean_value, quiz_missing_rows,
            score_min_value, score_max_value, scaled_min_value, scaled_max_value,
            original_rows,
        )
        row = {
            "student_id": student_id, "course_id": course_id, "course_name": course_name,
            "name": name, "test_date": test_date, "test_year": test_year,
            **score_fields,
            "grade_level": ctx.get("grade_level", ""), "school_level": ctx.get("school_level", ""),
            "course_subject": ctx.get("subject", ""), "class_group": ctx.get("class_group", ""),
            **cls, "clean_score_rows": 1, "original_rows": int(original_rows),
            "duplicate_extra_rows": duplicate_extra,
        }
        clean_rows.append(row)
        t = test_name_rows.setdefault(name, {
            "name": name, **cls, "clean_score_rows": 0, "duplicate_extra_rows": 0,
            "students": set(), "courses": set(), "years": set(),
            "course_subjects": set(), "grade_levels": set(),
        })
        t["clean_score_rows"] += 1
        t["duplicate_extra_rows"] += duplicate_extra
        t["students"].add(student_id)
        t["courses"].add(course_id)
        t["years"].add(test_year)
        if ctx.get("subject"):
            t["course_subjects"].add(ctx["subject"])
        if ctx.get("grade_level"):
            t["grade_levels"].add(ctx["grade_level"])

    detail_fields = [
        "student_id", "course_id", "course_name", "name", "test_date", "test_year",
        "quiz_score", "score_min", "score_max", "scaled_score", "score_normalized_0_1",
        "score_validity_flag",
        "grade_level", "school_level", "course_subject", "class_group",
        "test_name_normalized", "test_family", "term", "timing", "subject_hint_from_name",
        "score_component", "classification_confidence", "clean_score_rows",
        "original_rows", "duplicate_extra_rows",
    ]
    write_csv(OUT / "clean_score_grain_local_only.csv", detail_fields, clean_rows)

    test_name_out = []
    for row in test_name_rows.values():
        test_name_out.append({
            "name": row["name"], "test_name_normalized": row["test_name_normalized"],
            "test_family": row["test_family"], "term": row["term"], "timing": row["timing"],
            "subject_hint_from_name": row["subject_hint_from_name"],
            "score_component": row["score_component"],
            "classification_confidence": row["classification_confidence"],
            "clean_score_rows": row["clean_score_rows"],
            "duplicate_extra_rows": row["duplicate_extra_rows"],
            "students": len(row["students"]), "courses": len(row["courses"]),
            "years": "|".join(sorted(row["years"])),
            "course_subjects": "|".join(sorted(row["course_subjects"])),
            "grade_levels": "|".join(sorted(row["grade_levels"])),
        })
    test_name_out.sort(key=lambda r: (-r["clean_score_rows"], r["name"]))
    write_csv(OUT / "test_name_classification.csv", [
        "name", "test_name_normalized", "test_family", "term", "timing",
        "subject_hint_from_name", "score_component", "classification_confidence",
        "clean_score_rows", "duplicate_extra_rows", "students", "courses",
        "years", "course_subjects", "grade_levels",
    ], test_name_out)

    summaries = {
        "summary_by_year.csv": ["test_year"],
        "summary_by_test_family.csv": ["test_family"],
        "summary_by_year_family.csv": ["test_year", "test_family"],
        "summary_by_grade_subject_family.csv": ["grade_level", "course_subject", "test_family"],
        "summary_by_term_timing.csv": ["term", "timing"],
        "summary_by_confidence.csv": ["classification_confidence"],
    }
    summary_outputs = {}
    for filename, dims in summaries.items():
        rows = aggregate(clean_rows, dims)
        summary_outputs[filename] = (dims, rows)
        write_csv(OUT / filename, dims + ["clean_score_rows", "duplicate_extra_rows", "students", "courses", "test_names"], rows)

    report = []
    report.append("# Grade/Test Table Profile")
    report.append("")
    report.append("## Scope And Cleaning Rule")
    report.append("- Source: analysis_development.course_student_scores.")
    report.append("- date_at is treated as the test conduct date.")
    report.append("- Rows with missing date_at are excluded from test-date-based analysis.")
    report.append("- Duplicate check grain: student_id + course_id + name + date_at.")
    report.append("- Clean analysis grain: one row per student_id/course_id/name/date_at.")
    report.append("")
    report.append("## Raw Coverage")
    labels = ["total_rows", "missing_date_rows", "dated_rows", "students", "courses", "test_names", "min_date", "max_date"]
    for label, value in zip(labels, overview_rows):
        report.append(f"- {label}: {value}")
    report.append("")
    report.append("## Duplicate Check")
    report.append(f"- duplicate groups at clean grain: {duplicate_rows[0]}")
    report.append(f"- duplicate extra rows removed at clean grain: {duplicate_rows[1]}")
    report.append("")
    report.append("## Clean Dated Dataset")
    report.append(f"- clean dated score rows: {len(clean_rows):,}")
    report.append(f"- distinct classified test names: {len(test_name_out):,}")
    validity_counts = aggregate(clean_rows, ["score_validity_flag"])
    for row in validity_counts:
        report.append(f"- score_validity_flag={row['score_validity_flag']}: {row['clean_score_rows']:,} rows")
    report.append("")
    for title, filename, max_rows in [
        ("By Test Family", "summary_by_test_family.csv", 20),
        ("By Year", "summary_by_year.csv", 20),
        ("By Year And Test Family", "summary_by_year_family.csv", 30),
        ("By Grade Subject And Family", "summary_by_grade_subject_family.csv", 30),
        ("Classification Confidence", "summary_by_confidence.csv", 10),
    ]:
        dims, rows = summary_outputs[filename]
        report.append(f"## {title}")
        for row in rows[:max_rows]:
            label = ", ".join(f"{dim}={row[dim]}" for dim in dims)
            report.append(
                f"- {label}: {row['clean_score_rows']:,} clean rows, "
                f"{row['students']:,} students, {row['courses']:,} courses, {row['test_names']:,} test names"
            )
        report.append("")
    report.append("## Top Test Names By Clean Row Count")
    for row in test_name_out[:30]:
        report.append(
            f"- {row['name']}: family={row['test_family']}, term={row['term']}, timing={row['timing']}, "
            f"subject_hint={row['subject_hint_from_name']}, component={row['score_component']}, "
            f"confidence={row['classification_confidence']}, rows={row['clean_score_rows']}, "
            f"students={row['students']}, courses={row['courses']}, years={row['years']}"
        )
    report.append("")
    report.append("## Initial Interpretation")
    report.append("- The dated grade/test table is large enough to start the outcome-side analysis after excluding missing date_at rows.")
    report.append("- Missing date_at rows should be kept out of test-window analysis unless a reliable date recovery rule is later provided.")
    report.append("- Test names are inconsistent and require a maintained classification layer; Benesse/mock exams should be separated from regular school exams.")
    report.append("- Low-confidence test-name classifications should not drive paper claims until reviewed or mapped manually.")
    (OUT / "grade_test_profile_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
