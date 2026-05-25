# Temporal Phase Strategy Analysis V1

## Design
- Strong candidate cells only, valid outcomes only.
- Three pre-test phases: early = test month minus 3, middle = minus 2, late = minus 1.
- Same-course old BookRoll monthly features use direct ClickHouse context_id after the saikyo_old reimport.
- Outcome comparison uses assessment fixed-effect residuals.
- Row-level phase assignments remain local only.

## Aggregate Scope
- rows after assessment fixed-effect filtering: 26,940
- unique students: 1,712
- represented old same-course events in these rows/windows: 39,335,655

## Strategy Summary
- distributed_sustained: rows=5,096, students=549, score_resid=+0.046 CI [-0.026, +0.116], active_months=3.00, entropy=0.87, late_share=0.33, navigation_share=0.19, memo_share=0.70
- distributed_navigation: rows=2,806, students=812, score_resid=+0.022 CI [-0.052, +0.096], active_months=3.00, entropy=0.87, late_share=0.32, navigation_share=0.63, memo_share=0.19
- late_intensive: rows=4,942, students=974, score_resid=-0.001 CI [-0.057, +0.050], active_months=1.69, entropy=0.25, late_share=0.86, navigation_share=0.45, memo_share=0.35
- no_same_course_activity: rows=6,240, students=1,355, score_resid=-0.014 CI [-0.058, +0.030], active_months=0.00, entropy=0.00, late_share=0.00, navigation_share=0.00, memo_share=0.00
- early_declining: rows=2,146, students=928, score_resid=-0.023 CI [-0.086, +0.044], active_months=1.79, entropy=0.28, late_share=0.06, navigation_share=0.71, memo_share=0.08
- intermittent_activity: rows=4,833, students=1,069, score_resid=-0.024 CI [-0.087, +0.031], active_months=2.61, entropy=0.65, late_share=0.31, navigation_share=0.53, memo_share=0.29
- single_month_activity: rows=877, students=533, score_resid=-0.041 CI [-0.133, +0.058], active_months=1.00, entropy=0.00, late_share=0.00, navigation_share=0.48, memo_share=0.07

## Interpretation
- This is the first direct temporal-strategy layer: it separates sustained, late-intensive, early-declining, intermittent, and no-activity patterns.
- Strategies with stable positive residuals are better paper candidates than simple behavior totals.
- The next check should combine phase strategy with behavior profile to see whether distributed navigation remains positive after separating late cramming from sustained use.
