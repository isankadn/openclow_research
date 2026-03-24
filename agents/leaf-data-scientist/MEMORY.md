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
- CSV exports should be clearly labeled and stored in an organized way.
- Raw extracts and derived datasets should be kept distinct.
- Analysis artifacts should make it possible to verify calculations later.

### Interpretation memory
- Different LEAF applications emit different xAPI patterns and attributes.
- Analyses must respect application context: BookRoll, Analysis, and LMS data should not be mixed casually.
- The same research question may require combining xAPI behavior data with relational metadata from BookRoll, Analysis, or Moodle.
- Before drawing conclusions, verify what each field actually represents in that specific system.