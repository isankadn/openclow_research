#!/usr/bin/env python3
import base64
import csv
import io
import os
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
REPORTS = ROOT / 'reports'
REPORTS.mkdir(exist_ok=True)
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

def read_csv(path):
    with path.open(encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_csv(path, fieldnames, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)

def month_index(ym):
    y,m = ym.split('-')
    return int(y)*12 + int(m)

def test_month(d):
    return d[:7]

def fetch_old_context_monthly():
    # After the old saikyo_old.statements_mv reimport, Bookroll rows carry Moodle
    # course context directly. Keep contents_id non-empty to preserve the previous
    # content-learning event universe while replacing the fragile content bridge.
    q = """
    SELECT
      splitByChar('@', actor_account_name)[1] AS student_id,
      context_id AS course_id,
      formatDateTime(toStartOfMonth(timestamp), '%Y-%m') AS event_month,
      count() AS events_total,
      uniqExact(toDate(timestamp)) AS active_days,
      sumIf(1, operation_name IN ('NEXT','PREV','PAGE_JUMP','BOOKMARK_JUMP','MEMO_JUMP','SEARCH_JUMP')) AS navigation_events,
      sumIf(1, position(operation_name, 'MEMO') > 0) AS memo_events,
      sumIf(1, position(operation_name, 'MARKER') > 0) AS marker_events,
      sumIf(1, position(operation_name, 'QUIZ') > 0 OR verb_display_en = 'answered') AS quiz_events,
      sumIf(1, position(operation_name, 'TIMER') > 0) AS timer_events,
      sumIf(1, operation_name IN ('OPEN','CLOSE')) AS content_session_events
    FROM saikyo_old.statements_mv
    WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
      AND timestamp < toDateTime('2025-04-01 00:00:00')
      AND position(actor_account_homePage, 'bookroll') > 0
      AND notEmpty(operation_name)
      AND notEmpty(contents_id)
      AND notEmpty(context_id)
    GROUP BY student_id, course_id, event_month
    ORDER BY student_id, course_id, event_month
    """
    return ch_tsv(q)

def fetch_old_context_audit():
    q = """
    SELECT
      count() AS bookroll_content_events,
      countIf(notEmpty(context_id)) AS events_with_context_id,
      countIf(empty(context_id)) AS events_missing_context_id,
      countIf(notEmpty(context_title)) AS events_with_context_title,
      countIf(notEmpty(context_label)) AS events_with_context_label,
      uniqExact(context_id) AS distinct_context_ids,
      uniqExact(splitByChar('@', actor_account_name)[1]) AS distinct_students,
      uniqExact(contents_id) AS distinct_contents
    FROM saikyo_old.statements_mv
    WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
      AND timestamp < toDateTime('2025-04-01 00:00:00')
      AND position(actor_account_homePage, 'bookroll') > 0
      AND notEmpty(operation_name)
      AND notEmpty(contents_id)
    """
    rows = ch_tsv(q)
    return rows[0] if rows else {}

def fetch_new_context_monthly():
    q = """
    SELECT
      splitByChar('@', actor_account_name)[1] AS student_id,
      context_id AS course_id,
      formatDateTime(toStartOfMonth(timestamp), '%Y-%m') AS event_month,
      count() AS events_total,
      uniqExact(toDate(timestamp)) AS active_days,
      sumIf(1, operation_name IN ('NEXT','PREV','PAGE_JUMP','BOOKMARK_JUMP','MEMO_JUMP','SEARCH_JUMP')) AS navigation_events,
      sumIf(1, position(operation_name, 'MEMO') > 0) AS memo_events,
      sumIf(1, position(operation_name, 'MARKER') > 0) AS marker_events,
      sumIf(1, position(operation_name, 'QUIZ') > 0 OR verb_display_en = 'answered') AS quiz_events,
      sumIf(1, position(operation_name, 'TIMER') > 0) AS timer_events,
      sumIf(1, operation_name IN ('OPEN','CLOSE')) AS content_session_events
    FROM saikyo_new.statements_mv
    WHERE timestamp >= toDateTime('2025-04-01 00:00:00')
      AND timestamp < now() + INTERVAL 1 DAY
      AND position(actor_account_homePage, 'bookroll') > 0
      AND notEmpty(operation_name)
      AND notEmpty(context_id)
    GROUP BY student_id, course_id, event_month
    ORDER BY student_id, course_id, event_month
    """
    return ch_tsv(q)

def merge_old_to_course(old_rows, score_students):
    by_key = defaultdict(lambda: defaultdict(int))
    represented = 0
    skipped_non_score_student = 0
    for r in old_rows:
        sid = r['student_id']
        if sid not in score_students:
            skipped_non_score_student += int(r['events_total'])
            continue
        cid = r['course_id']
        key = (sid, cid, r['event_month'])
        for field in ['events_total','active_days','navigation_events','memo_events','marker_events','quiz_events','timer_events','content_session_events']:
            by_key[key][field] += int(r[field])
        by_key[key]['old_events'] += int(r['events_total'])
        represented += int(r['events_total'])
    return by_key, represented, skipped_non_score_student

def add_new_to_course(by_key, new_rows, score_students):
    represented = 0
    for r in new_rows:
        sid = r['student_id']
        if sid not in score_students:
            continue
        key = (sid, r['course_id'], r['event_month'])
        for field in ['events_total','active_days','navigation_events','memo_events','marker_events','quiz_events','timer_events','content_session_events']:
            by_key[key][field] += int(r[field])
        by_key[key]['new_events'] += int(r['events_total'])
        represented += int(r['events_total'])
    return represented

def index_features(features):
    out = defaultdict(list)
    for (sid,cid,ym), vals in features.items():
        out[(sid,cid)].append((month_index(ym), vals))
    for k in out:
        out[k].sort(key=lambda x:x[0])
    return out

def window_sum(index, sid, cid, test_ym, months):
    cutoff = month_index(test_ym)
    start = cutoff - months
    out = defaultdict(int)
    for mi, vals in index.get((sid,cid), []):
        if start <= mi < cutoff:
            for k,v in vals.items():
                out[k] += int(v)
    return out

def source_schema_label(vals):
    has_old = vals.get('old_events', 0) > 0
    has_new = vals.get('new_events', 0) > 0
    if has_old and has_new:
        return 'old_and_new'
    if has_old:
        return 'old'
    if has_new:
        return 'new'
    return 'none'

def summarize(rows, dims):
    buckets = defaultdict(lambda: defaultdict(int))
    students = defaultdict(set); courses = defaultdict(set)
    for r in rows:
        key = tuple(r[d] for d in dims)
        b = buckets[key]
        b['score_rows'] += 1
        for w in ['m3','m6','m12']:
            b[f'{w}_rows'] += 1 if r[f'events_{w}'] > 0 else 0
            b[f'events_{w}'] += r[f'events_{w}']
        for w in ['m3','m6','m12']:
            b[f'active_days_{w}'] += r[f'active_days_{w}']
        students[key].add(r['student_id']); courses[key].add(r['course_id'])
    out=[]
    for key,b in buckets.items():
        n=b['score_rows']
        out.append({**{dims[i]:key[i] for i in range(len(dims))},
            'score_rows':n, 'students':len(students[key]), 'courses':len(courses[key]),
            'm3_rows':b['m3_rows'], 'm3_rate':round(b['m3_rows']/n,4),
            'm6_rows':b['m6_rows'], 'm6_rate':round(b['m6_rows']/n,4),
            'm12_rows':b['m12_rows'], 'm12_rate':round(b['m12_rows']/n,4),
            'events_m3':b['events_m3'], 'events_m6':b['events_m6'], 'events_m12':b['events_m12'],
            'active_days_m3':b['active_days_m3'], 'active_days_m6':b['active_days_m6'],
            'active_days_m12':b['active_days_m12']})
    return sorted(out, key=lambda r:(-r['m3_rows'], -r['score_rows'], tuple(r[d] for d in dims)))

def main():
    scores = read_csv(SCORE_PATH)
    score_students = {r['student_id'] for r in scores}
    old_audit = fetch_old_context_audit()
    old_rows = fetch_old_context_monthly()
    new_rows = fetch_new_context_monthly()
    if old_rows:
        write_csv(OUT / 'xapi_old_context_monthly_local_only.csv', list(old_rows[0].keys()), old_rows)
    if new_rows:
        write_csv(OUT / 'xapi_new_context_monthly_local_only.csv', list(new_rows[0].keys()), new_rows)
    features, old_rep, old_non_score = merge_old_to_course(old_rows, score_students)
    new_rep = add_new_to_course(features, new_rows, score_students)
    index = index_features(features)
    linked=[]
    for s in scores:
        sid=s['student_id']; cid=s['course_id']; tym=test_month(s['test_date'])
        m3=window_sum(index,sid,cid,tym,3); m6=window_sum(index,sid,cid,tym,6); m12=window_sum(index,sid,cid,tym,12)
        linked.append({'student_id':sid,'course_id':cid,'test_year':s['test_year'],'test_month':tym,
            'name':s.get('name',''),'test_date':s.get('test_date',''),
            'quiz_score':s.get('quiz_score',''),'score_min':s.get('score_min',''),'score_max':s.get('score_max',''),
            'score_normalized_0_1':s.get('score_normalized_0_1',''),'score_validity_flag':s.get('score_validity_flag',''),
            'grade_level':s['grade_level'] or '(missing)','course_subject':s['course_subject'] or '(missing)',
            'test_family':s['test_family'],'classification_confidence':s['classification_confidence'],
            'xapi_source_schema_m3':source_schema_label(m3),
            'events_m3':m3.get('events_total',0),'events_m6':m6.get('events_total',0),'events_m12':m12.get('events_total',0),
            'old_events_m3':m3.get('old_events',0),'new_events_m3':m3.get('new_events',0),
            'old_events_m6':m6.get('old_events',0),'new_events_m6':m6.get('new_events',0),
            'old_events_m12':m12.get('old_events',0),'new_events_m12':m12.get('new_events',0),
            'active_days_m3':m3.get('active_days',0),'active_days_m6':m6.get('active_days',0),
            'active_days_m12':m12.get('active_days',0),
            'navigation_m3':m3.get('navigation_events',0),'navigation_m6':m6.get('navigation_events',0),
            'navigation_m12':m12.get('navigation_events',0),
            'memo_m3':m3.get('memo_events',0),'memo_m6':m6.get('memo_events',0),
            'memo_m12':m12.get('memo_events',0),
            'marker_m3':m3.get('marker_events',0),'marker_m6':m6.get('marker_events',0),
            'marker_m12':m12.get('marker_events',0),
            'quiz_m3':m3.get('quiz_events',0),'quiz_m6':m6.get('quiz_events',0),
            'quiz_m12':m12.get('quiz_events',0),
            'timer_m3':m3.get('timer_events',0),'timer_m6':m6.get('timer_events',0),
            'timer_m12':m12.get('timer_events',0),
            'content_session_m3':m3.get('content_session_events',0),'content_session_m6':m6.get('content_session_events',0),
            'content_session_m12':m12.get('content_session_events',0)})
    write_csv(OUT / 'score_xapi_same_course_sufficiency_local_only.csv', list(linked[0].keys()), linked)
    summaries={
      'same_course_sufficiency_by_year_family.csv':['test_year','test_family'],
      'same_course_sufficiency_by_grade_subject_family.csv':['grade_level','course_subject','test_family'],
      'same_course_sufficiency_by_year.csv':['test_year']}
    summary_data={}
    for fn,dims in summaries.items():
        rows=summarize(linked,dims); summary_data[fn]=(dims,rows); write_csv(OUT/fn,list(rows[0].keys()),rows)
    report=[]
    report.append('# Same-Course Harmonized XAPI Sufficiency')
    report.append('')
    report.append('## Scope')
    report.append('- Old xAPI course mapping: direct non-empty context_id after the saikyo_old.statements_mv reimport.')
    report.append('- New xAPI course mapping: direct non-empty context_id.')
    report.append('- Old and new features are combined after mapping into the same student_id + course_id + event_month feature grain.')
    report.append('- Combined analysis rows retain source-schema counts old_events_* and new_events_* so old/new contribution can be audited.')
    report.append('- The old content-directory bridge is no longer used as the primary same-course mapping source.')
    report.append('- This pass keeps non-empty contents_id to preserve the previous content-learning event universe, but uses context_id for course linkage.')
    report.append('')
    report.append('## Extraction And Mapping Coverage')
    if old_audit:
        report.append(f'- Old Bookroll content events audited: {int(old_audit["bookroll_content_events"]):,}')
        report.append(f'- Old Bookroll content events with context_id: {int(old_audit["events_with_context_id"]):,}')
        report.append(f'- Old Bookroll content events missing context_id: {int(old_audit["events_missing_context_id"]):,}')
        report.append(f'- Old Bookroll content events with context_title: {int(old_audit["events_with_context_title"]):,}')
        report.append(f'- Old Bookroll content events with context_label: {int(old_audit["events_with_context_label"]):,}')
        report.append(f'- Distinct old context_id values in audited Bookroll content events: {int(old_audit["distinct_context_ids"]):,}')
    report.append(f'- Old context-month aggregate rows fetched: {len(old_rows):,}')
    report.append(f'- New context-month aggregate rows fetched: {len(new_rows):,}')
    report.append(f'- Old events represented in same-course context_id features for score students: {old_rep:,}')
    report.append(f'- Old events skipped because actor was not in score students: {old_non_score:,}')
    report.append(f'- New events represented in same-course mapped features for score students: {new_rep:,}')
    report.append('')
    for title,fn,maxn in [('By Year','same_course_sufficiency_by_year.csv',20),('By Year/Test Family','same_course_sufficiency_by_year_family.csv',30),('By Grade/Subject/Family','same_course_sufficiency_by_grade_subject_family.csv',50)]:
        dims,rows=summary_data[fn]; report.append(f'## {title}')
        for r in rows[:maxn]:
            label=', '.join(f'{d}={r[d]}' for d in dims)
            report.append(f'- {label}: score_rows={r["score_rows"]:,}, students={r["students"]:,}, courses={r["courses"]:,}, m3_rows={r["m3_rows"]:,} ({float(r["m3_rate"]):.1%}), m6_rows={r["m6_rows"]:,} ({float(r["m6_rate"]):.1%}), m12_rows={r["m12_rows"]:,} ({float(r["m12_rate"]):.1%}), events_m3={r["events_m3"]:,}')
        report.append('')
    report.append('## Validity Interpretation')
    report.append('- Cells with meaningful same-course coverage are candidates for stronger behavior-outcome claims.')
    report.append('- Cells with strong student-level but weak same-course coverage should be treated as general learner behavior context, not same-course reading behavior.')
    report.append('- The prior 59,209,738 old-event content-bridge exclusion is obsolete for this direct-context rerun and should not be reported as a current manuscript limitation unless a later audit finds missing old context_id values.')
    (REPORTS/'same_course_harmonized_xapi_sufficiency.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    print('\n'.join(report))

if __name__ == '__main__':
    main()
