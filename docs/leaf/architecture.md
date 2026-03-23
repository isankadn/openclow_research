# LEAF Agent Architecture

## Purpose
LEAF is an OpenClaw-based multi-agent system for automated research, analysis, synthesis, and drafting.

It is designed to transform a user request into a repeatable workflow:

question -> evidence collection -> extraction -> contextual mapping -> analysis -> draft output -> review/refinement

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
Role: Source intake and extraction specialist.

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
Role: Structured analysis and computational reasoning specialist.

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
1. User submits question, topic, or report request.
2. LEAF Conductor clarifies objective, deliverable type, deadline, and evidence expectations.
3. LEAF Content Reader gathers and extracts source material.
4. LEAF Context Mapper organizes extracted material into themes and relationships.
5. LEAF Methodologist evaluates scope, rigor, bias, and evidence gaps.
6. LEAF Data Scientist performs structured analysis if quantitative or tabular data is involved.
7. LEAF Conductor merges outputs into a research brief, report plan, or writing package.
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

## Current phase limitations
This scaffold intentionally avoids:
- database connections
- production credentials
- service restarts
- dependency installation
- infrastructure-specific wrappers

Those should be added only after you provide environment and access details.
