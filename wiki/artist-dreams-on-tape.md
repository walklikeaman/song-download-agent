# Dreams on Tape

> Electronic / ambient artist. 3 liked tracks downloaded in session 2026-05-21.

## Session 1: 2026-05-21

3 liked tracks downloaded from Amazon Music via lucida.to. Each required multiple download retries due to CDN connection drops. tag_fixer.py run on all 3. Spotify synced to "New Music 2026" playlist.

### Tracks downloaded

| Title | ASIN | File | Size | Retry notes |
|---|---|---|---|---|
| Wide Awake | B0939D9734 | Dreams on Tape - Wide Awake.flac | ~34.8 MB | ASIN B08LCK4J42 failed (uh-oh! / "undefined \| lucida"); B08LCJ1L3J partial; B0939D9734 succeeded after ~4 retries |
| Tomorrows Unknown | B0C17PH4DK | Dreams on Tape - Tomorrows Unknown.flac | ~28.9 MB | ASIN B0C17RX1YG failed (metadata load error); B0C17PH4DK succeeded after ~3 retries |
| Good Times | B0C17Q9BNP | Dreams on Tape - Good Times.flac | ~31.7 MB | ~8 retries needed due to CDN drops |

### Destination

`~/Downloads/Spotify downloads/Dreams on Tape/`

### Genre

Enriched via tag_fixer.py (iTunes / MusicBrainz).

### tag_fixer.py notes

- All 3 tracks processed successfully.
- Cover art, genre, and lyrics enriched.

## Quirks

- Wide Awake: ASIN B08LCK4J42 returns "uh-oh!" on lucida.to (title stays "undefined | lucida"); required trying alternate ASINs found via Amazon search.
- Tomorrows Unknown: ASIN B0C17RX1YG fails metadata load; B0C17PH4DK is the correct streaming ASIN.
- All 3 tracks required monitoring loop to detect completed FLAC vs CDN-dropped partials (crdownload disappears without producing .flac).

## Related

- [download-a-track.md](download-a-track.md) — the workflow used
- [cloudflare-behaviour.md](cloudflare-behaviour.md) — why browser-only downloads are needed
