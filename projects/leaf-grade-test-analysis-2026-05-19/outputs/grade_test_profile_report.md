# Grade/Test Table Profile

## Scope And Cleaning Rule
- Source: analysis_development.course_student_scores.
- date_at is treated as the test conduct date.
- Rows with missing date_at are excluded from test-date-based analysis.
- Duplicate check grain: student_id + course_id + name + date_at.
- Clean analysis grain: one row per student_id/course_id/name/date_at.

## Raw Coverage
- total_rows: 67672
- missing_date_rows: 24492
- dated_rows: 43180
- students: 2497
- courses: 226
- test_names: 1070
- min_date: 2019-04-10
- max_date: 2025-03-05

## Duplicate Check
- duplicate groups at clean grain: 0
- duplicate extra rows removed at clean grain: 0

## Clean Dated Dataset
- clean dated score rows: 43,180
- distinct classified test names: 862
- score_validity_flag=valid: 42,548 rows
- score_validity_flag=missing_quiz: 632 rows

## By Test Family
- test_family=school_regular_exam: 28,258 clean rows, 1,468 students, 94 courses, 468 test names
- test_family=external_benesse: 8,261 clean rows, 959 students, 129 courses, 231 test names
- test_family=unit_or_chapter_test: 4,074 clean rows, 478 students, 18 courses, 102 test names
- test_family=unclear: 1,864 clean rows, 270 students, 40 courses, 42 test names
- test_family=break_after_test: 718 clean rows, 478 students, 18 courses, 18 test names
- test_family=generic_test: 5 clean rows, 5 students, 1 courses, 1 test names

## By Year
- test_year=2024: 19,551 clean rows, 1,200 students, 90 courses, 383 test names
- test_year=2023: 15,901 clean rows, 1,183 students, 89 courses, 293 test names
- test_year=2025: 3,041 clean rows, 924 students, 39 courses, 65 test names
- test_year=2021: 1,431 clean rows, 358 students, 18 courses, 36 test names
- test_year=2019: 1,292 clean rows, 359 students, 30 courses, 54 test names
- test_year=2020: 1,252 clean rows, 353 students, 18 courses, 33 test names
- test_year=2022: 712 clean rows, 356 students, 18 courses, 18 test names

## By Year And Test Family
- test_year=2024, test_family=school_regular_exam: 14,313 clean rows, 1,200 students, 70 courses, 246 test names
- test_year=2023, test_family=school_regular_exam: 10,909 clean rows, 1,183 students, 53 courses, 158 test names
- test_year=2025, test_family=school_regular_exam: 3,036 clean rows, 919 students, 38 courses, 64 test names
- test_year=2024, test_family=unit_or_chapter_test: 2,160 clean rows, 360 students, 15 courses, 54 test names
- test_year=2024, test_family=external_benesse: 2,143 clean rows, 359 students, 27 courses, 54 test names
- test_year=2023, test_family=unit_or_chapter_test: 1,914 clean rows, 358 students, 9 courses, 48 test names
- test_year=2021, test_family=external_benesse: 1,431 clean rows, 358 students, 18 courses, 36 test names
- test_year=2023, test_family=external_benesse: 1,431 clean rows, 239 students, 18 courses, 36 test names
- test_year=2019, test_family=external_benesse: 1,292 clean rows, 359 students, 30 courses, 54 test names
- test_year=2023, test_family=unclear: 1,289 clean rows, 269 students, 30 courses, 42 test names
- test_year=2020, test_family=external_benesse: 1,252 clean rows, 353 students, 18 courses, 33 test names
- test_year=2022, test_family=external_benesse: 712 clean rows, 356 students, 18 courses, 18 test names
- test_year=2024, test_family=unclear: 575 clean rows, 269 students, 11 courses, 20 test names
- test_year=2024, test_family=break_after_test: 360 clean rows, 360 students, 9 courses, 9 test names
- test_year=2023, test_family=break_after_test: 358 clean rows, 358 students, 9 courses, 9 test names
- test_year=2025, test_family=generic_test: 5 clean rows, 5 students, 1 courses, 1 test names

## By Grade Subject And Family
- grade_level=高1, course_subject=数学, test_family=school_regular_exam: 5,025 clean rows, 833 students, 15 courses, 114 test names
- grade_level=高2, course_subject=英語, test_family=school_regular_exam: 4,923 clean rows, 817 students, 6 courses, 18 test names
- grade_level=高1, course_subject=英語, test_family=school_regular_exam: 4,753 clean rows, 835 students, 6 courses, 17 test names
- grade_level=高2, course_subject=数学, test_family=school_regular_exam: 2,759 clean rows, 544 students, 11 courses, 82 test names
- grade_level=中1, course_subject=数学, test_family=school_regular_exam: 2,040 clean rows, 360 students, 9 courses, 51 test names
- grade_level=中2, course_subject=数学, test_family=school_regular_exam: 2,026 clean rows, 352 students, 9 courses, 51 test names
- grade_level=中3, course_subject=数学, test_family=school_regular_exam: 1,901 clean rows, 357 students, 9 courses, 48 test names
- grade_level=高2, course_subject=数学, test_family=unclear: 1,864 clean rows, 270 students, 40 courses, 42 test names
- grade_level=中1, course_subject=数学, test_family=unit_or_chapter_test: 1,800 clean rows, 240 students, 6 courses, 45 test names
- grade_level=高3, course_subject=英語, test_family=school_regular_exam: 1,614 clean rows, 269 students, 2 courses, 6 test names
- grade_level=中2, course_subject=数学, test_family=unit_or_chapter_test: 1,560 clean rows, 240 students, 6 courses, 39 test names
- grade_level=中1, course_subject=数学, test_family=external_benesse: 1,313 clean rows, 720 students, 21 courses, 39 test names
- grade_level=中2, course_subject=数学, test_family=external_benesse: 1,286 clean rows, 710 students, 21 courses, 39 test names
- grade_level=中2, course_subject=英語, test_family=external_benesse: 1,286 clean rows, 710 students, 21 courses, 39 test names
- grade_level=中1, course_subject=英語, test_family=school_regular_exam: 1,079 clean rows, 360 students, 9 courses, 27 test names
- grade_level=中1, course_subject=英語, test_family=external_benesse: 1,073 clean rows, 715 students, 21 courses, 30 test names
- grade_level=中2, course_subject=英語, test_family=school_regular_exam: 1,070 clean rows, 353 students, 9 courses, 27 test names
- grade_level=中3, course_subject=英語, test_family=school_regular_exam: 1,068 clean rows, 356 students, 9 courses, 27 test names
- grade_level=中3, course_subject=数学, test_family=external_benesse: 1,056 clean rows, 594 students, 15 courses, 27 test names
- grade_level=中3, course_subject=英語, test_family=external_benesse: 1,055 clean rows, 594 students, 15 courses, 27 test names
- grade_level=中3, course_subject=数学, test_family=unit_or_chapter_test: 714 clean rows, 238 students, 6 courses, 18 test names
- grade_level=中1, course_subject=国語, test_family=external_benesse: 479 clean rows, 240 students, 6 courses, 12 test names
- grade_level=中2, course_subject=国語, test_family=external_benesse: 474 clean rows, 238 students, 6 courses, 12 test names
- grade_level=中1, course_subject=数学, test_family=break_after_test: 240 clean rows, 240 students, 6 courses, 6 test names
- grade_level=中2, course_subject=数学, test_family=break_after_test: 240 clean rows, 240 students, 6 courses, 6 test names
- grade_level=中3, course_subject=国語, test_family=external_benesse: 239 clean rows, 120 students, 3 courses, 6 test names
- grade_level=中3, course_subject=数学, test_family=break_after_test: 238 clean rows, 238 students, 6 courses, 6 test names
- grade_level=(missing), course_subject=(missing), test_family=generic_test: 5 clean rows, 5 students, 1 courses, 1 test names

## Classification Confidence
- classification_confidence=high: 36,519 clean rows, 1,717 students, 175 courses, 699 test names
- classification_confidence=medium: 4,792 clean rows, 478 students, 18 courses, 120 test names
- classification_confidence=low: 1,869 clean rows, 275 students, 41 courses, 43 test names

## Top Test Names By Clean Row Count
- EEC1　後期中間: family=school_regular_exam, term=second_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=285, students=285, courses=1, years=2023
- EEC1　後期期末: family=school_regular_exam, term=second_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=285, students=285, courses=1, years=2024
- IEC1　後期中間: family=school_regular_exam, term=second_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=285, students=285, courses=1, years=2023
- IEC1　後期期末: family=school_regular_exam, term=second_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=285, students=285, courses=1, years=2024
- EEC1　前期期末: family=school_regular_exam, term=first_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=284, students=284, courses=1, years=2023
- IEC1　前期期末: family=school_regular_exam, term=first_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=284, students=284, courses=1, years=2023
- 2024年度 前期中間 EECI: family=school_regular_exam, term=first_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=280, students=280, courses=1, years=2024
- 2024年度 前期中間 IECI: family=school_regular_exam, term=first_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=280, students=280, courses=1, years=2024
- 2024年度 前期期末 IECI: family=school_regular_exam, term=first_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=280, students=280, courses=1, years=2024
- 2024年度 後期中間 EECI: family=school_regular_exam, term=second_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=280, students=280, courses=1, years=2024
- 2024年度 後期中間 IECI: family=school_regular_exam, term=second_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=280, students=280, courses=1, years=2024
- 2024年度 後期期末 IECI: family=school_regular_exam, term=second_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=280, students=280, courses=1, years=2025
- 2024年度 前期中間 EECII: family=school_regular_exam, term=first_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=279, students=279, courses=1, years=2024
- 2024年度 前期中間 IECII: family=school_regular_exam, term=first_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=279, students=279, courses=1, years=2024
- 2024年度 前期期末 EECII: family=school_regular_exam, term=first_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=279, students=279, courses=1, years=2024
- 2024年度 前期期末 IECII: family=school_regular_exam, term=first_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=279, students=279, courses=1, years=2024
- 2024年度 後期中間 EECII: family=school_regular_exam, term=second_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=279, students=279, courses=1, years=2024
- 2024年度 後期中間 IECII: family=school_regular_exam, term=second_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=279, students=279, courses=1, years=2024
- 2024年度 後期期末 EECII: family=school_regular_exam, term=second_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=279, students=279, courses=1, years=2025
- 2024年度 後期期末 IECII: family=school_regular_exam, term=second_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=279, students=279, courses=1, years=2025
- EEC1　前期中間: family=school_regular_exam, term=first_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=278, students=278, courses=1, years=2023
- IEC1　前期中間: family=school_regular_exam, term=first_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=278, students=278, courses=1, years=2023
- 2024年度 後期中間 IECI（問題投稿共有）: family=school_regular_exam, term=second_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=274, students=274, courses=1, years=2024
- EEC2　前期期末: family=school_regular_exam, term=first_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=272, students=272, courses=1, years=2023
- EEC2　後期中間: family=school_regular_exam, term=second_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=272, students=272, courses=1, years=2023
- EEC2　後期期末: family=school_regular_exam, term=second_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=272, students=272, courses=1, years=2024
- IEC2　前期期末: family=school_regular_exam, term=first_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=272, students=272, courses=1, years=2023
- IEC2　後期中間: family=school_regular_exam, term=second_term, timing=midterm, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=272, students=272, courses=1, years=2023
- IEC2　後期期末: family=school_regular_exam, term=second_term, timing=final, subject_hint=英語, component=unspecified_or_single_score, confidence=high, rows=272, students=272, courses=1, years=2024
- 高1　数A　後期期末　数学: family=school_regular_exam, term=second_term, timing=final, subject_hint=数学, component=unspecified_or_single_score, confidence=high, rows=270, students=270, courses=1, years=2023

## Initial Interpretation
- The dated grade/test table is large enough to start the outcome-side analysis after excluding missing date_at rows.
- Missing date_at rows should be kept out of test-window analysis unless a reliable date recovery rule is later provided.
- Test names are inconsistent and require a maintained classification layer; Benesse/mock exams should be separated from regular school exams.
- Low-confidence test-name classifications should not drive paper claims until reviewed or mapped manually.
