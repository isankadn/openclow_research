# SQL Query Inventory

This file inventories the database queries used by the LEAF/Bookroll grade-test analysis scripts.

Important: credentials are intentionally omitted. Queries that used dynamic Python-generated lists are shown with placeholders such as `<course_id_list>` or `<student_id_list>`.

## Why 59,209,738 Old Events Were Excluded

The 59,209,738 events were not excluded directly by a SQL `WHERE` clause. They were fetched from old ClickHouse as Bookroll events with non-empty `contents_id`, then excluded locally in `06_same_course_harmonized_xapi.py` because their `contents_id` did not have a unique course mapping in the old Bookroll content-directory bridge.

Relevant local rule:

- keep old event only if `contents_id -> unique mapped_course_id` exists in `old_bookroll_content_course_bridge_unique.csv`
- skip old event if content is unmapped, low-confidence, or ambiguous across multiple possible courses
- skip old event if actor/student is not present in the cleaned score-student set

Therefore, onboarding those events is mainly a content-course mapping problem, not an xAPI extraction problem.

## Databases Queried

| Source | Database/table | Purpose |
| --- | --- | --- |
| Analysis MySQL | `analysis_development.course_student_scores` | Score/outcome rows and test metadata |
| LMS MySQL | `moodle.mdl_course`, `moodle.mdl_course_categories` | Course/category context for grade, subject, level |
| Old Bookroll MySQL | `bookroll.br_contents_*` | Old content-directory ownership bridge for course mapping |
| Old ClickHouse xAPI | `saikyo_old.statements_mv` | Pre-2025 Bookroll xAPI events |
| New ClickHouse xAPI | `saikyo_new.statements_mv` | Post-2025 Bookroll xAPI events |

## Analysis MySQL: `analysis_development.course_student_scores`

Scripts:

- `projects/leaf-grade-test-analysis-2026-05-19/01_profile_grade_tests.py`
- `projects/leaf-course-context-2026-05-19/build_course_context.py`
- `projects/leaf-course-context-2026-05-19/focus_2025_2026_tests.py`

### Score Overview

```sql
SELECT COUNT(*) AS total_rows,
       SUM(CASE WHEN date_at IS NULL THEN 1 ELSE 0 END) AS missing_date_rows,
       SUM(CASE WHEN date_at IS NOT NULL THEN 1 ELSE 0 END) AS dated_rows,
       COUNT(DISTINCT student_id) AS students,
       COUNT(DISTINCT course_id) AS courses,
       COUNT(DISTINCT name) AS test_names,
       MIN(date_at) AS min_date,
       MAX(date_at) AS max_date
FROM course_student_scores;
```

### Duplicate Outcome-Grain Check

```sql
SELECT COUNT(*) AS duplicate_groups,
       COALESCE(SUM(row_count - 1), 0) AS duplicate_extra_rows
FROM (
  SELECT student_id, course_id, name, date_at, COUNT(*) AS row_count
  FROM course_student_scores
  WHERE date_at IS NOT NULL
  GROUP BY student_id, course_id, name, date_at
  HAVING COUNT(*) > 1
) d;
```

### Clean Score Grain

```sql
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
ORDER BY test_date, course_id, name, student_id;
```

### Score Rows By Course

```sql
SELECT
  course_id,
  course_name,
  COUNT(*) AS score_rows,
  COUNT(DISTINCT student_id) AS students,
  COUNT(DISTINCT name) AS tests,
  COALESCE(DATE_FORMAT(MIN(date_at), '%Y-%m-%d'), '') AS min_date,
  COALESCE(DATE_FORMAT(MAX(date_at), '%Y-%m-%d'), '') AS max_date
FROM course_student_scores
GROUP BY course_id, course_name
ORDER BY course_id;
```

### 2025-2026 Test-Focus Query

```sql
SELECT
  course_id,
  course_name,
  name AS test_name,
  DATE_FORMAT(date_at, '%Y-%m-%d') AS test_date,
  DATE_FORMAT(date_at, '%Y') AS test_year,
  DATE_FORMAT(date_at, '%Y-%m') AS test_month,
  student_id,
  COUNT(*) AS score_rows
FROM course_student_scores
WHERE date_at >= '2025-01-01'
  AND date_at < '2027-01-01'
GROUP BY course_id, course_name, name, test_date, test_year, test_month, student_id
ORDER BY test_date, course_id, name, student_id;
```

## LMS MySQL: `moodle`

Script:

- `projects/leaf-course-context-2026-05-19/build_course_context.py`

### Moodle Course Metadata

```sql
SELECT id, fullname, shortname, category
FROM mdl_course
ORDER BY id;
```

### Moodle Course Categories

```sql
SELECT id, name, parent, depth, path
FROM mdl_course_categories
ORDER BY id;
```

## Old Bookroll MySQL: `bookroll`

Script:

- `projects/leaf-grade-test-analysis-2026-05-19/05_build_old_content_course_bridge.py`

### Old Content-To-Directory/Owner Bridge

```sql
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
LEFT JOIN br_contents_directory_owner do ON do.directory_id = d.directory_id;
```

## Old ClickHouse xAPI: `saikyo_old.statements_mv`

Scripts:

- `projects/leaf-grade-test-analysis-2026-05-19/02_xapi_sufficiency_by_student.py`
- `projects/leaf-grade-test-analysis-2026-05-19/02_xapi_sufficiency_monthly.py`
- `projects/leaf-grade-test-analysis-2026-05-19/06_same_course_harmonized_xapi.py`

### Old Student-Day Operation Sufficiency

```sql
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
  AND splitByChar('@', actor_account_name)[1] IN (<student_id_list>)
  AND notEmpty(operation_name)
GROUP BY student_id, event_date, operation_name, process_code, verb_display_en
ORDER BY student_id, event_date;
```

### Old Monthly Student-Level Sufficiency

This query was run through a parameterized function with `db='saikyo_old'`, `start='2019-01-01 00:00:00'`, and `end='2025-04-01 00:00:00'`.

```sql
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
FROM saikyo_old.statements_mv
WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
  AND timestamp < toDateTime('2025-04-01 00:00:00')
  AND position(actor_account_homePage, 'bookroll') > 0
  AND notEmpty(operation_name)
GROUP BY student_id, event_month
ORDER BY student_id, event_month;
```

### Old Content-Month Same-Course Extraction

This is the query behind the 59,209,738 skipped-old-event question. It fetches old Bookroll activity by student/content/month. The same-course exclusion happens after this query, during the local `contents_id -> course_id` bridge merge.

The `notEmpty(operation_name)` and `notEmpty(contents_id)` predicates are intentional for Bookroll behavior extraction. As clarified on 2026-05-24, roughly 24,937,088 old `saikyo_old.statements_mv` rows have empty values for these Bookroll-specific fields because they come from Moodle/LMS and Analysis application xAPI records.

```sql
SELECT
  splitByChar('@', actor_account_name)[1] AS student_id,
  contents_id,
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
GROUP BY student_id, contents_id, event_month
ORDER BY student_id, contents_id, event_month;
```

### Old Bookroll Event Log Context Bridge Safety Note

Do not run the full `br_event_log` context bridge as one grouped SQL query. Stream bounded `log_id` chunks with `projects/leaf-grade-test-analysis-2026-05-19/33_stream_old_event_log_context_by_content.py` and aggregate locally.

## New ClickHouse xAPI: `saikyo_new.statements_mv`

Scripts:

- `projects/leaf-course-context-2026-05-19/check_2025_xapi_sufficiency.py`
- `projects/leaf-grade-test-analysis-2026-05-19/02_xapi_sufficiency_by_student.py`
- `projects/leaf-grade-test-analysis-2026-05-19/02_xapi_sufficiency_monthly.py`
- `projects/leaf-grade-test-analysis-2026-05-19/06_same_course_harmonized_xapi.py`

### Recent Course-Level xAPI Coverage

Shared `WHERE` condition:

```sql
context_id IN (<course_id_list>)
AND timestamp >= toDateTime('2024-04-01 00:00:00')
AND timestamp < toDateTime('2025-03-06 00:00:00')
AND actor_name_role = 'student'
```

```sql
SELECT
  context_id AS course_id,
  any(context_title) AS context_title,
  count() AS xapi_events,
  uniqExact(actor_account_name) AS xapi_actor_accounts,
  uniqExact(splitByChar('@', actor_account_name)[1]) AS xapi_actor_prefixes,
  uniqExact(contents_id) AS contents,
  uniqExact(operation_name) AS operations,
  min(timestamp) AS first_xapi,
  max(timestamp) AS last_xapi
FROM saikyo_new.statements_mv
WHERE context_id IN (<course_id_list>)
  AND timestamp >= toDateTime('2024-04-01 00:00:00')
  AND timestamp < toDateTime('2025-03-06 00:00:00')
  AND actor_name_role = 'student'
GROUP BY context_id
ORDER BY xapi_events DESC;
```

### Recent Course-Actor Overlap

```sql
SELECT
  context_id AS course_id,
  splitByChar('@', actor_account_name)[1] AS actor_prefix,
  count() AS xapi_events
FROM saikyo_new.statements_mv
WHERE context_id IN (<course_id_list>)
  AND timestamp >= toDateTime('2024-04-01 00:00:00')
  AND timestamp < toDateTime('2025-03-06 00:00:00')
  AND actor_name_role = 'student'
GROUP BY context_id, actor_prefix;
```

### Recent Operations By Course

```sql
SELECT
  context_id AS course_id,
  operation_name,
  count() AS xapi_events
FROM saikyo_new.statements_mv
WHERE context_id IN (<course_id_list>)
  AND timestamp >= toDateTime('2024-04-01 00:00:00')
  AND timestamp < toDateTime('2025-03-06 00:00:00')
  AND actor_name_role = 'student'
GROUP BY context_id, operation_name
ORDER BY course_id, xapi_events DESC;
```

### New Student-Day Operation Sufficiency

```sql
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
  AND splitByChar('@', actor_account_name)[1] IN (<student_id_list>)
  AND notEmpty(operation_name)
GROUP BY student_id, event_date, operation_name, verb_display_en
ORDER BY student_id, event_date;
```

### New Monthly Student-Level Sufficiency

This query was run through a parameterized function with `db='saikyo_new'`, `start='2025-04-01 00:00:00'`, and `end='2026-12-31 23:59:59'`.

```sql
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
FROM saikyo_new.statements_mv
WHERE timestamp >= toDateTime('2025-04-01 00:00:00')
  AND timestamp < toDateTime('2026-12-31 23:59:59')
  AND position(actor_account_homePage, 'bookroll') > 0
  AND notEmpty(operation_name)
GROUP BY student_id, event_month
ORDER BY student_id, event_month;
```

### New Context-Month Same-Course Extraction

```sql
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
ORDER BY student_id, course_id, event_month;
```
