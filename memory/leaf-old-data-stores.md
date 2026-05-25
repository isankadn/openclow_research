# LEAF Old Data Stores

## Purpose
This file records the data-store separation for analyses that need data before the 2025 Japanese academic year boundary.

## Academic-year boundary and xAPI format change
- Japanese academic years run from April 1 through March 31 of the following year.
- From 2025-04-01, the ebook reader changed, and the xAPI format also changed.
- For analyses requiring data before 2025-04-01, use the OLD data stores rather than assuming compatibility with the post-2025 xAPI structure.
- For analyses covering 2025-04-01 through 2026-04-01, include the NEW relational data stores listed below, not only `saikyo_new` xAPI.
- Treat pre-2025 and post-2025 xAPI as separate source schemas that need harmonization before combined analysis.

## NEW relational data stores

These are the post-2025/current MySQL endpoints provided by the user on 2026-05-22 for the 2025-04-01 to 2026-04-01 window.

### NEW Bookroll data store
- Host: localhost
- Port: 30100
- Database: bookroll
- Access: MySQL

### NEW Analysis data store
- Host: localhost
- Port: 30101
- Database: analysis_development
- Access: MySQL

### NEW Moodle data store
- Host: localhost
- Port: 30102
- Database: moodle
- Access: MySQL

## OLD Analysis grade data store
- Host: 10.236.173.145
- Port: 33308
- Username: reader
- Password: reader@123
- Database: analysis_development
- Table: course_student_scores
- Access: read mode
- Notes:
  - The grade table name remains course_student_scores.
  - date_at represents the test conduct date.

## OLD Moodle data store
- Host: 10.236.173.145
- Port: 33307
- Username: reader
- Password: reader@123
- Database: moodle
- Access: read mode
- Notes:
  - Use Moodle course and category metadata to map course IDs to academic year, grade/level, subject, and course names.

## OLD BookRoll data store
- Host: 10.236.173.145
- Port: 33306
- Username: reader
- Password: reader@123
- Database: bookroll
- Access: read mode
- Notes:
  - User originally typed `bokroll`, but direct verification on 2026-05-19 showed the actual database name is `bookroll`.
  - `br_event_log` has old BookRoll event fields including `log_id`, `user_id`, `contents_id`, `contents_name`, `operation_date`, `operation_name`, `process_code`, `contextid`, `context_title`, `context_label`, and `role`.
  - Do not aggregate the full `br_event_log` context bridge in one SQL query. Stream/chunk by `log_id` and aggregate locally; the grade/test project keeps a streaming helper at `projects/leaf-grade-test-analysis-2026-05-19/33_stream_old_event_log_context_by_content.py`.
  - `br_contents` does not expose `deleted_at` in the relevant schema; omit that column from content metadata queries unless a future metadata check identifies a valid replacement.

## OLD Clickhouse xAPI data store
- Host: `10.236.173.4`
- Username: `reader`
- Password: `a9847KHJLv2vK`
- Data table: `saikyo_old.statements_mv`

## Analysis rule
- Before using pre-2025 data for the planned paper, first map old xAPI/event fields into a canonical event model.
- Keep raw source columns and canonical mapped columns separately.
- Record mapping confidence for operation names and fields.
- Confirm sufficient overlap among:
  - score rows in analysis_development.course_student_scores
  - Moodle course IDs
  - student/user IDs
  - pre-test old xAPI events
- Do not combine pre-2025 and post-2025 xAPI directly without schema harmonization.
- Detailed accepted working definitions for `saikyo_old.statements_mv` are stored in `memory/leaf-old-xapi-statements-mv.md`.
- Formal old-to-canonical mapping artifacts are stored in `projects/leaf-pre2025-xapi-harmonization/`.
