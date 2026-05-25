# LEAF Grade/Test Analysis

Started: 2026-05-19

## Purpose
Build the outcome side of the research analysis from analysis_development.course_student_scores before mapping in old/new xAPI behavior data.

## Operating Rules
- Do not send raw/student-level data to an LLM for analysis.
- Use local Python scripts for extraction, cleaning, deduplication, classification, statistics, and figures.
- Exclude rows with missing date_at for analyses requiring test conduct date.
- Quantify duplicates before removing them.
- Preserve reproducible scripts and aggregate outputs in this project folder.

