# Student-Course Fixed-Effect Robustness V1

## Purpose
- Tests the main active-days mechanism under a stricter fixed-effect structure.
- Baseline model: student fixed effects + assessment-occasion fixed effects.
- Stricter model: student-course fixed effects + assessment-occasion fixed effects.
- Coefficients are standardized residual associations; standard errors are clustered by student.

## Main Active-Days Comparison
### course_embedded
- m3 / student FE: beta=+0.059, CI [+0.026, +0.093], p=0.001, rows=18,815, students=856, student-courses=2,861, assessments=501
- m3 / student-course FE: beta=+0.068, CI [+0.035, +0.101], p=0.000, rows=17,713, students=851, student-courses=2,089, assessments=483
- m6 / student FE: beta=+0.042, CI [+0.007, +0.078], p=0.020, rows=18,814, students=856, student-courses=2,863, assessments=501
- m6 / student-course FE: beta=+0.042, CI [+0.011, +0.072], p=0.008, rows=17,709, students=850, student-courses=2,089, assessments=483
- m12 / student FE: beta=+0.042, CI [+0.007, +0.078], p=0.020, rows=18,795, students=853, student-courses=2,860, assessments=501
- m12 / student-course FE: beta=+0.044, CI [+0.015, +0.073], p=0.003, rows=17,543, students=843, student-courses=2,067, assessments=483

### school_regular_exam
- m3 / student FE: beta=+0.067, CI [+0.029, +0.105], p=0.001, rows=14,810, students=856, student-courses=2,861, assessments=399
- m3 / student-course FE: beta=+0.077, CI [+0.039, +0.116], p=0.000, rows=13,706, students=850, student-courses=2,088, assessments=381
- m6 / student FE: beta=+0.045, CI [+0.005, +0.086], p=0.027, rows=14,809, students=856, student-courses=2,863, assessments=399
- m6 / student-course FE: beta=+0.047, CI [+0.010, +0.083], p=0.012, rows=13,702, students=849, student-courses=2,088, assessments=381
- m12 / student FE: beta=+0.045, CI [+0.004, +0.085], p=0.029, rows=14,790, students=853, student-courses=2,860, assessments=399
- m12 / student-course FE: beta=+0.050, CI [+0.016, +0.085], p=0.004, rows=13,536, students=842, student-courses=2,066, assessments=381

### unit_or_chapter_test
- m3 / student FE: beta=+0.058, CI [+0.010, +0.105], p=0.017, rows=4,002, students=471, student-courses=707, assessments=102
- m3 / student-course FE: beta=+0.039, CI [-0.006, +0.084], p=0.088, rows=4,002, students=471, student-courses=707, assessments=102
- m6 / student FE: beta=+0.046, CI [-0.004, +0.096], p=0.069, rows=4,002, students=471, student-courses=707, assessments=102
- m6 / student-course FE: beta=+0.033, CI [-0.012, +0.078], p=0.152, rows=4,002, students=471, student-courses=707, assessments=102
- m12 / student FE: beta=+0.046, CI [-0.006, +0.098], p=0.081, rows=4,002, students=471, student-courses=707, assessments=102
- m12 / student-course FE: beta=+0.034, CI [-0.011, +0.078], p=0.140, rows=4,002, students=471, student-courses=707, assessments=102

### external_benesse
- m3 / student FE: beta=+0.036, CI [-0.013, +0.085], p=0.150, rows=5,717, students=932, student-courses=3,306, assessments=164
- m3 / student-course FE: beta=+0.070, CI [+0.007, +0.133], p=0.030, rows=4,720, students=930, student-courses=2,360, assessments=138
- m6 / student FE: beta=+0.030, CI [-0.020, +0.081], p=0.238, rows=5,717, students=932, student-courses=3,306, assessments=164
- m6 / student-course FE: beta=+0.091, CI [+0.018, +0.163], p=0.014, rows=4,772, students=931, student-courses=2,386, assessments=138
- m12 / student FE: beta=+0.031, CI [-0.019, +0.082], p=0.227, rows=5,717, students=932, student-courses=3,306, assessments=164
- m12 / student-course FE: beta=+0.092, CI [+0.020, +0.165], p=0.012, rows=4,772, students=931, student-courses=2,386, assessments=138

## Interpretation
- Student-course fixed effects remove stable student-by-course differences, such as a learner's persistent strength or engagement in a particular course.
- A positive active-days coefficient under this stricter model supports the interpretation that within-student-course changes in regular pre-test Bookroll activity align with outcome changes.
- The model remains observational: it does not remove time-varying preparation, teacher support, offline study, or exam-specific effort.
