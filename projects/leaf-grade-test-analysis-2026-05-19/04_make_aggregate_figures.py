#!/usr/bin/env python3
import csv
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)


def read_csv(path):
    with path.open(encoding='utf-8') as f:
        return list(csv.DictReader(f))


def nice(n):
    return f'{int(float(n)):,}'


def hbar(rows, label_fn, value_key, title, filename, width=1200, row_h=44):
    rows = rows[:18]
    height = 90 + row_h * len(rows)
    left, right, top = 340, 120, 60
    maxv = max(int(float(r[value_key])) for r in rows) if rows else 1
    plot_w = width - left - right
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append('<style>text{font-family:Arial,sans-serif;fill:#222}.title{font-size:22px;font-weight:700}.label{font-size:13px}.value{font-size:13px;font-weight:700}.muted{fill:#666;font-size:12px}</style>')
    parts.append(f'<text x="24" y="34" class="title">{html.escape(title)}</text>')
    for i, r in enumerate(rows):
        y = top + i * row_h + 24
        label = html.escape(label_fn(r)[:52])
        value = int(float(r[value_key]))
        bar_w = int(plot_w * value / maxv) if maxv else 0
        parts.append(f'<text x="{left-12}" y="{y}" text-anchor="end" class="label">{label}</text>')
        parts.append(f'<rect x="{left}" y="{y-18}" width="{bar_w}" height="24" fill="#2f6fbb"/>')
        parts.append(f'<text x="{left+bar_w+8}" y="{y}" class="value">{nice(value)}</text>')
    parts.append('</svg>')
    (FIG / filename).write_text('\n'.join(parts), encoding='utf-8')


def coverage_bars(rows, title, filename):
    rows = rows[:18]
    width, row_h = 1300, 48
    height = 90 + row_h * len(rows)
    left, right, top = 390, 160, 60
    plot_w = width - left - right
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append('<style>text{font-family:Arial,sans-serif;fill:#222}.title{font-size:22px;font-weight:700}.label{font-size:13px}.value{font-size:13px;font-weight:700}.axis{stroke:#bbb}</style>')
    parts.append(f'<text x="24" y="34" class="title">{html.escape(title)}</text>')
    for pct in [0, .25, .5, .75, 1.0]:
        x = left + int(plot_w * pct)
        parts.append(f'<line x1="{x}" x2="{x}" y1="52" y2="{height-30}" class="axis"/>')
        parts.append(f'<text x="{x}" y="{height-10}" class="label" text-anchor="middle">{int(pct*100)}%</text>')
    for i, r in enumerate(rows):
        y = top + i * row_h + 24
        label = html.escape(f"{r.get('test_year','')} {r.get('grade_level','')} {r.get('course_subject','')} {r.get('test_family','')}"[:62])
        rate = float(r['m3_rate'])
        bar_w = int(plot_w * rate)
        parts.append(f'<text x="{left-12}" y="{y}" text-anchor="end" class="label">{label}</text>')
        parts.append(f'<rect x="{left}" y="{y-18}" width="{bar_w}" height="24" fill="#0f8b6f"/>')
        parts.append(f'<text x="{left+bar_w+8}" y="{y}" class="value">{rate:.0%}</text>')
    parts.append('</svg>')
    (FIG / filename).write_text('\n'.join(parts), encoding='utf-8')


def main():
    hbar(read_csv(OUT / 'summary_by_test_family.csv'), lambda r: r['test_family'], 'clean_score_rows', 'Clean Score Rows by Test Family', 'fig1_test_family_rows.svg')
    hbar(read_csv(OUT / 'summary_by_year.csv'), lambda r: r['test_year'], 'clean_score_rows', 'Clean Score Rows by Test Conduct Year', 'fig2_test_year_rows.svg')
    coverage_bars(read_csv(OUT / 'xapi_monthly_sufficiency_by_year_family.csv'), '3-Month Pre-Test XAPI Coverage by Year and Test Family', 'fig3_xapi_coverage_year_family.svg')
    coverage_bars(read_csv(OUT / 'xapi_monthly_sufficiency_by_grade_subject_family.csv'), 'Top 3-Month Pre-Test XAPI Coverage Candidate Cells', 'fig4_xapi_coverage_candidate_cells.svg')
    index = ['# Aggregate Figure Pack', '']
    for path in sorted(FIG.glob('*.svg')):
        index.append(f'- {path.name}')
    (FIG / 'README.md').write_text('\n'.join(index) + '\n', encoding='utf-8')
    print('\n'.join(index))


if __name__ == '__main__':
    main()
