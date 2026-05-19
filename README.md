# Song Download Agent

Download hi-res lossless audio and automatically enrich every FLAC with complete, correct metadata — original release dates, genre, lyrics, and cover art. No GUI required.

## How it works

**Step 1 — Download** via [lucida.to](https://lucida.to): paste an Amazon Music, Spotify, Qobuz, or Tidal URL and get a `.flac` file.

**Step 2 — Enrich** with `tag_fixer.py`: point it at one or more files and it handles everything else.

```bash
python3 tag_fixer.py ~/Downloads/*.flac
```

## What the script does

In order, for every file:

| Step | What happens |
|------|-------------|
| **Quality check** | Reports bit depth + sample rate. Warns if below 24-bit. |
| **Watermark removal** | Strips `encoder` (ffmpeg fingerprint) and lucida/tool download comments. |
| **Original date** | Looks up the ISRC on MusicBrainz to get the true first-release-date — not the reissue date. |
| **Metadata fill** | iTunes API fills missing `album`, `albumartist`, `tracknumber`, `discnumber`. Discogs as fallback. |
| **Genre** | Never left blank. Chain: existing → iTunes → artist cache → MusicBrainz artist tags. Consistent per artist across runs. |
| **Various Artists** | `albumartist = "Various Artists"` is always replaced with the track's own artist. |
| **Artist grouping** | `ARTISTSORT` / `ALBUMARTISTSORT` set from `artist_groups.json` so related artists group together in iTunes/Apple Music without changing display names. |
| **Cover art** | Original cover kept as-is. Resized to ≤ 600×600 px if larger. Fetched from iTunes if missing. |
| **Lyrics** | 6-source chain — LRCLib → lyrics.ovh → syncedlyrics → Genius → ChartLyrics → AZLyrics. Plain text, embedded in `LYRICS` tag. |
| **Move** | File moved to `~/Downloads/Spotify downloads/{Artist}/` if 2+ songs from that artist in the batch, otherwise flat in the root. |

## Setup

```bash
pip3 install mutagen requests syncedlyrics beautifulsoup4 azapi chartlyrics Pillow
```

**Optional — Genius API** (improves lyrics coverage):
1. Create a free app at [genius.com/api-clients](https://genius.com/api-clients) — App Website URL: `https://localhost`
2. Copy the Client Access Token
3. Add to `~/.zshrc`:
   ```bash
   export GENIUS_ACCESS_TOKEN="your_token_here"
   ```

## Usage

```bash
# Single file
python3 tag_fixer.py "Artist - Title.flac"

# Batch — everything in Downloads
python3 tag_fixer.py ~/Downloads/*.flac
```

**Output location:** `~/Downloads/Spotify downloads/`

```
Spotify downloads/
  Radiohead/                  ← subfolder: 2+ Radiohead tracks in batch
    Radiohead - Airbag.flac
    Radiohead - Karma Police.flac
  Fink - Wishing For Blue Sky.flac   ← flat: only one Fink track
```

## Download quality rule

Always pick the highest quality lossless source on lucida.to:

| Priority | Source | Max quality |
|----------|--------|------------|
| 1 | **Qobuz** | 24-bit / 192kHz FLAC |
| 2 | **Tidal** | 24-bit / 96kHz FLAC |
| 3 | **Amazon Music** | 24-bit FLAC |
| 4 | **Deezer** | 16-bit / 44.1kHz FLAC |
| ✗ | Soundcloud | Lossy — never use |

## Artist grouping

Edit `artist_groups.json` to group related artists together in iTunes:

```json
{
  "Grant-Lee Phillips": "Grant Lee Buffalo",
  "Grant Lee Phillips": "Grant Lee Buffalo"
}
```

The `artist` and `albumartist` tags stay as-is. Only `ARTISTSORT` and `ALBUMARTISTSORT` are set to the group key — iTunes uses these to show both under one artist entry.

## Config files

| File | Purpose |
|------|---------|
| `artist_groups.json` | User-edited artist grouping map |
| `artist_genres.json` | Auto-built genre cache (excluded from git) |

## Full documentation

See [WIKI.md](WIKI.md) for the complete reference — every rule, every API source, every tag explained.
