# Paper-Ready Result Set v1

## What This Result Set Supports Now
- Clean outcome-side analysis from dated grade/test data.
- A defensible test-name taxonomy separating regular school exams, Benesse/mock tests, unit/chapter tests, after-break tests, and unclear names.
- Student-level pre-test BookRoll behavior sufficiency across old and new xAPI stores using local aggregate features.
- Candidate grade/subject/test-family cells for deeper behavior-outcome modeling.

## What It Does Not Yet Support
- Historical note: this v1 report predates the old `saikyo_old.statements_mv` context reimport. Use the direct-context rerun outputs for current same-course behavior-outcome claims.
- Post-2025 new-xAPI outcome modeling, because the current grade/test table has no `date_at` rows after 2025-03-05.
- Strong claims from low-confidence test-name classifications.

## Outcome Data Quality
- Raw score rows: 67,672.
- Missing test conduct date (`date_at`) excluded: 24,492 rows.
- Clean dated score rows retained: 43,180.
- Duplicate groups at clean grain `(student_id, course_id, name, date_at)`: 0.
- Dated range: 2019-04-10 to 2025-03-05.

## Test Taxonomy
- school_regular_exam: 28,258 clean rows, 1468 students, 94 courses, 468 test names
- external_benesse: 8,261 clean rows, 959 students, 129 courses, 231 test names
- unit_or_chapter_test: 4,074 clean rows, 478 students, 18 courses, 102 test names
- unclear: 1,864 clean rows, 270 students, 40 courses, 42 test names
- break_after_test: 718 clean rows, 478 students, 18 courses, 18 test names
- generic_test: 5 clean rows, 5 students, 1 courses, 1 test names

## Classification Confidence
- high: 36,519 clean rows, 1717 students, 175 courses, 699 test names
- medium: 4,792 clean rows, 478 students, 18 courses, 120 test names
- low: 1,869 clean rows, 275 students, 41 courses, 43 test names

## XAPI Sufficiency By Year/Test Family
- 2024 school_regular_exam: 14,313 score rows, 1200 students, 70 courses, 3-month xAPI coverage 70.8%, 6-month 79.0%, 12-month 85.9%
- 2023 school_regular_exam: 10,909 score rows, 1183 students, 53 courses, 3-month xAPI coverage 80.7%, 6-month 88.8%, 12-month 97.0%
- 2025 school_regular_exam: 3,036 score rows, 919 students, 38 courses, 3-month xAPI coverage 82.1%, 6-month 94.6%, 12-month 96.8%
- 2024 unit_or_chapter_test: 2,160 score rows, 360 students, 15 courses, 3-month xAPI coverage 100.0%, 6-month 100.0%, 12-month 100.0%
- 2023 unit_or_chapter_test: 1,914 score rows, 358 students, 9 courses, 3-month xAPI coverage 99.7%, 6-month 99.8%, 12-month 100.0%
- 2024 external_benesse: 2,143 score rows, 359 students, 27 courses, 3-month xAPI coverage 83.2%, 6-month 83.2%, 12-month 83.2%
- 2020 external_benesse: 1,252 score rows, 353 students, 18 courses, 3-month xAPI coverage 98.4%, 6-month 98.4%, 12-month 98.4%
- 2021 external_benesse: 1,431 score rows, 358 students, 18 courses, 3-month xAPI coverage 80.8%, 6-month 81.2%, 12-month 81.5%
- 2023 external_benesse: 1,431 score rows, 239 students, 18 courses, 3-month xAPI coverage 74.8%, 6-month 74.8%, 12-month 74.8%
- 2019 external_benesse: 1,292 score rows, 359 students, 30 courses, 3-month xAPI coverage 52.8%, 6-month 52.8%, 12-month 52.8%
- 2022 external_benesse: 712 score rows, 356 students, 18 courses, 3-month xAPI coverage 66.3%, 6-month 66.3%, 12-month 66.3%
- 2023 unclear: 1,289 score rows, 269 students, 30 courses, 3-month xAPI coverage 29.7%, 6-month 54.5%, 12-month 85.1%
- 2024 break_after_test: 360 score rows, 360 students, 9 courses, 3-month xAPI coverage 100.0%, 6-month 100.0%, 12-month 100.0%
- 2023 break_after_test: 358 score rows, 358 students, 9 courses, 3-month xAPI coverage 99.4%, 6-month 100.0%, 12-month 100.0%
- 2024 unclear: 575 score rows, 269 students, 11 courses, 3-month xAPI coverage 12.3%, 6-month 35.8%, 12-month 63.1%
- 2025 generic_test: 5 score rows, 5 students, 1 courses, 3-month xAPI coverage 100.0%, 6-month 100.0%, 12-month 100.0%

## Strongest Student-Level Behavior-Outcome Candidate Cells
- 高1 数学 school_regular_exam: 5,025 score rows, 833 students, 15 courses, 3-month xAPI coverage 73.7%. Status: needs_same_course_linkage_check.
- 高1 英語 school_regular_exam: 4,753 score rows, 835 students, 6 courses, 3-month xAPI coverage 71.9%. Status: needs_same_course_linkage_check.
- 高2 数学 school_regular_exam: 2,759 score rows, 544 students, 11 courses, 3-month xAPI coverage 80.0%. Status: needs_same_course_linkage_check.
- 中1 数学 school_regular_exam: 2,040 score rows, 360 students, 9 courses, 3-month xAPI coverage 100.0%. Status: needs_same_course_linkage_check.
- 中2 数学 school_regular_exam: 2,026 score rows, 352 students, 9 courses, 3-month xAPI coverage 99.7%. Status: needs_same_course_linkage_check.
- 中3 数学 school_regular_exam: 1,901 score rows, 357 students, 9 courses, 3-month xAPI coverage 99.8%. Status: needs_same_course_linkage_check.
- 中1 数学 unit_or_chapter_test: 1,800 score rows, 240 students, 6 courses, 3-month xAPI coverage 100.0%. Status: needs_same_course_linkage_check.
- 中2 数学 unit_or_chapter_test: 1,560 score rows, 240 students, 6 courses, 3-month xAPI coverage 99.7%. Status: needs_same_course_linkage_check.
- 中2 数学 external_benesse: 1,286 score rows, 710 students, 21 courses, 3-month xAPI coverage 89.7%. Status: needs_same_course_linkage_check.
- 中2 英語 external_benesse: 1,286 score rows, 710 students, 21 courses, 3-month xAPI coverage 89.7%. Status: needs_same_course_linkage_check.
- 中1 英語 school_regular_exam: 1,079 score rows, 360 students, 9 courses, 3-month xAPI coverage 100.0%. Status: needs_same_course_linkage_check.
- 中3 英語 school_regular_exam: 1,068 score rows, 356 students, 9 courses, 3-month xAPI coverage 99.9%. Status: needs_same_course_linkage_check.
- 中2 英語 school_regular_exam: 1,070 score rows, 353 students, 9 courses, 3-month xAPI coverage 99.6%. Status: needs_same_course_linkage_check.
- 中3 数学 external_benesse: 1,056 score rows, 594 students, 15 courses, 3-month xAPI coverage 87.2%. Status: needs_same_course_linkage_check.
- 中3 英語 external_benesse: 1,055 score rows, 594 students, 15 courses, 3-month xAPI coverage 87.3%. Status: needs_same_course_linkage_check.
- 中3 数学 unit_or_chapter_test: 714 score rows, 238 students, 6 courses, 3-month xAPI coverage 100.0%. Status: needs_same_course_linkage_check.

## Recommended Paper Strategy
1. Use the grade/test layer as the outcome backbone.
2. Keep Benesse/external tests separate from regular school exams; do not pool them.
3. For the first behavior-outcome paper, prioritize high-confidence regular-exam and unit/chapter-test cells with high 3-month xAPI coverage.
4. Treat current xAPI sufficiency as student-level until same-course mapping is solved for old BookRoll.
5. For same-course claims, next resolve old BookRoll content/course linkage via relational metadata, not `saikyo_old.context_id` alone.

## Best Current Claim
The current data is strong enough to support a paper-ready outcome taxonomy and to identify high-coverage student-level pre-test BookRoll behavior windows. The next methodological gate is course/content linkage for old BookRoll events, which determines whether the final model should be student-level behavior prediction or same-course behavior prediction.
