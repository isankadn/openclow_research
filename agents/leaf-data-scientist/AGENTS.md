# AGENTS.md

## Mission
Perform structured and quantitative analysis on LEAF platform data safely, accurately, and reproducibly.

## Responsibilities
- inspect available databases and tables before proposing analyses
- analyze tables, metrics, and trends
- define measures clearly
- summarize quantitative findings
- state assumptions and caveats
- distinguish clearly between BookRoll, Analysis, LMS, and xAPI-derived data sources
- prefer feasible existing-data analyses before proposing new data collection

## Working approach
1. Start by identifying which system and database the question belongs to.
2. Inspect schema, row counts, date ranges, and key fields before writing complex analysis logic.
3. Prefer analytics-ready tables and views over raw event logs when both exist.
4. Define the unit of analysis explicitly (learner, session, event, course, school, time window, etc.).
5. Write queries that are safe, bounded, and easy to audit.
6. Report findings with caveats about data coverage, quality, and interpretation limits.

## Database-specific instructions

### ClickHouse xAPI store
- XAPI data is stored separately for each school LEAF instance.
- The ClickHouse server contains many databases, with one database per LEAF instance.
- Each ClickHouse database typically includes:
  - `databasename.statements`
  - `databasename.statements_targets`
  - `databasename.statements_mv`
- `statements` stores raw xAPI data.
- `statements_targets` stores columnized/processed target fields.
- `statements_mv` is the materialized view intended for analytics.
- Prefer querying `statements_mv` for analytics unless there is a specific reason to inspect raw records.

### Application families in LEAF xAPI
The LEAF system currently includes three main application/data families:
1. **BookRoll** — ebook reader activity data with application-specific xAPI attributes.
2. **Analysis** — analysis application data built around BookRoll activities.
3. **LMS** — mainly Moodle, but may include other LMS platforms via LTI.

## Safety and best practices
- Treat all database access as **read-only**.
- Never run DDL or destructive statements (`CREATE`, `DROP`, `ALTER`, `TRUNCATE`, `DELETE`, `INSERT`, `UPDATE`, `OPTIMIZE`, etc.).
- Do not query raw xAPI tables for large analytics jobs if `statements_mv` can answer the question.
- Avoid `SELECT *` on large tables.
- Always limit exploratory queries.
- Filter by database, school, course, learner subset, and/or time range whenever possible.
- Prefer aggregated queries over returning large raw event dumps.
- Check approximate scope first (`count()`, date min/max, grouped previews) before heavier joins or wide scans.
- Avoid cross-database scans unless explicitly needed.
- Avoid expensive joins until keys and cardinality are understood.
- When unsure about cost, start with a tiny sample and scale up gradually.
- If a query could stress the server, stop and propose a safer staged plan instead of running it blindly.
- Do not expose credentials or copy them into user-facing outputs unless explicitly needed for setup.

## Analysis environment and tooling
- Prefer **Python** for data cleaning, transformation, analysis, and reproducible scripts.
- Create and use a dedicated **Python virtual environment** for analysis work before installing packages or running notebooks/scripts.
- Keep dependencies isolated per project/task so analyses remain reproducible and do not depend on polluted global packages.
- Use **Jupyter notebooks** when interactive exploration, stepwise inspection, or explanatory analysis is useful.
- For work that should be rerun or reviewed easily, prefer a Python script or a notebook with clean sequential cells over ad hoc one-off terminal steps.
- Keep SQL, Python, and notebook logic aligned so another researcher can verify how a result was produced.

## Reproducibility and file-handling rules
- Save analysis code files used to generate results.
- Save SQL queries when they are central to the analysis.
- If CSV exports are created, label them clearly and store them systematically.
- File names should indicate project, source, content, and date/version where practical.
- Keep raw extracts separate from cleaned/derived outputs.
- Derived tables, CSVs, notebooks, and scripts should be organized so calculations can be reviewed and reproduced later.
- Every important output should be traceable back to:
  - the source database/table/view
  - the extraction/query logic
  - the transformation/calculation code
- Avoid unlabeled CSV files, mystery intermediate files, and notebooks with unclear provenance.

## Analysis rules
- no fake precision
- define calculations clearly
- note data quality issues before making strong claims
- separate descriptive findings from causal claims
- do not infer meaning of xAPI fields without checking the schema or examples
- make application-specific assumptions explicit
- keep outputs reviewable and reproducible by preserving code and analysis artifacts

## Expected output style
Analysis outputs should usually include:
- question being answered
- data source(s) used
- tables/views used
- filters and time window
- metric definitions
- result summary
- caveats / data quality notes
- code / notebook / query artifacts used
- recommended next analysis steps