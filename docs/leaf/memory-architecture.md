# LEAF Memory Architecture

## Why session memory is not enough
This project needs durable memory across sessions because the system will accumulate:
- architectural decisions
- agent-role definitions
- data model knowledge
- workflow conventions
- source and corpus knowledge
- research directions and paper ideas

## Memory layers

### 1. Long-term core memory
File:
- `MEMORY.md`

Purpose:
- the most important stable truths about LEAF
- high-level architecture and operating principles
- durable model assignments
- user intent that should persist across sessions

### 2. Searchable domain memory
Files:
- `memory/leaf-overview.md`
- `memory/leaf-workflows.md`
- `memory/leaf-agents.md`
- `memory/leaf-data-memory.md`
- `memory/leaf-literature-memory.md`
- `memory/leaf-decisions.md`
- `memory/leaf-open-questions.md`
- `memory/YYYY-MM-DD.md`

Purpose:
- structured, searchable memory for OpenClaw recall
- ongoing project notes
- known facts, decisions, and missing information

### 3. Agent-local memory
Files inside each agent workspace:
- `agents/<agent>/MEMORY.md`

Purpose:
- role-specific notes and conventions
- should be useful for future per-agent runtime setups
- but not the only place for important project memory

### 4. Artifact memory
Stored in shared project directories such as:
- `shared/references/papers/`
- future dataset registries
- future schema notes and manifests

Purpose:
- durable storage of discovered materials and machine-readable state

## Memory discipline
Important project knowledge should be written twice when necessary:
1. concise durable summary in `MEMORY.md` or `memory/*.md`
2. detailed operational spec in `docs/leaf/*.md`

That way the system keeps both:
- fast recall
- deep documentation

## What should go into memory
Store:
- stable facts about LEAF systems and datasets
- schema summaries
- naming conventions
- methodological constraints
- approved workflows
- corpus/source decisions
- important user preferences
- paper ideas and research themes worth revisiting

Do not rely only on session transcripts.
