# Grade/Subject Active-Days Consistency V1

## Design
- Course-embedded assessments only: regular exams and unit/chapter tests.
- Separate two-way fixed-effect models by grade + subject + test family.
- Each model adjusts for event volume and behavior composition; reported coefficient is log active days.
- This tests whether the mechanism is grade-, subject-, or assessment-family-local rather than uniform across all cells.

## Estimated Cells
- 中1 数学 school_regular_exam m3: beta=+0.082, CI [+0.015, +0.150], p=0.017
- 中1 数学 school_regular_exam m6: beta=+0.062, CI [+0.005, +0.120], p=0.033
- 中1 数学 school_regular_exam m12: beta=+0.083, CI [+0.024, +0.143], p=0.006
- 中1 数学 unit_or_chapter_test m3: beta=+0.039, CI [-0.018, +0.096], p=0.178
- 中1 数学 unit_or_chapter_test m6: beta=+0.039, CI [-0.021, +0.100], p=0.205
- 中1 数学 unit_or_chapter_test m12: beta=+0.041, CI [-0.017, +0.099], p=0.167
- 中1 英語 school_regular_exam m3: beta=+0.143, CI [-0.028, +0.313], p=0.101
- 中1 英語 school_regular_exam m6: beta=+0.126, CI [-0.039, +0.291], p=0.135
- 中1 英語 school_regular_exam m12: beta=+0.131, CI [-0.038, +0.300], p=0.128
- 中2 数学 school_regular_exam m3: beta=+0.107, CI [+0.033, +0.181], p=0.005
- 中2 数学 school_regular_exam m6: beta=+0.133, CI [+0.060, +0.206], p=0.000
- 中2 数学 school_regular_exam m12: beta=+0.150, CI [+0.075, +0.224], p=0.000
- 中2 数学 unit_or_chapter_test m3: beta=+0.061, CI [-0.025, +0.147], p=0.162
- 中2 数学 unit_or_chapter_test m6: beta=+0.058, CI [-0.021, +0.137], p=0.150
- 中2 数学 unit_or_chapter_test m12: beta=+0.060, CI [-0.019, +0.139], p=0.137
- 中2 英語 school_regular_exam m3: beta=+0.005, CI [-0.131, +0.142], p=0.938
- 中2 英語 school_regular_exam m6: beta=-0.023, CI [-0.153, +0.106], p=0.725
- 中2 英語 school_regular_exam m12: beta=-0.033, CI [-0.155, +0.088], p=0.592
- 中3 数学 school_regular_exam m3: beta=-0.040, CI [-0.106, +0.026], p=0.233
- 中3 数学 school_regular_exam m6: beta=+0.025, CI [-0.046, +0.096], p=0.493
- 中3 数学 school_regular_exam m12: beta=-0.010, CI [-0.104, +0.085], p=0.840
- 中3 数学 unit_or_chapter_test m3: beta=+0.049, CI [-0.061, +0.159], p=0.383
- 中3 数学 unit_or_chapter_test m6: beta=+0.054, CI [-0.054, +0.163], p=0.326
- 中3 数学 unit_or_chapter_test m12: beta=+0.054, CI [-0.054, +0.163], p=0.326
- 中3 英語 school_regular_exam m3: beta=+0.009, CI [-0.141, +0.159], p=0.904
- 中3 英語 school_regular_exam m6: beta=+0.011, CI [-0.118, +0.140], p=0.868
- 中3 英語 school_regular_exam m12: beta=+0.012, CI [-0.114, +0.139], p=0.849
- 高1 数学 school_regular_exam m3: beta=+0.100, CI [+0.029, +0.171], p=0.006
- 高1 数学 school_regular_exam m6: beta=+0.053, CI [-0.015, +0.121], p=0.130
- 高1 数学 school_regular_exam m12: beta=+0.065, CI [+0.003, +0.127], p=0.040
- 高2 数学 school_regular_exam m3: beta=+0.165, CI [+0.050, +0.281], p=0.005
- 高2 数学 school_regular_exam m6: beta=+0.122, CI [-0.007, +0.252], p=0.065
- 高2 数学 school_regular_exam m12: beta=+0.101, CI [-0.030, +0.232], p=0.131

## Interpretation
- Positive estimated cells: 29 / 33.
- Clearly positive cells with CI above zero: 9 / 33.
- If 中1/中2/中3 mathematics are consistently positive, the result is not driven by one grade.
