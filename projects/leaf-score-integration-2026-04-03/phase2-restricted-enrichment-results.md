# Score integration — phase 2 restricted enrichment results

Date: 2026-04-03

## Goal
Continue carefully after phase 1 by testing whether a highly conservative cross-system enrichment is currently possible without duplicate-driven inflation.

## Conservative rules used
- Read-only only.
- Avoid fallback joins that can duplicate rows.
- Do not use `course_students` fallback joins on `(student_id, course_id)` globally because phase 1 found duplicates there.
- For xAPI enrichment, only inspect the 13 course IDs that overlap between score-table `course_id` and `saikyo_new.context_id`.
- Treat any student-level xAPI alignment as empirical/candidate only unless the user confirms the identity bridge semantics.

## Overlapping score/xAPI courses
The 13 overlapping course IDs are:
- `280`, `446`, `472`, `590`, `593`, `603`, `605`, `606`, `614`, `616`, `617`, `619`, `629`

## Key findings

### 1) `course_students` coverage in the overlapping subset is very limited
Within these 13 overlapping courses:
- `course_students` rows were found only for course `280`
- no usable `course_students` coverage appeared for the other overlapping courses

Interpretation:
- the direct `course_student_id -> course_students.id` path is not enough for most of the score-bearing courses that overlap with `saikyo_new`
- fallback joining through `course_students` cannot rescue most of this subset right now

### 2) Course-level overlap with `saikyo_new` is real but sparse
For the 13 overlapping courses, score-side volume and xAPI-side volume are very uneven.
Examples:
- `629`: 1,394 score rows, 280 distinct score students, but only 21 xAPI rows and 2 actor prefixes
- `472`: 1,132 score rows, 285 distinct score students, but only 3 xAPI rows and 2 actor prefixes
- `605`: 638 score rows, 40 distinct score students, 14 xAPI rows and 4 actor prefixes
- `446`: 5 score rows, 5 distinct score students, but 7,895 xAPI rows and 46 actor prefixes

Interpretation:
- course-context overlap exists, but student-level coverage inside `saikyo_new` is usually tiny relative to the score table
- this already warns against aggressive student-level merging

### 3) Candidate student-ID overlap exists in some courses, but is sparse
Using exact matching between:
- score-table `student_id`
- xAPI actor prefix before `@` (or full actor when no `@`)
- same `course_id` / `context_id`

Observed intersections:
- `280`: 2 overlapping IDs out of 206 score students vs 2 xAPI prefixes
- `446`: 5 overlapping IDs out of 5 score students vs 46 xAPI prefixes
- `590`: 1 overlapping ID out of 40 vs 3 xAPI prefixes
- `605`: 4 overlapping IDs out of 40 vs 4 xAPI prefixes
- `606`: 1 overlapping ID out of 40 vs 1 xAPI prefix
- `614`: 2 overlapping IDs out of 40 vs 2 xAPI prefixes
- `616`: 1 overlapping ID out of 40 vs 1 xAPI prefix

But many courses showed zero overlap.

Interpretation:
- there is some evidence that score-table `student_id` can line up with xAPI actor prefixes in at least a subset of courses
- however, coverage is far too incomplete to support a broad student-level enrichment yet

### 4) Pre-test xAPI enrichment currently failed under a strict validity rule
I tested a very conservative linkage rule:
- same `course_id`
- exact `student_id` = xAPI actor prefix
- xAPI event date strictly **before** `date_at`

Result:
- score rows with non-null `date_at` in the candidate subset: `2,000`
- matched score rows with any **pre-test** xAPI activity: `0`

When checking looser student matches, the observed xAPI activity dates were generally **after** the score dates, not before them.

Interpretation:
- under a proper pre-test temporal rule, the current `saikyo_new` subset does **not** yet produce valid enriched student-level score records
- forcing a merge here would create misleading results

## Useful score-only results (safe and real)
Even without xAPI enrichment, the score table alone already yields meaningful research structure.

### Overall score-only coverage with valid date and score
Using rows with non-null `date_at` and non-null `quiz`:
- rows: `42,548`
- students: `1,722`
- courses: `216`
- distinct test names: `862`
- distinct course-test-date combinations: `900`
- date range: `2019-04-10` to `2025-03-05`
- average `quiz`: `63.06`
- min/max `quiz`: `0` / `100`

### Largest score-bearing courses
Top examples:
- `629` — `2024年度高校1年[英語]IECI`: 1,374 rows, 280 students, 5 tests, avg quiz 60.56
- `472` — `2023年度高校1年[英語]IEC1`: 1,102 rows, 283 students, 4 tests, avg quiz 62.67
- `521` — `2023年度高校1年[英語]EEC1`: 1,100 rows, 285 students, 4 tests, avg quiz 67.71
- `638` — `2024年度高校2年[英語]IECII`: 1,074 rows, 275 students, 4 tests, avg quiz 58.31
- `639` — `2024年度高校2年[英語]EECII`: 1,070 rows, 275 students, 4 tests, avg quiz 63.96
- `475` — `2023年度中学1年C組[数学]`: 800 rows, 40 students, 20 tests, avg quiz 68.85
- `473` — `2023年度中学1年A組[数学]`: 792 rows, 40 students, 20 tests, avg quiz 71.29
- `474` — `2023年度中学1年B組[数学]`: 790 rows, 40 students, 20 tests, avg quiz 67.56

### Repeated-test structure
Student-course pairs by number of score rows:
- 1 test: 1,462 pairs
- 2 tests: 4,866
- 4 tests: 1,682
- 8 tests: 767
- 20 tests: 116

Interpretation:
- repeated assessment structure is substantial
- this strongly supports longitudinal / within-student score analyses inside the score table itself, even before xAPI enrichment succeeds

## Practical conclusion

### What worked
- The score table itself is strong enough to support careful score-only research immediately.
- Course IDs align cleanly with Moodle course IDs.
- A small subset of score students appears to align empirically with xAPI actor prefixes in `saikyo_new`.

### What did not work yet
- A strict, validity-preserving **pre-test** student-level enrichment with `saikyo_new` produced `0` valid matched score rows.
- Therefore, I do **not** recommend claiming merged xAPI-score findings yet.

## Recommended next step
The safest productive next move is:
1. build a clean score-only longitudinal research layer first
2. produce within-course / within-student score trajectory summaries
3. separately diagnose why `saikyo_new` temporal coverage is mostly later than the score dates for overlapping IDs
4. only after that, revisit cross-system enrichment
