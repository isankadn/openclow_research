#!/usr/bin/env python3
import csv
import subprocess
from pathlib import Path

BASE = Path('/home/ubuntu/.openclaw/workspace/projects/leaf-score-integration-2026-04-03')
OUT = BASE / 'outputs'
OUT.mkdir(parents=True, exist_ok=True)

MYSQL = "mysql -N -h 10.236.173.145 -P 33308 -u reader -p'bar' -D analysis_development -e"


def run_sql(sql: str):
    cmd = f"{MYSQL} \"{sql}\""
    out = subprocess.check_output(cmd, shell=True, text=True)
    return [line.split('\t') for line in out.splitlines() if line.strip()]


def write_csv(path: Path, header, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    overall = run_sql("""
SELECT COUNT(*) AS rows_total,
       COUNT(DISTINCT student_id) AS students,
       COUNT(DISTINCT course_id) AS courses,
       COUNT(DISTINCT name) AS tests,
       COUNT(DISTINCT CONCAT(course_id,'|',name,'|',COALESCE(CAST(date_at AS CHAR),'NULL'))) AS course_test_dates,
       MIN(date_at) AS min_test_date,
       MAX(date_at) AS max_test_date,
       ROUND(AVG(quiz),2) AS avg_quiz,
       MIN(quiz) AS min_quiz,
       MAX(quiz) AS max_quiz
FROM course_student_scores
WHERE date_at IS NOT NULL AND quiz IS NOT NULL;
""")
    write_csv(OUT / 'overall_summary.csv',
              ['rows_total','students','courses','tests','course_test_dates','min_test_date','max_test_date','avg_quiz','min_quiz','max_quiz'],
              overall)

    top_courses = run_sql("""
SELECT course_id, course_name, COUNT(*) AS score_rows, COUNT(DISTINCT student_id) AS students,
       COUNT(DISTINCT name) AS tests, ROUND(AVG(quiz),2) AS avg_quiz
FROM course_student_scores
WHERE date_at IS NOT NULL AND quiz IS NOT NULL
GROUP BY course_id, course_name
ORDER BY score_rows DESC
LIMIT 50;
""")
    write_csv(OUT / 'top_courses_by_score_rows.csv',
              ['course_id','course_name','score_rows','students','tests','avg_quiz'],
              top_courses)

    top_tests = run_sql("""
SELECT name, COUNT(*) AS score_rows, COUNT(DISTINCT course_id) AS courses,
       COUNT(DISTINCT student_id) AS students, ROUND(AVG(quiz),2) AS avg_quiz
FROM course_student_scores
WHERE date_at IS NOT NULL AND quiz IS NOT NULL
GROUP BY name
ORDER BY score_rows DESC
LIMIT 50;
""")
    write_csv(OUT / 'top_tests_by_score_rows.csv',
              ['name','score_rows','courses','students','avg_quiz'],
              top_tests)

    repeat_dist = run_sql("""
SELECT tests_per_student_in_course, COUNT(*) AS student_course_pairs
FROM (
  SELECT student_id, course_id, COUNT(*) AS tests_per_student_in_course
  FROM course_student_scores
  WHERE date_at IS NOT NULL AND quiz IS NOT NULL
  GROUP BY student_id, course_id
) t
GROUP BY tests_per_student_in_course
ORDER BY tests_per_student_in_course;
""")
    write_csv(OUT / 'tests_per_student_course_distribution.csv',
              ['tests_per_student_in_course','student_course_pairs'],
              repeat_dist)

    monthly = run_sql("""
SELECT DATE_FORMAT(date_at, '%Y-%m') AS ym, COUNT(*) AS score_rows, ROUND(AVG(quiz),2) AS avg_quiz
FROM course_student_scores
WHERE date_at IS NOT NULL AND quiz IS NOT NULL
GROUP BY ym
ORDER BY ym;
""")
    write_csv(OUT / 'monthly_score_volume.csv',
              ['ym','score_rows','avg_quiz'],
              monthly)

    print(f'Wrote CSV outputs to {OUT}')

if __name__ == '__main__':
    main()
