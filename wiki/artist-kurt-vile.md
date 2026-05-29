# Kurt Vile

> Philadelphia singer-songwriter / guitarist (ex-The War on Drugs). Lo-fi indie/folk-rock.

## Session 1: 2026-05-29

4 liked tracks downloaded from Amazon Music via lucida.to. tag_fixer.py run. Spotify synced to "New Music 2026".

### Tracks downloaded

| Title | ASIN | File | Size | Album | Quality | Notes |
|---|---|---|---|---|---|---|
| Zoom 97 | B0GSH72WMM | Kurt Vile - Zoom 97.flac | ~34 MB | Philadelphia's been good to me (2026) — 1/12 | CD 16/44.1 | Lyrics embedded |
| Rock o' Stone | B0GSHGD3F1 | Kurt Vile - Rock o' Stone.flac | ~37 MB | Philadelphia's been good to me (2026) — 3/12 | CD 16/44.1 | Lyrics via lyrics.ovh; title has curly apostrophe (Rock o’ Stone) |
| Chance to Bleed | B0GSH845TQ | Kurt Vile - Chance to Bleed.flac | ~35 MB | Philadelphia's been good to me (2026) — 5/12 | CD 16/44.1 | Lyrics embedded |
| Another good year for the roses | B0CKDLJ9YV | Kurt Vile - Another good year for the roses.flac | ~37 MB | Back to Moon Beach (2023) | CD 16/44.1 | Explicit ASIN; ISRC USUG12307605; iTunes matched a compilation but date 2023-11-17 correct |

### Destination

`~/Downloads/Spotify downloads/Kurt Vile/` (Zoom 97 landed in root → manually `mv`d).

### Genre

`Rock` (from iTunes / tag_fixer.py) for all 4.

### Amazon ASIN notes

- 3 tracks from album **Philadelphia's been good to me** (2026) — used the album's `B0GSH…` single-track ASINs (confirmed album via Spotify album column).
- 1 track, **Another good year for the roses**, is from **Back to Moon Beach** (2023 EP) — `B0CKDLJ9YV` (explicit). Multiple other ASINs exist (B0DX/B0DV re-releases); picked the 2023 B0CK one.

### Quirks this session

- **lucida.to flaky:** first `.download-button` click frequently did NOT start the download. Reliable pattern: click → check for `*.crdownload` after ~12s → if none, reload the `?url=` page and click again. Confirmed download started by polling for `*.crdownload`.
- **lucida.to 520 / 404 outage:** mid-session lucida returned "520: Web server is returning an unknown error" and a transient 404 for Zoom 97. Waited ~90s and it recovered.
- **Spotify stubborn removal:** for some rows a bare `.click()` on "Remove from your Liked Songs" did NOT persist (survived page reload). Fix: dispatch a full pointer/mouse event sequence (pointerover→pointerdown→mousedown→pointerup→mouseup→click) with real clientX/clientY on the menu button and menuitem. This reliably removed them. (Add-to-playlist still works with the mouseenter/mouseover+click hover trick.)

## Related

- [download-a-track.md](download-a-track.md) — the workflow used
- [spotify-sync.md](spotify-sync.md) — the sync step
