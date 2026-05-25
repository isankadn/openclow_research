#!/usr/bin/env python3
import base64
import csv
import io
import json
import os
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
OUT.mkdir(parents=True, exist_ok=True)
SCORE_PATH = OUT / 'clean_score_grain_local_only.csv'
CROSSWALK_PATH = Path('/home/ubuntu/.openclaw/workspace/projects/leaf-pre2025-xapi-harmonization/old_operation_crosswalk.csv')

CLICKHOUSE_HOST = os.environ.get('CLICKHOUSE_HOST', 'http://10.236.173.4:8123/')
CLICKHOUSE_USER = os.environ.get('CLICKHOUSE_USER', 'reader')
CLICKHOUSE_PASSWORD = os.environ.get('CLICKHOUSE_PASSWORD', 'a9847KHJLv2vK')


def ch(query, fmt='TSVWithNames'):
    req = urllib.request.Request(CLICKHOUSE_HOST + '?query=' + urllib.parse.quote(query + ' FORMAT ' + fmt))
    if CLICKHOUSE_PASSWORD:
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


def parse_date(value):
    return datetime.strptime(value, '%Y-%m-%d').date()


def load_scores():
    with SCORE_PATH.open(encoding='utf-8') as f:
        return list(csv.DictReader(f))


def load_crosswalk():
    mapping = {}
    with CROSSWALK_PATH.open(encoding='utf-8') as f:
        for row in csv.DictReader(f):
            key = (row['old_operation_name'], row['old_process_code'], row['old_verb_display_en'])
            mapping[key] = row
            mapping.setdefault((row['old_operation_name'], row['old_process_code'], ''), row)
            mapping.setdefault((row['old_operation_name'], '', ''), row)
    return mapping


def canonical_group(row, crosswalk):
    key = (row.get('operation_name', ''), row.get('process_code', ''), row.get('verb_display_en', ''))
    mapped = crosswalk.get(key) or crosswalk.get((key[0], key[1], '')) or crosswalk.get((key[0], '', ''))
    if mapped:
        return mapped['operation_group'], mapped['canonical_operation'], mapped['confidence']
    op = row.get('operation_name', '')
    if op in {'NEXT', 'PREV', 'PAGE_JUMP'}:
        return 'navigation', op, 'high'
    if op in {'OPEN', 'CLOSE'}:
        return 'content_session', op, 'high'
    if 'MEMO' in op:
        return 'memo', op, 'medium'
    if 'MARKER' in op:
        return 'annotation_marker', op, 'medium'
    if 'QUIZ' in op or row.get('verb_display_en') == 'answered':
        return 'quiz', op, 'medium'
    return 'other_or_unmapped', op, 'low'


def fetch_old_daily(student_ids):
    ids_sql = sql_string_list(sorted(student_ids, key=lambda x: int(x) if x.isdigit() else x))
    # Blank operation_name rows in saikyo_old are expected for non-Bookroll apps.
    # This daily feature extract is intentionally scoped to Bookroll source rows.
    query = f"""
    SELECT
      splitByChar('@', actor_account_name)[1] AS student_id,
      toString(toDate(timestamp)) AS event_date,
      operation_name,
      process_code,
      verb_display_en,
      count() AS events,
      uniqExact(contents_id) AS contents
    FROM saikyo_old.statements_mv
    WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
      AND timestamp < toDateTime('2025-04-01 00:00:00')
      AND position(actor_account_homePage, 'bookroll') > 0
      AND splitByChar('@', actor_account_name)[1] IN ({ids_sql})
      AND notEmpty(operation_name)
    GROUP BY student_id, event_date, operation_name, process_code, verb_display_en
    ORDER BY student_id, event_date
    """
    return ch_tsv(query)


def fetch_new_daily(student_ids):
    ids_sql = sql_string_list(sorted(student_ids, key=lambda x: int(x) if x.isdigit() else x))
    query = f"""
    SELECT
      splitByChar('@', actor_account_name)[1] AS student_id,
      toString(toDate(timestamp)) AS event_date,
      operation_name,
      '' AS process_code,
      verb_display_en,
      count() AS events,
      uniqExact(contents_id) AS contents
    FROM saikyo_new.statements_mv
    WHERE timestamp >= toDateTime('2025-04-01 00:00:00')
      AND timestamp < now() + INTERVAL 1 DAY
      AND position(actor_account_homePage, 'bookroll') > 0
      AND splitByChar('@', actor_account_name)[1] IN ({ids_sql})
      AND notEmpty(operation_name)
    GROUP BY student_id, event_date, operation_name, verb_display_en
    ORDER BY student_id, event_date
    """
    return ch_tsv(query)


def build_student_day_features(rows, source_schema, crosswalk):
    by_student_day = defaultdict(lambda: defaultdict(int))
    content_by_student_day = defaultdict(set)
    totals = defaultdict(int)
    for row in rows:
        sid = row['student_id']
        d = parse_date(row['event_date'])
        group, canon, conf = canonical_group(row, crosswalk)
        events = int(row['events'])
        key = (sid, d)
        by_student_day[key]['events_total'] += events
        by_student_day[key][f'events_{group}'] += events
        by_student_day[key][f'events_op_{canon}'] += events
        by_student_day[key]['active_days'] = 1
        by_student_day[key][f'{source_schema}_events'] += events
        totals[f'{source_schema}_events'] += events
        totals[f'{source_schema}_groups'] += 1
        if int(row.get('contents') or 0) > 0:
            by_student_day[key]['content_day_count_proxy'] += int(row['contents'])
    return by_student_day, totals


def prefix_sums(day_features):
    by_student = defaultdict(list)
    for (sid, d), feats in day_features.items():
        by_student[sid].append((d, feats))
    cumulative = {}
    for sid, items in by_student.items():
        items.sort(key=lambda x: x[0])
        running = defaultdict(int)
        series = []
        for d, feats in items:
            for k, v in feats.items():
                running[k] += int(v)
            series.append((d, dict(running)))
        cumulative[sid] = series
    return cumulative


def cumulative_until(series, cutoff):
    # cutoff is exclusive.
    lo, hi = 0, len(series)
    while lo < hi:
        mid = (lo + hi) // 2
        if series[mid][0] < cutoff:
            lo = mid + 1
        else:
            hi = mid
    if lo == 0:
        return {}
    return series[lo - 1][1]


def window_features(day_features, sid, test_date, days):
    start = test_date - timedelta(days=days)
    out = defaultdict(int)
    for (student, d), feats in day_features.items():
        if student == sid and start <= d < test_date:
            for k, v in feats.items():
                out[k] += int(v)
    return out


def aggregate_sufficiency(scores, combined_day_features, cumulative):
    rows = []
    for s in scores:
        sid = s['student_id']
        tdate = parse_date(s['test_date'])
        any_prior = cumulative_until(cumulative.get(sid, []), tdate)
        w30 = window_features(combined_day_features, sid, tdate, 30)
        w90 = window_features(combined_day_features, sid, tdate, 90)
        w180 = window_features(combined_day_features, sid, tdate, 180)
        rows.append({
            'test_year': s['test_year'],
            'grade_level': s['grade_level'] or '(missing)',
            'course_subject': s['course_subject'] or '(missing)',
            'test_family': s['test_family'],
            'classification_confidence': s['classification_confidence'],
            'student_id': sid,
            'course_id': s['course_id'],
            'test_date': s['test_date'],
            'has_any_prior_xapi': 1 if any_prior.get('events_total', 0) > 0 else 0,
            'prior_events_total': any_prior.get('events_total', 0),
            'events_30d': w30.get('events_total', 0),
            'events_90d': w90.get('events_total', 0),
            'events_180d': w180.get('events_total', 0),
            'active_days_90d': w90.get('active_days', 0),
            'navigation_90d': w90.get('events_navigation', 0),
            'memo_90d': w90.get('events_memo_text', 0) + w90.get('events_memo_handwriting', 0) + w90.get('events_memo', 0),
            'marker_90d': w90.get('events_annotation_marker', 0),
            'quiz_90d': w90.get('events_quiz', 0),
            'timer_90d': w90.get('events_timer', 0),
            'recommendation_90d': w90.get('events_recommendation', 0),
            'search_90d': w90.get('events_search', 0) + w90.get('events_search_navigation', 0),
        })
    return rows


def summarize(rows, dims):
    buckets = defaultdict(lambda: defaultdict(int))
    students = defaultdict(set)
    courses = defaultdict(set)
    for r in rows:
        key = tuple(r[d] for d in dims)
        b = buckets[key]
        b['score_rows'] += 1
        b['rows_with_any_prior_xapi'] += r['has_any_prior_xapi']
        b['rows_with_30d_xapi'] += 1 if r['events_30d'] > 0 else 0
        b['rows_with_90d_xapi'] += 1 if r['events_90d'] > 0 else 0
        b['rows_with_180d_xapi'] += 1 if r['events_180d'] > 0 else 0
        b['prior_events_total'] += r['prior_events_total']
        b['events_90d'] += r['events_90d']
        b['active_days_90d'] += r['active_days_90d']
        students[key].add(r['student_id'])
        courses[key].add(r['course_id'])
    out = []
    for key, b in buckets.items():
        score_rows = b['score_rows']
        out.append({
            **{dims[i]: key[i] for i in range(len(dims))},
            'score_rows': score_rows,
            'students': len(students[key]),
            'courses': len(courses[key]),
            'rows_with_any_prior_xapi': b['rows_with_any_prior_xapi'],
            'any_prior_xapi_rate': round(b['rows_with_any_prior_xapi'] / score_rows, 4),
            'rows_with_30d_xapi': b['rows_with_30d_xapi'],
            'xapi_30d_rate': round(b['rows_with_30d_xapi'] / score_rows, 4),
            'rows_with_90d_xapi': b['rows_with_90d_xapi'],
            'xapi_90d_rate': round(b['rows_with_90d_xapi'] / score_rows, 4),
            'rows_with_180d_xapi': b['rows_with_180d_xapi'],
            'xapi_180d_rate': round(b['rows_with_180d_xapi'] / score_rows, 4),
            'prior_events_total': b['prior_events_total'],
            'events_90d': b['events_90d'],
            'active_days_90d': b['active_days_90d'],
        })
    return sorted(out, key=lambda r: (-r['rows_with_90d_xapi'], -r['score_rows'], tuple(r[d] for d in dims)))


def main():
    scores = load_scores()
    student_ids = {r['student_id'] for r in scores if r['student_id']}
    crosswalk = load_crosswalk()

    old_rows = fetch_old_daily(student_ids)
    new_rows = fetch_new_daily(student_ids)
    write_csv(OUT / 'xapi_old_daily_aggregate_local_only.csv', old_rows[0].keys() if old_rows else ['student_id'], old_rows)
    write_csv(OUT / 'xapi_new_daily_aggregate_local_only.csv', new_rows[0].keys() if new_rows else ['student_id'], new_rows)

    old_day, old_totals = build_student_day_features(old_rows, 'old', crosswalk)
    new_day, new_totals = build_student_day_features(new_rows, 'new', crosswalk)
    combined = defaultdict(lambda: defaultdict(int))
    for source in (old_day, new_day):
        for key, feats in source.items():
            for k, v in feats.items():
                combined[key][k] += int(v)

    cumulative = prefix_sums(combined)
    suff_rows = aggregate_sufficiency(scores, combined, cumulative)
    write_csv(OUT / 'score_xapi_sufficiency_by_score_row_local_only.csv', list(suff_rows[0].keys()), suff_rows)

    summaries = {
        'xapi_sufficiency_by_year.csv': ['test_year'],
        'xapi_sufficiency_by_year_family.csv': ['test_year', 'test_family'],
        'xapi_sufficiency_by_grade_subject_family.csv': ['grade_level', 'course_subject', 'test_family'],
        'xapi_sufficiency_by_confidence.csv': ['classification_confidence'],
    }
    summary_data = {}
    for filename, dims in summaries.items():
        summary = summarize(suff_rows, dims)
        summary_data[filename] = (dims, summary)
        write_csv(OUT / filename, list(summary[0].keys()) if summary else dims, summary)

    report = []
    report.append('# XAPI Sufficiency By Student')
    report.append('')
    report.append('## Scope')
    report.append('- Score rows: cleaned dated grade/test rows from course_student_scores.')
    report.append('- XAPI sources: saikyo_old and saikyo_new statements_mv.')
    report.append('- Link used in this pass: student Moodle ID only, extracted from actor_account_name prefix before @.')
    report.append('- Historical note: this student-level sufficiency pass predates the old saikyo_old context_id reimport. Current same-course analysis should use direct ClickHouse context_id.')
    report.append('- Features are local aggregate event counts by student/date/operation, not raw event rows.')
    report.append('')
    report.append('## XAPI Aggregate Extraction')
    report.append(f'- Relevant score students: {len(student_ids):,}')
    report.append(f'- Old daily aggregate rows: {len(old_rows):,}; old events represented: {sum(int(r["events"]) for r in old_rows):,}')
    report.append(f'- New daily aggregate rows: {len(new_rows):,}; new events represented: {sum(int(r["events"]) for r in new_rows):,}')
    report.append('')
    for title, filename, max_rows in [
        ('By Year', 'xapi_sufficiency_by_year.csv', 20),
        ('By Year And Test Family', 'xapi_sufficiency_by_year_family.csv', 40),
        ('By Grade Subject Family', 'xapi_sufficiency_by_grade_subject_family.csv', 40),
    ]:
        dims, rows = summary_data[filename]
        report.append(f'## {title}')
        for r in rows[:max_rows]:
            label = ', '.join(f'{d}={r[d]}' for d in dims)
            report.append(
                f'- {label}: score_rows={r["score_rows"]:,}, students={r["students"]:,}, courses={r["courses"]:,}, '
                f'90d_xapi_rows={r["rows_with_90d_xapi"]:,} ({r["xapi_90d_rate"]:.1%}), '
                f'180d_xapi_rows={r["rows_with_180d_xapi"]:,} ({r["xapi_180d_rate"]:.1%}), '
                f'events_90d={r["events_90d"]:,}'
            )
        report.append('')
    report.append('## Interpretation Guardrails')
    report.append('- This is a student-level sufficiency pass, not final same-course linkage.')
    report.append('- Candidate paper subsets should require high 90d/180d xAPI coverage and then be checked for course/content linkage.')
    report.append('- Low-confidence test-name groups should not be used for headline claims without manual review.')
    (OUT / 'xapi_sufficiency_by_student_report.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    print('\n'.join(report))


if __name__ == '__main__':
    main()
