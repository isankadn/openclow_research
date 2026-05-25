# Subject-Specific Refined Models

## Purpose
- Revisit whether the direct-context result is mathematics-only or also supported in English.
- Estimate subject-specific active-days models by assessment family and window.
- Compare student + assessment fixed effects with stricter student-course + assessment fixed effects.
- Keep claims at the level supported by subject-specific evidence.

## Coverage By Subject
- course_embedded / 数学: valid_rows=17,530, students=1,462, assessments=448, m3_xapi=14,915 (85.1%), events_m3=53,174,735
- course_embedded / 英語: valid_rows=3,189, students=596, assessments=81, m3_xapi=2,215 (69.5%), events_m3=686,773
- external_benesse / 数学: valid_rows=3,636, students=959, assessments=105, m3_xapi=2,003 (55.1%), events_m3=5,936,127
- external_benesse / 英語: valid_rows=2,348, students=838, assessments=69, m3_xapi=1,208 (51.4%), events_m3=823,763
- school_regular_exam / 数学: valid_rows=13,525, students=1,462, assessments=346, m3_xapi=10,915 (80.7%), events_m3=34,369,317
- school_regular_exam / 英語: valid_rows=3,189, students=596, assessments=81, m3_xapi=2,215 (69.5%), events_m3=686,773
- unit_or_chapter_test / 数学: valid_rows=4,005, students=473, assessments=102, m3_xapi=4,000 (99.9%), events_m3=18,805,418

## Main Active-Days Results (m3, adjusted behavior model)

- course_embedded / 数学: student FE beta=+0.089, CI [+0.052, +0.127], p=0.000, rows=15,630; student-course FE beta=+0.070, CI [+0.035, +0.105], p=0.000, rows=14,975
- course_embedded / 英語: student FE beta=+0.069, CI [-0.022, +0.160], p=0.135, rows=3,050; student-course FE beta=+0.064, CI [-0.022, +0.150], p=0.147, rows=2,738
- school_regular_exam / 数学: student FE beta=+0.098, CI [+0.054, +0.141], p=0.000, rows=11,625; student-course FE beta=+0.080, CI [+0.039, +0.122], p=0.000, rows=10,968
- school_regular_exam / 英語: student FE beta=+0.069, CI [-0.022, +0.160], p=0.135, rows=3,050; student-course FE beta=+0.064, CI [-0.022, +0.150], p=0.147, rows=2,738
- unit_or_chapter_test / 数学: student FE beta=+0.058, CI [+0.010, +0.105], p=0.017, rows=4,002; student-course FE beta=+0.039, CI [-0.006, +0.084], p=0.088, rows=4,002
- unit_or_chapter_test / 英語: not estimable with current thresholds.
- external_benesse / 数学: student FE beta=+0.033, CI [-0.031, +0.096], p=0.316, rows=3,484; student-course FE beta=+0.027, CI [-0.053, +0.107], p=0.506, rows=3,050
- external_benesse / 英語: student FE beta=+0.090, CI [-0.005, +0.184], p=0.062, rows=2,189; student-course FE beta=+0.140, CI [+0.033, +0.247], p=0.011, rows=1,670

## Regularity Versus Event Volume (m3, adjusted, student-course FE)

- course_embedded / 数学: active_days=+0.070 CI [+0.035, +0.105], log_events=-0.056 CI [-0.099, -0.012]
- course_embedded / 英語: active_days=+0.064 CI [-0.022, +0.150], log_events=-0.022 CI [-0.122, +0.079]
- school_regular_exam / 数学: active_days=+0.080 CI [+0.039, +0.122], log_events=-0.084 CI [-0.138, -0.030]
- school_regular_exam / 英語: active_days=+0.064 CI [-0.022, +0.150], log_events=-0.022 CI [-0.122, +0.079]
- unit_or_chapter_test / 数学: active_days=+0.039 CI [-0.006, +0.084], log_events=+0.025 CI [-0.023, +0.072]
- external_benesse / 数学: active_days=+0.027 CI [-0.053, +0.107], log_events=-0.049 CI [-0.136, +0.039]
- external_benesse / 英語: active_days=+0.140 CI [+0.033, +0.247], log_events=-0.116 CI [-0.264, +0.032]

## Claim Strength
- Strongest subject-specific claim: mathematics regular exams. Active days are positive under both student FE and student-course FE, and remain positive across windows.
- For mathematics regular exams, the adjusted student-course model shows active days positive while event volume is negative. This is the strongest subject-specific support for the claim that regularity is more informative than click volume alone.
- English regular exams are included and analyzable, but the strict student-course model is weaker/less precise than mathematics. Treat English regular exams as exploratory/supportive, not the headline claim.
- Unit/chapter-test strong cells are currently mathematics-only in the candidate set, so this family cannot support an English claim.
- English external Benesse shows a surprisingly strong positive active-days pattern, especially in the stricter model and longer windows. This is an important secondary finding, but it should be framed as subject/test-family specific rather than as the main course-alignment claim.
- The best-paper claim should stay: course-aligned regularity is a trace-validity principle; mathematics regular exams are the strongest empirical demonstration.
