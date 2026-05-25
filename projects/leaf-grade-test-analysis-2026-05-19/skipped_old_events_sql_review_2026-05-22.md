# Skipped Old Bookroll Events - SQL Review Pack

Date: 2026-05-22

Purpose: collect the SQL relevant to the old Bookroll/xAPI events that were excluded from the manuscript analysis, especially the 59,209,738 events skipped during same-course mapping.

Credentials are omitted here. Use the stored access details in agents/leaf-data-scientist/MEMORY.md and memory/leaf-old-data-stores.md.

## Key Finding

The 59,209,738 events were not excluded by an SQL WHERE clause.

They were fetched from saikyo_old.statements_mv by the old content-month query below, then excluded locally in projects/leaf-grade-test-analysis-2026-05-19/06_same_course_harmonized_xapi.py because:

1. the actor/student was in the cleaned score-student set, but
2. the event contents_id did not resolve to a unique mapped_course_id in outputs/old_bookroll_content_course_bridge_unique.csv.

Current local exclusion logic:

So the next task is to improve contents_id -> course_id mapping, not to loosen the xAPI extraction query.

Important clarification from 2026-05-24: the old table also has about 24,937,088 rows with empty `operation_name` and about 24,937,088 rows with empty `contents_id`. Those rows are expected Moodle/LMS and Analysis application records that do not carry Bookroll-specific fields; they are not the skipped old Bookroll reading events discussed here.

## Current Old xAPI Extraction Behind The Skipped Events

Source: ClickHouse saikyo_old.statements_mv.

## Diagnostic Query: Which Old Contents Drive Unmapped Events?

Use this to list content IDs by volume before applying any local bridge. It should help prioritize manual mapping.

Optional version after exporting a mapped contents list:

## Current Old Bookroll Content-Course Bridge Query

Source: old MySQL bookroll on 10.236.173.145:33306.

This is the current bridge. It maps contents_id -> directory -> directory_owner.owner_id, then locally uses the prefix before @ as a candidate Moodle/score course_id.

Current local mapping rule:

## Candidate Bridge Query 1: Add Content Metadata

Run against old Bookroll and new Bookroll. This adds content title, content parent directory, teacher fields, and publication dates. For old MySQL, some columns may differ. Do not select `c.deleted_at`; the relevant `br_contents` schema does not expose that column.

## Candidate Bridge Query 2: Directory Owner Tree

Use this to inspect whether ownership is on the content directory, parent directory, or higher directory.

## Candidate Bridge Query 3: Bookroll Event Log Context By Content

This is useful for old Bookroll because br_event_log has context fields in the old schema. It may provide content-course mapping when directory ownership is missing.

Run against old Bookroll first. The new br_event_log schema checked on 2026-05-22 does not expose contextid, context_title, or context_label.

Do not run this as a one-shot grouped SQL query. The full `br_event_log` aggregation can overload the SQL server. Use the local streaming helper, which fetches bounded `log_id` chunks and aggregates into local SQLite/CSV:

The bounded SQL shape used by the helper is:

## Candidate Bridge Query 4: Old Event Log Content-Course Candidates Only For Unmapped Contents

Use after preparing  from the diagnostic ClickHouse query/local excluded set. Keep this batched or streamed; do not use a huge one-shot `IN (...)` query against `br_event_log`.

## Moodle Course/Category Context Query

Run against old and new Moodle as needed.

## Analysis Score Courses Query

Run against old and new Analysis to see which course IDs and score windows exist.

## New Analysis Score Window Query

For the new 2025-04-01 to 2026-04-01 window.

## New xAPI Same-Course Extraction Should Be Windowed To 2026-04-01

Previous script used timestamp < now() + INTERVAL 1 DAY. For this rerun, use the explicit academic-year window.

## New xAPI Content Diagnostic Query

This helps compare saikyo_new.contents_id with new Bookroll MySQL br_contents.

## New Bookroll Tables Confirmed By Metadata Check

New Bookroll on 127.0.0.1:30100 has:

- br_contents
- br_contents_belong_directory
- br_contents_directory
- br_contents_directory_owner
- br_contents_owner
- br_event_log

New Moodle on 127.0.0.1:30102 has:

- mdl_course
- mdl_course_categories

New Analysis on 127.0.0.1:30101 has:

- course_student_scores
- course_students

Note: MySQL CLI should use 127.0.0.1 instead of localhost if it otherwise tries the Unix socket. The stored logical host remains localhost.

## Likely Inclusion Path For The 59,209,738 Events

1. Build a richer contents_id -> candidate_course_id table using:
  - current directory owner bridge,
  - direct br_contents_owner,
  - parent/grandparent directory owners,
  - old br_event_log.contextid/context_title/context_label,
  - Moodle course/category names,
  - Analysis score course list.
2. Classify each contents_id as:
  - unique high-confidence course,
  - unique medium-confidence course,
  - ambiguous multiple courses,
  - unmapped.
3. Re-run same-course harmonized features with an auditable mapping-confidence column rather than a binary unique-only bridge.
4. Report sensitivity:
  - high-confidence only,
  - high + medium,
  - manual-reviewed mapping,
  - ambiguous excluded.

## Additional Validated NEW Mapping Evidence Queries

The analysis worker suggested these, and metadata checks confirmed the tables exist on the NEW endpoints.

### NEW Bookroll tmp_sk_user_course

This table directly links actor, contents_id, context_id, and school_id. It may be the highest-value new Bookroll mapping source.

### NEW Moodle LTI Placement Evidence

Metadata confirms the relevant Moodle tables exist: mdl_lti, mdl_lti_types, mdl_course_modules, mdl_modules, and mdl_context.

### NEW Analysis contents Table

Metadata confirms analysis_development.contents has contentsid, course_id, contentsname, log_time, consumer_key, and old_consumer_key.

### NEW Analysis Quiz/Marker Evidence

Metadata confirms analysis_development.bookroll_quizzes and analysis_development.bookroll_marker_texts exist and expose content/course links.