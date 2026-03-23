# Shared Paper Corpus

This directory is the central LEAF paper cache.

## Layout
- `index/` -> registries, lookup maps, sync reports
- `queue/` -> pending jobs and staged tasks
- `items/<paper-id>/` -> one folder per paper

## Policy
- store once, reuse many times
- prefer DOI/arXiv/PubMed IDs for canonical identity
- keep metadata even when full text is unavailable
- do not re-download unless necessary
