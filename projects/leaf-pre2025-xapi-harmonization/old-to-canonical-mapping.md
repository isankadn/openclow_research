# Old-To-Canonical XAPI Mapping

## Purpose
This is the formal working mapping for harmonizing pre-2025 `saikyo_old.statements_mv` events into a canonical event model. It is intended for reproducible analysis scripts and for deciding which variables are safe for the paper analysis.

## Source And Boundary
- Old source: ClickHouse `saikyo_old.statements_mv`.
- Old analysis period: before 2025-04-01.
- Reason for separation: Japanese academic year starts April 1, and the ebookreader/xAPI format changed from 2025-04-01.
- New source may contain additional `operation_name` types; canonical mapping must preserve old-only, new-only, and shared operations.

## Canonical Event Model
| Canonical field | Old source column(s) | Transformation | Confidence | Notes |
|---|---|---|---|---|
| `source_system` | `actor_account_homePage`, `platform` | classify URL family first, platform second | high | Old BookRoll often has blank platform. |
| `source_schema` | constant | `old_pre_2025` | high | Keeps old/new schemas separated. |
| `statement_id` | `statement_id` | direct | high | Raw xAPI statement UUID. |
| `event_row_id` | `_id` | trim fixed-string padding if needed | high | Internal materialized-view row ID. |
| `event_hash` | `hash` | trim fixed-string padding if needed | high | Fingerprint/hash. |
| `student_moodle_id` | `actor_account_name` | take prefix before `@`; if no `@`, use value as-is | high | Candidate join key to Moodle/grade data. |
| `actor_account_raw` | `actor_account_name` | direct | high | Preserve full account string. |
| `actor_role_raw` | `actor_name_role` | direct | medium | Old role labels may be blank or use Learner/Instructor. |
| `actor_role_canonical` | `actor_name_role` | Learner -> student, Instructor -> teacher, admin -> admin | medium | Blank role should be inferred only from event family if needed. |
| `event_time` | `timestamp` | direct | high | Use for behavior windows. |
| `stored_time` | `stored` | direct | high | Ingestion/storage time, not learning time. |
| `operation_raw` | `operation_name` | direct | high | Preserve old spelling. |
| `process_code_raw` | `process_code` | direct | high | Supporting operation code; not always one-to-one. |
| `operation_canonical` | `operation_name`, `process_code`, `verb_display_en` | use operation crosswalk | medium/high | Confidence varies by operation. |
| `operation_group` | mapped | use operation crosswalk group | medium/high | Prefer for cross-era comparisons. |
| `verb_raw` | `verb_id`, `verb_display_en` | direct | high | Useful for score/Moodle/quiz. |
| `content_id` | `contents_id`, `object_definition_description_en` | prefer `contents_id`; fallback only after validation | high for contents_id | Old object description often equals content hash. |
| `content_name` | `contents_name`, `object_definition_name_en` | prefer `contents_name` | high | Object name may be content title or score item. |
| `page_no` | `page_no` | parse numeric/string page if needed | high | Page-specific BookRoll events. |
| `course_id` | `context_id` | direct only when non-empty | low/medium | Sparse in old BookRoll; relational joins likely needed. |
| `course_name` | `context_title`, `context_label` | direct only when non-empty | low/medium | Sparse in old BookRoll. |
| `result_success` | `results_success` | direct 0/1 | high | Interpret by event family. |
| `result_response` | `results_response` | direct | medium | Can contain answer/score/text response. |
| `marker_payload` | `marker_color`, `marker_position`, `marker_text` | preserve as raw marker fields | high | Use only for marker analyses. |
| `memo_payload` | `memo_text`, `memo_hand`, `memo_hand_bg`, `canvas`, `lineColor` | preserve raw, avoid sending large payloads to AI | high | May include base64 image data. |
| `mapping_confidence` | generated | high/medium/low/needs_confirmation | high | Required for reproducibility. |

## Source-System Classification
| Rule | Canonical `source_system` | Notes |
|---|---|---|
| `actor_account_homePage` contains `bookroll` | `bookroll_old` | Primary rule for old ebookreader behavior. |
| `actor_account_homePage` contains `moodle` and not `#score` | `moodle_old` | LMS events. |
| `actor_account_homePage` contains `#score` | `analysis_score_old` | Grade/score xAPI-like events. |
| `actor_account_homePage` contains `analysis` and not `#score` | `analysis_old` | Analysis/dashboard-like events. |
| `platform` is `LogPalette` or `Log Palette` | `logpalette_old` | Dashboard/analytics events. |
| otherwise | `unknown_old` | Do not use for modeling until reviewed. |

## Analysis Guidance
- For cross-era behavior analysis, use `operation_group` first, then high-confidence `operation_canonical` where needed.
- For outcome-linked modeling, require confirmed overlap between score rows, `student_moodle_id`, course/context mapping, and pre-test event windows.
- Do not use sparse old `context_id` alone to claim course linkage for all BookRoll events.
- Keep raw old fields in derived datasets so mappings can be audited.
