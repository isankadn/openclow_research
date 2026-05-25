# Review Response Check

Source review file: `paper_draft/review.md`  
Checked against: `paper_draft/manuscript_draft.md` after the May 21 revision.

## Addressed in the Manuscript

| Review concern | Current manuscript response |
| --- | --- |
| Define strong-cell and linkage criteria | Section 3 now defines the strong-cell rule explicitly: at least 100 valid outcomes, 100 students, 100 m3 same-course linked rows, and at least 50% m3 same-course coverage over clean score rows. |
| Add sample construction / inclusion flow | Table 1 now reports the path from 67,672 raw score rows to 43,180 dated rows, 42,548 valid outcomes, 14,248 strong-cell rows, 9,906 course-embedded rows, and 9,547 student-course FE rows. |
| Explain linkage validation | Section 3 explains old-source content-course linkage, unique mapping retention, exclusion of ambiguous/unmapped content, direct new-source context IDs, and the old-source dominance of current strong cells. |
| Replace Moodle-specific wording | The draft now uses Learning Management System (LMS) rather than Moodle-specific framing. |
| Reduce risky title wording | The title no longer uses “causal-cautious”; that phrase is retained only as a design interpretation with observational caveats. |
| Strengthen theory/literature framing | Section 1.1 now synthesizes trace validity, distributed practice/self-regulation, and course alignment into a coherent framing. |
| Add practical effect-size interpretation | Section 6.4 and Table 5 now translate the unstandardized student-course FE estimate into predicted differences for active-day contrasts. |
| Add robustness/sensitivity checks | Table 5 and the supporting report now include top-1% event-volume exclusion, active-day bin checks, coverage-threshold sensitivity, and a residual correlation check for log event volume vs log active days. |
| Cautious Benesse interpretation | Section 6.3 now frames the Benesse contrast as consistent with course alignment while noting test purpose, content coverage, stakes, timing, and preparation culture. |
| Add model specification details | Section 4 and Section 5 now state log(1+x), zero-activity handling, rate denominators, fixed-effect filtering, standardized vs unstandardized reporting, CI/SE approach, and student clustering. |
| Add ethics/data privacy paragraph | Section 3.1 now describes de-identified secondary analysis, local retention of row-level data, aggregate reporting, data minimization, and exclusion of uncertain links. |
| Fix presentation issues | Figure labels were regenerated in English; local file-path captions were removed; “Table 0” was renamed; equations are typeset in display math; broken control characters were checked and absent. |
| Sharpen the Best Paper “WOW” | Introduction, Discussion, and Conclusion now frame the finding as a field-level validity principle: trace meaning depends on temporal ordering, course alignment, and assessment context. |

## Remaining Author Confirmation

| Item | Why it still needs confirmation |
| --- | --- |
| Ethics/approval wording | The manuscript cannot invent the applicable institutional approval, administrative permission, or consent basis. Replace the current generic sentence with the exact approved wording before submission. |
| Venue-specific formatting | Markdown tables/figures are now cleaner, but final ICCE formatting may require Word/LaTeX/PDF-specific table sizing and figure placement. |
| Optional stronger robustness | Current robustness covers the review's feasible checks using available aggregate/model outputs. If prior-score fields or a venue-demanded two-way clustered/wild-cluster procedure become available, those could further strengthen the appendix. |

## Verification Performed

- Re-ran the paper table generator: `27_prepare_paper_summary_tables.py`.
- Re-ran the student-course FE robustness script: `28_student_course_fe_robustness.py`.
- Re-ran the strict FE table script: `29_prepare_strict_fe_table.py`.
- Re-ran the effect-size and sensitivity diagnostics: `30_effect_size_and_sensitivity.py`.
- Re-ran the English coverage figure generator: `31_make_english_coverage_figure.py`.
- Compiled all changed scripts with `python3 -m py_compile`.
- Searched the manuscript for removed/risky strings: `Causal-Cautious`, `Table 0`, `See figures/`, broken control-character patterns, and `Moodle`.

