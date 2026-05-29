# Violet Grohl

> Alternative / alt-rock singer-songwriter (daughter of Dave Grohl). Solo material debuting 2025–2026.

## Session 1: 2026-05-29

3 liked tracks downloaded from Amazon Music via lucida.to. tag_fixer.py run on all. Spotify synced to "New Music 2026" playlist (and auto-playback paused on each collection load — see quirk).

### Tracks downloaded

| Title | ASIN | File | Size | Album | Quality | Notes |
|---|---|---|---|---|---|---|
| Bug In The Cake | B0GQCWR2QZ | Violet Grohl - Bug In The Cake.flac | ~21 MB | Be Sweet To Me — track 3/11 | CD 16/44.1 | Lyrics via lyrics.ovh; ISRC USUG12601781 |
| 595 | B0GQD7BSRJ | Violet Grohl - 595.flac | ~19 MB | Be Sweet To Me — track 2/11 | CD 16/44.1 | "595 [Explicit]" on Amazon; ISRC USUG12601779 |
| THUM | B0GQDZD2DB | Violet Grohl - THUM.flac | ~17 MB | THUM - Single (2026) — track 1/2 | CD 16/44.1 | Date corrected to 2025-12-05 (MusicBrainz); ISRC QMEU32517945 |

### Destination

`~/Downloads/Spotify downloads/Violet Grohl/` (tag_fixer auto-created the subfolder this time).

### Genre

`Alternative` (from iTunes / tag_fixer.py enrichment) for all 3.

### tag_fixer.py notes

- All 3 CD quality 16-bit/44.1kHz from Amazon Music — tag_fixer flagged "check if hi-res exists on Qobuz". Kept Amazon versions per Amazon-first workflow (consistent with prior CD-quality sessions); hi-res unlikely for these brand-new 2026 releases.
- Cover art (750→600px), discnumber, genre enriched on all.
- Lyrics: Bug In The Cake via lyrics.ovh; 595 and THUM already had lyrics embedded from source.

### Amazon ASIN notes

- THUM had multiple ASINs (B0GQDZD2DB, B0GFT7T8N6 @ 3.68; B0GFSN1925 @ 7.35). Picked B0GQDZD2DB — same recent B0GQ… batch as Bug In The Cake and 595 (the current single/EP release).
- Other Violet Grohl singles seen but not liked: Be Sweet To Me, Cool Buzz, Nausea (feat. Dave Grohl).

### Quirk: Spotify auto-playback

- `open.spotify.com/collection/tracks` auto-starts playback on load every time. Paused via `[data-testid="control-button-playpause"]` before/after sync per the "don't load my song" rule.

## Related

- [download-a-track.md](download-a-track.md) — the workflow used
