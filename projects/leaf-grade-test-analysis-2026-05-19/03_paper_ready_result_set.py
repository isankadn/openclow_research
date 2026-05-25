#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
REPORTS = ROOT / 'reports'
REPORTS.mkdir(exist_ok=True)


def read_csv(path):
    with path.open(encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def as_int(row, key):
    return int(float(row.get(key) or 0))


def as_float(row, key):
    return float(row.get(key) or 0)


def main():
    grade_subject = read_csv(OUT / 'summary_by_grade_subject_family.csv')
    by_year_family = read_csv(OUT / 'summary_by_year_family.csv')
    xapi_grade = read_csv(OUT / 'xapi_monthly_sufficiency_by_grade_subject_family.csv')
    xapi_year = read_csv(OUT / 'xapi_monthly_sufficiency_by_year_family.csv')
    confidence = read_csv(OUT / 'summary_by_confidence.csv')

    outcome_candidates = []
    for r in grade_subject:
        if as_int(r, 'clean_score_rows') >= 500 and r['test_family'] != 'unclear':
            outcome_candidates.append({
                'candidate_type': 'outcome_descriptive_or_model_baseline',
                'grade_level': r['grade_level'],
                'course_subject': r['course_subject'],
                'test_family': r['test_family'],
                'score_rows': r['clean_score_rows'],
                'students': r['students'],
                'courses': r['courses'],
                'test_names': r['test_names'],
                'xapi_m3_rate': '',
                'xapi_m3_rows': '',
                'status': 'usable_outcome_cell',
            })

    behavior_candidates = []
    for r in xapi_grade:
        if as_int(r, 'score_rows') >= 500 and as_float(r, 'm3_rate') >= 0.70 and r['test_family'] != 'unclear':
            behavior_candidates.append({
                'candidate_type': 'student_level_behavior_outcome_candidate',
                'grade_level': r['grade_level'],
                'course_subject': r['course_subject'],
                'test_family': r['test_family'],
                'score_rows': r['score_rows'],
                'students': r['students'],
                'courses': r['courses'],
                'test_names': '',
                'xapi_m3_rate': r['m3_rate'],
                'xapi_m3_rows': r['m3_rows'],
                'status': 'needs_same_course_linkage_check',
            })

    candidates = behavior_candidates + outcome_candidates
    write_csv(REPORTS / 'candidate_analysis_cells_v1.csv', list(candidates[0].keys()), candidates)

    md = []
    md.append('# Paper-Ready Result Set v1')
    md.append('')
    md.append('## What This Result Set Supports Now')
    md.append('- Clean outcome-side analysis from dated grade/test data.')
    md.append('- A defensible test-name taxonomy separating regular school exams, Benesse/mock tests, unit/chapter tests, after-break tests, and unclear names.')
    md.append('- Student-level pre-test BookRoll behavior sufficiency across old and new xAPI stores using local aggregate features.')
    md.append('- Candidate grade/subject/test-family cells for deeper behavior-outcome modeling.')
    md.append('')
    md.append('## What It Does Not Yet Support')
    md.append('- Historical note: this v1 report predates the old `saikyo_old.statements_mv` context reimport. Use the direct-context rerun outputs for current same-course behavior-outcome claims.')
    md.append('- Post-2025 new-xAPI outcome modeling, because the current grade/test table has no `date_at` rows after 2025-03-05.')
    md.append('- Strong claims from low-confidence test-name classifications.')
    md.append('')
    md.append('## Outcome Data Quality')
    md.append('- Raw score rows: 67,672.')
    md.append('- Missing test conduct date (`date_at`) excluded: 24,492 rows.')
    md.append('- Clean dated score rows retained: 43,180.')
    md.append('- Duplicate groups at clean grain `(student_id, course_id, name, date_at)`: 0.')
    md.append('- Dated range: 2019-04-10 to 2025-03-05.')
    md.append('')
    md.append('## Test Taxonomy')
    for r in read_csv(OUT / 'summary_by_test_family.csv'):
        md.append(f"- {r['test_family']}: {int(r['clean_score_rows']):,} clean rows, {r['students']} students, {r['courses']} courses, {r['test_names']} test names")
    md.append('')
    md.append('## Classification Confidence')
    for r in confidence:
        md.append(f"- {r['classification_confidence']}: {int(r['clean_score_rows']):,} clean rows, {r['students']} students, {r['courses']} courses, {r['test_names']} test names")
    md.append('')
    md.append('## XAPI Sufficiency By Year/Test Family')
    for r in xapi_year[:16]:
        md.append(f"- {r['test_year']} {r['test_family']}: {int(r['score_rows']):,} score rows, {r['students']} students, {r['courses']} courses, 3-month xAPI coverage {float(r['m3_rate']):.1%}, 6-month {float(r['m6_rate']):.1%}, 12-month {float(r['m12_rate']):.1%}")
    md.append('')
    md.append('## Strongest Student-Level Behavior-Outcome Candidate Cells')
    for r in behavior_candidates[:20]:
        md.append(f"- {r['grade_level']} {r['course_subject']} {r['test_family']}: {int(r['score_rows']):,} score rows, {r['students']} students, {r['courses']} courses, 3-month xAPI coverage {float(r['xapi_m3_rate']):.1%}. Status: {r['status']}.")
    md.append('')
    md.append('## Recommended Paper Strategy')
    md.append('1. Use the grade/test layer as the outcome backbone.')
    md.append('2. Keep Benesse/external tests separate from regular school exams; do not pool them.')
    md.append('3. For the first behavior-outcome paper, prioritize high-confidence regular-exam and unit/chapter-test cells with high 3-month xAPI coverage.')
    md.append('4. Treat current xAPI sufficiency as student-level until same-course mapping is solved for old BookRoll.')
    md.append('5. For same-course claims, next resolve old BookRoll content/course linkage via relational metadata, not `saikyo_old.context_id` alone.')
    md.append('')
    md.append('## Best Current Claim')
    md.append('The current data is strong enough to support a paper-ready outcome taxonomy and to identify high-coverage student-level pre-test BookRoll behavior windows. The next methodological gate is course/content linkage for old BookRoll events, which determines whether the final model should be student-level behavior prediction or same-course behavior prediction.')
    (REPORTS / 'paper_ready_result_set_v1.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
