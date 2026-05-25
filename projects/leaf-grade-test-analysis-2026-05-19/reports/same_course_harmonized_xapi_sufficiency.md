# Same-Course Harmonized XAPI Sufficiency

## Scope
- Old xAPI course mapping: direct non-empty context_id after the saikyo_old.statements_mv reimport.
- New xAPI course mapping: direct non-empty context_id.
- Old and new features are combined after mapping into the same student_id + course_id + event_month feature grain.
- Combined analysis rows retain source-schema counts old_events_* and new_events_* so old/new contribution can be audited.
- The old content-directory bridge is no longer used as the primary same-course mapping source.
- This pass keeps non-empty contents_id to preserve the previous content-learning event universe, but uses context_id for course linkage.

## Extraction And Mapping Coverage
- Old Bookroll content events audited: 46,701,509
- Old Bookroll content events with context_id: 46,633,944
- Old Bookroll content events missing context_id: 67,565
- Old Bookroll content events with context_title: 46,633,944
- Old Bookroll content events with context_label: 46,633,944
- Distinct old context_id values in audited Bookroll content events: 417
- Old context-month aggregate rows fetched: 74,749
- New context-month aggregate rows fetched: 19,194
- Old events represented in same-course context_id features for score students: 45,681,730
- Old events skipped because actor was not in score students: 952,214
- New events represented in same-course mapped features for score students: 4,095,770

## By Year
- test_year=2024: score_rows=19,551, students=1,200, courses=90, m3_rows=10,037 (51.3%), m6_rows=10,774 (55.1%), m12_rows=10,903 (55.8%), events_m3=45,866,842
- test_year=2023: score_rows=15,901, students=1,183, courses=89, m3_rows=8,745 (55.0%), m6_rows=9,319 (58.6%), m12_rows=9,627 (60.5%), events_m3=10,756,394
- test_year=2025: score_rows=3,041, students=924, courses=39, m3_rows=1,865 (61.3%), m6_rows=2,185 (71.9%), m12_rows=2,231 (73.4%), events_m3=8,115,090
- test_year=2020: score_rows=1,252, students=353, courses=18, m3_rows=1,143 (91.3%), m6_rows=1,143 (91.3%), m12_rows=1,143 (91.3%), events_m3=1,828,806
- test_year=2019: score_rows=1,292, students=359, courses=30, m3_rows=673 (52.1%), m6_rows=673 (52.1%), m12_rows=673 (52.1%), events_m3=531,076
- test_year=2021: score_rows=1,431, students=358, courses=18, m3_rows=661 (46.2%), m6_rows=686 (47.9%), m12_rows=686 (47.9%), events_m3=731,108
- test_year=2022: score_rows=712, students=356, courses=18, m3_rows=0 (0.0%), m6_rows=0 (0.0%), m12_rows=0 (0.0%), events_m3=0

## By Year/Test Family
- test_year=2024, test_family=school_regular_exam: score_rows=14,313, students=1,200, courses=70, m3_rows=6,614 (46.2%), m6_rows=7,280 (50.9%), m12_rows=7,408 (51.8%), events_m3=21,657,189
- test_year=2023, test_family=school_regular_exam: score_rows=10,909, students=1,183, courses=53, m3_rows=5,698 (52.2%), m6_rows=6,236 (57.2%), m12_rows=6,544 (60.0%), events_m3=5,783,147
- test_year=2024, test_family=unit_or_chapter_test: score_rows=2,160, students=360, courses=15, m3_rows=2,158 (99.9%), m6_rows=2,160 (100.0%), m12_rows=2,160 (100.0%), events_m3=15,547,031
- test_year=2023, test_family=unit_or_chapter_test: score_rows=1,914, students=358, courses=9, m3_rows=1,899 (99.2%), m6_rows=1,899 (99.2%), m12_rows=1,899 (99.2%), events_m3=3,307,107
- test_year=2025, test_family=school_regular_exam: score_rows=3,036, students=919, courses=38, m3_rows=1,860 (61.3%), m6_rows=2,180 (71.8%), m12_rows=2,226 (73.3%), events_m3=8,114,343
- test_year=2020, test_family=external_benesse: score_rows=1,252, students=353, courses=18, m3_rows=1,143 (91.3%), m6_rows=1,143 (91.3%), m12_rows=1,143 (91.3%), events_m3=1,828,806
- test_year=2024, test_family=external_benesse: score_rows=2,143, students=359, courses=27, m3_rows=875 (40.8%), m6_rows=935 (43.6%), m12_rows=935 (43.6%), events_m3=3,244,886
- test_year=2019, test_family=external_benesse: score_rows=1,292, students=359, courses=30, m3_rows=673 (52.1%), m6_rows=673 (52.1%), m12_rows=673 (52.1%), events_m3=531,076
- test_year=2021, test_family=external_benesse: score_rows=1,431, students=358, courses=18, m3_rows=661 (46.2%), m6_rows=686 (47.9%), m12_rows=686 (47.9%), events_m3=731,108
- test_year=2023, test_family=external_benesse: score_rows=1,431, students=239, courses=18, m3_rows=570 (39.8%), m6_rows=603 (42.1%), m12_rows=603 (42.1%), events_m3=550,089
- test_year=2024, test_family=break_after_test: score_rows=360, students=360, courses=9, m3_rows=360 (100.0%), m6_rows=360 (100.0%), m12_rows=360 (100.0%), events_m3=5,415,030
- test_year=2023, test_family=break_after_test: score_rows=358, students=358, courses=9, m3_rows=355 (99.2%), m6_rows=356 (99.4%), m12_rows=356 (99.4%), events_m3=1,079,951
- test_year=2023, test_family=unclear: score_rows=1,289, students=269, courses=30, m3_rows=223 (17.3%), m6_rows=225 (17.5%), m12_rows=225 (17.5%), events_m3=36,100
- test_year=2024, test_family=unclear: score_rows=575, students=269, courses=11, m3_rows=30 (5.2%), m6_rows=39 (6.8%), m12_rows=40 (7.0%), events_m3=2,706
- test_year=2025, test_family=generic_test: score_rows=5, students=5, courses=1, m3_rows=5 (100.0%), m6_rows=5 (100.0%), m12_rows=5 (100.0%), events_m3=747
- test_year=2022, test_family=external_benesse: score_rows=712, students=356, courses=18, m3_rows=0 (0.0%), m6_rows=0 (0.0%), m12_rows=0 (0.0%), events_m3=0

## By Grade/Subject/Family
- grade_level=高1, course_subject=数学, test_family=school_regular_exam: score_rows=5,025, students=833, courses=15, m3_rows=3,096 (61.6%), m6_rows=3,497 (69.6%), m12_rows=3,720 (74.0%), events_m3=2,090,676
- grade_level=中1, course_subject=数学, test_family=school_regular_exam: score_rows=2,040, students=360, courses=9, m3_rows=2,040 (100.0%), m6_rows=2,040 (100.0%), m12_rows=2,040 (100.0%), events_m3=21,728,042
- grade_level=中2, course_subject=数学, test_family=school_regular_exam: score_rows=2,026, students=352, courses=9, m3_rows=2,018 (99.6%), m6_rows=2,021 (99.8%), m12_rows=2,022 (99.8%), events_m3=4,288,817
- grade_level=高2, course_subject=数学, test_family=school_regular_exam: score_rows=2,759, students=544, courses=11, m3_rows=1,991 (72.2%), m6_rows=2,181 (79.0%), m12_rows=2,289 (83.0%), events_m3=1,012,540
- grade_level=中3, course_subject=数学, test_family=school_regular_exam: score_rows=1,901, students=357, courses=9, m3_rows=1,895 (99.7%), m6_rows=1,899 (99.9%), m12_rows=1,899 (99.9%), events_m3=5,337,001
- grade_level=中1, course_subject=数学, test_family=unit_or_chapter_test: score_rows=1,800, students=240, courses=6, m3_rows=1,800 (100.0%), m6_rows=1,800 (100.0%), m12_rows=1,800 (100.0%), events_m3=13,941,639
- grade_level=中2, course_subject=数学, test_family=unit_or_chapter_test: score_rows=1,560, students=240, courses=6, m3_rows=1,550 (99.4%), m6_rows=1,552 (99.5%), m12_rows=1,552 (99.5%), events_m3=2,399,618
- grade_level=中2, course_subject=英語, test_family=school_regular_exam: score_rows=1,070, students=353, courses=9, m3_rows=853 (79.7%), m6_rows=922 (86.2%), m12_rows=945 (88.3%), events_m3=179,381
- grade_level=中1, course_subject=英語, test_family=school_regular_exam: score_rows=1,079, students=360, courses=9, m3_rows=776 (71.9%), m6_rows=841 (77.9%), m12_rows=852 (79.0%), events_m3=446,402
- grade_level=中2, course_subject=数学, test_family=external_benesse: score_rows=1,286, students=710, courses=21, m3_rows=709 (55.1%), m6_rows=712 (55.4%), m12_rows=712 (55.4%), events_m3=1,165,288
- grade_level=中1, course_subject=数学, test_family=external_benesse: score_rows=1,313, students=720, courses=21, m3_rows=707 (53.8%), m6_rows=707 (53.8%), m12_rows=707 (53.8%), events_m3=3,851,435
- grade_level=中3, course_subject=数学, test_family=unit_or_chapter_test: score_rows=714, students=238, courses=6, m3_rows=707 (99.0%), m6_rows=707 (99.0%), m12_rows=707 (99.0%), events_m3=2,512,881
- grade_level=高1, course_subject=英語, test_family=school_regular_exam: score_rows=4,753, students=835, courses=6, m3_rows=690 (14.5%), m6_rows=1,371 (28.8%), m12_rows=1,473 (31.0%), events_m3=369,829
- grade_level=中2, course_subject=英語, test_family=external_benesse: score_rows=1,286, students=710, courses=21, m3_rows=659 (51.2%), m6_rows=673 (52.3%), m12_rows=673 (52.3%), events_m3=221,971
- grade_level=中3, course_subject=数学, test_family=external_benesse: score_rows=1,056, students=594, courses=15, m3_rows=598 (56.6%), m6_rows=599 (56.7%), m12_rows=599 (56.7%), events_m3=929,039
- grade_level=中3, course_subject=英語, test_family=school_regular_exam: score_rows=1,068, students=356, courses=9, m3_rows=594 (55.6%), m6_rows=686 (64.2%), m12_rows=692 (64.8%), events_m3=61,411
- grade_level=中1, course_subject=英語, test_family=external_benesse: score_rows=1,073, students=715, courses=21, m3_rows=555 (51.7%), m6_rows=567 (52.8%), m12_rows=567 (52.8%), events_m3=602,869
- grade_level=中3, course_subject=英語, test_family=external_benesse: score_rows=1,055, students=594, courses=15, m3_rows=387 (36.7%), m6_rows=400 (37.9%), m12_rows=400 (37.9%), events_m3=83,373
- grade_level=高2, course_subject=数学, test_family=unclear: score_rows=1,864, students=270, courses=40, m3_rows=253 (13.6%), m6_rows=264 (14.2%), m12_rows=265 (14.2%), events_m3=38,806
- grade_level=中1, course_subject=数学, test_family=break_after_test: score_rows=240, students=240, courses=6, m3_rows=240 (100.0%), m6_rows=240 (100.0%), m12_rows=240 (100.0%), events_m3=4,718,316
- grade_level=中2, course_subject=数学, test_family=break_after_test: score_rows=240, students=240, courses=6, m3_rows=239 (99.6%), m6_rows=239 (99.6%), m12_rows=239 (99.6%), events_m3=606,053
- grade_level=中3, course_subject=数学, test_family=break_after_test: score_rows=238, students=238, courses=6, m3_rows=236 (99.2%), m6_rows=237 (99.6%), m12_rows=237 (99.6%), events_m3=1,170,612
- grade_level=高2, course_subject=英語, test_family=school_regular_exam: score_rows=4,923, students=817, courses=6, m3_rows=218 (4.4%), m6_rows=236 (4.8%), m12_rows=244 (5.0%), events_m3=40,578
- grade_level=中1, course_subject=国語, test_family=external_benesse: score_rows=479, students=240, courses=6, m3_rows=143 (29.8%), m6_rows=173 (36.1%), m12_rows=173 (36.1%), events_m3=18,937
- grade_level=中2, course_subject=国語, test_family=external_benesse: score_rows=474, students=238, courses=6, m3_rows=119 (25.1%), m6_rows=136 (28.7%), m12_rows=136 (28.7%), events_m3=9,501
- grade_level=中3, course_subject=国語, test_family=external_benesse: score_rows=239, students=120, courses=3, m3_rows=45 (18.8%), m6_rows=73 (30.5%), m12_rows=73 (30.5%), events_m3=3,552
- grade_level=(missing), course_subject=(missing), test_family=generic_test: score_rows=5, students=5, courses=1, m3_rows=5 (100.0%), m6_rows=5 (100.0%), m12_rows=5 (100.0%), events_m3=747
- grade_level=高3, course_subject=英語, test_family=school_regular_exam: score_rows=1,614, students=269, courses=2, m3_rows=1 (0.1%), m6_rows=2 (0.1%), m12_rows=2 (0.1%), events_m3=2

## Validity Interpretation
- Cells with meaningful same-course coverage are candidates for stronger behavior-outcome claims.
- Cells with strong student-level but weak same-course coverage should be treated as general learner behavior context, not same-course reading behavior.
- The prior 59,209,738 old-event content-bridge exclusion is obsolete for this direct-context rerun and should not be reported as a current manuscript limitation unless a later audit finds missing old context_id values.
