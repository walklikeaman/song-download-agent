---
name: llm-wiki
description: >
  Build and maintain a persistent, compounding wiki from raw sources using
  Karpathy's LLM-wiki pattern. The LLM acts as programmer, the wiki is the
  codebase. Supports three operations: Ingest (add new sources, update pages),
  Query (answer questions from synthesized wiki pages), and Lint (audit for
  contradictions, stale pages, orphaned links).
  Trigger this skill whenever the user wants to: build or update a wiki/knowledge
  base, ingest documents or session transcripts into structured notes, ask "update
  the wiki with...", "add this to the wiki", "what does our wiki say about...",
  "lint the wiki", or maintain any growing body of documentation that should
  stay consistent and cross-linked over time.
---

# LLM Wiki Skill

> "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."
> — Andrej Karpathy

The core insight: LLMs are exceptionally good at the bookkeeping that causes human-maintained wikis to fail — cross-referencing, consistency checks, updating 10 pages when one fact changes. Let the LLM do that work persistently, so knowledge compounds rather than decays.

---

## Three-layer structure

Every wiki has three layers:

```
raw/          ← immutable source material (transcripts, docs, notes, code)
wiki/         ← LLM-maintained markdown pages (the living knowledge base)
SCHEMA.md     ← configuration: page types, conventions, ingest rules
```

Raw sources are **never modified**. The wiki is **always mutable**. The schema tells you (and the LLM) how the wiki is organized.

---

## Three operations

### 1. Ingest

Add new knowledge from a source into the wiki.

**Steps:**
1. Read the source (transcript, document, code file, URL, etc.)
2. Identify what's new, corrected, or expanded relative to existing wiki pages
3. Update or create 5–15 pages that this source touches
4. Add the source to the ingest log with a one-line summary
5. Update the wiki index if new pages were created

**Rules for good ingest:**
- Each page covers one concept, entity, or process — not everything at once
- Cross-link aggressively: if page A mentions something covered by page B, add a link
- Prefer updating existing pages over creating new ones (keeps the wiki dense)
- Preserve what was there before; only add, correct, or extend
- If something in the source contradicts a wiki page, note the conflict explicitly rather than silently overwriting

**Ingest log format** (`wiki/_ingest_log.md`):
```markdown
| Date | Source | Pages touched | Summary |
|------|--------|---------------|---------|
| 2026-05-21 | session_transcript.md | 8 | First Jim Noir download session; lucida.to token flow, poll error handling |
```

### 2. Query

Answer a question using only the wiki (not raw sources).

**Steps:**
1. Identify which wiki pages are relevant to the question
2. Read those pages
3. Synthesize an answer with citations to specific pages
4. If the answer surfaces something valuable and reusable, write it back into the wiki as a new note or update

**Why query from the wiki instead of raw sources:**
Raw sources are verbose, redundant, and context-heavy. Wiki pages are already synthesized — querying them is faster and the answers are more precise. The wiki is the compiled binary; raw sources are the source code.

### 3. Lint

Audit the wiki for health issues.

**Run lint when:**
- The wiki hasn't been touched in a while
- You suspect contradictions after many ingests
- You want to find gaps before a big project

**What to check:**
- **Contradictions**: Two pages that make incompatible claims about the same fact
- **Stale claims**: Pages that reference things that have since changed (old token values, deprecated workflows)
- **Orphaned pages**: Pages with no inbound links from other pages or the index
- **Missing links**: A page mentions something that has its own page but doesn't link to it
- **Stub pages**: Pages with fewer than 3 bullet points that could be merged into a parent

**Output:** A lint report in `wiki/_lint_report.md` with a checklist. Fix issues inline or flag them for the user.

---

## Schema file

Every wiki should have a `SCHEMA.md` (or `CLAUDE.md`) that defines:

```markdown
# Wiki Schema

## Page types
- **Process pages**: step-by-step workflows (e.g., "How to download a track")
- **Concept pages**: explanations of technical ideas (e.g., "How lucida.to's handoff API works")
- **Entity pages**: things with persistent identity (e.g., "Jim Noir", "lucida.to")
- **Error pages**: known failure modes and their fixes
- **Reference pages**: lookup tables, config values, API fields

## Naming conventions
- Use lowercase-with-hyphens for filenames
- Entity pages: just the name (e.g., `jim-noir.md`)
- Process pages: verb phrase (e.g., `download-a-track.md`)
- Error pages: prefix with `error-` (e.g., `error-cloudflare-block.md`)

## Ingest rules
- Always update the index after adding a page
- Date format: YYYY-MM-DD
- Citations: link to the source file in raw/ using relative paths

## What NOT to put in the wiki
- Raw transcripts or logs (those go in raw/)
- Temporary/session-specific notes
- Anything that changes every run (timestamps, file sizes)
```

---

## Applying this skill to a project

When the user says "build the wiki" or "update the wiki from this session":

1. **Check if a wiki already exists** — look for a `wiki/` folder or existing `WIKI.md`
2. **Check for a schema** — look for `SCHEMA.md`, `CLAUDE.md`, or schema section in existing wiki
3. **Identify available raw sources** — session transcripts, code files, error logs, chat history
4. **Run Ingest** on each source in chronological order
5. **Update the index** (`wiki/index.md` or `wiki/README.md`)
6. **Optionally run Lint** after a large ingest

### Converting a flat WIKI.md to a structured wiki

If the project already has a monolithic `WIKI.md`:

1. Treat the existing `WIKI.md` as a raw source
2. Parse it into page-type sections
3. Create individual files in `wiki/` for each major section
4. Keep the original `WIKI.md` as a generated summary/entry point (regenerate it from the individual pages)
5. The individual pages become the authoritative source; `WIKI.md` becomes the human-readable overview

---

## Page template

```markdown
# [Page Title]

> One-sentence summary of what this page covers.

## Overview
[2–4 sentence explanation]

## Details
[The actual content — bullet points, code blocks, tables as appropriate]

## Related
- [[other-page]] — why it's related
- [[another-page]] — why it's related

## Sources
- `raw/session-2026-05-21.md` — where this was first recorded
```

---

## Example: Song Download Agent wiki

For the `/Users/whofarted/Claude/Songs Download/` project:

**Raw sources to ingest:**
- Session transcripts from `~/.claude/projects/-Users-whofarted-Claude-Songs-Download/`
- `tag_fixer.py` (code is a source)
- `WIKI.md` (existing flat wiki)
- `playwright_download.py`, `receive_server.py` (historical approaches)

**Suggested page structure:**
```
wiki/
  index.md
  download-a-track.md          ← the core workflow
  lucida-to-api.md             ← handoff API, polling, download URL
  cloudflare-behavior.md       ← why Python fails, what works
  tag-fixer-pipeline.md        ← all enrichment steps
  genre-pipeline.md            ← 5-source genre chain
  lyrics-pipeline.md           ← 6-source lyrics chain
  chrome-extension-setup.md    ← iMac vs laptop, deviceId
  token-management.md          ← lucida.to token, renewal
  error-cloudflare-block.md    ← 403, TLS fingerprinting
  error-poll-failed-to-fetch.md ← transient CDN errors
  artist-jim-noir.md           ← session notes, ASINs, results
  _ingest_log.md
  _lint_report.md
```

**Schema for this project** (`/Users/whofarted/Claude/Songs Download/wiki/SCHEMA.md`) — create on first ingest.
