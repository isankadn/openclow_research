# Paper-Ready Outcome And Harmonized XAPI Diagnostics V2

## Analysis Matrix
- Grain: one row per student_id + course_id + test name + test date.
- Outcome: normalized quiz score from (quiz - min) / (max - min) in course_student_scores.
- xAPI features: old and new BookRoll events harmonized to student_id + course_id + event_month, then rolled up in pre-test windows.
- Privacy rule: row-level matrix remains local only; this report contains aggregate diagnostics.

## Overall Quality
- total clean score rows: 43,180
- rows with valid normalized score: 42,548 (98.5%)
- rows with any same-course xAPI in 3-month pre-test window: 23,124 (53.6%)
- rows with old-source same-course xAPI in 3-month window: 23,124 (53.6%)
- rows with new-source same-course xAPI in 3-month window: 0 (0.0%)

## Candidate Grade/Subject/Test Cells
- grade_level=高1, course_subject=数学, test_family=school_regular_exam: valid_scores=4,957/5,025, students=833, courses=15, m3_xapi=3,096 (61.6%), old_m3_rows=3,096, new_m3_rows=0, score_mean=0.566, score_median=0.570, flag=strong_candidate
- grade_level=中1, course_subject=数学, test_family=school_regular_exam: valid_scores=2,031/2,040, students=360, courses=9, m3_xapi=2,040 (100.0%), old_m3_rows=2,040, new_m3_rows=0, score_mean=0.645, score_median=0.660, flag=strong_candidate
- grade_level=中2, course_subject=数学, test_family=school_regular_exam: valid_scores=1,999/2,026, students=352, courses=9, m3_xapi=2,018 (99.6%), old_m3_rows=2,018, new_m3_rows=0, score_mean=0.625, score_median=0.630, flag=strong_candidate
- grade_level=高2, course_subject=数学, test_family=school_regular_exam: valid_scores=2,667/2,759, students=544, courses=11, m3_xapi=1,991 (72.2%), old_m3_rows=1,991, new_m3_rows=0, score_mean=0.565, score_median=0.580, flag=strong_candidate
- grade_level=中3, course_subject=数学, test_family=school_regular_exam: valid_scores=1,871/1,901, students=357, courses=9, m3_xapi=1,895 (99.7%), old_m3_rows=1,895, new_m3_rows=0, score_mean=0.604, score_median=0.620, flag=strong_candidate
- grade_level=中1, course_subject=数学, test_family=unit_or_chapter_test: valid_scores=1,783/1,800, students=240, courses=6, m3_xapi=1,800 (100.0%), old_m3_rows=1,800, new_m3_rows=0, score_mean=0.676, score_median=0.680, flag=strong_candidate
- grade_level=中2, course_subject=数学, test_family=unit_or_chapter_test: valid_scores=1,528/1,560, students=240, courses=6, m3_xapi=1,550 (99.4%), old_m3_rows=1,550, new_m3_rows=0, score_mean=0.656, score_median=0.660, flag=strong_candidate
- grade_level=中2, course_subject=英語, test_family=school_regular_exam: valid_scores=1,057/1,070, students=353, courses=9, m3_xapi=853 (79.7%), old_m3_rows=853, new_m3_rows=0, score_mean=0.661, score_median=0.680, flag=strong_candidate
- grade_level=中1, course_subject=英語, test_family=school_regular_exam: valid_scores=1,074/1,079, students=360, courses=9, m3_xapi=776 (71.9%), old_m3_rows=776, new_m3_rows=0, score_mean=0.663, score_median=0.680, flag=strong_candidate
- grade_level=中2, course_subject=数学, test_family=external_benesse: valid_scores=1,275/1,286, students=710, courses=21, m3_xapi=709 (55.1%), old_m3_rows=709, new_m3_rows=0, score_mean=0.706, score_median=0.710, flag=strong_candidate
- grade_level=中1, course_subject=数学, test_family=external_benesse: valid_scores=1,312/1,313, students=720, courses=21, m3_xapi=707 (53.8%), old_m3_rows=707, new_m3_rows=0, score_mean=0.718, score_median=0.730, flag=strong_candidate
- grade_level=中3, course_subject=数学, test_family=unit_or_chapter_test: valid_scores=694/714, students=238, courses=6, m3_xapi=707 (99.0%), old_m3_rows=707, new_m3_rows=0, score_mean=0.624, score_median=0.630, flag=strong_candidate
- grade_level=中2, course_subject=英語, test_family=external_benesse: valid_scores=1,276/1,286, students=710, courses=21, m3_xapi=659 (51.2%), old_m3_rows=659, new_m3_rows=0, score_mean=0.745, score_median=0.760, flag=strong_candidate
- grade_level=中3, course_subject=数学, test_family=external_benesse: valid_scores=1,049/1,056, students=594, courses=15, m3_xapi=598 (56.6%), old_m3_rows=598, new_m3_rows=0, score_mean=0.715, score_median=0.730, flag=strong_candidate
- grade_level=中3, course_subject=英語, test_family=school_regular_exam: valid_scores=1,058/1,068, students=356, courses=9, m3_xapi=594 (55.6%), old_m3_rows=594, new_m3_rows=0, score_mean=0.611, score_median=0.620, flag=strong_candidate
- grade_level=中1, course_subject=英語, test_family=external_benesse: valid_scores=1,072/1,073, students=715, courses=21, m3_xapi=555 (51.7%), old_m3_rows=555, new_m3_rows=0, score_mean=0.736, score_median=0.740, flag=strong_candidate
- grade_level=中1, course_subject=数学, test_family=break_after_test: valid_scores=237/240, students=240, courses=6, m3_xapi=240 (100.0%), old_m3_rows=240, new_m3_rows=0, score_mean=0.700, score_median=0.710, flag=strong_candidate
- grade_level=中2, course_subject=数学, test_family=break_after_test: valid_scores=236/240, students=240, courses=6, m3_xapi=239 (99.6%), old_m3_rows=239, new_m3_rows=0, score_mean=0.685, score_median=0.700, flag=strong_candidate
- grade_level=中3, course_subject=数学, test_family=break_after_test: valid_scores=233/238, students=238, courses=6, m3_xapi=236 (99.2%), old_m3_rows=236, new_m3_rows=0, score_mean=0.717, score_median=0.750, flag=strong_candidate

## Year/Test Family Outcome Coverage
- test_year=2024, test_family=school_regular_exam: valid_scores=14,005/14,313, students=1,200, courses=70, m3_xapi=6,614 (46.2%), old_m3_rows=6,614, new_m3_rows=0, score_mean=0.603, score_median=0.610, flag=limited_xapi_coverage
- test_year=2023, test_family=school_regular_exam: valid_scores=10,809/10,909, students=1,183, courses=53, m3_xapi=5,698 (52.2%), old_m3_rows=5,698, new_m3_rows=0, score_mean=0.618, score_median=0.630, flag=strong_candidate
- test_year=2024, test_family=unit_or_chapter_test: valid_scores=2,128/2,160, students=360, courses=15, m3_xapi=2,158 (99.9%), old_m3_rows=2,158, new_m3_rows=0, score_mean=0.651, score_median=0.660, flag=strong_candidate
- test_year=2023, test_family=unit_or_chapter_test: valid_scores=1,877/1,914, students=358, courses=9, m3_xapi=1,899 (99.2%), old_m3_rows=1,899, new_m3_rows=0, score_mean=0.669, score_median=0.680, flag=strong_candidate
- test_year=2025, test_family=school_regular_exam: valid_scores=2,941/3,036, students=919, courses=38, m3_xapi=1,860 (61.3%), old_m3_rows=1,860, new_m3_rows=0, score_mean=0.557, score_median=0.560, flag=strong_candidate
- test_year=2020, test_family=external_benesse: valid_scores=1,252/1,252, students=353, courses=18, m3_xapi=1,143 (91.3%), old_m3_rows=1,143, new_m3_rows=0, score_mean=0.720, score_median=0.725, flag=strong_candidate
- test_year=2024, test_family=external_benesse: valid_scores=2,143/2,143, students=359, courses=27, m3_xapi=875 (40.8%), old_m3_rows=875, new_m3_rows=0, score_mean=0.736, score_median=0.740, flag=limited_xapi_coverage
- test_year=2019, test_family=external_benesse: valid_scores=1,292/1,292, students=359, courses=30, m3_xapi=673 (52.1%), old_m3_rows=673, new_m3_rows=0, score_mean=0.746, score_median=0.760, flag=strong_candidate
- test_year=2021, test_family=external_benesse: valid_scores=1,397/1,431, students=358, courses=18, m3_xapi=661 (46.2%), old_m3_rows=661, new_m3_rows=0, score_mean=0.734, score_median=0.740, flag=limited_xapi_coverage
- test_year=2023, test_family=external_benesse: valid_scores=1,431/1,431, students=239, courses=18, m3_xapi=570 (39.8%), old_m3_rows=570, new_m3_rows=0, score_mean=0.732, score_median=0.750, flag=limited_xapi_coverage
- test_year=2024, test_family=break_after_test: valid_scores=354/360, students=360, courses=9, m3_xapi=360 (100.0%), old_m3_rows=360, new_m3_rows=0, score_mean=0.681, score_median=0.670, flag=strong_candidate
- test_year=2023, test_family=break_after_test: valid_scores=352/358, students=358, courses=9, m3_xapi=355 (99.2%), old_m3_rows=355, new_m3_rows=0, score_mean=0.721, score_median=0.740, flag=strong_candidate
- test_year=2023, test_family=unclear: valid_scores=1,286/1,289, students=269, courses=30, m3_xapi=223 (17.3%), old_m3_rows=223, new_m3_rows=0, score_mean=0.508, score_median=0.520, flag=limited_xapi_coverage
- test_year=2024, test_family=unclear: valid_scores=568/575, students=269, courses=11, m3_xapi=30 (5.2%), old_m3_rows=30, new_m3_rows=0, score_mean=0.517, score_median=0.530, flag=insufficient
- test_year=2025, test_family=generic_test: valid_scores=5/5, students=5, courses=1, m3_xapi=5 (100.0%), old_m3_rows=5, new_m3_rows=0, score_mean=0.520, score_median=0.600, flag=insufficient
- test_year=2022, test_family=external_benesse: valid_scores=708/712, students=356, courses=18, m3_xapi=0 (0.0%), old_m3_rows=0, new_m3_rows=0, score_mean=0.728, score_median=0.740, flag=insufficient

## Year Grade/Subject/Test Cells
- test_year=2023, grade_level=高1, course_subject=数学, test_family=school_regular_exam: valid_scores=2,202/2,219, students=552, courses=8, m3_xapi=1,695 (76.4%), old_m3_rows=1,695, new_m3_rows=0, score_mean=0.577, score_median=0.580, flag=strong_candidate
- test_year=2024, grade_level=高2, course_subject=数学, test_family=school_regular_exam: valid_scores=1,615/1,674, students=279, courses=10, m3_xapi=1,238 (74.0%), old_m3_rows=1,238, new_m3_rows=0, score_mean=0.561, score_median=0.570, flag=strong_candidate
- test_year=2024, grade_level=高1, course_subject=数学, test_family=school_regular_exam: valid_scores=2,204/2,246, students=563, courses=14, m3_xapi=1,059 (47.1%), old_m3_rows=1,059, new_m3_rows=0, score_mean=0.568, score_median=0.570, flag=limited_xapi_coverage
- test_year=2024, grade_level=中1, course_subject=数学, test_family=school_regular_exam: valid_scores=958/960, students=240, courses=6, m3_xapi=960 (100.0%), old_m3_rows=960, new_m3_rows=0, score_mean=0.646, score_median=0.660, flag=strong_candidate
- test_year=2024, grade_level=中1, course_subject=数学, test_family=unit_or_chapter_test: valid_scores=950/960, students=240, courses=6, m3_xapi=960 (100.0%), old_m3_rows=960, new_m3_rows=0, score_mean=0.636, score_median=0.645, flag=strong_candidate
- test_year=2024, grade_level=中2, course_subject=数学, test_family=school_regular_exam: valid_scores=944/960, students=240, courses=6, m3_xapi=960 (100.0%), old_m3_rows=960, new_m3_rows=0, score_mean=0.627, score_median=0.630, flag=strong_candidate
- test_year=2024, grade_level=中3, course_subject=数学, test_family=school_regular_exam: valid_scores=941/958, students=239, courses=6, m3_xapi=956 (99.8%), old_m3_rows=956, new_m3_rows=0, score_mean=0.599, score_median=0.600, flag=strong_candidate
- test_year=2023, grade_level=中1, course_subject=数学, test_family=school_regular_exam: valid_scores=835/840, students=240, courses=6, m3_xapi=840 (100.0%), old_m3_rows=840, new_m3_rows=0, score_mean=0.660, score_median=0.680, flag=strong_candidate
- test_year=2023, grade_level=中1, course_subject=数学, test_family=unit_or_chapter_test: valid_scores=833/840, students=120, courses=3, m3_xapi=840 (100.0%), old_m3_rows=840, new_m3_rows=0, score_mean=0.721, score_median=0.730, flag=strong_candidate
- test_year=2024, grade_level=中2, course_subject=数学, test_family=unit_or_chapter_test: valid_scores=821/840, students=240, courses=6, m3_xapi=838 (99.8%), old_m3_rows=838, new_m3_rows=0, score_mean=0.669, score_median=0.680, flag=strong_candidate
- test_year=2023, grade_level=中2, course_subject=数学, test_family=school_regular_exam: valid_scores=820/826, students=232, courses=6, m3_xapi=820 (99.3%), old_m3_rows=820, new_m3_rows=0, score_mean=0.629, score_median=0.630, flag=strong_candidate
- test_year=2023, grade_level=中2, course_subject=数学, test_family=unit_or_chapter_test: valid_scores=707/720, students=120, courses=3, m3_xapi=712 (98.9%), old_m3_rows=712, new_m3_rows=0, score_mean=0.642, score_median=0.650, flag=strong_candidate
- test_year=2023, grade_level=中3, course_subject=数学, test_family=school_regular_exam: valid_scores=696/703, students=236, courses=6, m3_xapi=699 (99.4%), old_m3_rows=699, new_m3_rows=0, score_mean=0.655, score_median=0.680, flag=strong_candidate
- test_year=2024, grade_level=高1, course_subject=英語, test_family=school_regular_exam: valid_scores=2,198/2,244, students=565, courses=4, m3_xapi=439 (19.6%), old_m3_rows=439, new_m3_rows=0, score_mean=0.610, score_median=0.620, flag=limited_xapi_coverage
- test_year=2024, grade_level=中2, course_subject=英語, test_family=school_regular_exam: valid_scores=471/480, students=240, courses=6, m3_xapi=428 (89.2%), old_m3_rows=428, new_m3_rows=0, score_mean=0.696, score_median=0.720, flag=strong_candidate
- test_year=2025, grade_level=高2, course_subject=数学, test_family=school_regular_exam: valid_scores=525/558, students=279, courses=10, m3_xapi=409 (73.3%), old_m3_rows=409, new_m3_rows=0, score_mean=0.487, score_median=0.480, flag=strong_candidate
- test_year=2024, grade_level=中3, course_subject=数学, test_family=unit_or_chapter_test: valid_scores=357/360, students=120, courses=3, m3_xapi=360 (100.0%), old_m3_rows=360, new_m3_rows=0, score_mean=0.651, score_median=0.650, flag=strong_candidate
- test_year=2023, grade_level=中3, course_subject=数学, test_family=unit_or_chapter_test: valid_scores=337/354, students=118, courses=3, m3_xapi=347 (98.0%), old_m3_rows=347, new_m3_rows=0, score_mean=0.595, score_median=0.610, flag=strong_candidate
- test_year=2023, grade_level=高2, course_subject=数学, test_family=school_regular_exam: valid_scores=527/527, students=265, courses=1, m3_xapi=344 (65.3%), old_m3_rows=344, new_m3_rows=0, score_mean=0.653, score_median=0.680, flag=strong_candidate
- test_year=2025, grade_level=高1, course_subject=数学, test_family=school_regular_exam: valid_scores=551/560, students=280, courses=7, m3_xapi=342 (61.1%), old_m3_rows=342, new_m3_rows=0, score_mean=0.512, score_median=0.510, flag=strong_candidate
- test_year=2024, grade_level=中1, course_subject=英語, test_family=school_regular_exam: valid_scores=478/480, students=240, courses=6, m3_xapi=333 (69.4%), old_m3_rows=333, new_m3_rows=0, score_mean=0.664, score_median=0.670, flag=strong_candidate
- test_year=2023, grade_level=中1, course_subject=英語, test_family=school_regular_exam: valid_scores=477/479, students=240, courses=6, m3_xapi=327 (68.3%), old_m3_rows=327, new_m3_rows=0, score_mean=0.673, score_median=0.690, flag=strong_candidate
- test_year=2023, grade_level=中2, course_subject=英語, test_family=school_regular_exam: valid_scores=467/470, students=233, courses=6, m3_xapi=307 (65.3%), old_m3_rows=307, new_m3_rows=0, score_mean=0.643, score_median=0.660, flag=strong_candidate
- test_year=2023, grade_level=中3, course_subject=英語, test_family=school_regular_exam: valid_scores=465/469, students=235, courses=6, m3_xapi=254 (54.2%), old_m3_rows=254, new_m3_rows=0, score_mean=0.638, score_median=0.650, flag=strong_candidate
- test_year=2025, grade_level=中1, course_subject=数学, test_family=school_regular_exam: valid_scores=238/240, students=120, courses=3, m3_xapi=240 (100.0%), old_m3_rows=240, new_m3_rows=0, score_mean=0.586, score_median=0.570, flag=strong_candidate

## Interpretation
- The combined matrix is suitable for selecting defensible analysis cells, not yet for making causal claims.
- Strong candidate cells require at least 100 valid outcomes, at least 100 students, at least 100 pre-test same-course xAPI-linked rows, and at least 50% 3-month same-course xAPI coverage.
- Strong candidate cells should be modeled with fixed effects for test family/grade/subject and random or clustered effects for student/course where feasible.
- Old-source same-course linkage now uses direct context_id after the saikyo_old reimport; sensitivity checks should focus on alternate xAPI windows and the small residual set with missing context_id.
- Because scaled is zero in the source table, normalized quiz score should be the primary numeric outcome unless the score table semantics are revised.
