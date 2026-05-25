# Exact Manuscript Changes for Word Copy

Use these as search-and-replace blocks in the Word document copied from `icce_award_full_paper.md`. I kept the edits compact for the 10-page limit and avoided adding a new validity table.

Main additions from the review:
- Narrowed the claim to mathematics regular exams as the strongest evidence.
- Replaced stronger "study days" wording with "same-course active eBook days" where it matters.
- Added the requested robustness model: `any_activity + log_active_days_given_activity + controls + student-course and assessment fixed effects`.
- Added an event-intensity diagnostic to protect the negative event-volume interpretation.
- Clarified that 67.1 million refers to event-window observations, not necessarily unique raw xAPI statements.
- Clarified the regular-exam placebo limitation.

## Change 1

Replace this:

```markdown
# Regular Study Days, Not Click Volume Alone: Course-Aligned Trace Validity in K-12 Ebook Learning Analytics
```

With this:

```markdown
# Regular Same-Course eBook Activity, Not Click Volume Alone: Course-Aligned Trace Validity in K-12 Learning Analytics
```

## Change 2

Replace this:

```markdown
Learning analytics dashboards often treat frequent clicks as evidence of engagement, yet a click only becomes interpretable when it is aligned with the instructional context in which learning is expected to occur. This paper proposes **course-aligned trace validity** as a design and analysis principle for ebook learning analytics: behavioral traces should be evaluated according to whether they are temporally prior to, and instructionally aligned with, the assessment outcome they are used to explain. We apply this principle to Bookroll ebook activity and course assessment records from a Japanese K-12 learning environment. The analysis uses 43,180 dated assessment records, direct course-context xAPI linkage, and 67.1 million same-course pre-assessment-month ebook events in strong analysis cells. Models include student and assessment fixed effects, stricter student-course and assessment fixed effects, family-specific models, subject-specific models, window checks, strategy-adjusted models, and future-activity placebo checks. The strongest finding is not that more ebook interaction is always better. In mathematics regular exams, the strict student-course fixed-effect model shows that active study days in the three complete calendar months before the assessment month are positively associated with normalized scores (beta = +0.080, 95% CI [+0.039, +0.122]), while residual event intensity after adjustment is negative (beta = -0.084, 95% CI [-0.138, -0.030]). Across course-embedded assessments, active days remain positive across 3-, 6-, and 12-month windows. A shift from the first to the third quartile of active days corresponds to approximately +2.54 percentage points in normalized score. English regular exams show a positive but imprecise pattern, while course-linked external Benesse English assessments show a notable secondary pattern. These results argue for a shift from click-count analytics to validity-aware indicators of regular, course-aligned study.
```

With this:

```markdown
Learning analytics dashboards often treat frequent clicks as evidence of engagement, yet a click only becomes interpretable when it is aligned with the instructional context in which learning is expected to occur. This paper proposes **course-aligned trace validity** as a design and analysis principle for ebook learning analytics: behavioral traces should be evaluated according to whether they are temporally prior to, and instructionally aligned with, the assessment outcome they are used to explain. We apply this principle to Bookroll ebook activity and course assessment records from a Japanese K-12 learning environment. The analysis uses 43,180 dated assessment records, direct course-context xAPI linkage, and 67.1 million same-course pre-assessment-month event-window observations in strong analysis cells. Models include student and assessment fixed effects, stricter student-course and assessment fixed effects, family-specific models, subject-specific models, window checks, strategy-adjusted models, and future-activity placebo checks. The strongest evidence appears in mathematics regular exams: same-course active eBook days in the three complete calendar months before the assessment month are positively associated with normalized scores (beta = +0.080, 95% CI [+0.039, +0.122]), while residual event intensity after adjustment is negative (beta = -0.084, 95% CI [-0.138, -0.030]). Across course-embedded assessments, active days remain positive across 3-, 6-, and 12-month windows. A shift from the first to the third quartile of active days corresponds to approximately +2.54 percentage points in normalized score. English regular exams show a positive but imprecise pattern, while course-linked external Benesse English assessments are treated as secondary, assessment-specific evidence. These results argue for a shift from click-count analytics to validity-aware indicators of regular, course-aligned eBook activity.
```

## Change 3

Replace this:

```markdown
The paper makes four contributions. Conceptually, it offers course-aligned trace validity as a practical criterion for transforming raw learning records into interpretable educational evidence. Methodologically, it demonstrates a data-construction and modeling approach that links same-course, pre-assessment-month ebook traces to assessment outcomes with fixed effects and placebo checks. Empirically, it shows that the most robust signal is not raw event volume, but the regularity of same-course active study days before the assessment month. For analytics design, it demonstrates why indicators should be subject- and assessment-aware: the clearest evidence appears in mathematics regular exams, English regular exams are positive but imprecise, and course-linked external Benesse English assessments reveal a secondary pattern that should be interpreted differently from teacher-made course exams.

The intended contribution is therefore not another predictive model using large educational logs. The stronger claim is methodological and educational: when trace data are correctly aligned to course context and assessment timing, regular study days become a more defensible indicator than click volume alone.
```

With this:

```markdown
The paper makes four contributions. Conceptually, it offers course-aligned trace validity as a practical criterion for transforming raw learning records into interpretable educational evidence. Methodologically, it demonstrates a data-construction and modeling approach that links same-course, pre-assessment-month ebook traces to assessment outcomes with fixed effects and placebo checks. Empirically, it shows that the most robust signal is not raw event volume, but the regularity of same-course active eBook days before the assessment month. For analytics design, it demonstrates why indicators should be subject- and assessment-aware: the clearest evidence appears in mathematics regular exams, English regular exams are positive but imprecise, and course-linked external Benesse English assessments reveal a secondary pattern that should be interpreted differently from teacher-made course exams.

The intended contribution is therefore not another predictive model using large educational logs. The stronger claim is methodological and educational: when trace data are correctly aligned to course context and assessment timing, regular same-course eBook activity becomes a more defensible indicator than click volume alone.
```

## Change 4

Replace this:

```markdown
RQ2. Is the association better explained by raw event volume, behavior composition, or regularity of active study days?
```

With this:

```markdown
RQ2. Is the association better explained by raw event volume, behavior composition, or regularity of same-course active eBook days?
```

## Change 5

Replace this:

```markdown
| Item | Value |
| --- | --- |
| School level / grades | Junior high and senior high; grades 1-3 in each level |
| Bookroll/xAPI trace availability | Through May 2026 at analysis time |
| Outcome-linked assessment date range | 2019-04-10 to 2025-03-05 |
| Students in clean dated matrix | 1,722 |
| Courses in clean dated matrix | 216 |
| Assessment occasions | 900 |
| Subjects detected in score records | Mathematics, English, Japanese language |
| Rows with 3-month same-course Bookroll activity | 23,124 / 43,180 (53.6%) |
| Same-course pre-assessment-month Bookroll events in strong cells | 67.1 million |
```

With this:

```markdown
| Item | Value |
| --- | --- |
| School level / grades | Junior high and senior high; grades 1-3 in each level |
| Bookroll/xAPI trace availability | Through May 2026 at analysis time |
| Outcome-linked assessment date range | 2019-04-10 to 2025-03-05 |
| Students in clean dated matrix | 1,722 |
| Courses in clean dated matrix | 216 |
| Assessment occasions | 900 |
| Subjects detected in score records | Mathematics, English, Japanese language |
| Rows with 3-month same-course Bookroll activity | 23,124 / 43,180 (53.6%) |
| Same-course pre-assessment-month Bookroll event-window observations in strong cells | 67.1 million |
```

## Change 6

Replace this:

```markdown
Strong analysis cells were defined before modeling using minimum sample and coverage rules: at least 100 valid outcomes, at least 100 students, at least 100 score rows with same-course xAPI activity in the 3-month window, and at least 50% same-course xAPI coverage. Coverage is the proportion of clean score rows in a grade-level by subject by assessment-family cell with at least one same-course Bookroll event in the 3-month pre-assessment-month window. This rule prevents large but weakly linked cells from dominating the evidence. Strong cells contain 27,409 valid score rows: 20,719 course-embedded assessment rows, 5,984 course-linked external Benesse rows, and 706 break-after-test diagnostic rows that are retained in diagnostics but not used for the main course-embedded or Benesse claims. The strong cells contain 67.1 million same-course pre-assessment-month ebook events in the 3-month window.
```

With this:

```markdown
Strong analysis cells were defined before modeling using minimum sample and coverage rules: at least 100 valid outcomes, at least 100 students, at least 100 score rows with same-course xAPI activity in the 3-month window, and at least 50% same-course xAPI coverage. Coverage is the proportion of clean score rows in a grade-level by subject by assessment-family cell with at least one same-course Bookroll event in the 3-month pre-assessment-month window. This rule prevents large but weakly linked cells from dominating the evidence. Strong cells contain 27,409 valid score rows: 20,719 course-embedded assessment rows, 5,984 course-linked external Benesse rows, and 706 break-after-test diagnostic rows that are retained in diagnostics but not used for the main course-embedded or Benesse claims. The 67.1 million event count refers to assessment-window observations, so a raw xAPI statement may contribute to more than one later assessment window when windows overlap.
```

## Change 7

Replace this:

```markdown
The analysis also includes robustness checks. First, active-days models are repeated across 3-, 6-, and 12-month pre-assessment-month windows. Second, temporal strategy categories are compared before and after adding behavior features. Third, future-activity placebo models test whether activity after an assessment predicts the earlier score in the same positive direction. Fourth, the primary mathematics regular-exam model is re-estimated with stricter active-day definitions and with a within-assessment z-score outcome. A positive future-placebo effect would weaken the temporal interpretation.
```

With this:

```markdown
The analysis also includes robustness checks. First, active-days models are repeated across 3-, 6-, and 12-month pre-assessment-month windows. Second, an access/regularity check separates any same-course activity from the number of active days among rows with activity, using the same student-course and assessment fixed-effect structure; a parallel diagnostic re-expresses event volume as event intensity. Third, temporal strategy categories are compared before and after adding behavior features. Fourth, future-activity placebo models test whether activity after an assessment predicts the earlier score in the same positive direction. The primary model is also re-estimated with stricter active-day definitions and with a within-assessment z-score outcome. A positive future-placebo effect would weaken the temporal interpretation.
```

## Change 8

Replace this:

```markdown
The most important result is subject-specific. In mathematics regular exams, active study days remain positive in the strict student-course fixed-effect model, while adjusted residual event intensity is negative. The adjusted 3-month student-course fixed-effect estimate for active days is +0.080 (95% CI [+0.039, +0.122], p < .001, 10,968 rows). In the same model, the adjusted log-event coefficient is -0.084 (95% CI [-0.138, -0.030]).

This does not mean that clicking is harmful. It means that, after controlling for a student's stable course-specific differences, assessment occasion, active days, and behavior composition, extra event intensity is not the educationally meaningful signal. The interpretable signal is returning to same-course materials across multiple days in the complete calendar months before the assessment month.

To check whether active days merely reflect minimal access logging, we recomputed the same mathematics regular-exam student-course fixed-effect specification using stricter daily definitions from same-course daily xAPI aggregates. The active-days result remained positive when an active day required at least two events (beta = +0.077, 95% CI [+0.036, +0.118]), at least three events (beta = +0.085, 95% CI [+0.044, +0.125]), or at least one non-open/close event (beta = +0.078, 95% CI [+0.038, +0.119]). This supports the interpretation that the main signal is not driven only by accidental open/close access days.
```

With this:

```markdown
The most important result is subject-specific. In mathematics regular exams, same-course active eBook days remain positive in the strict student-course fixed-effect model, while adjusted residual event intensity is negative. The adjusted 3-month student-course fixed-effect estimate for active days is +0.080 (95% CI [+0.039, +0.122], p < .001, 10,968 rows). In the same model, the adjusted log-event coefficient is -0.084 (95% CI [-0.138, -0.030]).

This does not mean that clicking is harmful. It means that, after controlling for a student's stable course-specific differences, assessment occasion, active days, and behavior composition, extra event intensity is not the educationally meaningful signal. A reparameterized model separating regularity from event intensity gave the same interpretation: active days remained positive (beta = +0.049, 95% CI [+0.018, +0.081]) and event intensity remained negative (beta = -0.062, 95% CI [-0.102, -0.022]).

To check whether active days merely reflect any access rather than regularity, we split the primary predictor into any same-course activity and log active days among active rows. In the same model, the any-activity coefficient was -0.085 (95% CI [-0.154, -0.017]), while the active-days component remained positive (beta = +0.044, 95% CI [+0.013, +0.075]). The negative any-activity coefficient should not be interpreted as evidence that access itself is harmful; in this specification, it represents minimal or occasional access after separating out regular active-day engagement, behavior composition, student-course differences, and assessment effects. The active-days result also remained positive under stricter daily definitions requiring at least two events, at least three events, or at least one non-open/close event (betas +0.077 to +0.085).
```

## Change 9

Replace this:

```markdown
Figure 1. Subject-specific trace-validity evidence from adjusted 3-month models with student-course and assessment fixed effects. Mathematics regular exams show the clearest contrast: active days are positive, while adjusted residual event intensity is negative. The event-volume coefficient should be read as residual event intensity conditional on active days and behavior composition, not as a claim that all clicking is harmful.
```

With this:

```markdown
Figure 1. Subject-specific trace-validity evidence from adjusted 3-month models with student-course and assessment fixed effects. Mathematics regular exams show the clearest contrast: active days are positive, while adjusted residual event intensity is negative. Other assessment types provide supportive or exploratory evidence rather than equally strong confirmation.
```

## Change 10

Replace this:

```markdown
The sensitivity checks support the stability of the estimate. Excluding the top 1% of event-volume rows slightly increases the estimate rather than removing it. Changing the coverage threshold from 40% to 90% leaves the coefficient essentially unchanged. The high residual correlation between event volume and active days also clarifies why the adjusted contrast is meaningful: once the regularity of study is modeled, remaining event volume behaves like concentrated event intensity rather than simple engagement volume.
```

With this:

```markdown
The sensitivity checks support the stability of the estimate. Excluding the top 1% of event-volume rows slightly increases the estimate rather than removing it. Changing the coverage threshold from 40% to 90% leaves the coefficient essentially unchanged. The high residual correlation between event volume and active days motivates the intensity diagnostic above: once regularity is modeled, remaining event volume is better interpreted as concentrated event intensity than as simple engagement volume.
```

## Change 11

Replace this:

```markdown
Temporal strategy categories provide a useful descriptive language, but they are not the main mechanism. Distributed navigation and distributed sustained activity are positive when entered alone: +0.034 and +0.036, respectively. After adding behavior features, the coefficients shrink to +0.012 and +0.010 and the confidence intervals cross zero. This means the apparent advantage of named strategies is largely explained by measurable regularity and behavior composition.
```

With this:

```markdown
Temporal strategy categories provide useful descriptive labels, but they are not the main mechanism. Distributed navigation and distributed sustained activity are positive when entered alone, but after adding behavior features the coefficients shrink and the confidence intervals cross zero. The practical implication is that dashboards should foreground concrete regularity indicators rather than opaque strategy labels.
```

## Change 12

Replace this:

```markdown
For practical analytics, this is a useful finding. Rather than presenting students or teachers with opaque strategy labels, dashboards should foreground concrete indicators such as the number of same-course active study days and whether those days are distributed before assessment.
```

With this:

```markdown
For practical analytics, the table supports using strategy labels mainly as summaries of measurable activity patterns, not as independent explanations.
```

## Change 13

Replace this:

```markdown
The future-activity placebo asks whether activity after an assessment predicts the earlier score. For unit/chapter tests, pre-assessment-month active days are positive (+0.077, 95% CI [+0.033, +0.120]) while future active days are negative (-0.061, 95% CI [-0.115, -0.007]). This strengthens the temporal interpretation for that family. For regular exams, the placebo model does not reproduce a positive future effect, but the pre-assessment-month estimate in that specific placebo specification is also imprecise (+0.015, 95% CI [-0.020, +0.049]). Therefore, placebo checks support temporal interpretation for unit/chapter tests and do not contradict the regular-exam findings, but they do not independently prove the mathematics regular-exam mechanism.
```

With this:

```markdown
The future-activity placebo asks whether activity after an assessment predicts the earlier score. For unit/chapter tests, pre-assessment-month active days are positive (+0.077, 95% CI [+0.033, +0.120]) while future active days are negative (-0.061, 95% CI [-0.115, -0.007]). For regular exams, the placebo model does not reproduce a positive future effect, but its pre-window estimate is also imprecise (+0.015, 95% CI [-0.020, +0.049]) because the future-window specification changes the identified within-student sample and variation. Thus, placebo checks support temporal interpretation for unit/chapter tests and do not contradict the regular-exam findings, but they do not independently prove the mathematics regular-exam mechanism.
```

## Change 14

Replace this:

```markdown
The headline result is not simply that ebook use predicts scores. That would be too broad and too easy to overstate. The stronger contribution is that trace validity changes what counts as meaningful engagement. When activity is aligned to the same course, restricted to the pre-assessment-month period, and modeled with student-course and assessment fixed effects, regular active study days carry the clearest educational signal. Event volume alone is less interpretable, and its adjusted coefficient should be understood as concentrated event intensity after regularity has already been accounted for.
```

With this:

```markdown
The headline result is not simply that ebook use predicts scores. That would be too broad and too easy to overstate. The stronger contribution is that trace validity changes what counts as meaningful engagement. When activity is aligned to the same course, restricted to the pre-assessment-month period, and modeled with student-course and assessment fixed effects, regular same-course active eBook days carry the clearest educational signal. Event volume alone is less interpretable, and its adjusted coefficient should be understood as concentrated event intensity after regularity has already been accounted for.
```

## Change 15

Replace this:

```markdown
Second, dashboards should make regularity visible. A student with moderate activity across many days may be showing a stronger learning pattern than a student with a single intense burst of clicks.
```

With this:

```markdown
Second, dashboards should make regularity visible. A student with moderate same-course eBook activity across many days may be showing a stronger learning pattern than a student with a single intense burst of clicks.
```

## Change 16

Replace this:

```markdown
This paper argues that learning analytics needs trace validity before trace volume. In a large K-12 Bookroll dataset with direct course-context linkage, the most defensible indicator of assessment performance is not how many ebook events students generated, but whether they returned to same-course materials across multiple days in the complete calendar months before the assessment month. The strongest evidence appears in mathematics regular exams: active study days remain positive under student-course and assessment fixed effects, while adjusted residual event intensity is negative. The result is educationally meaningful, modest in size, and robust enough to guide analytics design.
```

With this:

```markdown
This paper argues that learning analytics needs trace validity before trace volume. In a large K-12 Bookroll dataset with direct course-context linkage, the most defensible indicator of assessment performance is not how many ebook events students generated, but whether they returned to same-course materials across multiple days in the complete calendar months before the assessment month. The strongest evidence appears in mathematics regular exams: same-course active eBook days remain positive under student-course and assessment fixed effects, while adjusted residual event intensity is negative. The result is educationally meaningful, modest in size, and robust enough to guide analytics design.
```

## Change 17

Replace this:

```markdown
The analysis grain is one row per student, course, test name, and test date. Ebook features are computed only from same-course Bookroll activity before the assessment. The primary feature is log_active_days, defined as log(1 + the number of distinct active days with same-course ebook activity in the pre-assessment-month window). Raw event volume is represented by log_events, defined as log(1 + same-course event count). Additional behavior-composition controls include navigation, memo, marker, and content-session rates. These rates are shares of all same-course events in the window; the omitted remainder consists of other logged action types not represented by those controls. Zero-activity rows are retained with log features equal to zero and event-share features equal to zero.
```

With this:

```markdown
The analysis grain is one row per student, course, test name, and test date. Ebook features are computed only from same-course Bookroll activity before the assessment. The primary feature is log_active_days, defined as log(1 + the number of distinct active days with same-course ebook activity in the pre-assessment-month window). Raw event volume is represented by log_events, defined as log(1 + same-course event count). Event intensity is operationalized as log_events - log_active_days, capturing concentrated event volume conditional on active-day regularity. Additional behavior-composition controls include navigation, memo, marker, and content-session rates. These rates are shares of all same-course events in the window; the omitted remainder consists of other logged action types not represented by those controls. Zero-activity rows are retained with log features equal to zero and event-share features equal to zero.
```

## Change 18

Replace this:

```markdown
| Coverage threshold sensitivity, 40%-90% | beta = 0.0175 across thresholds |
```

With this:

```markdown
| Coverage threshold sensitivity, 40%-90% | beta remained approximately 0.0175 |
```
