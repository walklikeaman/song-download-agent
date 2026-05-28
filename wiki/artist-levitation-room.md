# Levitation Room

> Los Angeles psychedelic-rock / neo-psych band. Reverb-drenched, garage-psych sound.

## Session 1: 2026-05-28

1 liked track downloaded from Amazon Music via lucida.to. tag_fixer.py run. Spotify synced to "New Music 2026" playlist (and auto-playback paused — see quirk below).

### Tracks downloaded

| Title | ASIN | File | Size | Album | Notes |
|---|---|---|---|---|---|
| Equinox | B0GXGFD7V4 | levitation room - Equinox.flac | ~63 MB | Equinox - EP (2026) — track 5/5 | Hi-Res 24-bit/48kHz; lyrics not found (new 2026 release) |

### Destination

`~/Downloads/Spotify downloads/levitation room/` (tag_fixer placed it in the root `Spotify downloads/` — manually `mv`d to artist subfolder).

### Genre

`Rock` (from iTunes / tag_fixer.py enrichment).

### tag_fixer.py notes

- Hi-Res 24-bit/48kHz confirmed (~63 MB).
- Genre + cover art (resized 750→600px) enriched.
- ISRC QZGLS2635198 looked up on MusicBrainz — no date found.
- Lyrics not found (Genius needs token; AZLyrics index error; lrclib/syncedlyrics empty — new 2026 release).

### Amazon ASIN notes

- `amazon.com/s?k=Levitation+Room+Equinox&i=digital-music` returned two "Equinox" MP3 listings: B0GXG25QDJ (ILS 18.38) and B0GXGFD7V4 (ILS 3.68, the single-track buy). Used the cheaper single-track ASIN B0GXGFD7V4. Also a vinyl listing "Equinox Solar Custard" (B0GTW2DWKJ).

### Quirk: Spotify auto-playback on collection load

- Navigating to `open.spotify.com/collection/tracks` auto-started playback (tab title showed a now-playing track). Per the standing "don't load my song" rule, paused immediately via `[data-testid="control-button-playpause"]` before doing the sync.

## Related

- [download-a-track.md](download-a-track.md) — the workflow used
