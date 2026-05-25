# Harmonized Old/New Research Dataset Specification

## Purpose

Create one auditable research-analysis layer from the old and new BookRoll/xAPI stores without mixing raw schemas directly.

The combined layer is designed for paper-grade analysis of:
- pre-test reading behavior
- grade/test outcomes
- grade, subject, and test-family differences
- robustness checks across old/new schema boundaries

## Source Separation

Raw sources remain separate:
- old xAPI: saikyo_old.statements_mv, used for events before 2025-04-01
- new xAPI: saikyo_new.statements_mv, used for events from 2025-04-01 onward
- score outcomes: analysis_development.course_student_scores
- course/grade/subject context: Moodle course/category metadata
- old Bookroll course context: direct ClickHouse context_id mapped to Moodle/score course_id after the saikyo_old reimport

## Score Outcome Layer

Clean score grain:
- student_id
- course_id
- name
- date_at

Rules:
- exclude rows with missing date_at
- check duplicates at student_id + course_id + name + date_at
- retain only locally derived row-level score data in local CSVs
- do not use scaled as the outcome because dated rows currently have scaled = 0

Primary numeric outcome:
- score_normalized_0_1 = (quiz - min) / (max - min)

Outcome validity flags:
- valid
- missing_quiz
- invalid_score_range
- duplicate_score_conflict
- score_below_min
- score_above_max

## Old XAPI Course Mapping

Old Bookroll xAPI same-course features now use direct non-empty context_id as course_id.
This follows the 2026-05-24 saikyo_old reimport, which populated context_id/context_title/context_label for nearly all old Bookroll content events.
The prior content-directory ownership bridge is obsolete for the main manuscript analysis and should only be retained as a historical/fallback audit artifact.

## New XAPI Course Mapping

New BookRoll xAPI same-course features use direct non-empty context_id as course_id.

This is cleaner than the old bridge, but the current score table has no 2026 dated rows and the latest dated outcomes are 2025-03-05. Therefore the current pre-test windows are dominated by old xAPI. New xAPI should become important once post-2025-04-01 score outcomes are available.

## Combined Feature Grain

Old and new events are harmonized into:
- student_id
- course_id
- event_month

Feature families currently generated:
- total events
- active days
- navigation events
- memo events
- marker events
- quiz events
- timer events
- content session events

Pre-test windows:
- 3 months before test month
- 6 months before test month
- 12 months before test month

The final local matrix is:
outputs/score_xapi_same_course_sufficiency_local_only.csv

It retains provenance:
- old_events_m3, new_events_m3
- old_events_m6, new_events_m6
- old_events_m12, new_events_m12
- xapi_source_schema_m3

## Current Strong Candidate Rule

A grade/subject/test-family cell is treated as a strong candidate only when it has:
- at least 100 valid score outcomes
- at least 100 students
- at least 100 same-course xAPI-linked score rows in the 3-month pre-test window
- at least 50% 3-month same-course xAPI coverage

This prevents large but weakly linked cells from being overclaimed.

## Current Result

The direct-context rerun expands the paper-ready candidate set beyond junior-high mathematics, including several English and high-school mathematics cells. Final claims should be based on the rerun fixed-effect and robustness outputs, not the earlier bridge-limited coverage.

## Required Robustness Checks

Before modeling claims:
- compare 3-, 6-, and 12-month windows
- model only valid normalized scores
- exclude low-confidence test-name classifications
- run sensitivity around alternate xAPI windows and the small residual missing-context set
- keep old/new source counts in all model inputs
- report same-course coverage explicitly for every modeled cell
