# Song Download Agent — Wiki Schema

## Philosophy

This wiki follows Karpathy's LLM-wiki pattern. Raw sources (transcripts, code, error logs) are
immutable and stored in `raw/`. This `wiki/` directory is the LLM-maintained, synthesized knowledge
base. The flat `WIKI.md` at the repo root is a generated human-readable entry point — the individual
pages here are the authoritative source.

## Page types

| Type | Prefix | Example |
|---|---|---|
| **Process** | verb phrase | `download-a-track.md` |
| **Concept** | noun phrase | `lucida-to-api.md` |
| **Entity** | name | `jim-noir.md` |
| **Error** | `error-` | `error-cloudflare-block.md` |
| **Reference** | `ref-` | `ref-tag-fields.md` |
| **Meta** | `_` | `_ingest_log.md`, `_lint_report.md` |

## Naming conventions

- Lowercase, hyphen-separated filenames
- No dates in filenames (dates go in the ingest log and page content)
- Cross-link using relative markdown links: `[lucida.to API](lucida-to-api.md)`

## Ingest rules

1. Treat every new source (transcript, code change, error session) as a raw source
2. Copy or reference it in `raw/`
3. Update 5–15 pages it touches; prefer updating over creating
4. Note contradictions explicitly rather than silently overwriting
5. Add a row to `_ingest_log.md`
6. Update `index.md` if new pages were added

## What NOT to put in the wiki

- Raw transcript text or stdout logs
- Session-specific values that change every run (timestamps, file sizes, exact download durations)
- Temp file paths like `/tmp/...`
- Things that are already well-documented in code comments in `tag_fixer.py`

## Three operations

- **Ingest** — process a new source, update pages, log it
- **Query** — answer a question from wiki pages (not raw sources)
- **Lint** — audit for contradictions, orphan pages, stale values, missing links
