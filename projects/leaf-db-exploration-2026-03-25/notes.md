# LEAF DB exploration notes — 2026-03-25

## Scope
Slow first-pass reconnaissance of the available LEAF databases using bounded read-only queries.

## Infrastructure reached
- Analysis MySQL reachable at `10.236.173.145:33308`
- BookRoll MySQL reachable at `10.236.173.145:33306`
- Moodle MySQL reachable at `10.236.173.145:33307`
- ClickHouse reachable at `10.236.173.4:8123` and `10.236.173.4:9000`

## Early findings

### Analysis database (`analysis_development`)
- `course_student_scores` exists and currently has `67,672` rows.
- `course_students` exists and currently has `27,558` rows.
- `courses` exists.
- `contents` exists.

#### `course_student_scores` schema highlights
- key columns seen: `id`, `course_student_id`, `quiz`, `user_id`, `student_id`, `course_id`, `scaled`, `name`, `course_name`, `date_at`, `consumer_key`
- null check:
  - `course_student_id`: `43,180` nulls
  - `quiz`: `632` nulls
  - `student_id`, `user_id`, `course_id`, `name`, `scaled`: no nulls in quick check

#### `course_students` schema highlights
- key columns seen: `id`, `course_id`, `student_id`, `username`, `firstname`, `lastname`, `fullname`, `email`, `uuid`, `user_id`
- quick profile:
  - `27,558` rows
  - `2,868` distinct `student_id`
  - `294` distinct `course_id`
  - `82` distinct `user_id`

#### Join observation
- `course_student_scores.course_student_id` can join to `course_students.id` when populated.
- But many `course_student_scores.course_student_id` values are null, so this join is only partially available.
- `course_student_scores.user_id` has very low cardinality (`8` distinct values in the first profile), so it likely is **not** the student identity field.

### Moodle database
- User table name is `mdl_user` (not plain `user`).

### BookRoll database (`bookroll`)
Large tables visible even from a quick scan:
- `br_event_log` ~ `43,153,170` rows
- `br_draw_object` ~ `3,060,948` rows
- `br_bookmark` ~ `51,030` rows
- `br_annotation` ~ `41,706` rows
- `br_direct_memo` ~ `29,112` rows
- `br_contents` ~ `17,570` rows

This suggests substantial raw behavioral activity is present in BookRoll-side storage.

### ClickHouse xAPI structure
- There are many per-school/per-instance databases.
- Most databases have either 3 or 4 tables.
- Example (`leaf02`):
  - `statements`
  - `statements_mv`
  - `statements_target`

#### Sample `leaf02.statements_mv` profile
- rows: `6,723,904`
- time range: `1970-01-01` to `2026-03-23`
- unique `actor_account_name`: `1,657`
- unique `contents_id`: `3,782`
- unique `operation_name`: `160`

#### Sample event rows from `leaf02`
- examples include `NEXT`, `PREV`, and `LOGIN`
- `actor_account_name` may be a numeric-looking user identifier (for example `3147`) but may also vary by instance/user type (for example `admin`)

## Important caution
The user indicated that in BookRoll-related xAPI, `actor_account_name` often looks like:
- `<moodle_user_id>@<tenant_or_uuid>`

This means:
- the prefix before `@` should be treated as a likely cross-source join key to Moodle `user.id`
- but real values may vary across instances, so parsing logic should be validated per database before large-scale joining

## Good next steps
1. Profile one chosen school/instance in ClickHouse more carefully:
   - row counts by `operation_name`
   - date coverage
   - how often `actor_account_name` contains `@`
   - whether `contents_id`, `context_id`, and `actor_account_name` are well populated
2. Map the Analysis-side joins more carefully:
   - `course_student_scores` -> `course_students`
   - `course_students.course_id` -> `courses.id` or external course key
   - identify what `user_id` represents in each table
3. Inspect Moodle tables needed for joins:
   - `mdl_user`
   - likely course / enrolment tables
4. Build a tiny data dictionary for the first usable research slice.
