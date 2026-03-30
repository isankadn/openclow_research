# LEAF Data Memory

## Known so far
The lab has an existing system/application called LEAF.
It generates xPAI and other relational data.
Detailed structure has not been provided yet.

## Current remembered constraints
- Before using any dataset for analysis, first check how much relevant usable data exists.
- If data is too sparse, too small, or too incomplete for the intended analysis, do not use that dataset for that analysis.
- Report the insufficiency explicitly rather than forcing an analysis from weak data.
- Until the user explicitly says otherwise, use only the ClickHouse database `saikyo_new` for xAPI exploration and analysis.
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
- `platform`: platform name, such as BookRoll, Moodle, Logpalette, GOAL, SCROLL, etc.
- `actor_name_role`: user role, such as teacher, student, admin, etc.
- `context_id`: Moodle course ID.
- `context_title`: Moodle course name.
- `context_label`: Moodle course name.

## BookRoll operation name definitions
Use the latest CSV at `/home/ubuntu/.openclaw/external-resources/new-operation-names.csv` as the current canonical working source unless superseded by better official documentation.
Use only the new operation names and definitions from that CSV going forward; do not retain or rely on older saved name variants.
It includes both learner/content actions and `#...` dashboard/aggregate metric names.

- `OPEN`: Open new PDF content
- `ZOOM_FIT`: Zoom the ebook reader to fit into user screen
- `ADD_MEMO`: Add memo
- `ADD_QUIZ`: Add quiz
- `ZOOM_IN`: Click zoom in button
- `CLOSE`: Close PDF content
- `PREV`: Move to previous page
- `LOGOUT`: Logout from the bookrooll application
- `NEXT`: Move to next page
- `ZOOM_OUT`: Click the Zoom out button
- `SEARCH`: Search bookroll contents
- `LOGIN`: Login to bookroll
- `#browsing-time`: definition not provided in CSV
- `EXCLUDE_CONTENTS`: Exclude contents from class
- `#activity-view`: definition not provided in CSV
- `CHANGE_SVG_TEXT`: Change SVG text
- `ADD_HW_MEMO`: Add hand writing memo
- `PAGE_JUMP`: Jump to another page
- `CLEAR_HW_QUIZ`: Clear hand writing quiz
- `ERASE_HW_MEMO`: Erase hand writing memo
- `#daily-view-time`: definition not provided in CSV
- `#page-view`: definition not provided in CSV
- `MEMO_JUMP`: Jumo to another memo
- `ADD_BOOKMARK`: Add a bookmark
- `#character-count`: definition not provided in CSV
- `EDIT_CONTENTS`: Edit content metadata
- `CHANGE_HW_CANVAS`: Change hand writing
- `DELETE_MEMO`: Delete memo
- `TIMER_START`: Click and start timer on the page
- `CLOSE_FILL_BLANK`: Close fill blank question
- `ADD_HW_CANVAS`: Add handwriting canvas
- `ADD_MARKER`: Add marker
- `ANSWER_QUIZ`: Answer quiz
- `REMOVE_FAVORITE`: Remove from Favorite
- `#feedback`: definition not provided in CSV
- `ADD_HW_QUIZ`: Add hand writing quiz
- `START_FILL_BLANK`: Start fill blank question
- `DELETE_CONTENTS`: Delete pdf contents
- `#marker-list`: definition not provided in CSV
- `EDIT_QUIZ`: Edit quiz
- `#student-table`: definition not provided in CSV
- `CHANGE_SVG_PATH`: Change SVG path
- `OPEN_FILL_BLANK`: Open fill in black question
- `CLICK_LINK`: Click link
- `DELETE_QUIZ`: Delete quiz
- `#memo-list`: definition not provided in CSV
- `DELETE_HW_CANVAS`: Delete hand writing canvas
- `CHANGE_MEMO`: Change memo
- `UNDO_SVG_PATH`: Undo SVG path
- `REDO_SVG_PATH`: Redo SVG path
- `MEANING_SELECT`: Meaning select
- `TRANSLATE`: Use translate
- `#attain-grade`: definition not provided in CSV
- `CLOSE_QUIZ`: Close quiz
- `DELETE_SVG_TEXT`: Delete SVG text
- `ZOOM_FULL`: Zoom in to full
- `DELETE_MARKER`: Delete marker
- `TIMER_PAUSE`: Pause timer
- `DELETE_BOOKMARK`: Delete book mark
- `SEARCH_JUMP`: Search jump
- `DELETE_SVG_PATH`: Delete SVG path
- `#memo-count`: definition not provided in CSV
- `ADD_SVG_TEXT`: Add SVG text
- `ADD_FAVORITE`: Add favorite
- `OPEN_QUIZ`: Open quiz
- `#student-view`: definition not provided in CSV
- `#page-thumbnail`: definition not provided in CSV
- `#student-chart`: definition not provided in CSV
- `UNDO_HW_MEMO`: Undo hand writing memo
- `REDO_HW_MEMO`: Redo hand writing memo
- `ADD_SVG_PATH`: Add SVG path
- `TIMER_STOP`: Stop timer
- `CLEAR_HW_MEMO`: Clear hand writing memo
- `#marker-count`: definition not provided in CSV
- `#hourly-view-time`: definition not provided in CSV
- `MEMO_TEXT_CHANGE_HISTORY`: Check memo text change history
- `EDIT_QUESTIONNAIRE`: Edit questionnaire
- `#weekly-view-time`: definition not provided in CSV
- `ADD_QUESTIONNAIRE`: Add questionnaire
- `OPEN_RECOMMENDATION`: Open recommendation
- `CLOSE_RECOMMENDATION`: Close recommendation
- `CLICK_RECOMMENDATION`: Click recommendation
- `ANSWER_FILL_BLANK`: Answer fill in black question
- `#select-past-senior`: definition not provided in CSV
- `DELETE_RECOMMENDATION`: Delete recommendation
- `DELETE_QUESTIONNAIRE`: Delete questionnaire
- `#context-selector`: definition not provided in CSV
- `REGISTER_CONTENTS`: Register contents
- `ADD_RECOMMENDATION`: Add recommendation
- `OPEN_QUESTIONNAIRE`: Open questionnaire
- `CLOSE_QUESTIONNAIRE`: Close questionnaire
- `ANSWER_QUESTIONNAIRE`: Answer questionnaire
- `#select-old-dashboard`: definition not provided in CSV
- `#monthly-view-time`: definition not provided in CSV
- `EDIT_RECOMMENDATION`: Edit recommendation
- `#select-current-peer`: definition not provided in CSV
- `#download-page-stats`: definition not provided in CSV
- `#select-past-senior-comparison`: definition not provided in CSV
- `#save-comment-past-senior`: definition not provided in CSV
- `#save-comment-current-peer`: definition not provided in CSV
- `#select-current-peer-comparison`: definition not provided in CSV

## Expected future memory here
When the user provides more detail, record:
- system/module names
- dataset names
- schema summaries
- key entities and relationships
- IDs and time fields
- what each data source measures
- known data quality limits
