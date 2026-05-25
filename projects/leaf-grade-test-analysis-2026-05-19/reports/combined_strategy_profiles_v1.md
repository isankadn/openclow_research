# Combined Temporal Strategy And Behavior Profile V1

## Design
- Merges temporal phase strategies with behavior-profile clusters at the local row level.
- Reports only aggregate combinations with at least 100 rows.
- Outcome is assessment fixed-effect residual score in SD units.

## Strongest Combined Strategies
- intermittent_activity + high_volume_marker_intensive: rows=109, students=92, score_resid=+0.093 CI [-0.125, +0.263]
- early_declining + memo_intensive: rows=220, students=134, score_resid=+0.084 CI [-0.103, +0.251]
- distributed_sustained + memo_intensive: rows=5,048, students=545, score_resid=+0.046 CI [-0.027, +0.117]
- distributed_navigation + distributed_navigation: rows=1,477, students=672, score_resid=+0.030 CI [-0.063, +0.124]
- late_intensive + memo_intensive: rows=2,335, students=538, score_resid=+0.020 CI [-0.051, +0.085]
- distributed_navigation + memo_intensive: rows=1,319, students=377, score_resid=+0.013 CI [-0.099, +0.132]
- intermittent_activity + memo_intensive: rows=1,997, students=502, score_resid=-0.004 CI [-0.089, +0.069]
- no_same_course_activity + no_same_course_xapi: rows=6,240, students=1,355, score_resid=-0.014 CI [-0.058, +0.030]
- late_intensive + distributed_navigation: rows=2,172, students=869, score_resid=-0.016 CI [-0.075, +0.048]
- intermittent_activity + low_regular_activity: rows=139, students=104, score_resid=-0.026 CI [-0.256, +0.169]
- early_declining + distributed_navigation: rows=1,731, students=826, score_resid=-0.035 CI [-0.105, +0.041]
- single_month_activity + distributed_navigation: rows=558, students=358, score_resid=-0.041 CI [-0.155, +0.071]
- early_declining + low_regular_activity: rows=126, students=106, score_resid=-0.042 CI [-0.247, +0.151]
- intermittent_activity + distributed_navigation: rows=2,588, students=934, score_resid=-0.045 CI [-0.112, +0.020]
- late_intensive + low_regular_activity: rows=371, students=258, score_resid=-0.060 CI [-0.181, +0.063]
- single_month_activity + low_regular_activity: rows=194, students=139, score_resid=-0.099 CI [-0.284, +0.091]

## Interpretation
- This table helps separate sustained strategy from behavior-type composition.
- Combinations with positive residuals and enough rows are candidates for the paper's strategy typology figure.
- Small high-performing combinations should be treated as hypothesis-generating only.
