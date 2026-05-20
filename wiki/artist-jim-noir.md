# Jim Noir

> Manchester-based indie pop / lo-fi artist. All 8 liked tracks downloaded across two sessions.

## Session 2: 2026-05-21 (continuation)

1 missing track discovered via Spotify liked-songs audit and downloaded. Source: Qobuz GB (only source that worked — Amazon ASIN invalid, Qobuz US 404). Downloaded as ZIP, extracted FLAC, run through tag_fixer.py.

### Track downloaded (session 2)

| Title | Source URL | File | Size | Notes |
|---|---|---|---|---|
| Eanie Meany (Fatboy Slim Remix - radio edit) | qobuz.com/gb-en/album/…/0825646361366 | 1. Jim Noir - Eanie Meany  (Fatboy Slim Remix - radio edit).flac | ~22 MB | ISRC GBAHS0600292, 2006, genre=Pop, lyrics found |

## Session 1: 2026-05-21

All 7 tracks downloaded as FLAC from Amazon Music via lucida.to. tag_fixer.py run on all 7.

### Tracks downloaded (session 1)

| Title | ASIN | File | Size |
|---|---|---|---|
| What U Gonna Do | B09Z44CPG6 | Jim Noir - What U Gonna Do.flac | ~21 MB |
| Tea | B00968MG4K | Jim Noir - Tea.flac | ~17 MB |
| Strange Range | B00OI1USJK | Jim Noir - Strange Range.flac | ~20 MB |
| The Ancoats Dream | B00OI1URSW | Jim Noir - The Ancoats Dream.flac | ~22 MB |
| A.M Jazz | B08232C9NQ | Jim Noir - A.M Jazz.flac | ~41 MB |
| Eggshell | B0822XMXDD | Jim Noir - Eggshell.flac | ~24 MB |
| Upside Down | B08232Y99D | Jim Noir - Upside Down.flac | ~28 MB |

### Destination

`~/Downloads/Spotify downloads/Jim Noir/`

### Destination

`~/Downloads/Spotify downloads/Jim Noir/`

### Genre

`Alternative` (sessions 1 tracks) / `Pop` (Eanie Meany — from iTunes). Seeded into `artist_genres.json` at start of session 1.

### tag_fixer.py notes

- All 8 tracks processed successfully
- Session 1: genre source = seeded manually into cache
- Session 2 (Eanie Meany): genre=Pop from iTunes; lyrics found via lyrics.ovh; cover resized 1426→600px; single-file run → moved to parent `Spotify downloads/` then manually placed in `Jim Noir/`

## Quirks

- Eanie Meany ASIN (`B073LDGQQR`) was a purchase ASIN, not Amazon Music streaming — returned error from lucida.to
- Qobuz US URL returned 404 from lucida.to; GB URL worked
- Lucida downloaded as ZIP (single-track album); extracted with `unzip -j`

## Related

- [download-a-track.md](download-a-track.md) — the workflow used
- [error-poll-failed-to-fetch.md](error-poll-failed-to-fetch.md) — A.M Jazz first attempt failed due to all-error polls

## Sources

- `raw/session-2026-05-21-jim-noir.md`
