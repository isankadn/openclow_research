# Strong-Cell Assessment-Fixed-Effects Modeling V1

## Model Scope
- Uses only strong candidate grade/subject/test-family cells from candidate_analysis_cells_v2.csv.
- Uses only valid normalized quiz-score outcomes.
- Excludes low-confidence test-name classifications.
- Outcome and predictors are residualized by assessment_id = course_id + test name + test date.
- Coefficients are standardized effects: SD change in score residual per 1 SD change in behavior residual.
- Uncertainty uses student-cluster bootstrap resampling; only aggregate coefficients are exported.

## Analysis Rows
- rows entering candidate-cell model filter: 27,409
- excluded low-confidence rows: 0
- rows after assessment fixed-effect filtering in global model: 26,940
- students in global model: 1,712
- assessment occasions in global model: 687

## Global Multivariable Model
- log_events_m3: beta=+0.059, 95% bootstrap CI [+0.013, +0.109], p_boot=0.010
- log_active_days_m3: beta=+0.083, 95% bootstrap CI [+0.034, +0.127], p_boot=0.000
- navigation_rate_m3: beta=-0.113, 95% bootstrap CI [-0.152, -0.080], p_boot=0.000
- memo_rate_m3: beta=-0.016, 95% bootstrap CI [-0.054, +0.017], p_boot=0.350
- marker_rate_m3: beta=-0.003, 95% bootstrap CI [-0.019, +0.010], p_boot=0.630
- content_session_rate_m3: beta=-0.025, 95% bootstrap CI [-0.041, -0.009], p_boot=0.000

## Largest Cell-Level Univariate Signals
- 中3 数学 break_after_test / log_active_days_m3: beta=+0.355, CI [+0.181, +0.476], n=233, students=233, assessments=6
- 中3 数学 school_regular_exam / log_events_m3: beta=+0.287, CI [+0.195, +0.374], n=1,871, students=355, assessments=48
- 中3 数学 break_after_test / log_events_m3: beta=+0.270, CI [+0.103, +0.431], n=233, students=233, assessments=6
- 中3 数学 school_regular_exam / log_active_days_m3: beta=+0.250, CI [+0.125, +0.378], n=1,871, students=355, assessments=48
- 中2 数学 break_after_test / log_events_m3: beta=+0.213, CI [+0.104, +0.296], n=236, students=236, assessments=6
- 中2 数学 break_after_test / log_active_days_m3: beta=+0.212, CI [+0.068, +0.327], n=236, students=236, assessments=6
- 中2 数学 school_regular_exam / log_events_m3: beta=+0.161, CI [+0.083, +0.229], n=1,999, students=350, assessments=51
- 中3 数学 school_regular_exam / memo_rate_m3: beta=+0.155, CI [+0.078, +0.224], n=1,871, students=355, assessments=48
- 中1 英語 school_regular_exam / log_events_m3: beta=+0.139, CI [+0.052, +0.206], n=1,074, students=360, assessments=27
- 中2 数学 school_regular_exam / log_active_days_m3: beta=+0.135, CI [+0.070, +0.187], n=1,999, students=350, assessments=51
- 中2 数学 break_after_test / navigation_rate_m3: beta=-0.126, CI [-0.210, +0.002], n=236, students=236, assessments=6
- 中3 数学 school_regular_exam / content_session_rate_m3: beta=-0.124, CI [-0.185, -0.037], n=1,871, students=355, assessments=48
- 中1 英語 school_regular_exam / log_active_days_m3: beta=+0.119, CI [+0.022, +0.210], n=1,074, students=360, assessments=27
- 中1 英語 external_benesse / log_active_days_m3: beta=+0.117, CI [+0.047, +0.173], n=1,034, students=677, assessments=28
- 中2 英語 school_regular_exam / log_active_days_m3: beta=+0.114, CI [+0.069, +0.208], n=1,057, students=352, assessments=27
- 中3 英語 school_regular_exam / log_events_m3: beta=+0.112, CI [+0.031, +0.169], n=1,058, students=356, assessments=27
- 中2 数学 school_regular_exam / navigation_rate_m3: beta=-0.110, CI [-0.175, -0.034], n=1,999, students=350, assessments=51
- 中2 英語 external_benesse / log_active_days_m3: beta=+0.110, CI [+0.071, +0.187], n=1,221, students=688, assessments=36
- 中3 数学 school_regular_exam / navigation_rate_m3: beta=-0.109, CI [-0.195, -0.037], n=1,871, students=355, assessments=48
- 中1 英語 external_benesse / log_events_m3: beta=+0.106, CI [+0.045, +0.152], n=1,034, students=677, assessments=28

## Interpretation Guardrails
- These are associational models, not causal estimates.
- Assessment fixed effects mean the estimates compare students taking the same course/test/date, reducing test-difficulty confounding.
- Strong signals should be checked with alternate windows, exclusion of ambiguous old mappings, and sequence/profile features before paper claims.
