# Proposed Runtime Shape (Draft)

This is a planning document, not a live OpenClaw config.

## Suggested logical topology
- main: LEAF Conductor
- specialist-1: LEAF Content Reader
- specialist-2: LEAF Context Mapper
- specialist-3: LEAF Methodologist
- specialist-4: LEAF Data Scientist

## Workspace pattern
- agents/leaf-conductor/
- agents/leaf-content-reader/
- agents/leaf-context-mapper/
- agents/leaf-methodologist/
- agents/leaf-data-scientist/
- shared/
- docs/leaf/

## Initial tool posture
Before data access is provided:
- allow reading local docs/workspace
- allow web research tools if desired
- keep external system connectors as placeholders
- avoid automatic elevated or destructive operations

## Future extensions
Potential later additions:
- LEAF Writer
- LEAF Reviewer
- LEAF Citation Manager
- LEAF Corpus Indexer


## Recommended model policy
- LEAF Conductor -> `gpt-5.4` with `high`
- LEAF Content Reader -> `gpt-5.4` with `high` (escalate to `xhigh` when source complexity is high)
- LEAF Context Mapper -> `gpt-5.4` with `high`
- LEAF Methodologist -> `gpt-5.4` with `high`
- LEAF Data Scientist -> `Codex (highest available)` for code/data execution work
