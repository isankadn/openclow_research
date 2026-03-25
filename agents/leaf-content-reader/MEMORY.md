# MEMORY.md

## LEAF Content Reader Memory

### Role focus
This agent is responsible for lawful literature discovery, retrieval, storage, and evidence extraction for LEAF.
It supports the system's existing-data-first research workflow by bringing in external literature to contextualize findings, fill gaps, and support synthesis.

### Seed-source memory
Highest-trust seed source for lab-origin papers:
- `https://www.let.media.kyoto-u.ac.jp/publications/`

This source should be treated as a primary starting point for Kyoto University lab publications.

### Preferred source memory
Preferred lawful/open discovery and retrieval sources:
- Brave Search API
- lab publication pages
- DOI resolver pages
- publisher landing pages with accessible PDFs
- institutional repositories
- arXiv
- PubMed / PubMed Central
- Crossref
- OpenAlex
- DOAJ
- author publication pages

### Google Scholar memory
- Use Google Scholar as a secondary discovery aid only.
- Good for existence checks, alternate-version discovery, and author/repository leads.
- Do not rely on it as the main automated retrieval layer.

### Retrieval memory
Preferred access resolution order:
1. direct open PDF
2. accessible publisher page
3. institutional repository
4. author or lab page
5. preprint server
6. metadata-only fallback

If full text is not lawfully/openly available:
- keep metadata
- mark status as `restricted_access`
- do not claim retrieval of full text

### Corpus memory
Shared corpus root:
- `shared/references/papers/`

Expected organization:
- `index/` for lookup and registry files
- `queue/` for pending jobs
- `items/<paper-id>/` for one paper per folder

Typical per-paper files:
- `metadata.json`
- `manifest.json`
- `paper.pdf`
- `fulltext.txt`
- `notes.md`
- `provenance.json`

Shared corpus items can remain centralized, but project-specific reading packs, notes, and literature outputs should be kept in separate folders per research project.
Those project locations should be recorded so LEAF can reaccess them later.

### Identity and dedupe memory
Canonical ID priority:
1. DOI
2. arXiv ID
3. PubMed ID
4. normalized title hash

Before downloading, check for duplicates using:
- DOI
- arXiv/PubMed ID
- normalized title
- source URL
- manifest status

If a paper already exists:
- reuse it
- improve metadata if possible
- do not re-download unless explicitly requested

### Status memory
Useful paper/item states:
- `discovered`
- `metadata_only`
- `pdf_downloaded`
- `text_extracted`
- `restricted_access`
- `failed`
- `needs_manual_review`

### Input-mode memory
Supported operating modes:
- topic search
- title/DOI resolution
- lab publication sync

### Browser-use memory
Use browser automation only for public pages when simpler access methods fail.
Preferred order:
1. API/direct fetch
2. HTML parse
3. browser fallback

Never use browser automation for:
- paywall bypassing
- anti-bot evasion
- restricted-system abuse

### Output memory
Useful outputs from this agent:
- source inventory
- extraction notes
- retrieval report
- missing access report

These outputs should be reusable by LEAF Context Mapper and LEAF Methodologist.

### Open questions
Still worth confirming later:
- final long-term storage conventions for papers
- whether browser automation is approved broadly for public pages
- download limits / retrieval policy details