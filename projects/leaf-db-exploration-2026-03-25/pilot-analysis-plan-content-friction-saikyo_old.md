# Pilot analysis plan

## Project
**Content-level friction diagnostics across Japanese K-12 courses using BookRoll traces**

## Data scope for pilot
- **Primary source:** ClickHouse `saikyo_old.statements_mv`
- **Current rule:** use only `saikyo_old` unless explicitly told otherwise
- **Current objective:** build a first pilot that is simple, interpretable, and defensible
- **Initial principle:** start with xAPI-only content diagnostics before adding relational joins

## Pilot aim
To produce a first, evidence-grounded content-level friction scan that:
1. cleans and profiles the usable xAPI data
2. builds candidate content-level friction variables
3. identifies a small set of likely high-friction contents
4. produces 3–5 interpretable figures
5. clarifies what relational metadata is needed next

---

# 1. Pilot questions

## PQ1
Which contents in `saikyo_old` show unusually high behavioral friction signals?

## PQ2
Which variables appear most useful for distinguishing likely friction from ordinary engagement?

## PQ3
What minimum metadata from Moodle / BookRoll is needed to interpret those contents correctly by course, subject, and grade level?

---

# 2. Unit of analysis

## Primary unit
- `contents_id`

## Secondary units
- `actor_account_name`
- optionally content × user
- later: content × course / subject / grade-level (after mapping is confirmed)

Rationale:
- `contents_id` is a BookRoll content/PDF ID and is unique among databases
- content-level is the target unit for friction diagnostics

---

# 3. Data quality rules for pilot

## Must-handle rules
1. `_id` can have duplicates
   - do not blindly count raw rows if duplicates are possible
   - where possible, compare `count()` vs `uniqExact(_id)`
2. blank `operation_name` must be profiled before analysis
3. anomalous timestamps must be excluded or isolated
   - obvious 1970 artifacts
   - obvious future-date anomalies
4. content-level metrics should only be computed for contents with enough data
   - use a minimum threshold on unique users and total events

## Proposed timestamp filter for pilot
Use rows where:
- `timestamp >= toDateTime('2019-01-01 00:00:00')`
- `timestamp < now() + INTERVAL 1 DAY`

This can be adjusted, but it removes the clearly anomalous early rows.

---

# 4. Exact first queries

Below are the exact first-pass ClickHouse queries I would run.

## Q1. Dataset sanity profile
Purpose:
- establish usable scale after timestamp filtering
- check duplicate risk
- quantify blank operation names

```sql
SELECT
    count() AS raw_rows,
    uniqExact(_id) AS uniq_record_ids,
    count() - uniqExact(_id) AS duplicate_row_gap,
    min(timestamp) AS min_ts,
    max(timestamp) AS max_ts,
    uniqExact(actor_account_name) AS uniq_users,
    uniqExact(contents_id) AS uniq_contents,
    uniqExact(operation_name) AS uniq_ops,
    countIf(operation_name = '' OR operation_name IS NULL) AS blank_op_rows
FROM saikyo_old.statements_mv
WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
  AND timestamp < now() + INTERVAL 1 DAY;
```

## Q2. Operation profile after filtering
Purpose:
- see the event mix used in the pilot
- decide which operations are stable enough to model

```sql
SELECT
    operation_name,
    count() AS rows,
    uniqExact(_id) AS uniq_record_ids,
    uniqExact(actor_account_name) AS uniq_users,
    uniqExact(contents_id) AS uniq_contents
FROM saikyo_old.statements_mv
WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
  AND timestamp < now() + INTERVAL 1 DAY
GROUP BY operation_name
ORDER BY rows DESC;
```

## Q3. Content coverage distribution
Purpose:
- determine thresholds for “enough data” at content level

```sql
SELECT
    contents_id,
    any(contents_name) AS contents_name,
    count() AS raw_events,
    uniqExact(_id) AS uniq_events,
    uniqExact(actor_account_name) AS uniq_users,
    min(timestamp) AS first_ts,
    max(timestamp) AS last_ts
FROM saikyo_old.statements_mv
WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
  AND timestamp < now() + INTERVAL 1 DAY
  AND contents_id != ''
GROUP BY contents_id
ORDER BY uniq_events DESC
LIMIT 200;
```

## Q4. Candidate content-level feature extraction
Purpose:
- build first-pass friction variables per content

```sql
SELECT
    contents_id,
    any(contents_name) AS contents_name,
    uniqExact(_id) AS uniq_events,
    uniqExact(actor_account_name) AS uniq_users,

    countIf(operation_name = 'NEXT') AS n_next,
    countIf(operation_name = 'PREV') AS n_prev,
    countIf(operation_name = 'PAGE_JUMP') AS n_page_jump,
    countIf(operation_name = 'BOOKMARK_JUMP') AS n_bookmark_jump,

    countIf(operation_name = 'ADD MEMO') AS n_add_memo,
    countIf(operation_name = 'CHANGE MEMO') AS n_change_memo,
    countIf(operation_name = 'ADD_HW_MEMO') AS n_add_hw_memo,
    countIf(operation_name = 'ADD MARKER') AS n_add_marker,
    countIf(operation_name = 'DELETE MARKER') AS n_delete_marker,

    countIf(operation_name = 'OPEN_RECOMMENDATION') AS n_open_rec,
    countIf(operation_name = 'CLICK_RECOMMENDATION') AS n_click_rec,
    countIf(operation_name = 'CLOSE_RECOMMENDATION') AS n_close_rec,

    countIf(operation_name = 'QUIZ_ANSWER') AS n_quiz_answer,
    countIf(operation_name = 'QUIZ_ANSWER_CORRECT') AS n_quiz_correct,

    avgIf(time_from_last_activity, time_from_last_activity IS NOT NULL) AS avg_gap,
    medianIf(time_from_last_activity, time_from_last_activity IS NOT NULL) AS median_gap,

    min(timestamp) AS first_ts,
    max(timestamp) AS last_ts
FROM saikyo_old.statements_mv
WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
  AND timestamp < now() + INTERVAL 1 DAY
  AND contents_id != ''
GROUP BY contents_id
HAVING uniq_users >= 30
   AND uniq_events >= 300
ORDER BY uniq_events DESC;
```

## Q5. Derived normalized metrics for candidate friction ranking
Purpose:
- avoid favoring high-volume contents only
- create interpretable rates per content

```sql
WITH content_features AS (
    SELECT
        contents_id,
        any(contents_name) AS contents_name,
        uniqExact(_id) AS uniq_events,
        uniqExact(actor_account_name) AS uniq_users,
        countIf(operation_name = 'NEXT') AS n_next,
        countIf(operation_name = 'PREV') AS n_prev,
        countIf(operation_name = 'PAGE_JUMP') AS n_page_jump,
        countIf(operation_name = 'BOOKMARK_JUMP') AS n_bookmark_jump,
        countIf(operation_name IN ('ADD MEMO','CHANGE MEMO','ADD_HW_MEMO')) AS n_memo,
        countIf(operation_name IN ('ADD MARKER','DELETE MARKER')) AS n_marker,
        countIf(operation_name = 'OPEN_RECOMMENDATION') AS n_open_rec,
        countIf(operation_name = 'CLICK_RECOMMENDATION') AS n_click_rec,
        countIf(operation_name IN ('QUIZ_ANSWER','QUIZ_ANSWER_CORRECT')) AS n_quiz,
        medianIf(time_from_last_activity, time_from_last_activity IS NOT NULL) AS median_gap
    FROM saikyo_old.statements_mv
    WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
      AND timestamp < now() + INTERVAL 1 DAY
      AND contents_id != ''
    GROUP BY contents_id
    HAVING uniq_users >= 30
       AND uniq_events >= 300
)
SELECT
    contents_id,
    contents_name,
    uniq_events,
    uniq_users,
    round((n_prev + n_page_jump + n_bookmark_jump) / uniq_events, 4) AS nav_instability_rate,
    round(n_memo / uniq_events, 4) AS memo_rate,
    round(n_marker / uniq_events, 4) AS marker_rate,
    round(n_open_rec / uniq_events, 4) AS rec_open_rate,
    round(if(n_open_rec = 0, 0, n_click_rec / n_open_rec), 4) AS rec_click_through_rate,
    round(n_quiz / uniq_events, 4) AS quiz_rate,
    median_gap
FROM content_features
ORDER BY nav_instability_rate DESC, memo_rate DESC
LIMIT 200;
```

## Q6. User-level concentration check for top candidate contents
Purpose:
- avoid falsely calling a content “high friction” when only a tiny number of users generate the events

```sql
WITH top_contents AS (
    SELECT contents_id
    FROM (
        SELECT
            contents_id,
            uniqExact(_id) AS uniq_events,
            uniqExact(actor_account_name) AS uniq_users,
            (countIf(operation_name = 'PREV') + countIf(operation_name = 'PAGE_JUMP') + countIf(operation_name = 'BOOKMARK_JUMP')) / uniqExact(_id) AS nav_instability_rate
        FROM saikyo_old.statements_mv
        WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
          AND timestamp < now() + INTERVAL 1 DAY
          AND contents_id != ''
        GROUP BY contents_id
        HAVING uniq_users >= 30
           AND uniq_events >= 300
        ORDER BY nav_instability_rate DESC
        LIMIT 20
    )
)
SELECT
    contents_id,
    actor_account_name,
    uniqExact(_id) AS user_events,
    countIf(operation_name = 'PREV') AS n_prev,
    countIf(operation_name = 'PAGE_JUMP') AS n_page_jump,
    countIf(operation_name IN ('ADD MEMO','CHANGE MEMO','ADD_HW_MEMO')) AS n_memo,
    countIf(operation_name = 'OPEN_RECOMMENDATION') AS n_open_rec
FROM saikyo_old.statements_mv
WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
  AND timestamp < now() + INTERVAL 1 DAY
  AND contents_id IN top_contents
GROUP BY contents_id, actor_account_name
ORDER BY contents_id, user_events DESC;
```

## Q7. Top candidate content event sequence summary
Purpose:
- inspect whether candidate friction contents truly show unstable navigation / support behavior

```sql
SELECT
    contents_id,
    any(contents_name) AS contents_name,
    operation_name,
    count() AS rows,
    uniqExact(actor_account_name) AS uniq_users
FROM saikyo_old.statements_mv
WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
  AND timestamp < now() + INTERVAL 1 DAY
  AND contents_id IN (
      /* replace with shortlisted contents_id values from Q5/Q6 */
  )
GROUP BY contents_id, operation_name
ORDER BY contents_id, rows DESC;
```

---

# 5. Exact pilot variables

## A. Core identifiers
- `_id`
- `actor_account_name`
- `contents_id`
- `contents_name`
- `timestamp`
- `operation_name`

## B. Coverage variables
- `uniq_events`
- `uniq_users`
- `first_ts`
- `last_ts`
- active span in days

## C. Navigation variables
- `n_next`
- `n_prev`
- `n_page_jump`
- `n_bookmark_jump`
- `nav_instability_rate = (n_prev + n_page_jump + n_bookmark_jump) / uniq_events`
- `prev_next_ratio = n_prev / nullIf(n_next, 0)`

## D. Annotation variables
- `n_add_memo`
- `n_change_memo`
- `n_add_hw_memo`
- `n_add_marker`
- `n_delete_marker`
- `memo_rate`
- `marker_rate`

## E. Support / recommendation variables
- `n_open_rec`
- `n_click_rec`
- `n_close_rec`
- `rec_open_rate`
- `rec_click_through_rate = n_click_rec / nullIf(n_open_rec, 0)`

## F. Assessment variables
- `n_quiz_answer`
- `n_quiz_correct`
- `quiz_rate`
- possible `quiz_correct_rate = n_quiz_correct / nullIf(n_quiz_answer, 0)`
  - interpret carefully because exact semantics may need confirmation

## G. Timing variables
- `avg_gap`
- `median_gap`
- optional gap percentiles

## H. Candidate pilot friction score
For pilot use only, define a simple provisional score:

```text
pilot_friction_score
= z(nav_instability_rate)
+ z(memo_rate)
+ z(rec_open_rate)
+ z(median_gap)
- z(rec_click_through_rate)
```

Notes:
- This is a provisional heuristic, not a final scientific construct.
- Standardize within the selected content subset.
- Consider a robust z-score if distributions are heavily skewed.

---

# 6. Inclusion thresholds for pilot contents

To reduce noise, analyze only contents with:
- `uniq_users >= 30`
- `uniq_events >= 300`

These thresholds can be revised after Q3.

Why:
- prevents overinterpreting small-sample contents
- follows the existing LEAF rule to avoid using insufficient data

---

# 7. First figure set

## Figure 1. Data quality and event mix overview
**Type:** bar chart

Show:
- top operation counts after filtering
- optionally annotate blank operation rows and duplicate-row gap summary

Purpose:
- gives a clean overview of what the pilot is actually built from

## Figure 2. Content coverage scatterplot
**Type:** scatter plot

Axes:
- x = unique users per content
- y = unique events per content

Highlight:
- included vs excluded contents by threshold

Purpose:
- justifies threshold choice
- shows pilot is based on sufficiently populated contents

## Figure 3. Friction signature heatmap for shortlisted contents
**Type:** heatmap

Rows:
- top 20 candidate contents

Columns:
- nav instability
- memo rate
- marker rate
- rec open rate
- rec click-through rate
- quiz rate
- median gap

Purpose:
- reveals whether “high-friction” contents share consistent multi-signal patterns

## Figure 4. Shortlisted content profile cards
**Type:** small multiples / ranked bars

For each top content:
- title / contents_id
- unique users
- unique events
- friction score
- top event mix

Purpose:
- makes candidate contents interpretable for human review

## Figure 5. User concentration plot for top friction contents
**Type:** Lorenz-style or ranked user contribution plot

Purpose:
- shows whether a content’s friction is broad-based or driven by a few extreme users

Optional if time allows:

## Figure 6. Timeline density plot for top 10 contents
**Type:** monthly activity trend or density plot

Purpose:
- check whether friction candidates are stable or time-local anomalies

---

# 8. First table set

## Table 1. Data cleaning summary
- raw rows
- filtered rows
- unique `_id`
- duplicate gap
- blank operation rows
- anomalous timestamp rows excluded

## Table 2. Content inclusion summary
- total contents observed
- contents meeting threshold
- median users per content
- median events per content

## Table 3. Top 20 candidate friction contents
Columns:
- rank
- `contents_id`
- `contents_name`
- unique users
- unique events
- nav instability rate
- memo rate
- marker rate
- rec open rate
- rec click-through rate
- median gap
- pilot friction score

---

# 9. Interpretation rules for pilot

## What counts as a strong candidate friction content?
A content is a strong candidate if it shows:
- enough unique users
- enough unique events
- high navigation instability relative to peers
- elevated support-seeking and/or annotation rates
- non-trivial distribution across many users rather than one extreme case

## What should NOT be called friction too quickly?
- high memo rate alone
- high marker rate alone
- high quiz activity alone

These may reflect productive deep engagement.

Friction should be inferred from a **combination of signals**.

---

# 10. Required metadata next (needs user definitions)

To interpret results properly, the next stage will require the exact relational mapping for:
1. content → course
2. course → subject
3. course → grade / level

Because the user asked us not to guess relational schema meanings, the next step after the xAPI-only pilot should be to ask for:
- exact relevant table names
- join keys
- subject field
- grade/level field

---

# 11. Recommended pilot workflow

## Phase A: xAPI-only pilot
- run Q1–Q7
- shortlist candidate contents
- create Figures 1–5
- identify the most interpretable 10–20 contents

## Phase B: metadata enrichment
- ask user for exact relational schema definitions
- map shortlisted contents to course / subject / grade level
- reinterpret candidate contents within course context

## Phase C: refined pilot note
- revise the friction score
- separate productive engagement from likely friction more carefully
- propose a paper-ready analysis subset

---

# 12. Immediate next action
If moving from planning to execution, I would do this exact sequence:
1. Run Q1 and Q2
2. Decide final timestamp and blank-operation handling
3. Run Q3 and choose inclusion thresholds
4. Run Q4 and Q5 to build content features
5. Shortlist top 20 contents
6. Run Q6 to check user concentration
7. Prepare Figures 1–5
8. Ask user for exact course/subject/grade mapping definitions

---

# 13. One-line summary
**This pilot starts with a clean xAPI-only content scan in `saikyo_old`, builds interpretable friction variables at the `contents_id` level, and produces a shortlist of candidate high-friction contents before adding Moodle course context.**
