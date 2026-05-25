# 2025 Score-To-XAPI Sufficiency Check

## Scope
- Score/test window: test conduct dates in 2025 and 2026, currently 2025 only.
- XAPI window checked: 2024-04-01 through 2025-03-05, matching the school-year lead-up to the 2025 tests.
- XAPI source: saikyo_new.statements_mv.
- Course link: score course_id equals xAPI context_id.
- Student link tested: score student_id equals xAPI actor_account_name prefix before @.

## Overall
- Score courses in recent-test set: 39
- Courses with any matching xAPI: 0
- Courses with any score-student/xAPI-actor overlap: 0
- Courses meeting basic sequence-analysis threshold (>=1000 xAPI events and >=30 xAPI students): 0
- Courses meeting basic outcome-link threshold (>=30 overlapping students): 0
- Total xAPI events on matching courses: 0
- Total overlapping course-student links: 0

## By Grade And Subject
- 高1 数学: 7 courses, 560 score rows, 0 xAPI events, 0 xAPI course-student counts, 0 overlapping course-student links
- 高2 数学: 10 courses, 558 score rows, 0 xAPI events, 0 xAPI course-student counts, 0 overlapping course-student links
- 高2 英語: 2 courses, 558 score rows, 0 xAPI events, 0 xAPI course-student counts, 0 overlapping course-student links
- 高1 英語: 1 courses, 280 score rows, 0 xAPI events, 0 xAPI course-student counts, 0 overlapping course-student links
- 中1 数学: 3 courses, 240 score rows, 0 xAPI events, 0 xAPI course-student counts, 0 overlapping course-student links
- 中2 数学: 3 courses, 240 score rows, 0 xAPI events, 0 xAPI course-student counts, 0 overlapping course-student links
- 中3 数学: 3 courses, 240 score rows, 0 xAPI events, 0 xAPI course-student counts, 0 overlapping course-student links
- 中1 英語: 3 courses, 120 score rows, 0 xAPI events, 0 xAPI course-student counts, 0 overlapping course-student links
- 中2 英語: 3 courses, 120 score rows, 0 xAPI events, 0 xAPI course-student counts, 0 overlapping course-student links
- 中3 英語: 3 courses, 120 score rows, 0 xAPI events, 0 xAPI course-student counts, 0 overlapping course-student links
- (unclassified) (unclassified): 1 courses, 5 score rows, 0 xAPI events, 0 xAPI course-student counts, 0 overlapping course-student links

## Top XAPI-Covered Courses
- 446 緒方研究室デモコース: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 5 score rows, 1 tests
- 590 2024年度中学1年A組[英語]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 40 score rows, 1 tests
- 591 2024年度中学1年B組[英語]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 40 score rows, 1 tests
- 592 2024年度中学1年C組[英語]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 40 score rows, 1 tests
- 593 2024年度中学1年A組[数学]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 80 score rows, 2 tests
- 594 2024年度中学1年B組[数学]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 80 score rows, 2 tests
- 595 2024年度中学1年C組[数学]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 80 score rows, 2 tests
- 602 2024年度中学2年A組[英語]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 40 score rows, 1 tests
- 603 2024年度中学2年B組[英語]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 40 score rows, 1 tests
- 604 2024年度中学2年C組[英語]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 40 score rows, 1 tests
- 605 2024年度中学2年A組[数学]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 80 score rows, 2 tests
- 606 2024年度中学2年B組[数学]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 80 score rows, 2 tests
- 607 2024年度中学2年C組[数学]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 80 score rows, 2 tests
- 614 2024年度中学3年A組[英語]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 40 score rows, 1 tests
- 615 2024年度中学3年B組[英語]: 0 xAPI events, 0 xAPI students, 0 overlapping score students, 40 score rows, 1 tests

## Sufficiency Interpretation
- Outcome-linked modeling is not yet safe because confirmed student overlap is too small.
- Descriptive behavior mapping and sequence/pattern discovery are possible for xAPI-covered courses with enough events/students.
- Mixed-effects modeling across all K-12 courses is not justified unless many grade/subject cells show confirmed score-xAPI student overlap.
- The paper should report this as a deliberately scoped recent-course subset, not as full K-12 coverage.
