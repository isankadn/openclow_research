#!/usr/bin/env python3
import subprocess
import html
from pathlib import Path

OUTDIR = Path('/home/ubuntu/.openclaw/workspace/projects/leaf-score-integration-2026-04-03/charts')
OUTDIR.mkdir(parents=True, exist_ok=True)

MYSQL = "mysql -N -h 10.236.173.145 -P 33308 -u reader -p'bar' -D analysis_development -e"


def run_sql(sql: str):
    cmd = f"{MYSQL} \"{sql}\""
    out = subprocess.check_output(cmd, shell=True, text=True)
    return [line.split('\t') for line in out.splitlines() if line.strip()]


def nice_num(x):
    return f"{x:,}"


def wrap(text, width=30):
    words = str(text).split()
    lines, cur = [], ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if len(test) <= width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:3]


def make_hbar_svg(title, subtitle, items, value_key, label_key, filename, width=1200, row_h=60):
    left = 430
    right = 170
    top = 120
    height = top + len(items) * row_h + 70
    plot_w = width - left - right
    maxv = max(item[value_key] for item in items) if items else 1
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    svg.append('<style>')
    svg.append('text { font-family: Arial, Helvetica, sans-serif; fill: #1f2937; }')
    svg.append('.title { font-size: 30px; font-weight: 700; }')
    svg.append('.subtitle { font-size: 16px; fill: #4b5563; }')
    svg.append('.label { font-size: 16px; }')
    svg.append('.value { font-size: 16px; font-weight: 700; }')
    svg.append('.axis { stroke: #94a3b8; stroke-width: 1; }')
    svg.append('</style>')
    svg.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>')
    svg.append(f'<text x="40" y="45" class="title">{html.escape(title)}</text>')
    svg.append(f'<text x="40" y="75" class="subtitle">{html.escape(subtitle)}</text>')
    svg.append(f'<line x1="{left}" y1="95" x2="{left}" y2="{height-40}" class="axis"/>')
    for i, item in enumerate(items):
        y = top + i * row_h
        bar_w = 0 if maxv == 0 else int((item[value_key] / maxv) * plot_w)
        svg.append(f'<rect x="{left}" y="{y-18}" width="{bar_w}" height="28" rx="5" fill="#2563eb"/>')
        label_lines = wrap(item[label_key], 34)
        ly = y - 4
        for j, line in enumerate(label_lines):
            svg.append(f'<text x="40" y="{ly + j*18}" class="label">{html.escape(line)}</text>')
        svg.append(f'<text x="{left + bar_w + 10}" y="{y+1}" class="value">{nice_num(item[value_key])}</text>')
    svg.append('</svg>')
    (OUTDIR / filename).write_text('\n'.join(svg), encoding='utf-8')


def make_distribution_svg(title, subtitle, items, x_key, y_key, filename, width=1200, height=700):
    left, right, top, bottom = 90, 80, 110, 90
    plot_w = width - left - right
    plot_h = height - top - bottom
    maxy = max(item[y_key] for item in items) if items else 1
    n = len(items)
    bar_w = max(12, int(plot_w / max(n, 1) * 0.7))
    gap = int((plot_w - n * bar_w) / max(n, 1)) if n else 10
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    svg.append('<style>')
    svg.append('text { font-family: Arial, Helvetica, sans-serif; fill: #1f2937; }')
    svg.append('.title { font-size: 30px; font-weight: 700; }')
    svg.append('.subtitle { font-size: 16px; fill: #4b5563; }')
    svg.append('.label { font-size: 14px; }')
    svg.append('.value { font-size: 13px; }')
    svg.append('.axis { stroke: #94a3b8; stroke-width: 1; }')
    svg.append('</style>')
    svg.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>')
    svg.append(f'<text x="40" y="45" class="title">{html.escape(title)}</text>')
    svg.append(f'<text x="40" y="75" class="subtitle">{html.escape(subtitle)}</text>')
    svg.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{width-right}" y2="{top+plot_h}" class="axis"/>')
    svg.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" class="axis"/>')
    for i, item in enumerate(items):
        x = left + i * (bar_w + gap) + gap // 2
        bar_h = 0 if maxy == 0 else int((item[y_key] / maxy) * (plot_h - 20))
        y = top + plot_h - bar_h
        svg.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" rx="4" fill="#059669"/>')
        svg.append(f'<text x="{x + bar_w/2}" y="{top+plot_h+24}" class="label" text-anchor="middle">{html.escape(str(item[x_key]))}</text>')
        svg.append(f'<text x="{x + bar_w/2}" y="{y-8}" class="value" text-anchor="middle">{nice_num(item[y_key])}</text>')
    svg.append('</svg>')
    (OUTDIR / filename).write_text('\n'.join(svg), encoding='utf-8')


def make_summary_html(summary_cards):
    cards_html = []
    for c in summary_cards:
        cards_html.append(f'''<div class="card"><div class="k">{html.escape(c[0])}</div><div class="v">{html.escape(c[1])}</div></div>''')
    page = f'''<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>LEAF score integration charts</title>
  <style>
    body {{ font-family: Arial, Helvetica, sans-serif; margin: 24px; color: #1f2937; }}
    h1 {{ margin-bottom: 8px; }}
    .muted {{ color: #6b7280; margin-bottom: 24px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(180px, 1fr)); gap: 12px; margin-bottom: 24px; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px; background: #f9fafb; }}
    .card .k {{ font-size: 13px; color: #6b7280; margin-bottom: 6px; }}
    .card .v {{ font-size: 26px; font-weight: 700; }}
    .chart {{ margin: 28px 0 40px; }}
    img {{ max-width: 100%; border: 1px solid #e5e7eb; border-radius: 10px; }}
  </style>
</head>
<body>
  <h1>LEAF score data charts</h1>
  <div class="muted">Generated from <code>analysis_development.course_student_scores</code> using bounded read-only queries. These are score-only charts for quick visual review.</div>
  <div class="grid">{''.join(cards_html)}</div>
  <div class="chart"><h2>Top courses by score rows</h2><img src="top_courses_by_score_rows.svg" /></div>
  <div class="chart"><h2>Top test names by score rows</h2><img src="top_tests_by_score_rows.svg" /></div>
  <div class="chart"><h2>Score rows per test-date month</h2><img src="score_rows_by_month.svg" /></div>
  <div class="chart"><h2>Repeated-test structure</h2><img src="tests_per_student_course_distribution.svg" /></div>
</body>
</html>'''
    (OUTDIR / 'index.html').write_text(page, encoding='utf-8')


def main():
    summary = run_sql("""
SELECT COUNT(*) AS rows_total,
       COUNT(DISTINCT student_id) AS students,
       COUNT(DISTINCT course_id) AS courses,
       COUNT(DISTINCT name) AS tests,
       MIN(date_at) AS min_test_date,
       MAX(date_at) AS max_test_date,
       ROUND(AVG(quiz),2) AS avg_quiz
FROM course_student_scores
WHERE date_at IS NOT NULL AND quiz IS NOT NULL;
""")[0]

    top_courses_rows = run_sql("""
SELECT course_name, COUNT(*) AS score_rows
FROM course_student_scores
WHERE date_at IS NOT NULL AND quiz IS NOT NULL
GROUP BY course_id, course_name
ORDER BY score_rows DESC
LIMIT 10;
""")
    top_courses = [{'label': r[0], 'value': int(r[1])} for r in top_courses_rows]
    make_hbar_svg(
        'Top courses by score rows',
        'Rows with non-null date_at and non-null quiz',
        [{'course_name': x['label'], 'score_rows': x['value']} for x in top_courses],
        'score_rows', 'course_name', 'top_courses_by_score_rows.svg'
    )

    top_tests_rows = run_sql("""
SELECT name, COUNT(*) AS score_rows
FROM course_student_scores
WHERE date_at IS NOT NULL AND quiz IS NOT NULL
GROUP BY name
ORDER BY score_rows DESC
LIMIT 10;
""")
    top_tests = [{'test_name': r[0], 'score_rows': int(r[1])} for r in top_tests_rows]
    make_hbar_svg(
        'Top test names by score rows',
        'Most frequent named tests in the score table',
        top_tests,
        'score_rows', 'test_name', 'top_tests_by_score_rows.svg'
    )

    monthly_rows = run_sql("""
SELECT DATE_FORMAT(date_at, '%Y-%m') AS ym, COUNT(*) AS score_rows
FROM course_student_scores
WHERE date_at IS NOT NULL AND quiz IS NOT NULL
GROUP BY ym
ORDER BY ym;
""")
    monthly = [{'ym': r[0], 'score_rows': int(r[1])} for r in monthly_rows]
    make_distribution_svg(
        'Score rows by month',
        'Monthly count of dated score rows',
        monthly,
        'ym', 'score_rows', 'score_rows_by_month.svg', height=760
    )

    repeat_rows = run_sql("""
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
    repeat = [{'tests_per_student_in_course': int(r[0]), 'student_course_pairs': int(r[1])} for r in repeat_rows]
    make_distribution_svg(
        'Repeated-test structure',
        'How many score rows each student-course pair has',
        repeat,
        'tests_per_student_in_course', 'student_course_pairs', 'tests_per_student_course_distribution.svg', height=700
    )

    make_summary_html([
        ('Rows with score + date', f"{int(summary[0]):,}"),
        ('Students', f"{int(summary[1]):,}"),
        ('Courses', f"{int(summary[2]):,}"),
        ('Test names', f"{int(summary[3]):,}"),
        ('Date range', f"{summary[4]} → {summary[5]}"),
        ('Average quiz', str(summary[6])),
    ])

    print(f'Wrote charts to {OUTDIR}')

if __name__ == '__main__':
    main()
