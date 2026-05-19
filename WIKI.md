# Song Download Agent — Wiki

> A two-step pipeline for downloading hi-res audio and auto-enriching it with complete metadata and lyrics. No GUI required.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Step 1 — Download via lucida.to](#step-1--download-via-lucidato)
4. [Step 2 — Tag & Lyrics enrichment via tag_fixer.py](#step-2--tag--lyrics-enrichment-via-tag_fixerpy)
   - [Output folder](#output-folder)
   - [Quality report](#quality-report)
   - [Album cover](#album-cover)
   - [Watermark removal](#watermark-removal)
   - [Original date via MusicBrainz](#original-date-via-musicbrainz)
   - [Metadata pipeline](#metadata-pipeline)
   - [Genre enforcement](#genre-enforcement)
   - [Various Artists rule](#various-artists-rule)
   - [Artist grouping](#artist-grouping)
   - [Lyrics pipeline](#lyrics-pipeline)
5. [Setup](#setup)
6. [Usage](#usage)
7. [Environment Variables](#environment-variables)
8. [Config Files](#config-files)
9. [Lyrics Sources — Full Chain](#lyrics-sources--full-chain)
10. [Tag Reference](#tag-reference)
11. [Known Limitations](#known-limitations)
12. [Changelog](#changelog)

---

## Overview

**Goal:** Given a song on Spotify, Amazon Music, Qobuz, Tidal, or Deezer — download it as a lossless FLAC, fill in any missing tags (album, year, track number, genre, disc number), and embed the full plain-text lyrics, all from the terminal.

**Two commands, that's it:**

```bash
# 1. Download via lucida.to (browser, one-time per song)
# 2. Fix tags + embed lyrics
python3 tag_fixer.py ~/Downloads/Artist\ -\ Title.flac
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     SONG DOWNLOAD AGENT                       │
│                                                              │
│  ┌─────────────────────┐     ┌───────────────────────────┐  │
│  │   Step 1: Download  │     │  Step 2: Enrich           │  │
│  │                     │     │                           │  │
│  │  lucida.to (web UI) │────▶│  tag_fixer.py             │  │
│  │                     │     │                           │  │
│  │  Sources:           │     │  Metadata:                │  │
│  │  • Amazon Music     │     │  iTunes API → Discogs     │  │
│  │  • Qobuz (hi-res)   │     │                           │  │
│  │  • Tidal            │     │  Lyrics:                  │  │
│  │  • Deezer           │     │  LRCLib → lyrics.ovh →   │  │
│  │  • Soundcloud       │     │  syncedlyrics → Genius →  │  │
│  │  • Yandex Music     │     │  ChartLyrics → AZLyrics  │  │
│  │                     │     │                           │  │
│  │  Output: .flac      │     │  Output: .flac (tagged)   │  │
│  └─────────────────────┘     └───────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## Step 1 — Download via lucida.to

**URL:** https://lucida.to

lucida.to is the hosted web frontend for the open-source [lucida](https://codeberg.org/lucida/lucida) library. It uses its own service accounts — you don't need credentials for any music service.

### Quality rule

**Always download lossless, always prefer hi-res.** Target: 24-bit FLAC. Never accept MP3, AAC, or any lossy format.

Select the source in this priority order — pick the highest one available for the track:

| Priority | Source | Max quality | Notes |
|---|---|---|---|
| 1 | **Qobuz** | 24-bit / 192kHz FLAC | Best available quality; largest hi-res catalog |
| 2 | **Tidal** | 24-bit / 96kHz FLAC | Good hi-res option |
| 3 | **Amazon Music** | 24-bit FLAC | Good for new releases |
| 4 | **Deezer** | 16-bit / 44.1kHz FLAC | CD quality only — use only if above unavailable |
| ✗ | **Soundcloud** | 128–320 kbps MP3 | Lossy — never use for music collection |

If a track is only available at CD quality (16-bit/44.1kHz) on all sources, that is the master and there is no hi-res to find. `tag_fixer.py` will warn you when this happens.

### How to download a track

1. Open https://lucida.to in Chrome
2. Paste a direct URL **or** type a search query into the search box
3. In the source list, pick the **highest quality lossless source** available (see table above)
4. Confirm the format shows **FLAC** — never download if it shows MP3/AAC
5. Click download — the file saves as a `.flac`

### Supported URL formats

| Service | Example |
|---------|---------|
| Amazon Music | `https://music.amazon.com/albums/B0GFSN1925` |
| Spotify track | `https://open.spotify.com/track/…` |
| Qobuz album | `https://www.qobuz.com/album/…` |
| Tidal track | `https://tidal.com/browse/track/…` |

### Source quality guide

| Source | Max quality | Notes |
|--------|-------------|-------|
| Qobuz | 24-bit / 192kHz FLAC | Best quality; richest metadata |
| Tidal | 24-bit / 96kHz FLAC | Good quality |
| Amazon Music | 24-bit FLAC | Good for newer releases |
| Deezer | 16-bit / 44.1kHz FLAC | Standard CD quality |

### Known quirks

- **Long URLs:** If pasting a long URL truncates in the search field, use the browser's address bar or paste into a text editor first to verify it's complete.
- **Deezer / Tidal** sometimes return JSON parse errors on lucida.to. Switch to Qobuz if that happens.
- If a download silently fails (`.crdownload` disappears with no `.flac`), click the download button again — retry always works.

---

## Step 2 — Tag & Lyrics enrichment via tag_fixer.py

**File:** `tag_fixer.py`  
**Requires:** Python 3.10+, see [Setup](#setup)

The script reads existing FLAC tags, reports audio quality, strips watermarks, corrects the release date to the original using MusicBrainz, fills in any missing metadata, fetches lyrics, and writes everything back into the file in place.

### Output folder

Every processed file is automatically moved to `~/Downloads/Spotify downloads/`. The folder is created if it doesn't exist.

**Artist subfolders** are created only when a batch contains **2 or more songs by the same artist**. A single song goes flat into the root:

```
# One Radiohead + one Fink → flat
~/Downloads/Spotify downloads/
  Radiohead - Airbag.flac
  Fink - Wishing For Blue Sky.flac

# Two Radiohead + one Fink → Radiohead gets a subfolder, Fink stays flat
~/Downloads/Spotify downloads/
  Radiohead/
    Radiohead - Airbag.flac
    Radiohead - Karma Police.flac
  Fink - Wishing For Blue Sky.flac
```

The script pre-scans all files before processing and announces at the start which artists will get subfolders. Folder names use the `albumartist` tag (already cleaned — no "Various Artists"). Characters invalid on macOS/Windows are replaced with `_`.

### Quality report

Runs first on every file. Reads the audio stream directly from the FLAC container and prints:

```
Quality : Hi-Res 24-bit/48kHz  stereo  [✓ Hi-Res]
Quality : CD quality 16-bit/44.1kHz  stereo  [⚠ CD quality — check if hi-res exists on Qobuz]
```

Quality tiers recognised:

| Label | Bits | Sample rate |
|---|---|---|
| Hi-Res 24-bit/192kHz | 24 | 192,000 Hz |
| Hi-Res 24-bit/96kHz | 24 | 96,000 Hz |
| Hi-Res 24-bit/88.2kHz | 24 | 88,200 Hz |
| Hi-Res 24-bit/48kHz | 24 | 48,000 Hz |
| Hi-Res 24-bit/44.1kHz | 24 | 44,100 Hz |
| CD quality 16-bit/44.1kHz | 16 | 44,100 Hz |

A `⚠` warning is printed for anything below 24-bit as a reminder to verify no hi-res source exists. It does **not** block processing — some albums genuinely have no hi-res master.

### Album cover

**Rule: the cover downloaded with the file is always the source of truth. It is never overwritten.**

The script checks for an embedded front cover (FLAC Picture type 3):

```
audio.pictures type=3 present?
        │ yes
        ▼
   Log "present (N KB) — kept as-is"
   → no action taken, original cover preserved

        │ no
        ▼
   Fetch from iTunes (up to 3000×3000 px JPEG)
        │ hit  → embed as type 3 Front Cover
        │ miss → log warning, skip (embed manually if needed)
```

Cover art from Qobuz is typically 600×600–3000×3000 px embedded JPEG. Amazon Music embeds smaller artwork. Either way, whatever lucida.to downloaded is kept intact — MusicBrainz, iTunes, and Discogs lookups never touch the picture data.

**Size rule:** Cover art must not exceed **600×600 px**. If the embedded image is larger, it is resized in-place using LANCZOS resampling before saving. The `MAX_COVER_PX = 600` constant in `tag_fixer.py` controls this limit.

### Watermark removal

Always runs first, before any lookups. Removes:

| Tag | What gets removed |
|---|---|
| `encoder` | ffmpeg fingerprint (`Lavf58.76.100`, etc.) — always deleted |
| `encoded_by` | Same — always deleted |
| `comment` | Any value matching: `lucida`, `downloaded`, `qobuz.com`, `amazon.com`, `tidal.com`, `deezer`, `ffmpeg`, `lavf` |

Comments that don't match those patterns (user-added notes) are kept.

### Original date via MusicBrainz

**Rule:** The `DATE` tag must reflect the *original* release, not a reissue or digital re-upload date.

The FLAC downloaded from lucida.to always contains an `ISRC` tag (International Standard Recording Code). This is used as a precise key into MusicBrainz to find the recording's `first-release-date` across all known releases:

```
ISRC tag present?
        │ yes
        ▼
   MusicBrainz ISRC lookup
   musicbrainz.org/ws/2/isrc/{ISRC}
        │
        ├── found → use earliest first-release-date across all recordings
        │           → force-update DATE tag (overrides reissue dates)
        │
        └── not found → leave DATE as-is, iTunes/Discogs fill it if empty
```

**Priority:** MusicBrainz runs before iTunes/Discogs. iTunes and Discogs can only fill the DATE tag if it is still empty after MusicBrainz — they never overwrite a date MusicBrainz already set.

### Metadata pipeline

Tags filled in (only if empty after MusicBrainz): `album`, `albumartist`, `date`, `tracknumber`, `discnumber`, `genre`  
Tags never overwritten: `title`, `artist` (assumed correct from the download)

```
ISRC → MusicBrainz (original date, authoritative)
        │
        ▼
   iTunes Search API  ──── hit ────▶  fill: album, albumartist, date (if empty),
   (itunes.apple.com)                       tracknumber, discnumber, genre
        │
       miss
        │
        ▼
   Discogs API  ──── hit ────▶  fill: album, date (if empty), genre
   (api.discogs.com)
```

**iTunes API fields used:**

| iTunes field | FLAC tag |
|---|---|
| `collectionName` | `album` |
| `artistName` | `albumartist` |
| `releaseDate` (first 4 chars) | `date` (only if MusicBrainz didn't set it) |
| `trackNumber/trackCount` | `tracknumber` |
| `discNumber/discCount` | `discnumber` |
| `primaryGenreName` | `genre` |

### Genre enforcement

**Rule: genre must never be blank.**

Sources tried in order until a non-empty value is found:

```
existing tag → iTunes primaryGenreName → artist cache → MusicBrainz artist tags → ⚠ warn
```

- **Artist cache** (`artist_genres.json`) — once a genre is found for an artist, it is stored and reused for all future tracks by that artist without hitting any API. This guarantees consistency: every Radiohead track gets the same genre.
- **MusicBrainz artist tags** — crowd-voted genre tags sorted by vote count; the top tag is used.
- If all sources fail, a `⚠` warning is printed. The tag is left empty rather than guessing.

### Various Artists rule

**Rule: `ALBUMARTIST` must never be set to "Various Artists".**

For compilation albums where the source sets `albumartist = "Various Artists"`, the script replaces it with the track's own `artist` value. The individual song artist is always more useful than a generic placeholder.

Patterns matched (case-insensitive): `Various Artists`, `Various Artist`, `Various`.

### Artist grouping

**Rule: related artists are grouped in iTunes/Apple Music without changing their display name.**

iTunes groups albums by `ALBUMARTISTSORT`. By setting the same sort key on multiple artists, they appear under one artist entry in the library while each track still shows its correct artist name.

**How it works:**

| Tag | Grant Lee Buffalo track | Grant-Lee Phillips track |
|-----|------------------------|--------------------------|
| `ARTIST` | `Grant Lee Buffalo` | `Grant-Lee Phillips` ← unchanged |
| `ALBUMARTIST` | `Grant Lee Buffalo` | `Grant-Lee Phillips` ← unchanged |
| `ARTISTSORT` | `Grant Lee Buffalo` | `Grant Lee Buffalo` ← group key |
| `ALBUMARTISTSORT` | `Grant Lee Buffalo` | `Grant Lee Buffalo` ← group key |

**Configuration:** Edit `artist_groups.json` in the same folder as `tag_fixer.py`:

```json
{
  "Grant-Lee Phillips": "Grant Lee Buffalo",
  "Grant Lee Phillips": "Grant Lee Buffalo"
}
```

Key = artist name as it appears in the tag. Value = the group name to use as the sort key. Add as many entries as needed.

### Lyrics pipeline

Lyrics are fetched as **plain text** and stored in the `LYRICS` Vorbis comment tag. If lyrics already exist in the tag, they are never overwritten.

Six sources are tried in order — first hit wins:

```
LRCLib ──▶ lyrics.ovh ──▶ syncedlyrics ──▶ Genius ──▶ ChartLyrics ──▶ AZLyrics
  #1           #2              #3             #4            #5             #6
(keyless)   (keyless)       (keyless)    (free token)   (keyless)     (keyless)
```

See [Lyrics Sources — Full Chain](#lyrics-sources--full-chain) for details on each.

---

## Setup

### Install Python dependencies

```bash
pip3 install mutagen requests syncedlyrics beautifulsoup4 azapi chartlyrics Pillow
```

### Set Genius API token (optional but recommended)

1. Go to https://genius.com/api-clients
2. Sign in / create a free account
3. Click **New API Client** — App Website URL: `https://localhost`
4. Copy the **Client Access Token**
5. Add to your shell profile:

```bash
echo 'export GENIUS_ACCESS_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

Without this token, source #4 (Genius) is silently skipped. Sources #1–3 and #5–6 still work.

---

## Usage

### Single file

```bash
python3 "/path/to/tag_fixer.py" ~/Downloads/Radiohead\ -\ Airbag.flac
```

### Multiple files

```bash
python3 "/path/to/tag_fixer.py" ~/Downloads/*.flac
```

### Full workflow (download → tag → lyrics)

```bash
# 1. Download from lucida.to → file lands in ~/Downloads/

# 2. Run the agent
python3 "/Users/whofarted/Claude/Songs Download/tag_fixer.py" ~/Downloads/*.flac
```

### Example output

```
Processing 1 file(s)...

────────────────────────────────────────────────────────────
  File : Radiohead - Airbag.flac
  All core tags present — will still verify/enrich
  iTunes search: "Airbag" by Radiohead
  iTunes result: OK Computer (1997) — track 1/12
  Lyrics search: "Airbag" by Radiohead
  Lyrics  : found via lrclib (474 chars)
  Updated : 2 tag(s)
    + discnumber='1/1'
    + lyrics=<474 chars from lrclib>

────────────────────────────────────────────────────────────
Done.
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GENIUS_ACCESS_TOKEN` | Optional | Free API token from genius.com/api-clients. Enables source #4 in the lyrics chain. Without it, Genius is skipped silently. |

---

## Config Files

Two JSON files live alongside `tag_fixer.py` in the `Songs Download/` folder:

### `artist_groups.json` — user-edited

Maps artist names to a shared group sort key. Edit this freely.

```json
{
  "Grant-Lee Phillips": "Grant Lee Buffalo",
  "Grant Lee Phillips": "Grant Lee Buffalo"
}
```

### `artist_genres.json` — auto-generated cache

Built automatically as tracks are processed. Maps `artist_name_lower → genre_string`. You can edit it manually to fix or seed genres before processing.

```json
{
  "radiohead": "Alternative Rock",
  "fink": "Folk/Americana"
}
```

---

## Lyrics Sources — Full Chain

Sources are tried in this exact order. The first one that returns a non-empty result wins; the rest are skipped.

### #1 — LRCLib (`lrclib.net`)
- **Key required:** No
- **API:** `GET https://lrclib.net/api/search?q={title artist}`
- **Coverage:** ~3 million tracks, community-contributed, open-source database
- **Returns:** Both `plainLyrics` and `syncedLyrics` (LRC format) — we use `plainLyrics`
- **Strength:** Best first stop. Purpose-built for FOSS music players, no rate limit, no auth.
- **Weakness:** Misses very new releases and obscure tracks.

### #2 — lyrics.ovh
- **Key required:** No
- **API:** `GET https://api.lyrics.ovh/v1/{artist}/{title}`
- **Coverage:** Moderate English + French catalog
- **Returns:** `{"lyrics": "..."}`
- **Strength:** Zero friction, good French coverage.
- **Weakness:** Unmaintained; occasionally slow or returns empty.

### #3 — syncedlyrics (Musixmatch → NetEase → Megalobiz)
- **Key required:** No (uses community token internally)
- **Install:** `pip3 install syncedlyrics`
- **Coverage:** Musixmatch (mainstream English), NetEase (Chinese catalog), Megalobiz (karaoke LRC community)
- **Returns:** Plain text or LRC (timestamps stripped to plain)
- **Strength:** Best Asian/Chinese track coverage via NetEase.
- **Weakness:** Musixmatch may return 30% snippet for some tracks (free-tier restriction).

### #4 — Genius
- **Key required:** Free token (see [Setup](#setup))
- **API:** `GET https://api.genius.com/search` + HTML scrape of result page
- **Coverage:** Largest English lyrics database; strong for hip-hop, pop, rock
- **Returns:** Scraped plain text from `data-lyrics-container` divs
- **Strength:** Unmatched English coverage. Also has annotations, translations.
- **Weakness:** Very new tracks may have no transcriptions yet. Scraping can be slow.

### #5 — ChartLyrics
- **Key required:** No
- **Install:** `pip3 install chartlyrics`
- **API:** SOAP — `http://api.chartlyrics.com/apiv1.asmx`
- **Coverage:** Charting hits, strongest for pre-2015 Western pop/rock
- **Returns:** Plain text
- **Strength:** No key, no scraping, stable legacy service.
- **Weakness:** Thin coverage for anything not on the charts. SOAP is slow.

### #6 — AZLyrics (last resort)
- **Key required:** No
- **Install:** `pip3 install azapi`
- **Coverage:** One of the largest English lyrics databases. Very strong for rock, metal, pop.
- **Returns:** Scraped plain text
- **Strength:** Enormous catalog; often the only source for niche English tracks.
- **Weakness:** Active anti-scraping. Hard rate limit (2s delay enforced in code). May block after heavy use. Library unmaintained since 2022.

---

## Tag Reference

Tags written by this agent (Vorbis Comment / FLAC format):

| Tag | Example | Source | Rule |
|---|---|---|---|
| `title` | `Airbag` | From file | Never modified |
| `artist` | `Radiohead` | From file | Never modified |
| `albumartist` | `Radiohead` | iTunes `artistName` | Never "Various Artists" — replaced with `artist` if so |
| `album` | `OK Computer` | iTunes `collectionName` | Filled if empty |
| `date` | `1997-05-21` | MusicBrainz ISRC → iTunes → Discogs | MusicBrainz is authoritative (original release date) |
| `tracknumber` | `1/12` | iTunes `trackNumber/trackCount` | Filled if empty |
| `discnumber` | `1/1` | iTunes `discNumber/discCount` | Filled if empty |
| `genre` | `Alternative Rock` | iTunes → cache → MusicBrainz | Never left blank |
| `artistsort` | `Grant Lee Buffalo` | `artist_groups.json` | Set only if artist is in the groups map |
| `albumartistsort` | `Grant Lee Buffalo` | `artist_groups.json` | Set only if artist is in the groups map |
| `lyrics` | *(full text)* | 6-source chain | Never overwritten if already present |
| *(picture)* | *(JPEG, type 3)* | From file / iTunes fallback | Original kept; resized to ≤600×600 px |

**Tags removed:** `encoder`, `encoded_by` (always); `comment` if it contains download tool references.  
**Tags never touched:** `isrc`, `label`, `copyright`, `composer`, `performer`, `lyricist`, `rating`, and all other tags not listed above.

---

## Known Limitations

| Issue | Status |
|---|---|
| MusicBrainz blocked at network/TLS level | Permanent on this network. iTunes + Discogs used instead. |
| Megalobiz connection refused | syncedlyrics tries it internally; errors are printed by the library but harmless — the chain continues. |
| Fink — Wishing For Blue Sky: lyrics found via AZLyrics | The track is a 2026 release with no transcriptions on LRCLib, Genius, etc. AZLyrics is the only source that has it. |
| lyricsgenius 3.7.x incompatible with Python 3.10 | Uses `typing.Self` (requires 3.11+). Replaced with direct Genius API calls — no library needed. |
| ChartLyrics has very sparse coverage | Returns 0 results for most modern tracks. Kept as a fallback for pre-2015 charting hits. |
| syncedlyrics prints its own errors to stdout | Internal behavior of the library, not suppressible without patching. Harmless. |

---

## Changelog

| Date | Change |
|---|---|
| 2026-05-19 | Initial version. iTunes + Discogs metadata pipeline. |
| 2026-05-19 | Added 6-source lyrics chain: LRCLib, lyrics.ovh, syncedlyrics, Genius, ChartLyrics, AZLyrics. |
| 2026-05-19 | Replaced lyricsgenius library (Python 3.11+ only) with direct Genius API + BeautifulSoup scrape. |
| 2026-05-19 | Added watermark removal: strips `encoder`, `encoded_by`, and download-tool `comment` tags. |
| 2026-05-19 | Added MusicBrainz ISRC lookup for authoritative original release dates. iTunes/Discogs no longer overwrite MB-confirmed dates. |
| 2026-05-19 | Added quality check: reports bit depth and sample rate on every file; warns if below 24-bit. Documented source priority rule (Qobuz > Tidal > Amazon > Deezer, never lossy). |
| 2026-05-19 | Added album cover check: existing covers kept untouched; missing covers fetched from iTunes. All covers resized to ≤600×600 px via Pillow/LANCZOS. |
| 2026-05-19 | All processed files automatically moved to ~/Downloads/Spotify downloads/ after tagging. |
| 2026-05-19 | Genre enforcement: never blank. Chain: existing → iTunes → artist cache → MusicBrainz. Cache persists in artist_genres.json. |
| 2026-05-19 | Various Artists rule: albumartist "Various Artists" always replaced with track artist. |
| 2026-05-19 | Artist grouping: artist_groups.json maps artists to shared ARTISTSORT/ALBUMARTISTSORT for iTunes grouping without changing display names. |
| 2026-05-19 | Artist subfolders created only when batch has 2+ songs by the same artist. Single songs stay flat in Spotify downloads/. |

---

*This wiki is updated as new functions are added to the agent.*
