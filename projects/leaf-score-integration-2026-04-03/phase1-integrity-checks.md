# Score integration — phase 1 integrity checks

Date: 2026-04-03

## Purpose
Bounded read-only integrity checks for integrating `analysis_development.course_student_scores` into LEAF research.

## Confirmed table semantics from user
- `student_id` = student link key within the score table
- `quiz` = score column
- `name` = test name
- `course_name` = course name
- `course_id` = course identifier
- `date_at` = test date conducted

## Core results

### Score table coverage
- Total score rows: `67,672`
- Rows with non-null `course_student_id`: `24,492` (`36.19%`)
- Rows without `course_student_id`: `43,180` (`63.81%`)

### Direct join coverage
- Rows matching `course_students` through `course_student_id = course_students.id`: `24,492`
- This indicates the direct FK-style join works for all populated `course_student_id` rows, but only covers about 36% of the score table.

### Duplicate risk in fallback key
- Duplicate `(student_id, course_id)` pairs in `course_students`: `305`
- Therefore, fallback joining on `(student_id, course_id)` is not automatically safe without deduplication rules.

### Score-grain consistency
- Duplicate groups in `course_student_scores` by `(student_id, course_id, name, date_at)`: `0`
- This is a good sign for a student-test-date style grain.

### Course identity consistency inside score table
- `course_id` values mapping to multiple `course_name` values: `0`
- `course_name` values mapping to multiple `course_id` values: `0`
- Within the score table, course identity appears internally consistent.

## Cross-system overlap checks

### Analysis course IDs vs Moodle course IDs
- Distinct `course_id` values in score table: `226`
- Distinct Moodle `mdl_course.id` values checked: `644`
- Overlap: `226`
- Score-table `course_id` values not found in Moodle: `0`

Interpretation:
- This strongly suggests `analysis_development.course_student_scores.course_id` is on the same identifier system as Moodle `mdl_course.id`.
- Still worth treating as empirically supported rather than semantically proven until user confirms.

### Analysis course IDs vs `saikyo_new.statements_mv.context_id`
- Distinct score-table `course_id` values: `226`
- Distinct non-empty `context_id` values in `saikyo_new`: `118`
- Overlap: `13`
- Score-table `course_id` values absent from `saikyo_new.context_id`: `213`

Top overlapping score-bearing course IDs:
- `629` -> `1,394` score rows
- `472` -> `1,132`
- `593` -> `678`
- `606` -> `640`
- `605` -> `638`
- `617` -> `560`
- `619` -> `559`
- `280` -> `269`
- `603` -> `240`
- `614` -> `240`
- `616` -> `239`
- `590` -> `238`
- `446` -> `5`

Interpretation:
- Course-level linkage to `saikyo_new` is possible only for a narrow subset right now.
- The score table is broader than the current `saikyo_new` context coverage.

## Practical conclusion

### Safe now
- Build an Analysis-only score research layer using:
  - `student_id`
  - `course_id`
  - `course_name`
  - `name`
  - `date_at`
  - `quiz`
- Use direct joins through `course_student_id` where available.
- Treat the score table itself as internally coherent at the student-test-date grouping level.

### Not safe yet without more rules
- Broad fallback joining from scores to `course_students` on `(student_id, course_id)` without handling the `305` duplicate pairs in `course_students`
- Student-level xAPI merging without confirming how Analysis student identifiers bridge to Moodle / xAPI user identity

### Most defensible next step
1. Create a clean score dataset at score-table grain.
2. Profile the `305` duplicate `(student_id, course_id)` cases in `course_students`.
3. Restrict cross-system enrichment first to the `13` course IDs overlapping with `saikyo_new.context_id`.
4. Only then test pre-test xAPI feature construction around `date_at`.
