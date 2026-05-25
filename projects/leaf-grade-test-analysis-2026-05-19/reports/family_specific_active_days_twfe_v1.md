# Family-Specific Active-Days Mechanism V1

## Design
- Separate models for regular exams, unit/chapter tests, and Benesse tests.
- Student fixed effects + assessment fixed effects within each assessment family.
- Model A: active days only.
- Model B: active days adjusted for raw event volume and behavior composition.
- Coefficients are standardized within-family two-way residual associations.

## school_regular_exam
- m3 / active_days_only_twfe: beta=+0.043, CI [+0.023, +0.063], p=0.000
- m3 / adjusted_behavior_twfe: beta=+0.067, CI [+0.029, +0.105], p=0.001
- m6 / active_days_only_twfe: beta=+0.044, CI [+0.023, +0.065], p=0.000
- m6 / adjusted_behavior_twfe: beta=+0.045, CI [+0.005, +0.086], p=0.027
- m12 / active_days_only_twfe: beta=+0.050, CI [+0.028, +0.072], p=0.000
- m12 / adjusted_behavior_twfe: beta=+0.045, CI [+0.004, +0.085], p=0.029

## unit_or_chapter_test
- m3 / active_days_only_twfe: beta=+0.049, CI [+0.016, +0.082], p=0.004
- m3 / adjusted_behavior_twfe: beta=+0.058, CI [+0.010, +0.105], p=0.017
- m6 / active_days_only_twfe: beta=+0.039, CI [+0.005, +0.073], p=0.023
- m6 / adjusted_behavior_twfe: beta=+0.046, CI [-0.004, +0.096], p=0.069
- m12 / active_days_only_twfe: beta=+0.037, CI [+0.002, +0.073], p=0.039
- m12 / adjusted_behavior_twfe: beta=+0.046, CI [-0.006, +0.098], p=0.081

## external_benesse
- m3 / active_days_only_twfe: beta=+0.026, CI [-0.002, +0.054], p=0.073
- m3 / adjusted_behavior_twfe: beta=+0.036, CI [-0.013, +0.085], p=0.150
- m6 / active_days_only_twfe: beta=+0.024, CI [-0.004, +0.052], p=0.089
- m6 / adjusted_behavior_twfe: beta=+0.030, CI [-0.020, +0.081], p=0.238
- m12 / active_days_only_twfe: beta=+0.025, CI [-0.003, +0.053], p=0.076
- m12 / adjusted_behavior_twfe: beta=+0.031, CI [-0.019, +0.082], p=0.227

## Interpretation
- A mechanism is stronger if active days remains positive in the adjusted model within multiple assessment families.
- If it appears only in one test family, the paper should frame it as context-specific rather than general.
- Because these are within-student observational estimates, causal language should remain cautious.
