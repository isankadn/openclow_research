# LEAF Coordination Protocol

## Routing principle
The user talks to LEAF Conductor.
LEAF Conductor delegates internally based on task type.

## Delegation rules

### Send to LEAF Content Reader when:
- the task needs source reading
- a document/web set must be extracted
- claims, quotes, or evidence snippets are needed
- the system needs source-by-source notes

### Send to LEAF Context Mapper when:
- findings need thematic grouping
- you need entity/timeline/relationship mapping
- multiple sources must be reconciled into a coherent structure
- gaps or contradictions need surfacing

### Send to LEAF Methodologist when:
- the request needs rigor checks
- evidence sufficiency is unclear
- research framing may be weak or biased
- a validation or review checklist is required

### Send to LEAF Data Scientist when:
- the work involves datasets, metrics, tables, trends, or statistical summaries
- comparison across structured variables is needed
- analytical outputs must be quantified

## Handoff contract
Every handoff should include:
1. task objective
2. input materials
3. output format expected
4. evidence/citation expectations
5. constraints and deadline if any

Every specialist response should include:
1. what was reviewed
2. key findings
3. confidence/caveats
4. gaps/open questions
5. recommended next action

## Escalation rules
- If a specialist lacks enough input, it should not invent missing material.
- If evidence quality is poor, flag it explicitly.
- If the task requires external systems not yet wired, respond with placeholders and requirements.
- If outputs conflict, LEAF Conductor decides whether to reconcile, ask for clarification, or request additional evidence.

## Writing policy
Until a dedicated writer agent exists:
- LEAF Conductor handles synthesis and final drafting.
- Specialist agents should optimize for structured, reusable intermediate outputs rather than polished prose.
