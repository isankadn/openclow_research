# Paper Draft Package

Working title:
Regular Study Days, Not Click Volume: Temporally Ordered Evidence from Ebook Reading Traces and Course-Aligned Mathematics Outcomes

## Main Files

- manuscript_draft.md - full first manuscript draft for a compact 10-page paper.
- figures/ - selected figures only, copied from the analysis project and renamed for the paper.
- tables/ - paper tables generated from rerunnable analysis outputs.

## Recommended 10-Page Allocation

- Title + abstract: 0.5 page
- Introduction + research questions: 1.5 pages
- Data/linkage + measures: 1.5 pages
- Analysis design: 1 page
- Results with 4 figures and 6 compact tables: 3 pages
- Discussion, limitations, conclusion: 2 pages
- References: fit remaining space or use conference reference style

## Selected Figures

- Figure 1: figures/Figure1_same_course_coverage_candidate_cells.svg
  Shows same-course pre-test xAPI coverage in candidate analysis cells and justifies the primary modeled subset.
- Figure 2: figures/Figure2_window_robustness.svg
  Shows that active days are stable across 3-, 6-, and 12-month windows while raw event volume is not.
- Figure 3: figures/Figure3_family_active_days.svg
  Shows that active days work for course-embedded assessments but not Benesse.
- Figure 4: figures/Figure4_future_placebo.svg
  Shows the future-activity placebo check.
- Supplement Figure S1: figures/supplement/FigureS1_strategy_adjusted_twfe.svg
  Shows that temporal strategy category effects shrink after behavior-feature adjustment.

## Main Tables

- Table 1: tables/table1_sample_construction.md
- Table 2: tables/table2_strategy_adjustment.md
- Table 3: tables/table1_family_active_days.md
- Table 4: tables/table4_student_course_fe_robustness.md
- Table 5: tables/table_effect_size_interpretation.md
- Table 6: tables/table3_future_placebo.md
- Data-quality flow: tables/table_data_quality_flow.md
- Supplement: tables/supp_table_grade_consistency_m12.md

## Rerunnable Analysis Code

All analysis scripts are retained in:

projects/leaf-grade-test-analysis-2026-05-19/

The paper asset generator is:

projects/leaf-grade-test-analysis-2026-05-19/26_prepare_paper_assets.py

The stricter student-course fixed-effect robustness analysis is:

projects/leaf-grade-test-analysis-2026-05-19/28_student_course_fe_robustness.py

The paper table generator for that robustness result is:

projects/leaf-grade-test-analysis-2026-05-19/29_prepare_strict_fe_table.py

The effect-size and sensitivity diagnostics are:

projects/leaf-grade-test-analysis-2026-05-19/30_effect_size_and_sensitivity.py

The English-label coverage figure generator is:

projects/leaf-grade-test-analysis-2026-05-19/31_make_english_coverage_figure.py
