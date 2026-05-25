# XAPI Monthly Sufficiency Map

## Scope
- Local aggregate sufficiency pass using student-month BookRoll xAPI summaries.
- Link: score student_id to xAPI actor_account_name prefix before @.
- Windows are month-based approximations: 3, 6, and 12 months before the test month.
- This is not yet same-course linkage; it identifies feasible candidate subsets before deeper course/content mapping.

## XAPI Aggregate Extraction
- Relevant score students: 1,722
- Old monthly aggregate rows: 33,970; old events represented: 74,452,949
- New monthly aggregate rows: 4,935; new events represented: 4,116,001

## By Year
- test_year=2024: score_rows=19,551, students=1,200, courses=90, m3_rows=14,503 (74.2%), m6_rows=15,814 (80.9%), m12_rows=16,954 (86.7%), events_m3=129,791,060
- test_year=2023: score_rows=15,901, students=1,183, courses=89, m3_rows=12,523 (78.8%), m6_rows=13,728 (86.3%), m12_rows=15,027 (94.5%), events_m3=19,266,373
- test_year=2025: score_rows=3,041, students=924, courses=39, m3_rows=2,498 (82.1%), m6_rows=2,876 (94.6%), m12_rows=2,944 (96.8%), events_m3=21,612,327
- test_year=2020: score_rows=1,252, students=353, courses=18, m3_rows=1,232 (98.4%), m6_rows=1,232 (98.4%), m12_rows=1,232 (98.4%), events_m3=19,546,196
- test_year=2021: score_rows=1,431, students=358, courses=18, m3_rows=1,156 (80.8%), m6_rows=1,162 (81.2%), m12_rows=1,166 (81.5%), events_m3=9,676,470
- test_year=2019: score_rows=1,292, students=359, courses=30, m3_rows=682 (52.8%), m6_rows=682 (52.8%), m12_rows=682 (52.8%), events_m3=2,129,992
- test_year=2022: score_rows=712, students=356, courses=18, m3_rows=472 (66.3%), m6_rows=472 (66.3%), m12_rows=472 (66.3%), events_m3=1,348,478

## By Year And Test Family
- test_year=2024, test_family=school_regular_exam: score_rows=14,313, students=1,200, courses=70, m3_rows=10,129 (70.8%), m6_rows=11,305 (79.0%), m12_rows=12,288 (85.9%), events_m3=65,822,627
- test_year=2023, test_family=school_regular_exam: score_rows=10,909, students=1,183, courses=53, m3_rows=8,804 (80.7%), m6_rows=9,686 (88.8%), m12_rows=10,587 (97.0%), events_m3=11,094,412
- test_year=2025, test_family=school_regular_exam: score_rows=3,036, students=919, courses=38, m3_rows=2,493 (82.1%), m6_rows=2,871 (94.6%), m12_rows=2,939 (96.8%), events_m3=21,607,290
- test_year=2024, test_family=unit_or_chapter_test: score_rows=2,160, students=360, courses=15, m3_rows=2,160 (100.0%), m6_rows=2,160 (100.0%), m12_rows=2,160 (100.0%), events_m3=30,990,968
- test_year=2023, test_family=unit_or_chapter_test: score_rows=1,914, students=358, courses=9, m3_rows=1,909 (99.7%), m6_rows=1,911 (99.8%), m12_rows=1,914 (100.0%), events_m3=4,117,778
- test_year=2024, test_family=external_benesse: score_rows=2,143, students=359, courses=27, m3_rows=1,783 (83.2%), m6_rows=1,783 (83.2%), m12_rows=1,783 (83.2%), events_m3=21,837,909
- test_year=2020, test_family=external_benesse: score_rows=1,252, students=353, courses=18, m3_rows=1,232 (98.4%), m6_rows=1,232 (98.4%), m12_rows=1,232 (98.4%), events_m3=19,546,196
- test_year=2021, test_family=external_benesse: score_rows=1,431, students=358, courses=18, m3_rows=1,156 (80.8%), m6_rows=1,162 (81.2%), m12_rows=1,166 (81.5%), events_m3=9,676,470
- test_year=2023, test_family=external_benesse: score_rows=1,431, students=239, courses=18, m3_rows=1,071 (74.8%), m6_rows=1,071 (74.8%), m12_rows=1,071 (74.8%), events_m3=2,878,491
- test_year=2019, test_family=external_benesse: score_rows=1,292, students=359, courses=30, m3_rows=682 (52.8%), m6_rows=682 (52.8%), m12_rows=682 (52.8%), events_m3=2,129,992
- test_year=2022, test_family=external_benesse: score_rows=712, students=356, courses=18, m3_rows=472 (66.3%), m6_rows=472 (66.3%), m12_rows=472 (66.3%), events_m3=1,348,478
- test_year=2023, test_family=unclear: score_rows=1,289, students=269, courses=30, m3_rows=383 (29.7%), m6_rows=702 (54.5%), m12_rows=1,097 (85.1%), events_m3=54,396
- test_year=2024, test_family=break_after_test: score_rows=360, students=360, courses=9, m3_rows=360 (100.0%), m6_rows=360 (100.0%), m12_rows=360 (100.0%), events_m3=11,129,650
- test_year=2023, test_family=break_after_test: score_rows=358, students=358, courses=9, m3_rows=356 (99.4%), m6_rows=358 (100.0%), m12_rows=358 (100.0%), events_m3=1,121,296
- test_year=2024, test_family=unclear: score_rows=575, students=269, courses=11, m3_rows=71 (12.3%), m6_rows=206 (35.8%), m12_rows=363 (63.1%), events_m3=9,906
- test_year=2025, test_family=generic_test: score_rows=5, students=5, courses=1, m3_rows=5 (100.0%), m6_rows=5 (100.0%), m12_rows=5 (100.0%), events_m3=5,037

## By Grade Subject Family
- grade_level=高1, course_subject=数学, test_family=school_regular_exam: score_rows=5,025, students=833, courses=15, m3_rows=3,701 (73.7%), m6_rows=4,382 (87.2%), m12_rows=4,637 (92.3%), events_m3=3,892,939
- grade_level=高1, course_subject=英語, test_family=school_regular_exam: score_rows=4,753, students=835, courses=6, m3_rows=3,417 (71.9%), m6_rows=4,107 (86.4%), m12_rows=4,366 (91.9%), events_m3=3,300,675
- grade_level=高2, course_subject=英語, test_family=school_regular_exam: score_rows=4,923, students=817, courses=6, m3_rows=2,801 (56.9%), m6_rows=3,508 (71.3%), m12_rows=4,300 (87.4%), events_m3=2,349,843
- grade_level=高2, course_subject=数学, test_family=school_regular_exam: score_rows=2,759, students=544, courses=11, m3_rows=2,207 (80.0%), m6_rows=2,416 (87.6%), m12_rows=2,608 (94.5%), events_m3=2,162,275
- grade_level=中1, course_subject=数学, test_family=school_regular_exam: score_rows=2,040, students=360, courses=9, m3_rows=2,040 (100.0%), m6_rows=2,040 (100.0%), m12_rows=2,040 (100.0%), events_m3=40,989,798
- grade_level=中2, course_subject=数学, test_family=school_regular_exam: score_rows=2,026, students=352, courses=9, m3_rows=2,019 (99.7%), m6_rows=2,022 (99.8%), m12_rows=2,026 (100.0%), events_m3=7,224,699
- grade_level=中3, course_subject=数学, test_family=school_regular_exam: score_rows=1,901, students=357, courses=9, m3_rows=1,898 (99.8%), m6_rows=1,901 (100.0%), m12_rows=1,901 (100.0%), events_m3=9,427,317
- grade_level=中1, course_subject=数学, test_family=unit_or_chapter_test: score_rows=1,800, students=240, courses=6, m3_rows=1,800 (100.0%), m6_rows=1,800 (100.0%), m12_rows=1,800 (100.0%), events_m3=25,722,733
- grade_level=中2, course_subject=数学, test_family=unit_or_chapter_test: score_rows=1,560, students=240, courses=6, m3_rows=1,555 (99.7%), m6_rows=1,557 (99.8%), m12_rows=1,560 (100.0%), events_m3=4,094,444
- grade_level=中2, course_subject=数学, test_family=external_benesse: score_rows=1,286, students=710, courses=21, m3_rows=1,154 (89.7%), m6_rows=1,156 (89.9%), m12_rows=1,156 (89.9%), events_m3=8,573,813
- grade_level=中2, course_subject=英語, test_family=external_benesse: score_rows=1,286, students=710, courses=21, m3_rows=1,154 (89.7%), m6_rows=1,156 (89.9%), m12_rows=1,156 (89.9%), events_m3=8,573,813
- grade_level=中1, course_subject=英語, test_family=school_regular_exam: score_rows=1,079, students=360, courses=9, m3_rows=1,079 (100.0%), m6_rows=1,079 (100.0%), m12_rows=1,079 (100.0%), events_m3=20,320,730
- grade_level=中3, course_subject=英語, test_family=school_regular_exam: score_rows=1,068, students=356, courses=9, m3_rows=1,067 (99.9%), m6_rows=1,068 (100.0%), m12_rows=1,068 (100.0%), events_m3=4,963,458
- grade_level=中2, course_subject=英語, test_family=school_regular_exam: score_rows=1,070, students=353, courses=9, m3_rows=1,066 (99.6%), m6_rows=1,068 (99.8%), m12_rows=1,070 (100.0%), events_m3=3,865,511
- grade_level=中3, course_subject=数学, test_family=external_benesse: score_rows=1,056, students=594, courses=15, m3_rows=921 (87.2%), m6_rows=922 (87.3%), m12_rows=924 (87.5%), events_m3=5,469,642
- grade_level=中3, course_subject=英語, test_family=external_benesse: score_rows=1,055, students=594, courses=15, m3_rows=921 (87.3%), m6_rows=922 (87.4%), m12_rows=924 (87.6%), events_m3=5,469,642
- grade_level=中3, course_subject=数学, test_family=unit_or_chapter_test: score_rows=714, students=238, courses=6, m3_rows=714 (100.0%), m6_rows=714 (100.0%), m12_rows=714 (100.0%), events_m3=5,291,569
- grade_level=中1, course_subject=数学, test_family=external_benesse: score_rows=1,313, students=720, courses=21, m3_rows=707 (53.8%), m6_rows=707 (53.8%), m12_rows=707 (53.8%), events_m3=12,107,193
- grade_level=中1, course_subject=英語, test_family=external_benesse: score_rows=1,073, students=715, courses=21, m3_rows=587 (54.7%), m6_rows=587 (54.7%), m12_rows=587 (54.7%), events_m3=8,980,253
- grade_level=中2, course_subject=国語, test_family=external_benesse: score_rows=474, students=238, courses=6, m3_rows=474 (100.0%), m6_rows=474 (100.0%), m12_rows=474 (100.0%), events_m3=1,520,318
- grade_level=高2, course_subject=数学, test_family=unclear: score_rows=1,864, students=270, courses=40, m3_rows=454 (24.4%), m6_rows=908 (48.7%), m12_rows=1,460 (78.3%), events_m3=64,302
- grade_level=中1, course_subject=数学, test_family=break_after_test: score_rows=240, students=240, courses=6, m3_rows=240 (100.0%), m6_rows=240 (100.0%), m12_rows=240 (100.0%), events_m3=9,188,629
- grade_level=中1, course_subject=国語, test_family=external_benesse: score_rows=479, students=240, courses=6, m3_rows=239 (49.9%), m6_rows=239 (49.9%), m12_rows=239 (49.9%), events_m3=5,279,085
- grade_level=中2, course_subject=数学, test_family=break_after_test: score_rows=240, students=240, courses=6, m3_rows=239 (99.6%), m6_rows=240 (100.0%), m12_rows=240 (100.0%), events_m3=943,103
- grade_level=中3, course_subject=国語, test_family=external_benesse: score_rows=239, students=120, courses=3, m3_rows=239 (100.0%), m6_rows=239 (100.0%), m12_rows=239 (100.0%), events_m3=1,443,777
- grade_level=中3, course_subject=数学, test_family=break_after_test: score_rows=238, students=238, courses=6, m3_rows=237 (99.6%), m6_rows=238 (100.0%), m12_rows=238 (100.0%), events_m3=2,119,214
- grade_level=高3, course_subject=英語, test_family=school_regular_exam: score_rows=1,614, students=269, courses=2, m3_rows=131 (8.1%), m6_rows=271 (16.8%), m12_rows=719 (44.5%), events_m3=27,084
- grade_level=(missing), course_subject=(missing), test_family=generic_test: score_rows=5, students=5, courses=1, m3_rows=5 (100.0%), m6_rows=5 (100.0%), m12_rows=5 (100.0%), events_m3=5,037

## Initial Paper-Subset Rule
- Prefer cells with at least 200 score rows and at least 50% 3-month xAPI coverage for behavior-outcome modeling.
- If same-course linkage later reduces coverage sharply, downgrade those cells to descriptive-only.
