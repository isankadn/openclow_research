# Behavior Profiles V1

## Scope
- Strong candidate cells only, valid outcomes only.
- Profiles use 3-month same-course xAPI features.
- Outcome comparison uses assessment fixed-effect residuals, so profiles are compared within the same course/test/date.
- Row-level profile assignments remain local only.

## Coverage
- rows after assessment fixed-effect filtering: 26,940
- rows with same-course xAPI used in k-means: 20,700
- rows without same-course xAPI kept as separate profile: 6,240
- k-means clusters: 4, starts: 12, SSE: 41752.16

## Profile Summary
- high_volume_marker_intensive: rows=353, students=205, score_resid=+0.096 CI [-0.036, +0.196], active_days_mean=8.93, events_mean=66969.0, memo_rate=0.046, navigation_rate=0.303
- memo_intensive: rows=10,967, students=686, score_resid=+0.027 CI [-0.047, +0.091], active_days_mean=31.47, events_mean=3451.3, memo_rate=0.657, navigation_rate=0.226
- no_same_course_xapi: rows=6,240, students=1,355, score_resid=-0.014 CI [-0.049, +0.033], active_days_mean=0.00, events_mean=0.0, memo_rate=0.000, navigation_rate=0.000
- distributed_navigation: rows=8,528, students=1,386, score_resid=-0.023 CI [-0.066, +0.021], active_days_mean=10.83, events_mean=617.6, memo_rate=0.023, navigation_rate=0.780
- low_regular_activity: rows=852, students=421, score_resid=-0.060 CI [-0.157, +0.032], active_days_mean=3.93, events_mean=174.7, memo_rate=0.017, navigation_rate=0.216

## Interpretation
- Profiles are descriptive strategy groups, not causal mechanisms.
- A profile is paper-relevant only if it is interpretable, common enough, and has a stable assessment-residual score difference.
- This profile layer can support a stronger narrative than coefficients alone: regular/distributed engagement appears more valuable than raw click volume.
