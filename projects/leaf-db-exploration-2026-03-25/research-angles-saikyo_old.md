# Candidate research angles from existing data (`saikyo_old`)

Date: 2026-03-25

## What this is based on
A bounded read-only scan of `saikyo_old.statements_mv`.

Quick profile:
- total rows: `101,847,089`
- unique accounts: `7,939`
- unique contents: `13,294`
- unique operations: `43`
- time span observed: `1969-12-31 23:59:59` to `2026-02-13 04:54:14`

Important data-quality note:
- there are clear timestamp anomalies (`1970...`, and one row in `2149...`)
- empty `operation_name` is also very common (`24,937,088` rows)
- these should be filtered/handled in any real study

## Strong candidate angles

### 1. Annotation / note-taking behavior as a proxy for active learning
**Question:** Are memo- and marker-based interactions associated with richer or more persistent engagement patterns?

Why this looks strong:
- memo-related events are abundant:
  - memo events (`ADD_HW_MEMO`, `CHANGE MEMO`, `ADD MEMO`) ≈ `24.6M`
- marker-related events are also abundant:
  - marker events (`ADD MARKER`, `DELETE MARKER`) ≈ `15.0M`
- these behaviors appear across many users and contents

Potential outcomes:
- session depth
- revisit behavior
- navigation persistence
- later quiz participation / correctness (if joinable carefully)

Why publishable:
- active annotation is pedagogically meaningful
- the signal is very large and likely robust after filtering

### 2. Navigation patterns and reading strategy
**Question:** Can distinct reading/navigation strategies be identified from `NEXT`, `PREV`, `PAGE_JUMP`, and `BOOKMARK_JUMP`, and do those strategies differ by content or learner group?

Why this looks strong:
- navigation events are abundant:
  - navigation events ≈ `22.8M`
- broad coverage:
  - `NEXT` seen across `3,091` users and `7,164` contents
  - `PREV` across `2,980` users and `6,116` contents
  - `PAGE_JUMP` across `2,654` users and `5,861` contents

Potential framing:
- linear readers vs skimmers vs revisitors
- exploratory vs targeted navigation
- content structures that induce more backtracking or jumping

Why publishable:
- directly tied to digital reading behavior and self-regulated learning
- can produce interpretable user/content typologies

### 3. Recommendation exposure and uptake
**Question:** Do recommendation interactions represent meaningful support behavior, and what predicts recommendation uptake?

Why this looks strong:
- recommendation events are present at scale:
  - recommendation events ≈ `1.03M`
  - `OPEN_RECOMMENDATION` appears across `2,422` users and `1,523` contents
- but actual `CLICK_RECOMMENDATION` is much lower:
  - `783` users, `166` contents

This gap is interesting because it suggests a funnel:
- recommendation shown/opened
- recommendation clicked or ignored

Possible angle:
- what behavioral patterns precede opening recommendations?
- what differentiates clickers vs non-clickers?
- are recommendations associated with struggle signals such as repeated navigation or memo behavior?

Why publishable:
- clean intervention-adoption framing
- high practical value for system design

### 4. Quiz-related engagement and correctness pathways
**Question:** What learner behavior patterns precede quiz participation and quiz correctness?

Why this looks promising:
- quiz signals exist:
  - `QUIZ_ANSWER` / `QUIZ_ANSWER_CORRECT` ≈ `635k` events combined
  - quiz correctness spans `2,256` users and `736` contents

Potential predictors from xAPI only:
- navigation intensity
n- memo use
- marker use
- recommendation exposure/clicks
- timing and revisits

Why strong:
- naturally outcome-oriented
- easier to explain than pure clustering studies
- can become a practical early-warning or support-design paper

### 5. Content-level difficulty / friction signatures from behavioral traces
**Question:** Can content units be profiled by behavioral friction signatures such as backtracking, annotation density, recommendation opening, or timer behavior?

Why this looks strong:
- there are `13,294` unique contents
- behavior types are rich enough to characterize contents beyond simple usage volume

Possible content signatures:
- high backtracking
- high memo density
- high recommendation opening
- high quiz-error behavior
- high timer-stop / pause behavior

Why publishable:
- shifts unit of analysis from learner to content
- useful for instructional design and content revision

## Best first bets
If choosing only three to pursue first:
1. **Annotation / memo behavior and engagement**
2. **Navigation strategy typology**
3. **Recommendation funnel and uptake**

## Why these three first
- strong data volume
- conceptually clean
- likely feasible with xAPI alone before requiring complicated relational joins
- good chance of producing interpretable figures quickly

## Immediate cautions
- filter invalid timestamps
- inspect the huge blank `operation_name` bucket before using all events blindly
- validate per-user identifiers in `saikyo_old` before any cross-source linking
- obey the data sufficiency rule at each subgroup/content slice
