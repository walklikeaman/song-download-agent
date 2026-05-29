# Paul McCartney

> Legendary singer-songwriter (The Beatles, Wings). 2026 album *The Boys of Dungeon Lane*.

## Session 1: 2026-05-29

3 liked tracks downloaded from Amazon Music via lucida.to — all from the 2026 album **The Boys of Dungeon Lane** (14 tracks). tag_fixer.py run. Spotify synced to "New Music 2026".

### Tracks downloaded

| Title | ASIN | File | Size | Album track | Quality | Notes |
|---|---|---|---|---|---|---|
| As You Lie There | B0GTNM1468 | Paul McCartney - As You Lie There.flac | ~31 MB | 1/14 | CD 16/44.1 | Lyrics embedded (3789 chars); ISRC GBCCS2600016 |
| Salesman Saint | B0GTN6PT3B | Paul McCartney - Salesman Saint.flac | ~23 MB | 13/14 | CD 16/44.1 | Lyrics embedded; ISRC GBCCS2600028 |
| Momma Gets By | B0GTNCD76T | Paul McCartney - Momma Gets By.flac | ~24 MB | 14/14 | CD 16/44.1 | Lyrics embedded; ISRC GBCCS2600029 |

### Destination

`~/Downloads/Spotify downloads/Paul McCartney/`

### Genre

`Rock` (from iTunes / tag_fixer.py enrichment) for all 3.

### Amazon ASIN notes — IMPORTANT: avoid the deluxe/commentary edition

- *The Boys of Dungeon Lane* exists on Amazon in multiple editions. Each song has several ASINs:
  - **Standard album (use these):** `B0GTN…` prefix — e.g. As You Lie There B0GTNM1468, Salesman Saint B0GTN6PT3B, Momma Gets By B0GTNCD76T. Standard album MP3 = B0GTNJJ8LY.
  - **Deluxe edition (avoid):** `B0H35…` prefix — interleaved with "(Commentary)" and "(Amazon Music Track by Track)" / "In Conversation with Paul McCartney & Paul Mescal" spoken-word tracks. These are NOT the plain songs.
- Confirmed correct album by reading the album column in Spotify Liked Songs ("The Boys of Dungeon Lane", no Deluxe/Commentary suffix), then matched the B0GTN batch.

### Quirks this session

- **lucida "uh-oh!" error on As You Lie There:** first download attempt produced no file and the page showed an "uh-oh!" error element. Fix: reloaded the lucida `?url=` page fresh and re-clicked — succeeded. (Don't double-click the button as a workaround — a stray extra click triggered a duplicate "As You Lie There (1).flac" download which had to be moved to Trash.)
- **CD quality** from Amazon for all 3 — brand-new 2026 release; hi-res unlikely.
- **Spotify auto-playback** on collection load — paused each time per "don't load my song".

## Related

- [download-a-track.md](download-a-track.md) — the workflow used
