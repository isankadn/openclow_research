#!/usr/bin/env python3
import csv
import os
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)
SCORE_CONTEXT = Path('/home/ubuntu/.openclaw/workspace/projects/leaf-course-context-2026-05-19/outputs/score_course_context.csv')

BOOKROLL_HOST = os.environ.get('BOOKROLL_MYSQL_HOST', '10.236.173.145')
BOOKROLL_PORT = os.environ.get('BOOKROLL_MYSQL_PORT', '33306')
BOOKROLL_USER = os.environ.get('BOOKROLL_MYSQL_USER', 'reader')
BOOKROLL_DB = os.environ.get('BOOKROLL_MYSQL_DB', 'bookroll')

def mysql_query(sql):
    env = os.environ.copy()
    pwd = os.environ.get('BOOKROLL_MYSQL_PWD', os.environ.get('MYSQL_PWD', ''))
    if pwd:
        env['MYSQL_PWD'] = pwd
    cmd = ['mysql','-N','-B','-h',BOOKROLL_HOST,'-P',BOOKROLL_PORT,'-u',BOOKROLL_USER,'-D',BOOKROLL_DB,'-e',sql]
    proc = subprocess.run(cmd, env=env, text=True, capture_output=True, check=True)
    return [line.split('\t') for line in proc.stdout.splitlines()]

def write_csv(path, fieldnames, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)

def course_id_from_owner(owner_id):
    if not owner_id:
        return ''
    return owner_id.split('@',1)[0]

def main():
    score_courses = {}
    if SCORE_CONTEXT.exists():
        with SCORE_CONTEXT.open(encoding='utf-8') as f:
            for r in csv.DictReader(f):
                score_courses[r['course_id']] = r

    rows = mysql_query("""
    SELECT
      cbd.contents_id,
      cbd.parent_id AS directory_id,
      d.name AS directory_name,
      d.parent_id AS parent_directory_id,
      pd.name AS parent_directory_name,
      do.owner_id,
      do.owner_name,
      do.owner_type
    FROM br_contents_belong_directory cbd
    JOIN br_contents_directory d ON d.directory_id = cbd.parent_id
    LEFT JOIN br_contents_directory pd ON pd.directory_id = d.parent_id
    LEFT JOIN br_contents_directory_owner do ON do.directory_id = d.directory_id
    """)

    bridge = []
    candidates_by_content = defaultdict(list)
    for contents_id, directory_id, directory_name, parent_directory_id, parent_directory_name, owner_id, owner_name, owner_type in rows:
        cid = course_id_from_owner(owner_id)
        if cid and cid in score_courses:
            source = 'directory_owner_id_matches_score_course_id'
            confidence = 'high'
        elif cid and directory_name in {v.get('score_course_name') for v in score_courses.values()}:
            source = 'directory_name_matches_score_course_name_owner_unverified'
            confidence = 'medium'
        else:
            source = 'unmatched'
            confidence = 'low'
        rec = {
            'contents_id': contents_id,
            'directory_id': directory_id,
            'directory_name': directory_name,
            'parent_directory_id': parent_directory_id,
            'parent_directory_name': parent_directory_name,
            'owner_id': owner_id,
            'owner_name': owner_name,
            'owner_type': owner_type,
            'mapped_course_id': cid if cid in score_courses else '',
            'mapped_course_name': score_courses.get(cid, {}).get('score_course_name',''),
            'grade_level': score_courses.get(cid, {}).get('grade_level',''),
            'subject': score_courses.get(cid, {}).get('subject',''),
            'mapping_source': source,
            'mapping_confidence': confidence,
        }
        bridge.append(rec)
        if rec['mapped_course_id']:
            candidates_by_content[contents_id].append(rec)

    # Keep one high-confidence row per content when unambiguous.
    final = []
    ambiguous = []
    for content_id, recs in candidates_by_content.items():
        keys = {(r['mapped_course_id'], r['directory_id']) for r in recs}
        course_ids = {r['mapped_course_id'] for r in recs}
        if len(course_ids) == 1:
            best = recs[0].copy()
            best['content_course_mapping_status'] = 'unique_course'
            best['candidate_count'] = len(recs)
            final.append(best)
        else:
            for r in recs:
                x = r.copy(); x['content_course_mapping_status'] = 'ambiguous_multiple_courses'; x['candidate_count'] = len(recs); ambiguous.append(x)

    write_csv(OUT / 'old_bookroll_content_course_bridge_all_candidates.csv', list(bridge[0].keys()), bridge)
    if final:
        write_csv(OUT / 'old_bookroll_content_course_bridge_unique.csv', list(final[0].keys()), sorted(final, key=lambda r:(r['mapped_course_id'], r['contents_id'])))
    if ambiguous:
        write_csv(OUT / 'old_bookroll_content_course_bridge_ambiguous.csv', list(ambiguous[0].keys()), ambiguous)

    counts = Counter(r['mapping_confidence'] for r in bridge)
    unique_by_course = Counter(r['mapped_course_id'] for r in final)
    report=[]
    report.append('# Old BookRoll Content-Course Bridge')
    report.append('')
    report.append('## Method')
    report.append('- Source tables: br_contents_belong_directory, br_contents_directory, br_contents_directory_owner.')
    report.append('- Candidate mapping: contents_id -> directory -> directory_owner.owner_id prefix before @ -> Moodle/score course_id.')
    report.append('- High confidence requires owner_id prefix to match a known score-table/Moodle course_id.')
    report.append('')
    report.append('## Coverage')
    report.append(f'- Raw content-directory-owner candidate rows: {len(bridge):,}')
    report.append(f'- Unique contents with one mapped score course: {len(final):,}')
    report.append(f'- Ambiguous content-course candidate rows: {len(ambiguous):,}')
    for k,v in counts.items(): report.append(f'- Candidate confidence {k}: {v:,}')
    report.append('')
    report.append('## Top Courses By Unique Mapped Contents')
    for cid,n in unique_by_course.most_common(30):
        report.append(f'- {cid} {score_courses.get(cid,{}).get("score_course_name","")}: {n:,} contents')
    report.append('')
    report.append('## Interpretation')
    report.append('- This bridge is strong enough to test same-course old BookRoll linkage for uniquely mapped contents.')
    report.append('- Ambiguous contents should be excluded from same-course modeling until reviewed.')
    (OUT / 'old_bookroll_content_course_bridge_report.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    print('\n'.join(report))

if __name__ == '__main__':
    main()
