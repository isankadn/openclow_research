# LEAF Data Memory

## Known so far
The lab has an existing system/application called LEAF.
It generates xPAI and other relational data.
Detailed structure has not been provided yet.

## Current remembered constraints
- Before using any dataset for analysis, first check how much relevant usable data exists.
- If data is too sparse, too small, or too incomplete for the intended analysis, do not use that dataset for that analysis.
- Report the insufficiency explicitly rather than forcing an analysis from weak data.
- Until the user explicitly says otherwise, use only the ClickHouse database `saikyo_old` for xAPI exploration and analysis.
- For Moodle, BookRoll, and Analysis relational databases, ask the user for table/column definitions when they are needed for interpretation; do not guess unclear schema semantics.

## Cross-source user matching
- Analysis student score data is in `analysis_development.course_student_scores`.
- In ClickHouse BookRoll/xAPI data, student user ID / username is commonly stored in `actor_account_name`.
- For BookRoll xAPI records, `actor_account_name` often looks like `2665@0122CF32-84AF-E55C-3CED-647BBC4F44A7`.
- The value before `@` is the Moodle `user.id`.
- That prefix can be used to match the same user across ClickHouse xAPI data and other Moodle-related relational data sources.

## Course-context interpretation
- In Moodle, course information provides important context for BookRoll content usage.
- BookRoll contents basically belong to courses.
- Courses vary by Japanese K-12 grade/level and by subject area (for example English, Japanese, etc.).
- Analyses should therefore account for course context, grade/level, and subject instead of pooling all contents together blindly.

## ClickHouse column interpretation notes
- ClickHouse table column names should generally be interpreted literally unless the user provides a special definition.
- Even when names are literal, important columns may still need explicit operational definitions before analysis.
- `_id`: ID of each record. It can contain duplicates, so analyses should check for duplicate records and avoid double-counting.
- `contents_id`: BookRoll content (PDF) ID. These IDs are unique among the databases.
- `contents_name`: BookRoll content name.
- `time_from_last_activity`: for a particular user, the time gap from that user’s previous action.

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
