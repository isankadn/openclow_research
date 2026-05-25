# Strategy Categories Plus Behavior Features: Two-Way Fixed Effects V1

## Design
- Observational, causal-cautious model.
- Fixed effects: student and assessment occasion.
- Strategy baseline: no_same_course_activity.
- Model 1 estimates the within-student total strategy contrast against the no-activity baseline.
- Model 2 adds measured behavior features, so strategy coefficients become residual/direct contrasts beyond active days, navigation, memo, marker, and content-session composition.
- This adjustment may control away part of the strategy mechanism; therefore Model 1 and Model 2 answer different questions.

## Model 1: Strategy Categories Only
- distributed_navigation: beta=+0.034, CI [+0.006, +0.061], p_boot=0.016
- distributed_sustained: beta=+0.036, CI [+0.009, +0.063], p_boot=0.010
- early_declining: beta=+0.006, CI [-0.015, +0.027], p_boot=0.558
- intermittent_activity: beta=+0.024, CI [-0.006, +0.054], p_boot=0.111
- late_intensive: beta=+0.018, CI [-0.003, +0.039], p_boot=0.092
- single_month_activity: beta=+0.012, CI [-0.004, +0.027], p_boot=0.133

## Model 2: Strategy Categories Plus Behavior Features
- distributed_navigation: beta=+0.012, CI [-0.064, +0.087], p_boot=0.765
- distributed_sustained: beta=+0.010, CI [-0.064, +0.083], p_boot=0.796
- early_declining: beta=+0.000, CI [-0.061, +0.062], p_boot=0.989
- intermittent_activity: beta=+0.002, CI [-0.096, +0.100], p_boot=0.970
- late_intensive: beta=+0.011, CI [-0.061, +0.083], p_boot=0.765
- single_month_activity: beta=+0.015, CI [-0.026, +0.056], p_boot=0.485

Behavior-feature covariates in adjusted model:
- log_events_m3: beta=-0.005, CI [-0.047, +0.036], p_boot=0.799
- log_active_days_m3: beta=+0.062, CI [+0.030, +0.095], p_boot=0.000
- navigation_rate_m3: beta=-0.034, CI [-0.087, +0.018], p_boot=0.195
- memo_rate_m3: beta=+0.001, CI [-0.033, +0.035], p_boot=0.954
- marker_rate_m3: beta=+0.016, CI [-0.001, +0.032], p_boot=0.066
- content_session_rate_m3: beta=-0.009, CI [-0.042, +0.024], p_boot=0.594

## Causal Interpretation
- Student fixed effects remove stable ability/background differences; assessment fixed effects remove test/course/date difficulty.
- The remaining comparison is within-student variation across assessments.
- Time-varying confounding remains possible, especially changing effort, offline study, teacher support, and preparation cycles.
- Use language such as 'consistent with' or 'supports a causal-cautious interpretation', not definitive causal claims.
