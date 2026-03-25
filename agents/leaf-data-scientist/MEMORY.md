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
- Until the user explicitly says otherwise, use only the ClickHouse database `saikyo_old` for xAPI exploration and analysis.
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

### BookRoll operation name definitions
These operation labels should be treated as canonical working definitions unless better official documentation appears.

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
