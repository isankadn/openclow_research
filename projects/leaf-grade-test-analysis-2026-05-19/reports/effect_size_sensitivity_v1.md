# Effect Size and Sensitivity Diagnostics V1

## Practical Effect Size
- Scope: strong course-embedded cells (regular exams and unit/chapter tests), m3 window, student-course FE + assessment-occasion FE.
- Unstandardized log-active-days coefficient: 0.01756 normalized-score points; clustered SE=0.00432.
- Active-day distribution among active identified rows: Q1=7, median=21, Q3=33.
- Moving from Q1 to Q3 active days corresponds to about 2.54 normalized-score percentage points.
- Moving from 3 to 10 active days corresponds to about 1.78 normalized-score percentage points.

## Sensitivity
- main: beta=+0.01756, SE=0.00432, rows=17,713.
- exclude_top_1pct_event_volume: beta=+0.01971, SE=0.00437, rows=17,505.

## Coverage Threshold Sensitivity
- m3 threshold >= 40%: cells=11, beta=+0.01756, SE=0.00432, rows=17,713.
- m3 threshold >= 50%: cells=11, beta=+0.01756, SE=0.00432, rows=17,713.
- m3 threshold >= 60%: cells=10, beta=+0.01824, SE=0.00448, rows=16,822.
- m3 threshold >= 75%: cells=7, beta=+0.01732, SE=0.00729, rows=10,488.
- m3 threshold >= 90%: cells=6, beta=+0.02207, SE=0.00865, rows=9,551.

## Active-Day Bin Sensitivity
- Baseline is zero active days. Bin indicators are estimated with student-course FE, assessment FE, log event volume, and behavior-composition controls.
- 1-2 days: beta=-0.02703, SE=0.01846.
- 3-5 days: beta=-0.03844, SE=0.02000.
- 6-10 days: beta=-0.02992, SE=0.02108.
- 11-20 days: beta=-0.02984, SE=0.02206.
- 21+ days: beta=-0.00693, SE=0.02296.

## Collinearity Check
- Residual correlation between log event volume and log active days after student-course and assessment demeaning: 0.777.
- This confirms related but non-identical variation; active days is not merely a relabeled event-volume variable.
