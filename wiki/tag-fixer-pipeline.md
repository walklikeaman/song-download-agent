# tag_fixer.py Pipeline

> All enrichment steps run by tag_fixer.py on a FLAC file, in order.

## Overview

`tag_fixer.py` is a single-pass enrichment script. Pass it one or more FLAC files; it reads
existing tags, runs the pipeline below, and writes everything back in place. Files are moved
to `~/Downloads/Spotify downloads/{Artist}/` after processing.

```bash
python3 "/Users/whofarted/Claude/Songs Download/tag_fixer.py" *.flac
```

## Pipeline steps (in order)

### 1. Pre-scan (batch only)
Scans all files to determine which artists get subfolders.
**Rule:** Artist subfolder is created only if 2+ tracks by the same artist are in the batch.
Single tracks go flat into `Spotify downloads/`.

### 2. Quality check
Reads audio stream specs directly from the FLAC container.
Prints bit depth, sample rate, channel count, and a quality tier label.
Warns (`⚠`) if below 24-bit — this is informational only, does not block processing.

### 3. Watermark removal
Removes tool-injected tags before any lookups:
- `encoder` — always deleted
- `encoded_by` — always deleted
- `comment` — deleted only if value matches: `lucida`, `downloaded`, `qobuz.com`, `amazon.com`, `tidal.com`, `deezer`, `ffmpeg`, `lavf`

### 4. MusicBrainz ISRC date lookup
Uses the `ISRC` tag (always present in lucida.to downloads) to query MusicBrainz for the
recording's earliest `first-release-date`. This corrects reissue dates — the original release
year is what goes in the `DATE` tag.

**MusicBrainz blocked on this network:** When the TLS handshake fails, this step is skipped
silently and iTunes fills the date instead.

### 5. iTunes metadata search
Searches `itunes.apple.com/search` for `"{title}" "{artist}"`. Fills any empty tags:
`album`, `albumartist`, `date` (if MusicBrainz didn't set it), `tracknumber`, `discnumber`, `genre`.

Tags already present are never overwritten.

### 6. Discogs fallback (if iTunes missed)
If iTunes returns no result, queries the Discogs API as a secondary source.
Fills: `album`, `date` (if empty), `genre`.

### 7. Genre enforcement
If genre is still empty after iTunes/Discogs, escalates through the
[genre pipeline](genre-pipeline.md): artist cache → MusicBrainz → Wikipedia.

### 8. Various Artists rule
If `albumartist` is "Various Artists" (any variant), replace it with the track's own `artist`.

### 9. Artist grouping
If the artist appears in `artist_groups.json`, sets `ARTISTSORT` and `ALBUMARTISTSORT` to
the group key — enables iTunes/Apple Music library grouping without changing display names.

### 10. Cover art check
- If embedded front cover (type 3) exists: keep as-is; resize to ≤600×600 px if needed
- If missing: fetch from iTunes (600×600 JPEG); warn if fetch fails

### 11. Lyrics fetch
Six sources tried in order — first hit wins. See [lyrics-pipeline.md](lyrics-pipeline.md).
Existing `LYRICS` tag is never overwritten.

### 12. Move to destination
File is moved to `~/Downloads/Spotify downloads/{Artist}/` (subfolder) or
`~/Downloads/Spotify downloads/` (flat) per the pre-scan rule.

## What tags are never touched

`title`, `artist`, `isrc`, `label`, `copyright`, `composer`, `performer`, `lyricist`, `rating`,
and any tag not explicitly listed in the pipeline above.

## Related

- [genre-pipeline.md](genre-pipeline.md) — step 7 in detail
- [lyrics-pipeline.md](lyrics-pipeline.md) — step 11 in detail
- [ref-tag-fields.md](ref-tag-fields.md) — full tag reference table
- [ref-config-files.md](ref-config-files.md) — artist_groups.json and artist_genres.json

## Sources

- `tag_fixer.py` — source of truth
- `WIKI.md` — original flat wiki
