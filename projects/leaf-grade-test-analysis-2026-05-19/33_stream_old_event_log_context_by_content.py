#!/usr/bin/env python3
import argparse
import csv
import os
import sqlite3
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)

BOOKROLL_HOST = os.environ.get('BOOKROLL_MYSQL_HOST', '10.236.173.145')
BOOKROLL_PORT = os.environ.get('BOOKROLL_MYSQL_PORT', '33306')
BOOKROLL_USER = os.environ.get('BOOKROLL_MYSQL_USER', 'reader')
BOOKROLL_DB = os.environ.get('BOOKROLL_MYSQL_DB', 'bookroll')

KEY_COLS = ['contents_id', 'contents_name', 'contextid', 'context_title', 'context_label', 'role']


def mysql_literal(value):
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


def decode_mysql_field(value):
    if value == r'\N':
        return ''
    return (
        value
        .replace(r'\t', '\t')
        .replace(r'\n', '\n')
        .replace(r'\r', '\r')
        .replace(r'\\', '\\')
    )


def mysql_env():
    env = os.environ.copy()
    pwd = os.environ.get('BOOKROLL_MYSQL_PWD', os.environ.get('MYSQL_PWD', ''))
    if pwd:
        env['MYSQL_PWD'] = pwd
    return env


def stream_mysql_rows(sql):
    cmd = [
        'mysql',
        '--quick',
        '--batch',
        '--skip-column-names',
        '-h', BOOKROLL_HOST,
        '-P', BOOKROLL_PORT,
        '-u', BOOKROLL_USER,
        '-D', BOOKROLL_DB,
        '-e', sql,
    ]
    proc = subprocess.Popen(
        cmd,
        env=mysql_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None
    for line in proc.stdout:
        yield [decode_mysql_field(part) for part in line.rstrip('\\n').split('\\t')]
    stderr = proc.stderr.read() if proc.stderr is not None else ''
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(stderr.strip() or f'mysql exited with status {rc}')


def init_db(path, reset):
    if reset and path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    con.execute('PRAGMA journal_mode=WAL')
    con.execute('PRAGMA synchronous=NORMAL')
    key_defs = ', '.join(f'{c} TEXT NOT NULL' for c in KEY_COLS)
    key_list = ', '.join(KEY_COLS)
    con.execute(f'''
        CREATE TABLE IF NOT EXISTS agg (
            {key_defs},
            event_rows INTEGER NOT NULL,
            first_event TEXT NOT NULL,
            last_event TEXT NOT NULL,
            PRIMARY KEY ({key_list})
        )
    ''')
    con.execute(f'''
        CREATE TABLE IF NOT EXISTS key_users (
            {key_defs},
            user_id TEXT NOT NULL,
            PRIMARY KEY ({key_list}, user_id)
        )
    ''')
    con.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            last_log_id INTEGER NOT NULL,
            chunks INTEGER NOT NULL,
            rows_seen INTEGER NOT NULL
        )
    ''')
    con.execute('INSERT OR IGNORE INTO progress(id, last_log_id, chunks, rows_seen) VALUES (1, 0, 0, 0)')
    con.commit()
    return con


def progress(con):
    row = con.execute('SELECT last_log_id, chunks, rows_seen FROM progress WHERE id = 1').fetchone()
    return {'last_log_id': row[0], 'chunks': row[1], 'rows_seen': row[2]}


def update_progress(con, last_log_id, chunk_count, row_count):
    con.execute(
        'UPDATE progress SET last_log_id = ?, chunks = chunks + ?, rows_seen = rows_seen + ? WHERE id = 1',
        (last_log_id, chunk_count, row_count),
    )


def make_chunk_query(last_log_id, start, end, chunk_rows):
    return f'''
    SELECT
      log_id,
      contents_id,
      contents_name,
      contextid,
      context_title,
      context_label,
      role,
      user_id,
      DATE_FORMAT(operation_date, '%Y-%m-%d %H:%i:%s') AS operation_date
    FROM br_event_log
    WHERE log_id > {int(last_log_id)}
      AND operation_date >= {mysql_literal(start)}
      AND operation_date < {mysql_literal(end)}
      AND contents_id IS NOT NULL
      AND contents_id <> ''
    ORDER BY log_id
    LIMIT {int(chunk_rows)}
    '''


def upsert_chunk(con, chunk_agg, chunk_users):
    if not chunk_agg:
        return
    key_list = ', '.join(KEY_COLS)
    placeholders = ', '.join('?' for _ in range(len(KEY_COLS) + 3))
    con.executemany(
        f'''
        INSERT INTO agg ({key_list}, event_rows, first_event, last_event)
        VALUES ({placeholders})
        ON CONFLICT({key_list}) DO UPDATE SET
          event_rows = event_rows + excluded.event_rows,
          first_event = CASE
            WHEN agg.first_event = '' OR excluded.first_event < agg.first_event THEN excluded.first_event
            ELSE agg.first_event
          END,
          last_event = CASE
            WHEN excluded.last_event > agg.last_event THEN excluded.last_event
            ELSE agg.last_event
          END
        ''',
        [(*key, vals['event_rows'], vals['first_event'], vals['last_event']) for key, vals in chunk_agg.items()],
    )
    if chunk_users:
        user_placeholders = ', '.join('?' for _ in range(len(KEY_COLS) + 1))
        con.executemany(
            f'INSERT OR IGNORE INTO key_users ({key_list}, user_id) VALUES ({user_placeholders})',
            [(*key, user_id) for key, user_id in chunk_users],
        )


def stream_to_sqlite(con, args):
    state = progress(con)
    last_log_id = state['last_log_id']
    total_new_rows = 0
    chunks = 0

    while True:
        rows_in_chunk = 0
        chunk_agg = defaultdict(lambda: {'event_rows': 0, 'first_event': '', 'last_event': ''})
        chunk_users = set()
        max_log_id = last_log_id

        for row in stream_mysql_rows(make_chunk_query(last_log_id, args.start, args.end, args.chunk_rows)):
            if len(row) != 9:
                raise RuntimeError(f'Unexpected mysql row shape with {len(row)} fields: {row!r}')
            log_id, contents_id, contents_name, contextid, context_title, context_label, role, user_id, operation_date = row
            max_log_id = max(max_log_id, int(log_id))
            key = (contents_id, contents_name, contextid, context_title, context_label, role)
            vals = chunk_agg[key]
            vals['event_rows'] += 1
            if operation_date and (not vals['first_event'] or operation_date < vals['first_event']):
                vals['first_event'] = operation_date
            if operation_date and operation_date > vals['last_event']:
                vals['last_event'] = operation_date
            if user_id:
                chunk_users.add((key, user_id))
            rows_in_chunk += 1

        if rows_in_chunk == 0:
            break

        with con:
            upsert_chunk(con, chunk_agg, chunk_users)
            update_progress(con, max_log_id, 1, rows_in_chunk)

        last_log_id = max_log_id
        chunks += 1
        total_new_rows += rows_in_chunk
        print(f'chunk={state["chunks"] + chunks} rows={rows_in_chunk:,} last_log_id={last_log_id}', flush=True)

        if args.max_chunks and chunks >= args.max_chunks:
            break

    return total_new_rows, chunks


def export_csv(con, output_path):
    con.execute('DROP VIEW IF EXISTS user_counts')
    con.execute(f'''
        CREATE TEMP VIEW user_counts AS
        SELECT {', '.join(KEY_COLS)}, COUNT(*) AS users
        FROM key_users
        GROUP BY {', '.join(KEY_COLS)}
    ''')
    join_clause = ' AND '.join(f'a.{c} = u.{c}' for c in KEY_COLS)
    rows = con.execute(f'''
        SELECT
          a.contents_id,
          a.contents_name,
          a.contextid,
          a.context_title,
          a.context_label,
          a.role,
          a.event_rows,
          COALESCE(u.users, 0) AS users,
          a.first_event,
          a.last_event
        FROM agg a
        LEFT JOIN user_counts u ON {join_clause}
        ORDER BY a.event_rows DESC
    ''')
    fieldnames = ['contents_id', 'contents_name', 'contextid', 'context_title', 'context_label', 'role', 'event_rows', 'users', 'first_event', 'last_event']
    with output_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        writer.writerows(rows)


def parse_args():
    parser = argparse.ArgumentParser(description='Stream old Bookroll br_event_log context rows and aggregate locally.')
    parser.add_argument('--start', default='2019-01-01')
    parser.add_argument('--end', default='2025-04-01')
    parser.add_argument('--chunk-rows', type=int, default=50000)
    parser.add_argument('--max-chunks', type=int, default=0, help='Optional smoke-test limit. 0 means run until complete.')
    parser.add_argument('--resume', action='store_true', help='Resume from the progress stored in the SQLite work file.')
    parser.add_argument('--sqlite-path', type=Path, default=OUT / 'old_bookroll_event_log_context_by_content_streamed.sqlite')
    parser.add_argument('--output', type=Path, default=OUT / 'old_bookroll_event_log_context_by_content_streamed.csv')
    return parser.parse_args()


def main():
    args = parse_args()
    con = init_db(args.sqlite_path, reset=not args.resume)
    total_new_rows, chunks = stream_to_sqlite(con, args)
    export_csv(con, args.output)
    state = progress(con)
    print(f'new_rows_streamed={total_new_rows:,}')
    print(f'new_chunks={chunks:,}')
    print(f'total_rows_streamed={state["rows_seen"]:,}')
    print(f'last_log_id={state["last_log_id"]}')
    print(f'output={args.output}')
    print(f'sqlite_work_file={args.sqlite_path}')


if __name__ == '__main__':
    main()
