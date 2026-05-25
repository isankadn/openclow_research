#!/usr/bin/env python3
import base64
import csv
import io
import os
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
SCORE_PATH = OUT / 'clean_score_grain_local_only.csv'

CLICKHOUSE_HOST = os.environ.get('CLICKHOUSE_HOST', 'http://10.236.173.4:8123/')
CLICKHOUSE_USER = os.environ.get('CLICKHOUSE_USER', 'reader')
CLICKHOUSE_PASSWORD = os.environ.get('CLICKHOUSE_PASSWORD', 'a9847KHJLv2vK')


def ch(query):
    req = urllib.request.Request(CLICKHOUSE_HOST + '?query=' + urllib.parse.quote(query + ' FORMAT TSVWithNames'))
    auth = base64.b64encode(f'{CLICKHOUSE_USER}:{CLICKHOUSE_PASSWORD}'.encode()).decode()
    req.add_header('Authorization', 'Basic ' + auth)
    with urllib.request.urlopen(req, timeout=600) as response:
        return response.read().decode('utf-8', 'replace')


def ch_tsv(query):
    return list(csv.DictReader(io.StringIO(ch(query)), delimiter='\t'))


def write_csv(path, fieldnames, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sql_string_list(values):
    return ','.join("'" + str(v).replace("'", "\\'") + "'" for v in values)


def month_index(ym):
    y, m = ym.split('-')
    return int(y) * 12 + int(m)


def test_month(value):
    return value[:7]


def load_scores():
    with SCORE_PATH.open(encoding='utf-8') as f:
        return list(csv.DictReader(f))


def fetch_monthly(db, start, end, student_ids):
    # Query all old/new BookRoll actor-month aggregates, then filter to score students locally.
    # This is faster in ClickHouse than a very large IN predicate over split actor IDs.
    # Blank operation_name/contents_id rows are expected for Moodle/Analysis source families,
    # so Bookroll behavior queries filter to bookroll source rows before using operation fields.
    query = f"""
    SELECT
      splitByChar('@', actor_account_name)[1] AS student_id,
      formatDateTime(toStartOfMonth(timestamp), '%Y-%m') AS event_month,
      count() AS events_total,
      uniqExact(toDate(timestamp)) AS active_days,
      uniqExact(contents_id) AS contents,
      sumIf(1, operation_name IN ('NEXT','PREV','PAGE_JUMP','BOOKMARK_JUMP','MEMO_JUMP','SEARCH_JUMP')) AS navigation_events,
      sumIf(1, position(operation_name, 'MEMO') > 0) AS memo_events,
      sumIf(1, position(operation_name, 'MARKER') > 0) AS marker_events,
      sumIf(1, position(operation_name, 'QUIZ') > 0 OR verb_display_en = 'answered') AS quiz_events,
      sumIf(1, position(operation_name, 'TIMER') > 0) AS timer_events,
      sumIf(1, position(operation_name, 'RECOMMENDATION') > 0) AS recommendation_events,
      sumIf(1, operation_name IN ('SEARCH','SEARCH_JUMP')) AS search_events,
      sumIf(1, operation_name IN ('OPEN','CLOSE')) AS content_session_events
    FROM {db}.statements_mv
    WHERE timestamp >= toDateTime('{start}')
      AND timestamp < toDateTime('{end}')
      AND position(actor_account_homePage, 'bookroll') > 0
      AND notEmpty(operation_name)
    GROUP BY student_id, event_month
    ORDER BY student_id, event_month
    """
    rows = ch_tsv(query)
    return [r for r in rows if r['student_id'] in student_ids]


def merge_monthly(old_rows, new_rows):
    merged = defaultdict(lambda: defaultdict(int))
    for source, rows in [('old', old_rows), ('new', new_rows)]:
        for r in rows:
            key = (r['student_id'], r['event_month'])
            for field in ['events_total','active_days','contents','navigation_events','memo_events','marker_events','quiz_events','timer_events','recommendation_events','search_events','content_session_events']:
                merged[key][field] += int(r[field])
            merged[key][source + '_events'] += int(r['events_total'])
    return merged


def index_by_student(months):
    by_student = defaultdict(list)
    for (student, ym), vals in months.items():
        by_student[student].append((month_index(ym), vals))
    for student in by_student:
        by_student[student].sort(key=lambda x: x[0])
    return by_student


def window_sum(months_by_student, sid, test_ym, lookback_months):
    cutoff = month_index(test_ym)
    start = cutoff - lookback_months
    out = defaultdict(int)
    for mi, vals in months_by_student.get(sid, []):
        if start <= mi < cutoff:
            for k, v in vals.items():
                out[k] += int(v)
    return out


def any_prior_sum(months_by_student, sid, test_ym):
    cutoff = month_index(test_ym)
    out = defaultdict(int)
    for mi, vals in months_by_student.get(sid, []):
        if mi < cutoff:
            for k, v in vals.items():
                out[k] += int(v)
    return out


def summarize(rows, dims):
    buckets = defaultdict(lambda: defaultdict(int))
    students = defaultdict(set)
    courses = defaultdict(set)
    for r in rows:
        key = tuple(r[d] for d in dims)
        b = buckets[key]
        b['score_rows'] += 1
        b['prior_any_rows'] += r['has_prior_any']
        b['m3_rows'] += 1 if r['events_m3'] > 0 else 0
        b['m6_rows'] += 1 if r['events_m6'] > 0 else 0
        b['m12_rows'] += 1 if r['events_m12'] > 0 else 0
        b['events_m3'] += r['events_m3']
        b['events_m6'] += r['events_m6']
        b['events_m12'] += r['events_m12']
        b['active_days_m3'] += r['active_days_m3']
        b['navigation_m3'] += r['navigation_m3']
        b['memo_m3'] += r['memo_m3']
        b['marker_m3'] += r['marker_m3']
        b['quiz_m3'] += r['quiz_m3']
        students[key].add(r['student_id'])
        courses[key].add(r['course_id'])
    out = []
    for key, b in buckets.items():
        n = b['score_rows']
        out.append({
            **{dims[i]: key[i] for i in range(len(dims))},
            'score_rows': n,
            'students': len(students[key]),
            'courses': len(courses[key]),
            'prior_any_rows': b['prior_any_rows'],
            'prior_any_rate': round(b['prior_any_rows']/n, 4),
            'm3_rows': b['m3_rows'],
            'm3_rate': round(b['m3_rows']/n, 4),
            'm6_rows': b['m6_rows'],
            'm6_rate': round(b['m6_rows']/n, 4),
            'm12_rows': b['m12_rows'],
            'm12_rate': round(b['m12_rows']/n, 4),
            'events_m3': b['events_m3'],
            'events_m6': b['events_m6'],
            'events_m12': b['events_m12'],
            'active_days_m3': b['active_days_m3'],
            'navigation_m3': b['navigation_m3'],
            'memo_m3': b['memo_m3'],
            'marker_m3': b['marker_m3'],
            'quiz_m3': b['quiz_m3'],
        })
    return sorted(out, key=lambda r: (-r['m3_rows'], -r['score_rows'], tuple(r[d] for d in dims)))


def main():
    scores = load_scores()
    student_ids = {r['student_id'] for r in scores if r['student_id']}
    old_rows = fetch_monthly('saikyo_old', '2019-01-01 00:00:00', '2025-04-01 00:00:00', student_ids)
    new_rows = fetch_monthly('saikyo_new', '2025-04-01 00:00:00', '2026-12-31 23:59:59', student_ids)
    write_csv(OUT / 'xapi_monthly_old_local_only.csv', list(old_rows[0].keys()) if old_rows else ['student_id'], old_rows)
    write_csv(OUT / 'xapi_monthly_new_local_only.csv', list(new_rows[0].keys()) if new_rows else ['student_id'], new_rows)
    months = merge_monthly(old_rows, new_rows)
    months_by_student = index_by_student(months)

    linked = []
    for s in scores:
        sid = s['student_id']
        tym = test_month(s['test_date'])
        prior = any_prior_sum(months_by_student, sid, tym)
        m3 = window_sum(months_by_student, sid, tym, 3)
        m6 = window_sum(months_by_student, sid, tym, 6)
        m12 = window_sum(months_by_student, sid, tym, 12)
        linked.append({
            'student_id': sid,
            'course_id': s['course_id'],
            'test_year': s['test_year'],
            'test_month': tym,
            'grade_level': s['grade_level'] or '(missing)',
            'course_subject': s['course_subject'] or '(missing)',
            'test_family': s['test_family'],
            'classification_confidence': s['classification_confidence'],
            'has_prior_any': 1 if prior.get('events_total', 0) > 0 else 0,
            'events_m3': m3.get('events_total', 0),
            'events_m6': m6.get('events_total', 0),
            'events_m12': m12.get('events_total', 0),
            'active_days_m3': m3.get('active_days', 0),
            'contents_m3': m3.get('contents', 0),
            'navigation_m3': m3.get('navigation_events', 0),
            'memo_m3': m3.get('memo_events', 0),
            'marker_m3': m3.get('marker_events', 0),
            'quiz_m3': m3.get('quiz_events', 0),
            'timer_m3': m3.get('timer_events', 0),
            'recommendation_m3': m3.get('recommendation_events', 0),
            'search_m3': m3.get('search_events', 0),
            'content_session_m3': m3.get('content_session_events', 0),
        })
    write_csv(OUT / 'score_xapi_monthly_sufficiency_local_only.csv', list(linked[0].keys()), linked)

    summaries = {
        'xapi_monthly_sufficiency_by_year.csv': ['test_year'],
        'xapi_monthly_sufficiency_by_year_family.csv': ['test_year', 'test_family'],
        'xapi_monthly_sufficiency_by_grade_subject_family.csv': ['grade_level', 'course_subject', 'test_family'],
        'xapi_monthly_sufficiency_by_confidence.csv': ['classification_confidence'],
    }
    summary_data = {}
    for filename, dims in summaries.items():
        rows = summarize(linked, dims)
        summary_data[filename] = (dims, rows)
        write_csv(OUT / filename, list(rows[0].keys()) if rows else dims, rows)

    report = []
    report.append('# XAPI Monthly Sufficiency Map')
    report.append('')
    report.append('## Scope')
    report.append('- Local aggregate sufficiency pass using student-month BookRoll xAPI summaries.')
    report.append('- Link: score student_id to xAPI actor_account_name prefix before @.')
    report.append('- Windows are month-based approximations: 3, 6, and 12 months before the test month.')
    report.append('- This is not yet same-course linkage; it identifies feasible candidate subsets before deeper course/content mapping.')
    report.append('')
    report.append('## XAPI Aggregate Extraction')
    report.append(f'- Relevant score students: {len(student_ids):,}')
    report.append(f'- Old monthly aggregate rows: {len(old_rows):,}; old events represented: {sum(int(r["events_total"]) for r in old_rows):,}')
    report.append(f'- New monthly aggregate rows: {len(new_rows):,}; new events represented: {sum(int(r["events_total"]) for r in new_rows):,}')
    report.append('')
    for title, filename, max_rows in [
        ('By Year', 'xapi_monthly_sufficiency_by_year.csv', 20),
        ('By Year And Test Family', 'xapi_monthly_sufficiency_by_year_family.csv', 50),
        ('By Grade Subject Family', 'xapi_monthly_sufficiency_by_grade_subject_family.csv', 50),
    ]:
        dims, rows = summary_data[filename]
        report.append(f'## {title}')
        for r in rows[:max_rows]:
            label = ', '.join(f'{d}={r[d]}' for d in dims)
            report.append(f'- {label}: score_rows={r["score_rows"]:,}, students={r["students"]:,}, courses={r["courses"]:,}, m3_rows={r["m3_rows"]:,} ({r["m3_rate"]:.1%}), m6_rows={r["m6_rows"]:,} ({r["m6_rate"]:.1%}), m12_rows={r["m12_rows"]:,} ({r["m12_rate"]:.1%}), events_m3={r["events_m3"]:,}')
        report.append('')
    report.append('## Initial Paper-Subset Rule')
    report.append('- Prefer cells with at least 200 score rows and at least 50% 3-month xAPI coverage for behavior-outcome modeling.')
    report.append('- If same-course linkage later reduces coverage sharply, downgrade those cells to descriptive-only.')
    (OUT / 'xapi_monthly_sufficiency_report.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    print('\n'.join(report))


if __name__ == '__main__':
    main()
