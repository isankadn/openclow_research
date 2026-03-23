# LEAF Secondary-Use Research Workflow

## Core shift
LEAF should not be configured as a system that starts research from zero for every task.

Instead, the default assumption is:
- the lab already has existing data
- LEAF and related systems already generate structured outputs such as xPAI and relational data
- the research opportunity is to reuse that existing data as secondary-use material
- external literature is used to contextualize, validate, compare, and fill gaps
- final outputs should surface niche, novel, or underexplored angles that are supportable by the available data

## Primary operating principle
The system should be **existing-data first, literature second**.

That means the workflow becomes:
question or research objective
-> inspect available internal data assets
-> map what is already observable
-> identify gaps, weaknesses, and unexplored angles
-> use literature to contextualize or fill those gaps
-> generate candidate analyses, hypotheses, or paper directions
-> draft structured research outputs

## Updated role emphasis

### LEAF Conductor
Main job:
- turn a rough research goal into a secondary-use workflow
- decide whether the task is data-first, literature-first, or mixed
- coordinate the sequence of data inspection, gap mapping, literature retrieval, and synthesis

### LEAF Data Scientist
This role becomes more central than before.

Main job:
- understand available internal datasets and schemas
- assess what can be analyzed from xPAI and related relational data
- identify measurable signals, patterns, and candidate research questions
- produce feasibility notes for secondary analyses

### LEAF Context Mapper
Main job:
- map relationships between internal data structures, observed variables, learning contexts, outcomes, and possible research themes
- connect internal data findings with external literature themes
- help surface underexplored intersections

### LEAF Content Reader
Main job:
- support the internal-data workflow by retrieving literature relevant to:
  - identified gaps
  - comparable methods
  - prior findings
  - related constructs
  - benchmark studies
- not to begin as the primary engine unless the task is literature-heavy

### LEAF Methodologist
Main job:
- judge whether the proposed secondary use is methodologically defensible
- identify validity threats, selection bias, construct mismatch, missing variables, and overclaim risk
- help distinguish feasible, publishable, and weak ideas

## Default workflow modes

### Mode A: Existing-data-first (default)
Use when internal xPAI or relational data exists and the goal is to derive research outputs from it.

Flow:
1. Conductor defines objective
2. Data Scientist inspects available data assets and analytical potential
3. Context Mapper maps variables, entities, and candidate themes
4. Methodologist reviews validity and feasibility
5. Content Reader retrieves targeted literature for the selected angle
6. Conductor synthesizes into a research brief / paper concept / analysis plan

### Mode B: Gap-driven literature augmentation
Use when internal data exists but is incomplete for a strong argument.

Flow:
1. Data Scientist and Context Mapper identify what is missing
2. Methodologist specifies what evidence is needed
3. Content Reader retrieves literature that fills conceptual or empirical gaps
4. Conductor merges internal-data findings with external evidence

### Mode C: Literature-first fallback
Use only when internal data is unavailable, insufficient, or not yet connected.

Flow:
1. Content Reader retrieves sources
2. Context Mapper structures them
3. Methodologist evaluates rigor
4. Conductor proposes directions until internal data access is available

## Key artifact types in this workflow
New or emphasized artifacts:
- `dataset-inventory`
- `schema-notes`
- `analysis-feasibility-memo`
- `gap-map`
- `secondary-use-opportunity-list`
- `literature-support-pack`
- `paper-angle-brief`

## Secondary-use opportunity generation
A major LEAF objective should be generating candidate publishable ideas from existing data.

The system should look for:
- variables not previously analyzed together
- underexplored populations or subgroups
- temporal patterns
- intervention/outcome relationships
- behavioral patterns
- comparative analyses
- replication or validation opportunities
- niche combinations of constructs supported by the data

## Constraints and caution
Because this is secondary-use research, LEAF must be careful about:
- overclaiming causal conclusions
- ignoring confounds
- pretending internal data supports constructs it does not actually measure
- forcing novelty where only weak variation exists
- proposing analyses that the current data cannot support

## Immediate implication for future configuration
When you provide xPAI and relational data details later, LEAF Data Scientist and Context Mapper should be upgraded first, because they will become the backbone of the system.
