# Research concept note

## Working title
**Diagnosing content-level learning friction in Japanese K-12 digital courses using BookRoll interaction traces**

## Short title
**Content-level friction diagnostics with BookRoll**

## 1. Research problem
Learning analytics studies using BookRoll and related systems have already shown that digital reading traces can reveal learner profiles, behavioral patterns, instructional processes, and recommendation effects. However, much of that work has focused on learners, recommendations, or course-level orchestration.

A still-promising direction is to shift the analytical unit from the learner alone to the **content unit within its course context**.

In Japanese K-12 settings, BookRoll contents belong to courses, and courses differ by grade/level and subject area (for example English, Japanese, mathematics, etc.). Therefore, behavioral traces should not be interpreted as if all contents are equivalent. The same interaction pattern may indicate productive engagement in one subject but confusion or friction in another.

This project proposes a **content-level friction diagnostics** approach: use large-scale BookRoll interaction traces to identify contents that appear to generate learner difficulty, hesitation, inefficient navigation, or heavy support-seeking behavior, while accounting for course context.

## 2. Motivation
Teachers and course designers often need answers such as:
- Which contents appear difficult for learners?
- Which materials produce repeated revisits, backtracking, or heavy annotation?
- Which contents may need revision, restructuring, or additional support?
- How do these patterns differ by subject and K-12 level?

Existing learner-profile studies are useful, but they do not always directly answer these instructional design questions. A content-level perspective could produce more actionable results for curriculum improvement and learning support design.

## 3. Gap statement
### What the lab / adjacent work already covers
Existing Kyoto/Ogata-lab and adjacent work already addresses:
- reader profiles in critical reading tasks
- behavior patterns across performance groups
- instructional process extraction from xAPI logs
- explainable recommendation and recommendation effects
- habit-building support through learning analytics
- marker-based grouping for collaborative learning

### What is still underexplored
There appears to be less direct work on:
- **systematically identifying friction-prone contents at scale**
- **comparing friction signatures across K-12 subjects and grade levels**
- **turning xAPI behavior traces into content/course revision signals**
- **distinguishing productive deep engagement from problematic content friction**

### Proposed contribution
This study aims to fill that gap by producing a framework for diagnosing likely content friction using behavioral traces from BookRoll, grounded in course context from the Japanese K-12 setting.

## 4. Research aim
To develop and evaluate a content-level analytics approach that identifies and interprets friction signatures in BookRoll materials across Japanese K-12 courses.

## 5. Research questions
### RQ1
Which BookRoll contents exhibit consistent behavioral signatures of friction across learners?

### RQ2
How do content-level friction signatures differ by course subject and K-12 level?

### RQ3
Which combinations of behavioral signals are more consistent with likely friction than with productive deep engagement?

### RQ4
Can content-level friction diagnostics generate actionable insights for content redesign, instructional support, or recommendation timing?

## 6. Initial hypotheses
### H1
Some content units will show stable high-friction behavioral signatures across many learners rather than random variation.

### H2
Friction signatures will differ by subject and grade/level, meaning that behavior should be interpreted within course context rather than pooled globally.

### H3
A composite pattern combining navigation instability, support-seeking behavior, and interaction density will diagnose friction better than any single event type alone.

### H4
There will be identifiable content groups where the same interaction counts imply different meanings (for example productive annotation vs difficulty), and this distinction will become clearer when subject/course context is included.

## 7. Data scope (current plan)
### Primary source
- ClickHouse xAPI database: `saikyo_old`
- preferred analytics table: `saikyo_old.statements_mv`

### Current bounded scan suggests
- ~101.8M rows
- ~7,939 accounts
- ~13,294 contents
- ~43 operation types

### Important note
Current operating rule: use only `saikyo_old` until the user explicitly says otherwise.

## 8. Related data context
This concept note assumes:
- BookRoll contents belong to courses
- course context matters for interpretation
- Moodle holds important course-related information
- course comparisons should account for Japanese K-12 subject and level

Where exact Moodle / BookRoll / Analysis table meanings are needed, the user should clarify the relevant schema definitions before interpretation.

## 9. Candidate behavioral indicators
The exact final variable set will depend on confirmed schema meanings, but the first-pass candidates from xAPI are:

### Navigation-related
- `NEXT`
- `PREV`
- `PAGE_JUMP`
- `BOOKMARK_JUMP`
- `OPEN`
- `CLOSE`

### Annotation-related
- `ADD MEMO`
- `CHANGE MEMO`
- `DELETE_MEMO`
- `ADD_HW_MEMO`
- `UNDO_HW_MEMO`
- `REDO_HW_MEMO`
- `CLEAR_HW_MEMO`
- `ADD MARKER`
- `DELETE MARKER`

### Support / recommendation-related
- `OPEN_RECOMMENDATION`
- `CLICK_RECOMMENDATION`
- `CLOSE_RECOMMENDATION`

### Assessment-related
- `QUIZ_ANSWER`
- `QUIZ_ANSWER_CORRECT`

### Time-related / pacing-related
- `TIMER_START`
- `TIMER_PAUSE`
- `TIMER_STOP`
- timestamp-based dwell / revisit / spacing signals

## 10. Key conceptual distinction
The study should explicitly distinguish:

### Productive deep engagement
Examples:
- annotation-rich but steady progress
- revisits that lead to later successful quiz behavior
- deliberate marking and memo use with coherent navigation

### Likely content friction
Examples:
- repeated backtracking without progress
- unstable jumping behavior
- support-seeking behavior without uptake
- recurrent revisits concentrated on the same content segment
- anomalously high interaction effort for certain contents relative to comparable course context

The goal is not to label all heavy interaction as “bad,” but to identify **patterns suggesting design or comprehension friction**.

## 11. Proposed analytical framework
### Step 1: Data cleaning and validity screening
- remove or isolate anomalous timestamps (for example 1970 and extreme future dates)
- inspect and handle blank `operation_name` values
- confirm usable content identifiers and learner identifiers
- check data sufficiency per content/course slice before analysis

### Step 2: Content-level aggregation
For each content unit, compute behavioral summaries such as:
- navigation instability index
- annotation density
- marker density
- support-seeking frequency
- recommendation opening/click ratio
- quiz interaction rates
- revisit frequency
- median / distributional pacing features
- unique learner coverage

### Step 3: Course-context integration
Join or map each content to:
- course
- subject
- grade/level
- possibly teacher / curriculum context if later available and appropriate

### Step 4: Friction signature modeling
Construct candidate friction signatures using one or more approaches:
- rule-based composite index
- standardized feature profiles per content
- clustering of contents by behavioral signature
- anomaly / outlier detection within subject-level peer groups

### Step 5: Interpretation
Compare content signatures:
- within the same course
- across courses in the same subject
- across grade levels

### Step 6: Actionability layer
Translate results into instructional interpretations such as:
- probable difficult content
- probable structurally confusing content
- probable annotation-rich deep-reading content
- probable support-needing content
- content where recommendation timing may be useful

## 12. Possible dependent outputs
This study can support one or more outputs:

### Output A: Research paper
A methodology + findings paper on content-level friction diagnostics in BookRoll-based K-12 learning.

### Output B: Teacher / designer dashboard concept
A friction-aware content dashboard highlighting contents that may require revision or support.

### Output C: Recommendation design input
Use friction states to trigger better-timed or context-aware interventions.

## 13. Why this angle is strong
### Strong data support
The current scan of `saikyo_old` shows large event volume across navigation, memo, marker, quiz, and recommendation behaviors.

### Better novelty positioning
This angle is less saturated than:
- another learner-profile paper
- another generic recommendation acceptance paper
- another generic annotation paper

### Practical relevance
The findings could directly help:
- teachers identify problematic materials
- designers revise content
- researchers understand subject-specific reading difficulty
- system designers improve support timing

## 14. Feasibility assessment
### Strengths
- very large xAPI dataset
- diverse operation types
- course context is known to matter
- likely strong practical story

### Risks
- interpreting behavior without context can be misleading
- some signals may reflect productive engagement rather than difficulty
- data quality issues already exist (blank operation names, anomalous timestamps)
- exact course/content mapping may require schema clarification from the user

### Feasibility judgement
**Promising**, provided the project begins with:
1. careful cleaning
2. clear course/content mapping
3. context-sensitive interpretation
4. explicit distinction between productive engagement and friction

## 15. Minimum viable first study
A realistic first paper version could be:

### Title candidate
**Detecting content-level friction signatures in a K-12 e-book learning platform using xAPI traces**

### Scope
- one ClickHouse database only: `saikyo_old`
- a carefully selected subset of courses with confirmed context
- descriptive + comparative analytics first
- no complex causal claims in version 1

### Core deliverables
- friction signature definition
- content ranking / taxonomy
- examples of high-friction vs low-friction content
- comparison across at least 2 subject or level groups
- implications for content redesign

## 16. Suggested paper structure
1. Introduction
2. Related work
3. Context: LEAF / BookRoll / Japanese K-12 courses
4. Data and preprocessing
5. Friction signature design
6. Results by content / subject / level
7. Discussion: productive engagement vs friction
8. Practical implications for teachers and designers
9. Limitations and future work

## 17. What we need next
Before moving from concept to execution, the next concrete needs are:
1. confirm the relevant course/content mapping fields
2. confirm how subject and grade/level are represented in Moodle/course data
3. define the first clean subset of courses for pilot analysis
4. inspect blank `operation_name` rows in `saikyo_old`
5. inspect content identifier quality and coverage in `saikyo_old`

## 18. Recommended next action
Create a **pilot analysis plan** for this concept note, limited to:
- one subset of courses
- confirmed course metadata
- a preliminary friction index
- 3 to 5 interpretable visualizations

## 19. One-sentence pitch
**This study uses large-scale BookRoll xAPI traces to identify which K-12 course contents appear to generate learning friction, and turns behavioral logs into actionable diagnostics for content and instructional improvement.**
