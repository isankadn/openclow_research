# Gap analysis for top 3 candidate angles (`saikyo_old`)

Date: 2026-03-25

## Purpose
Re-rank the initial top 3 research angles by comparing them against:
1. existing Kyoto / Ogata-lab / closely affiliated work
2. broader outside literature
3. the likely gap still open for LEAF data

## Current top 3 under review
1. Annotation / memo behavior and engagement
2. Navigation strategy patterns
3. Recommendation uptake funnel

## Key observed data facts from `saikyo_old`
- ~101.8M rows
- 7,939 accounts
- 13,294 contents
- 43 operation types
- very large signals for memo/marker/navigation events
- recommendation events exist at meaningful scale but are much smaller than navigation/memo events
- K-12 course/subject/level context should matter and should not be ignored

---

## 1) Annotation / memo behavior and engagement

### Relevant lab / close literature already found
- **Ogata et al. / BookRoll early work**: e-book based learning analytics already used marker and memo behaviors as meaningful active-reading traces.
- **Majumdar et al. (2021)**, *Learning analytics of humanities course: reader profiles in critical reading activity*:
  - focuses on reading profiles in a humanities critical reading task
  - uses BookRoll logs and profile analysis
- **Kannan et al. (2022)**, *Learning dialogs orchestrated with BookRoll*:
  - looks at engagement and memo artifacts in an undergraduate physics context
- **Takii et al. (2025)**, *Optimizing group formation ... using marker data*:
  - uses active-reading marker logs for group formation in high school EFL

### What outside literature already covers
- digital reading / annotation behavior is a recognized area
- social annotation and web-book reading analytics have been studied broadly
- reading behavior + lag/sequential/profile analyses are not new by themselves

### Gap still open
A generic “annotation matters” paper is **too close** to what the lab and adjacent literature already do.

### Better gap-filling version
Instead of asking whether annotation exists or relates to engagement, ask:
- **How does annotation behavior differ by course subject and Japanese K-12 level?**
- **Which annotation patterns indicate content-level friction vs productive engagement?**
- **Can annotation patterns predict where content design needs revision?**

### Why this is still promising
This reframes annotation from a learner-only lens to a **content/course diagnostic lens**.
That feels less saturated and more actionable for the lab.

### Novelty verdict
**Medium**, if framed as generic learner engagement.
**High**, if framed as **course-/content-aware friction diagnostics across K-12 subjects/levels**.

---

## 2) Navigation strategy patterns

### Relevant lab / close literature already found
- **Majumdar et al. (2021)** identified reader profiles such as effortful, strategic, wanderers, and check-out in a humanities critical reading task.
- **Geng et al. (2024)**, *Learning behavioral patterns of students with varying performance in a high school mathematics course using an e-book system*:
  - uses BookRoll data
  - uses lag sequential analysis
  - compares behavior patterns across performance groups
- some BookRoll-related work already links navigation/interaction sequences to learning strategies

### What outside literature already covers
- reading profiles are well-established in digital reading analytics
- lag sequential analysis for learning behavior is widely used
- navigation pattern mining as a generic objective is not novel enough by itself

### Gap still open
A plain “discover navigation strategies” paper is **too close** to both lab and broader literature.

### Better gap-filling version
Shift from generic behavior profiling to one of these:
- **Cross-subject / cross-grade stability of navigation strategies** in Japanese K-12
- **Mismatch between course design and actual navigation pathways**
- **Navigation patterns as indicators of content difficulty or instructional misalignment**, not merely learner style

### Why this is stronger
The lab already has profile papers. The gap is not “more profiles,” but **what profiles mean for instructional design at scale**.
This also connects nicely to:
- course context from Moodle
- content belonging to courses
- the 2025 instructional-process/teaching-analytics line

### Novelty verdict
**Low to medium** as a pure profile paper.
**High** if turned into **course-design / instructional-misalignment analytics**.

---

## 3) Recommendation uptake funnel

### Relevant lab / close literature already found
- **Dai et al. (2024)**, *Beyond recommendation acceptance: explanation’s learning effects in a math recommender system*:
  - goes beyond acceptance to learning effects
  - finds effects differ by prior ability
- **Takii et al. (2025)**, *Explainable eBook recommendation for extensive reading in K-12 EFL learning*:
  - K-12 EFL recommendation setting
  - focus on explainable recommendation and acceptance/motivation
- **Hsu et al. (2026)**, *Personalized recommendations for habit-building through learning analytics*:
  - recommendation for productive time habits
  - K-12 relevance and self-regulation framing
- **EXAIT / explainable AI tool line** suggests the lab is already actively investing in recommendation/explanation research

### What outside literature already covers
- educational recommender systems are a large area
- explainability, trust, acceptance, and effectiveness are already active themes
- systematic reviews suggest recommendation research often focuses on accuracy, presentation, and outcome evaluation

### Gap still open
A generic recommendation-uptake paper is **too close to the lab’s active frontier**.
This is the most crowded of the three if framed naively.

### Better gap-filling version
A viable gap would need to be narrower and more operational, for example:
- **When do learners ignore recommendations despite being behaviorally at risk?**
- **How do recommendation openings/clicks interact with content difficulty, subject, and learner navigation/annotation state?**
- **Recommendation timing and contextual triggers**, not recommendation quality alone

### Why this is still useful
The event funnel exists in the data, so it is analytically feasible.
But novelty will require a **behavioral-context** frame, not another acceptance/explainability paper.

### Novelty verdict
**Low** as a generic uptake/acceptance paper.
**Medium** if reframed around **context-aware intervention timing or ignored-help behavior**.

---

## Re-ranked shortlist by gap-filling potential

### #1 — Content-level friction diagnostics using annotation + navigation + recommendation traces
**Recommended framing:**
Identify which contents/courses generate behavioral friction signatures, while controlling for subject and K-12 level.

Why this rises to the top:
- leverages strong existing data
- uses Moodle course context that the user explicitly said matters
- is not just another learner-profile paper
- directly useful for instructional/content redesign
- aligns with the lab’s teaching analytics direction but does not merely duplicate it

### #2 — Course-design / instructional-misalignment analytics from navigation patterns
**Recommended framing:**
Compare expected course/content flow against actual learner navigation behavior to detect where learners backtrack, jump, or stall.

Why this is strong:
- builds on, but goes beyond, reader-profile and instructional-process work
- more actionable for teachers/content designers than another clustering paper
- can be done at scale across courses/subjects

### #3 — Context-aware ignored-help / recommendation timing analysis
**Recommended framing:**
Study when recommendations are opened but not clicked, and what behavioral/contextual states predict ignored vs accepted help.

Why this still makes the list:
- recommendations are present in the data
- there is a clear observable funnel
- but the novelty risk is higher because the lab already has several recommendation papers

---

## What I would *not* lead with now
- another generic learner-profile paper
- another generic annotation-is-good paper
- another generic explainable recommendation acceptance paper

Those areas are already too occupied by the lab and adjacent literature.

## Gap-filling principle going forward
To avoid duplication, every angle should be checked against these questions:
1. Does it use **course / subject / grade context** rather than pooling all content?
2. Does it produce **actionable design insight** for teachers/content designers?
3. Does it go beyond **profile description** to explain friction, misalignment, or intervention timing?
4. Can it exploit the lab’s **real-world scale** and longitudinal operational data better than prior small-context studies?

## Current recommendation
If choosing one angle to develop next, choose:

**Content-level friction diagnostics across Japanese K-12 courses using BookRoll interaction traces**

That seems like the best balance of:
- novelty
- feasibility
- data strength
- practical value
- distance from already-crowded recommendation/profile papers
