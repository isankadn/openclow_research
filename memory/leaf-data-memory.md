# LEAF Data Memory

## Known so far
The lab has an existing system/application called LEAF.
It generates xPAI and other relational data.
Detailed structure has not been provided yet.

## Current remembered constraints
- Before using any dataset for analysis, first check how much relevant usable data exists.
- If data is too sparse, too small, or too incomplete for the intended analysis, do not use that dataset for that analysis.
- Report the insufficiency explicitly rather than forcing an analysis from weak data.

## BookRoll operation name definitions
Use these as working definitions for operation/event names unless superseded by better official documentation.

- `OPEN`: open the page/content
- `GETIT`: content understood / learner indicates understanding
- `ADD MEMO`: add text memo using keyboard
- `CLOSE`: close the page
- `PREV`: go to previous page
- `NOTGETIT`: content not understood / learner indicates non-understanding
- `NEXT`: go to next page
- `SEARCH`: search in the ebook
- `AUDIO_START`: start audio playback
- `DELETE BOOKMARK`: delete bookmark
- `ADD_HW_MEMO`: add handwriting memo
- `PAGE_JUMP`: move to another page by number selection
- `ADD BOOKMARK`: add bookmark
- `QUIZ_ANSWER`: answer quiz in BookRoll
- `MEMO_JUMP`: jump to another memo
- `DELETE_MEMO`: delete memo
- `TIMER_START`: start page timer
- `LINK_CLICK`: click links or reference links
- `SUBMIT CONTENTS`: submit contents
- `CHANGE MEMO`: change existing memo
- `DELETE MARKER`: delete marker
- `ADD MARKER`: add marker using marker tool; marker types include yellow and red
- `CHANGE_SVG_PATH`: change SVG path
- `DELETE CONTENTS`: delete contents
- `AUDIO_PAUSE`: pause audio playback
- `AUDIO_END`: end audio playback
- `TIMER_PAUSE`: pause page timer
- `REGIST CONTENTS`: register contents, mostly by teacher or admin
- `SEARCH_JUMP`: jump to a search result
- `REDO_HW_MEMO`: redo handwriting memo
- `UNDO_HW_MEMO`: undo handwriting memo
- `ADD_SVG_PATH`: add SVG path
- `BOOKMARK_JUMP`: jump to bookmark
- `TIMER_STOP`: stop page timer
- `CLEAR_HW_MEMO`: clear handwriting memo
- `MEMO_TEXT_CHANGE_HISTORY`: memo text change history event
- `OPEN_RECOMMENDATION`: open recommendation panel/content
- `CLOSE_RECOMMENDATION`: close recommendation panel/content
- `CLICK_RECOMMENDATION`: click recommendation
- `DELETE_RECOMMENDATION`: delete recommendation
- `ADD_RECOMMENDATION`: add recommendation
- `QUIZ_ANSWER_CORRECT`: quiz answer correctness event

## Expected future memory here
When the user provides more detail, record:
- system/module names
- dataset names
- schema summaries
- key entities and relationships
- IDs and time fields
- what each data source measures
- known data quality limits
