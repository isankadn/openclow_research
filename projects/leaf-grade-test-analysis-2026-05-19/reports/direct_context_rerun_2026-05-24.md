# Direct-Context Rerun - 2026-05-24

## Why This Rerun Was Needed

The old ClickHouse table `saikyo_old.statements_mv` was reimported so that Bookroll rows now carry:
- `context_id`: Moodle course ID
- `context_title`: Moodle course name
- `context_label`: Moodle course name/label

This changes the manuscript analysis. The old same-course feature builder had used a fragile `contents_id -> course_id` bridge through Bookroll relational metadata, which caused the earlier 59,209,738 old-event exclusion. That exclusion is obsolete for the current analysis.

## Step 1: Audit Old Context Coverage

Script: `34_audit_reimported_old_context.py`

Audited old Bookroll content events from 2019-01-01 through before 2025-04-01, requiring non-empty `operation_name` and `contents_id`.

Results:
- Rows audited: 46,701,509
- Rows with `context_id`: 46,633,944 (99.86%)
- Rows missing `context_id`: 67,565 (0.14%)
- Distinct `context_id` values: 417
- Distinct students: 2,569
- Distinct contents: 13,291

Conclusion: direct ClickHouse `context_id` is now sufficient as the primary same-course linkage field.

## Step 2: Rebuild Same-Course XAPI Features

Script: `06_same_course_harmonized_xapi.py`

Change:
- old xAPI mapping now uses direct non-empty `context_id`
- new xAPI mapping already used direct non-empty `context_id`
- Bookroll relational `event_log` and content-directory bridge are not used in the main analysis path

Updated extraction/mapping coverage:
- Old context-month aggregate rows fetched: 74,749
- New context-month aggregate rows fetched: 19,194
- Old events represented in same-course features for score students: 45,681,730
- Old events skipped because actor was not in score students: 952,214
- New events represented in same-course features for score students: 4,095,770

## Step 3: Rebuild Analysis Matrix

Script: `07_score_outcome_descriptives.py`

Updated matrix:
- Clean dated assessment rows: 43,180
- Valid normalized outcomes: 42,548
- Rows with any same-course xAPI in 3-month pre-test window: 23,124 (53.6%)
- Rows with old-source same-course xAPI in 3-month window: 23,124
- Rows with new-source same-course xAPI in 3-month window: 0

The current dated score outcomes still end before the new xAPI period contributes materially, so modeled same-course pre-test evidence remains old-source dominated even though the course mapping is now direct.

## Step 4: Rerun Candidate-Cell and Fixed-Effect Models

Strong-cell rows increased from the prior bridge-limited draft:
- Strong-cell valid rows: 27,409
- Course-embedded rows: 20,719
- External Benesse rows: 5,984
- Same-course pre-test ebook events in strong cells: 67,095,840

Key two-way fixed-effect result:
- 3-month `log_active_days`: +0.060
- 6-month `log_active_days`: +0.048
- 12-month `log_active_days`: +0.042

Raw event volume is positive in broader assessment-fixed-effect models, but weaker in the stricter student + assessment fixed-effect model. The manuscript claim was revised from "event volume is not useful" to "active days are more stable and interpretable than click volume alone."

## Step 5: Rerun Robustness Checks

Family-specific active-days models:
- Regular exams: positive across 3-, 6-, and 12-month windows
- Unit/chapter tests: positive in the 3-month window; positive but less precise in longer windows
- External Benesse: positive in sign but not statistically clear in the student fixed-effect family model

Student-course fixed-effect robustness:
- Course-embedded m3: +0.068, 95% CI [+0.035, +0.101], p < .001
- Regular exams m3: +0.077, 95% CI [+0.039, +0.116], p < .001
- Unit/chapter tests m3: +0.039, 95% CI [-0.006, +0.084], p = .088
- External Benesse m3: +0.070, 95% CI [+0.007, +0.133], p = .030

This means the assessment-family contrast is more nuanced than in the previous draft. Course-embedded evidence remains stronger and more interpretable, but the manuscript should not claim that Benesse tests are unaffected.

## Step 6: Update Manuscript Draft

Updated file:
- `paper_draft/manuscript_draft.md`

Main changes:
- removed the old Bookroll event-log/content-directory bridge as the main linkage method
- marked the 59,209,738 skipped-old-event issue as obsolete for the current direct-context analysis
- updated sample construction counts
- updated strategy, family-specific, student-course FE, effect-size, and placebo results
- softened overstrong claims about raw event volume and Benesse tests
- reframed the main finding as: regular same-course active days are more stable and interpretable than click volume alone

## Step 7: Refine Subject-Specific Claims

Script: `35_subject_specific_refined_models.py`

Purpose:
- Check whether the result is mathematics-only or also supported in English.
- Estimate subject-specific models by assessment family and window.
- Compare student + assessment fixed effects with stricter student-course + assessment fixed effects.

Main findings:
- Mathematics regular exams are the strongest subject-specific result.
  - m3 adjusted student FE: beta = +0.098, 95% CI [+0.054, +0.141], p < .001, rows = 11,625.
  - m3 adjusted student-course FE: beta = +0.080, 95% CI [+0.039, +0.122], p < .001, rows = 10,968.
  - Under the same strict model, log event volume is negative: beta = -0.084, 95% CI [-0.138, -0.030].
- English regular exams are analyzable but weaker/less precise.
  - m3 adjusted student-course FE: beta = +0.064, 95% CI [-0.022, +0.150], p = .147.
- Unit/chapter-test strong cells are currently mathematics-only, so this family cannot support an English claim.
- English external Benesse is a notable secondary finding.
  - m3 adjusted student-course FE: beta = +0.140, 95% CI [+0.033, +0.247], p = .011.
  - m6/m12 are also positive in the strict model.
  - Because Benesse is less directly course-embedded, this should be framed as subject/test-family specific rather than the main course-alignment claim.

Subject-specific conclusion:
- The best-paper headline should not be "all subjects behave the same."
- Strongest empirical demonstration: mathematics regular exams.
- Important secondary result: English may show stronger signal for external Benesse-style assessments than for regular exams.
- Core claim remains: regular same-course active days are more defensible than click volume alone, especially when the trace is course-aligned and assessment-specific.

## Remaining Verification Before Submission

- Run the slow two-way fixed-effect bootstrap at the original higher count for final numeric verification if time permits.
- Review whether the title should stay broad ("course-aligned outcomes") or narrow back to mathematics after venue targeting.
- Add the institutional ethics/permission statement before submission.
