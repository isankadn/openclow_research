# Causal-Cautious Two-Way Fixed-Effects Models V1

## Design
- Observational design, not randomized causal identification.
- Adds student fixed effects to assessment fixed effects.
- Interpretation: within the same student, whether changes in pre-test behavior across assessments align with changes in normalized score, while controlling for assessment difficulty/date/course/test.
- This reduces confounding from stable student ability, motivation, and background, but not from time-varying unobserved factors.
- Coefficients are standardized residual associations after two-way demeaning.

## Multivariable Two-Way Fixed-Effects Results
### m3
- log_events: beta=-0.004, CI [-0.030, +0.021], p_boot=0.700
- log_active_days: beta=+0.060, CI [+0.035, +0.089], p_boot=0.000
- navigation_rate: beta=-0.028, CI [-0.064, +0.006], p_boot=0.200
- memo_rate: beta=+0.005, CI [-0.020, +0.029], p_boot=0.500
- marker_rate: beta=+0.017, CI [+0.008, +0.026], p_boot=0.000
- content_session_rate: beta=-0.004, CI [-0.015, +0.011], p_boot=0.800

### m6
- log_events: beta=+0.018, CI [-0.017, +0.058], p_boot=0.400
- log_active_days: beta=+0.048, CI [+0.007, +0.092], p_boot=0.000
- navigation_rate: beta=-0.035, CI [-0.065, -0.001], p_boot=0.100
- memo_rate: beta=-0.006, CI [-0.034, +0.024], p_boot=0.600
- marker_rate: beta=+0.010, CI [-0.005, +0.023], p_boot=0.400
- content_session_rate: beta=-0.009, CI [-0.027, +0.009], p_boot=0.400

### m12
- log_events: beta=+0.032, CI [-0.002, +0.079], p_boot=0.300
- log_active_days: beta=+0.042, CI [+0.003, +0.068], p_boot=0.100
- navigation_rate: beta=-0.038, CI [-0.085, -0.007], p_boot=0.000
- memo_rate: beta=-0.011, CI [-0.029, +0.013], p_boot=0.300
- marker_rate: beta=+0.007, CI [-0.012, +0.023], p_boot=1.000
- content_session_rate: beta=-0.008, CI [-0.017, +0.015], p_boot=0.700

## Binary Same-Course Activity Models
- m3: has_activity beta=+0.014, CI [+0.003, +0.024], p_boot=0.000
- m6: has_activity beta=+0.017, CI [+0.002, +0.034], p_boot=0.000
- m12: has_activity beta=+0.021, CI [+0.002, +0.034], p_boot=0.100

## Causal Interpretation
- If active-days remains positive here, it is less likely to be only a between-student ability artifact.
- Remaining threats: time-varying effort, teacher assignment, assessment preparation, unmeasured offline study, and reverse causality from motivated students choosing to read more.
- Paper language should use causal-cautious terms unless a stronger quasi-experimental design is added.
