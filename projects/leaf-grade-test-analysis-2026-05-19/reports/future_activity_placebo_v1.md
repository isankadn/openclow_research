# Future-Activity Placebo Check V1

## Design
- Tests whether future same-course activity after the test predicts the earlier score.
- Pre window: months -3, -2, -1 before test month.
- Future placebo window: months +1, +2, +3 after test month; test month excluded to avoid mixed before/after contamination.
- Student fixed effects + assessment fixed effects, adjusted for behavior composition.
- If future active days resembles the pre-test effect, temporal interpretation is weaker.

## school_regular_exam
- future_m3_placebo: beta=-0.039, CI [-0.084, +0.006], p=0.090
- pre_m3: beta=+0.015, CI [-0.020, +0.049], p=0.405

## unit_or_chapter_test
- future_m3_placebo: beta=-0.061, CI [-0.115, -0.007], p=0.028
- pre_m3: beta=+0.077, CI [+0.033, +0.120], p=0.001

## Interpretation
- The strongest temporal pattern would be positive pre-test active days with weak/null future-placebo active days.
- A positive future-placebo signal would suggest persistent time-varying motivation or post-test continuation rather than a clean pre-test mechanism.
