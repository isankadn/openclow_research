# LEAF Agent Architecture

## Purpose
LEAF is an OpenClaw-based multi-agent system for automated research, analysis, synthesis, and drafting.

It is designed to transform a user request into a repeatable workflow. The default operating model is existing-data-first secondary-use research, with external literature used to contextualize, validate, and fill gaps.

Default workflow:
question -> internal data inspection -> contextual mapping -> feasibility/method review -> targeted literature retrieval -> synthesis/draft output

## Design principles
- Separate research into distinct stages instead of using one generic agent for everything.
- Keep the main coordinator responsible for planning and orchestration, not deep execution of every step.
- Use specialist agents with explicit inputs, outputs, and stop conditions.
- Prefer traceable evidence handling over unsupported claims.
- Keep external systems decoupled until infrastructure details are provided.

## Agents

### 1) LEAF Conductor
Role: Main orchestrator and user-facing coordinator.

Responsibilities:
- Interpret user goals
- Break work into stages
- Decide which specialist agents to invoke
- Track progress across the workflow
- Merge specialist outputs into a coherent final response or plan
- Ask for missing constraints only when needed

Should not:
- Pretend to have collected evidence it has not seen
- Perform all deep reading/analysis itself when a specialist should do it
- Make infrastructure assumptions without confirmation

### 2) LEAF Content Reader
Role: Targeted literature intake and extraction specialist that supports internal-data-driven research.

Responsibilities:
- Read source materials from web, documents, or later connected corpora
- Extract relevant passages, claims, facts, quotes, and metadata
- Produce structured source notes
- Flag unclear or low-quality material

Outputs:
- source inventory
- extracted notes
- evidence snippets
- source-level confidence notes

### 3) LEAF Context Mapper
Role: Organize findings into themes, entities, timelines, relationships, and topic maps.

Responsibilities:
- Cluster extracted content by theme
- Identify concepts, actors, events, methods, and dependencies
- Build structured context maps from raw notes
- Surface conflicts, gaps, duplicates, and open questions

Outputs:
- thematic clusters
- relationship maps
- gap lists
- contradiction notes

### 4) LEAF Methodologist
Role: Research quality, scope, and rigor controller.

Responsibilities:
- Define and check research framing
- Assess whether evidence is sufficient for the requested output
- Identify missing perspectives, methodological risks, and bias
- Suggest validation steps and evidence thresholds
- Enforce distinctions between evidence, interpretation, and speculation

Outputs:
- scope checks
- quality/risk notes
- methodology recommendations
- validation checklist

### 5) LEAF Data Scientist
Role: Structured analysis, internal-data interpretation, and computational reasoning specialist.

Responsibilities:
- Work on structured/tabular data when available later
- Perform quantitative analysis, comparisons, trend identification, and statistical summaries
- Produce charts/tables/specs later when tool access exists
- Convert analysis into decision-useful findings

Outputs:
- quantitative findings
- trend summaries
- metric definitions
- assumptions and caveats

## Recommended workflow

### Standard workflow
1. User submits a question, paper idea, or analysis goal.
2. LEAF Conductor clarifies the objective, target output, and whether the task should be treated as existing-data-first secondary use.
3. LEAF Data Scientist inspects the available internal data and defines what is analytically feasible.
4. LEAF Context Mapper organizes variables, themes, entities, and possible research angles.
5. LEAF Methodologist evaluates validity, scope, confounds, and publishability risk.
6. LEAF Content Reader retrieves targeted literature to fill conceptual, methodological, or evidence gaps.
7. LEAF Conductor merges outputs into a research brief, analysis plan, paper-angle memo, or draft package.
8. Final writing/review stage can be handled by the Conductor initially, or later by an additional dedicated writing/review agent if needed.

## Why there is no separate writer agent yet
The original concept mentions a writing/review function. For the first scaffold, that responsibility stays with LEAF Conductor so the system remains simpler and easier to control. If writing volume grows, a dedicated LEAF Writer or LEAF Editor can be added later.

## Coordination model
The Conductor is the only agent that should normally interact directly with the user-facing brief at system level.

Specialists work through structured handoffs:
- Input contract
- Processing scope
- Output schema
- Confidence / caveat section
- Explicit unanswered questions

## Shared artifacts
All agents should eventually exchange work through common artifact types:
- source inventory
- extraction notes
- thematic map
- methodology review
- analysis memo
- final synthesis brief


## Recommended model assignments

### LEAF Conductor
- Model: `gpt-5.4`
- Thinking: `high`
- Reason: orchestration, planning, synthesis, and final decision quality matter more than raw speed.

### LEAF Content Reader
- Model: `gpt-5.4`
- Thinking: `high` by default, `xhigh` for difficult source packs
- Reason: careful reading, nuanced evidence extraction, and contradiction handling need strong reasoning.

### LEAF Context Mapper
- Model: `gpt-5.4`
- Thinking: `high`
- Reason: thematic clustering, relationship mapping, and gap detection are abstraction-heavy tasks.

### LEAF Methodologist
- Model: `gpt-5.4`
- Thinking: `high`
- Reason: evidence sufficiency, bias checks, and methodological rigor need strong judgment.

### LEAF Data Scientist
- Model: `Codex (highest available)`
- Thinking/Mode: highest practical reasoning setting available for code/data work
- Reason: this role is expected to be the most code- and tool-oriented when Python, SQL, and analysis scripts are introduced.

## Escalation policy
- Keep `xhigh` reserved mainly for LEAF Content Reader on especially difficult source sets.
- Use strong defaults across the rest of the system rather than maximum reasoning everywhere.
- If LEAF Data Scientist ends up being more interpretive than code-driven, consider pairing or shifting some analysis-summary work back to `gpt-5.4 high`.

## Current phase limitations
This scaffold intentionally avoids:
- database connections
- production credentials
- service restarts
- dependency installation
- infrastructure-specific wrappers

Those should be added only after you provide environment and access details.
