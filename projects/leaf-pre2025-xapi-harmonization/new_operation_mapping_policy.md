# New Operation Mapping Policy

The user confirmed that post-2025/new data has additional `operation_name` types. Therefore the canonical operation layer is not simply an old-to-new rename table.

## Required categories
- `shared`: operation exists in both old and new schemas after spelling normalization.
- `old_only`: operation appears in old data but has no exact new equivalent yet.
- `new_only`: operation appears in new data but has no old equivalent.
- `renamed`: old operation maps cleanly to a differently spelled new canonical operation.
- `split_or_merged`: old and new operations differ in granularity.
- `needs_confirmation`: semantic mapping is uncertain.

## Modeling rule
For cross-era papers, prefer operation groups for broad comparisons. Use exact canonical operation names only when the mapping confidence is high or the analysis is restricted to one schema era.

## Current known examples
- `DELETE MARKER` -> `DELETE_MARKER`: renamed, high confidence.
- `ADD MARKER` -> `ADD_MARKER`: renamed, high confidence.
- `ADD MEMO` -> `ADD_MEMO`: renamed, high confidence.
- `LINK_CLICK` -> `CLICK_LINK`: renamed, high confidence.
- `REGIST CONTENTS` -> `REGISTER_CONTENTS`: renamed, medium confidence.
- `QUIZ_ANSWER` and `QUIZ_ANSWER_CORRECT` -> `ANSWER_QUIZ`: split/merged, medium confidence.
- `AUDIO_START`, `AUDIO_PAUSE`, `AUDIO_END`: old_only until a new equivalent is found.
- New operations such as fill-blank, translate, meaning-select, questionnaire, and dashboard metric names may be new_only relative to the old schema.
