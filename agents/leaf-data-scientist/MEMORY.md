# MEMORY.md

## LEAF Data Scientist Memory

### Role focus
This agent is the structured analysis specialist for LEAF platform data.
It should prioritize existing internal data, especially xAPI and relational system data, before leaning on external literature.

### Core data-access memory

#### ClickHouse xAPI server
- Host: `10.236.173.4`
- Username: `reader`
- Password: `a9847KHJLv2vK`

#### ClickHouse structure
- XAPI data is stored separately for each school LEAF instance.
- The ClickHouse server contains many databases.
- Each database typically represents a different LEAF instance's xAPI data.
- Each instance database typically contains three main tables/views:
  - `databasename.statements`
  - `databasename.statements_targets`
  - `databasename.statements_mv`

#### Meaning of ClickHouse tables
- `statements`: raw xAPI data as ingested.
- `statements_targets`: columnized/processed representation derived from statements.
- `statements_mv`: materialized view intended for analytics queries.
- Preferred analytics target: `statements_mv`.

### Application families represented in xAPI
1. **BookRoll**
   - ebook reader application
   - mainly captures student learning/activity events
   - has application-specific xAPI attributes
2. **Analysis**
   - analysis application built around BookRoll activities
3. **LMS**
   - mainly Moodle
   - can support other LMS systems through LTI

### Relational databases

#### BookRoll database
- Host: `10.236.173.145`
- Port: `33306`
- User: `reader`
- Password: `bar`
- Database: `bookroll`

#### Analysis database
- Host: `10.236.173.145`
- Port: `33308`
- User: `reader`
- Password: `bar`
- Database: `analysis_development`
- Student score table: `analysis_development.course_student_scores`

#### Moodle database
- Host: `10.236.173.145`
- Port: `33307`
- User: `reader`
- Password: `bar`
- Database: `moodle`

### Safe-query memory
- Prefer `statements_mv` for analytics instead of raw `statements` where possible.
- Treat all connections as read-only.
- Use bounded exploratory queries first.
- Avoid server-heavy wide scans, raw dumps, and unbounded joins.
- Until the user explicitly says otherwise, use only the ClickHouse database `saikyo_new` for xAPI exploration and analysis.
- For Moodle, BookRoll, and Analysis relational databases, ask the user for table/column definitions when meanings are needed; do not guess unclear schema semantics.
- Always identify the correct school/instance database before querying xAPI.
- Be explicit about whether a finding comes from ClickHouse xAPI data or one of the relational databases.

### Reproducibility memory
- Prefer Python for repeatable data processing and analysis.
- Create and use a dedicated Python virtual environment for analysis tasks.
- If the project already has a suitable virtual environment, reuse it instead of recreating one unnecessarily.
- Avoid relying on system-wide Python packages when project-specific dependencies are needed.
- Prefer trusted third-party packages from reputable, well-maintained sources.
- Use Jupyter when interactive exploration or annotated analysis is helpful.
- Preserve notebooks, Python scripts, and important SQL used in analysis.
- Keep each research project's data/code/notebooks/outputs in its own separate folder.
- CSV exports should be clearly labeled and stored in an organized way.
- Raw extracts and derived datasets should be kept distinct.
- Analysis artifacts should make it possible to verify calculations later.
- Important project locations should be recorded so work can be reaccessed later.

### Interpretation memory
- Different LEAF applications emit different xAPI patterns and attributes.
- Analyses must respect application context: BookRoll, Analysis, and LMS data should not be mixed casually.
- The same research question may require combining xAPI behavior data with relational metadata from BookRoll, Analysis, or Moodle.
- Before drawing conclusions, verify what each field actually represents in that specific system.
- In ClickHouse BookRoll/xAPI data, the student user identifier is commonly stored in `actor_account_name`.
- For BookRoll xAPI records, `actor_account_name` often looks like `2665@0122CF32-84AF-E55C-3CED-647BBC4F44A7`.
- The substring before `@` is the Moodle user ID.
- That prefix can be used as the cross-source user key to match the same learner across xAPI/ClickHouse data and Moodle-linked relational sources.
- In the Moodle database, course-related information is important for interpreting BookRoll content usage.
- BookRoll contents basically belong to courses.
- Courses vary by Japanese K-12 grade/level and by subject area (for example English, Japanese, etc.).
- Content analyses should therefore consider course context, grade/level, and subject instead of treating all contents as interchangeable.

### Data sufficiency rule
- Before using any dataset for analysis, first check how much relevant data is actually available.
- If the amount of usable data is too small, insufficiently complete, or too sparse for the intended analysis, do not use that dataset for that analysis.
- State the insufficiency clearly and either narrow the question, combine with other appropriate data sources, or stop and report the limitation.

### ClickHouse column interpretation notes
- ClickHouse table column names should generally be interpreted literally unless the user provides a special definition.
- Even when names are literal, important columns may still need explicit operational definitions before analysis.
- `_id`: ID of each record. It can contain duplicates, so analyses should check for duplicate records and avoid double-counting.
- `contents_id`: BookRoll content (PDF) ID. These IDs are unique among the databases.
- `contents_name`: BookRoll content name.
- `time_from_last_activity`: for a particular user, the time gap from that user’s previous action.

### BookRoll operation name definitions
Use the latest CSV at `/home/ubuntu/.openclaw/external-resources/new-operation-names.csv` as the current canonical working source unless better official documentation appears.
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
- Note: preserve CSV wording as given for now, including spelling issues such as `bookrooll`, `Jumo`, and `fill in black`, unless the user later wants a cleaned/normalized glossary.
