# Paper Manifest Schema (Draft)

## Fields
- `paper_id`: canonical local identifier
- `title`: normalized title
- `authors`: array
- `year`: integer or null
- `venue`: string or null
- `doi`: string or null
- `arxiv_id`: string or null
- `pubmed_id`: string or null
- `seed_source`: where discovery started
- `source_urls`: candidate URLs considered
- `canonical_url`: best selected source URL
- `storage_path`: local folder path
- `status`: discovered | metadata_only | pdf_downloaded | text_extracted | restricted_access | failed | needs_manual_review
- `downloaded_at`: timestamp or null
- `checksum_sha256`: string or null
- `content_type`: application/pdf | text/html | other | null
- `access_notes`: notes about why content was or was not retrieved
- `provenance`: summary of discovery path
- `retryable`: boolean
- `last_error`: string or null
