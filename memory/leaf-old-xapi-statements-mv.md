# LEAF Old XAPI - saikyo_old.statements_mv

## Status
These definitions are accepted working memory as of 2026-05-19 after bounded profiling of ClickHouse `saikyo_old.statements_mv` and user confirmation.

## Scope
- Source table: `saikyo_old.statements_mv`.
- Intended use: pre-2025-04-01 ebookreader/xAPI analysis.
- Japanese academic-year rule: April 1 through March 31.
- Ebookreader/xAPI format changed from 2025-04-01; old and new xAPI must be harmonized before combined analysis.
- Bounded profile used: `timestamp >= 2019-01-01` and `timestamp < 2025-04-01`.

## High-level profile from bounded inspection
- Rows in pre-2025 bounded window: 101,204,086.
- Timestamp range: 2019-01-18 to 2025-03-31.
- Actor accounts: 7,923.
- Content IDs: 13,292.
- Operation names: 43 distinct `operation_name` values in the table-level profile.
- Platform values are incomplete for old BookRoll events; many BookRoll rows have blank `platform`.
- `actor_account_homePage` is the more reliable old-data source-system discriminator.
- After the 2026-05-24 reimport, old Bookroll content events have `context_id`, `context_title`, and `context_label` populated for nearly all relevant rows. A bounded audit of Bookroll rows with non-empty `operation_name` and `contents_id` from 2019-01-01 to before 2025-04-01 found 46,633,944 of 46,701,509 rows with `context_id` (99.86%). Use ClickHouse `context_id` directly as the primary course-link method for same-course analysis.
- As clarified on 2026-05-24, `empty(operation_name)` and `empty(contents_id)` each return about 24,937,088 rows in `saikyo_old.statements_mv`. These are expected Moodle/LMS and Analysis application records that do not carry Bookroll-specific `operation_name`/`contents_id` fields, not evidence that Bookroll reading events are missing those fields.

## Source-system identification rule
For `saikyo_old`, derive source family primarily from `actor_account_homePage`, with `platform` as a secondary hint.

Observed source families include:
- BookRoll/ebookreader: `actor_account_homePage` contains `bookroll`; many of these rows have blank `platform`.
- Moodle/LMS: `actor_account_homePage` contains `moodle`, often with `platform = Moodle`.
- Analysis/score-like events: `actor_account_homePage` contains Analysis URLs or `#score`.
- LogPalette/Analysis dashboard-like data: `platform` may be `LogPalette` or `Log Palette`.
- For Bookroll behavior analysis, filter to Bookroll/ebookreader source rows before applying `notEmpty(operation_name)` or `notEmpty(contents_id)`; blank Bookroll-specific fields are normal for Moodle/LMS and Analysis source families.

## Working column definitions

### Identity / raw statement
- `_id`: internal event-row identifier in the materialized view; not a semantic research variable by itself.
- `hash`: hash/fingerprint associated with the statement/event.
- `statement_id`: original xAPI statement UUID.
- `version`: xAPI statement version; observed mostly `1.0.0`.
- `log_id`: application-side log identifier for old BookRoll events.
- `uniqId`: application-specific unique identifier, often for memo/marker/canvas-like objects.
- `parentid`: parent object identifier for nested application objects.

### Actor / user
- `actor_name_id`: human-readable actor name/name field where present; not the stable join key.
- `actor_name_role`: actor role label. Old rows may use `Learner`, `Instructor`, `admin`, or blank.
- `actor_objectType`: xAPI actor object type; observed as `Agent`.
- `actor_account_name`: main user/account identifier. For BookRoll, commonly `moodle_user_id@tenant_uuid`; for Moodle it may be only the Moodle user ID. Extract prefix before `@` for the Moodle-user join key.
- `actor_account_homePage`: account namespace/source URL. Critical for source-family classification in old data.

### Verb / operation
- `verb_id`: full xAPI verb URI.
- `verb_display_en`: English xAPI verb label. Useful for Moodle/Analysis/quiz events, often blank for old BookRoll operation rows.
- `operation_name`: application-specific action name. Main BookRoll behavior column.
- `process_code`: old application process/action code corresponding closely to `operation_name`, but not always one-to-one. Use `operation_name` as primary and `process_code` as supporting evidence.
- `description`: operation-specific payload/detail; interpret by operation type only.

### Object / content
- `object_objectType`: xAPI object type; observed as `Activity`.
- `object_id`: full target URL/IRI. Moodle rows may contain course URLs; BookRoll rows may contain content URLs.
- `object_definition_name_en`: target label/name. In BookRoll this is often the content title; in score-like rows it can be the test/score item name.
- `object_definition_description_en`: in old BookRoll, often stores the content ID/hash.
- `contents_id`: BookRoll/ebook content identifier. Strong content key.
- `contents_name`: BookRoll/ebook content title/name.
- `page_no`: page number within the content.
- `object_version`: content/object version when populated.
- `title`: nested item/problem/content title when populated.

### Annotation / learner artifact payload
- `marker_color`: highlight/marker color.
- `marker_position`: highlight/marker coordinate or range payload.
- `marker_text`: selected/highlighted text.
- `memo_text`: text memo payload. May include embedded base64 image data; handle carefully.
- `memo_hand`: handwritten memo payload/reference, often base64 PNG.
- `memo_hand_bg`: handwriting memo background data/reference when present.
- `canvas`: canvas or drawing size/coordinate payload.
- `lineColor`: drawing/handwriting line color.

### Course / context
- `context_id`: Moodle/course context ID. After the 2026-05-24 reimport, this is populated for nearly all old Bookroll content events and should be the primary same-course linkage field.
- `context_title`: Moodle/course name when `context_id` is available.
- `context_label`: Moodle/course name/label, usually similar to `context_title`.
- `school_id`: not useful in the bounded profile.
- `competency1`, `competency2`, `competency3`: not useful in the bounded profile.

### Result / score / response
- `results_success`: xAPI result success flag stored as 0/1.
- `results_response`: response payload; can contain quiz answer, score, or text response depending on event type.
- Score-like Analysis events can be identified by `actor_account_homePage` containing `#score` and `verb_display_en = attained grade for`.
- In score-like rows, `object_definition_name_en` may contain test/score labels such as `前期中間-total(min:0, max:100)`, `前期期末`, or `後期中間`.

### Authority / time / ingestion
- `authority_objectType`: xAPI authority object type; observed as `Agent`.
- `authority_name`: authority/client name, mostly `New Client`, sometimes `default`.
- `authority_mbox`: authority mailbox identifier.
- `timestamp_raw`: raw source timestamp string.
- `timestamp`: parsed event timestamp. Use this for behavior windows.
- `stored`: ingestion/storage timestamp.
- `is_parsed`: parse flag; observed as 1 for all rows in the bounded profile.
- `time_from_last_activity`: not useful in old data from the bounded sample; observed as 0 in sample.

## Canonical-event mapping rule
Map old events into a canonical event model with raw values preserved:
- `source_system`: derived from `actor_account_homePage` plus `platform`.
- `student_moodle_id`: prefix of `actor_account_name` before `@`.
- `event_time`: `timestamp`.
- `operation_raw`: original `operation_name`.
- `process_code_raw`: original `process_code`.
- `operation_canonical`: mapped operation name from the formal crosswalk.
- `operation_group`: navigation, annotation, memo, quiz, timer, recommendation, content_admin, audio, feedback, score, lms, dashboard, or unknown.
- `content_id`: `contents_id`.
- `content_name`: `contents_name`, falling back to `object_definition_name_en` where appropriate.
- `page_no`: `page_no`.
- `course_id`: `context_id` when present; otherwise resolve through old BookRoll/Moodle relational metadata before using in outcome analysis.
- `mapping_confidence`: high, medium, low, or needs_confirmation.

## Operation harmonization rule
- New data has additional `operation_name` types not present in old data.
- Old data also has old-only names and spellings.
- The canonical operation layer must therefore support shared, old-only, and new-only operations.
- For combined pre/post-2025 analysis, do not compare raw `operation_name` directly. Compare canonical operation groups or high-confidence canonical names.
