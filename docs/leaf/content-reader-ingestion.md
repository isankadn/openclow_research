# LEAF Content Reader Ingestion Design

## Goal
Design LEAF Content Reader as a lawful, repeatable paper discovery and retrieval pipeline that can:
- discover research papers from trusted/open sources
- crawl the lab publication list as a seed source
- find openly accessible copies of papers on the web
- store papers and metadata in one shared corpus
- avoid re-downloading the same paper twice
- generate structured outputs for the rest of LEAF

## Non-goals
This design does not include:
- bypassing paywalls
- use of Sci-Hub or similar services
- credential stuffing or anti-bot evasion
- full production implementation of browser automation yet

## Primary seed sources
### 1. Lab publication list
Seed URL:
- https://www.let.media.kyoto-u.ac.jp/publications/

Use this as the highest-trust starting point for lab-origin papers.

### 2. Brave Search API
Use for:
- title-based discovery
- DOI page discovery
- open PDF discovery
- institutional repository discovery
- author-page discovery
- alternate mirror discovery on lawful/open sites

### 3. Open-access and scholarly sources
Priority list:
- DOI resolver pages
- publisher landing pages with accessible PDFs
- institutional repositories
- arXiv
- PubMed / PubMed Central
- Crossref
- OpenAlex
- DOAJ
- lab / author publication pages

### 4. Google Scholar
Use only as a secondary discovery aid, not the core retrieval layer.

Recommended use:
- confirm existence of a paper
- find alternate versions
- discover author-linked or repository-linked copies

Avoid making Scholar the primary automated retrieval pipeline because it is brittle and rate-limit sensitive.

## Retrieval policy
When a paper candidate is found, LEAF Content Reader should resolve access in this order:
1. direct open PDF URL
2. accessible publisher page
3. institutional repository
4. author/lab page
5. preprint server
6. metadata-only fallback

If no lawful/open full text is available:
- store metadata
- mark status as `restricted_access`
- do not pretend the full text was retrieved

## Browser automation policy
Use Playwright/browser automation only when needed for public pages.

Good uses:
- JS-rendered publication pages
- dynamic PDF-link reveal on public pages
- click-through on openly accessible landing pages
- extracting structured metadata from public sites

Bad uses:
- paywall bypassing
- anti-bot evasion
- account abuse
- automated access against restricted systems without permission

Pipeline order should be:
1. API or direct fetch
2. HTML parse
3. Playwright/browser fallback

## Canonical paper identity
Preferred ID order:
1. DOI
2. arXiv ID
3. PubMed ID
4. normalized title hash

This ID becomes the stable local paper key.

## Storage design
Shared corpus root:
- `shared/references/papers/`

Subfolders:
- `shared/references/papers/index/` -> registries and lookup files
- `shared/references/papers/queue/` -> pending discovery/retrieval jobs
- `shared/references/papers/items/<paper-id>/` -> one folder per paper

Per-paper structure:
- `metadata.json`
- `manifest.json`
- `paper.pdf` (if available)
- `fulltext.txt` (if extracted)
- `notes.md`
- `provenance.json`

## Dedupe and re-download policy
Before download, check:
- DOI exact match
- arXiv/PubMed ID match
- normalized title match
- source URL match
- existing manifest status

If a paper already exists locally:
- reuse it
- update metadata if better source info is found
- skip re-download unless a refresh is explicitly requested

## Status model
Paper states:
- `discovered`
- `metadata_only`
- `pdf_downloaded`
- `text_extracted`
- `restricted_access`
- `failed`
- `needs_manual_review`

## Input modes supported
### A. Topic search
User provides a research topic or question.
Content Reader discovers candidate papers using Brave plus open scholarly sources.

### B. Title/DOI search
User provides exact paper references.
Content Reader resolves canonical metadata and retrieval URLs.

### C. Lab publication sync
Content Reader crawls the Kyoto University lab publication page and processes entries into the shared corpus.

## Lab publication sync flow
1. fetch `https://www.let.media.kyoto-u.ac.jp/publications/`
2. identify publication categories and entries
3. extract title, authors, venue, year, links, DOI if visible
4. normalize titles
5. resolve each entry via Brave/open sources
6. retrieve the best accessible copy
7. save into `shared/references/papers/items/<paper-id>/`
8. update index files
9. generate a sync report

## Discovery query patterns
### For Brave
Use search patterns like:
- exact paper title in quotes
- exact title + PDF
- exact title + DOI
- exact title + site:edu
- exact title + site:ac.jp
- author + title fragment
- title + repository

### For lab-based discovery
Use combinations of:
- publication title
- lead author name
- venue/year
- DOI if known

## Output artifacts from Content Reader
For each batch, generate:
- `source-inventory`
- `extraction-notes`
- `retrieval-report`
- `missing-access-report`

These feed directly into Context Mapper and Methodologist.

## Failure handling
If retrieval fails:
- keep metadata
- keep attempted URLs
- keep failure reason
- mark retry eligibility
- surface to LEAF Conductor if important

## Future extensions
Later, add:
- MinIO-backed object storage
- database-backed corpus index
- PDF parsing pipeline
- OCR fallback for scanned documents
- citation graph enrichment
- Crossref/OpenAlex/Semantic Scholar connectors where allowed
