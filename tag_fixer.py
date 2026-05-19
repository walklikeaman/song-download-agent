#!/usr/bin/env python3
"""
tag_fixer.py — Fix audio file tags using the iTunes Search API + Discogs fallback,
               then fetch and embed plain-text lyrics from 8 sources.

Usage:
    python3 tag_fixer.py <file.flac> [file2.flac ...]
    python3 tag_fixer.py ~/Downloads/*.flac

What it does:
    1. Reads existing tags from each FLAC file
    2. Searches iTunes API (no auth needed) for the track
    3. Falls back to Discogs if iTunes has no result
    4. Fills in any missing tags: album, year, track number, album artist, genre
    5. Fetches plain-text lyrics — tries 8 sources in order until one hits:
         1. LRCLib       — keyless, 3M+ tracks, open-source
         2. lyrics.ovh   — keyless REST API
         3. syncedlyrics — Musixmatch → NetEase → Megalobiz (keyless)
         4. Genius       — direct API scrape (set GENIUS_ACCESS_TOKEN)
         5. ChartLyrics  — keyless SOAP, good for pre-2015 hits
         6. AZLyrics     — keyless scraper, large English DB (rate-limited)
    6. Embeds lyrics into the LYRICS tag and saves the file in place

Environment variables (all optional):
    GENIUS_ACCESS_TOKEN — free key from genius.com/api-clients

Note: MusicBrainz is blocked on this network (TLS handshake fails).
      iTunes and Discogs APIs work fine as replacements.
"""

import sys
import time
import os
import re
import io
import json
import shutil
import urllib.parse
import requests
from mutagen.flac import FLAC, Picture
from PIL import Image

try:
    import syncedlyrics
except ImportError:
    syncedlyrics = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import azapi
except ImportError:
    azapi = None

try:
    from chartlyrics import ChartLyricsClient
except ImportError:
    ChartLyricsClient = None

# ── Config ────────────────────────────────────────────────────────────────────
USER_AGENT   = "LucidaTagger/1.0"
ITUNES_BASE  = "https://itunes.apple.com/search"
DISCOGS_BASE = "https://api.discogs.com"
RATE_LIMIT   = 0.5   # seconds between requests

WANTED_TAGS  = ["title", "artist", "albumartist", "album", "date", "tracknumber", "genre"]

# Default destination folder — files are moved here after tagging
DEST_FOLDER = os.path.expanduser("~/Downloads/Spotify downloads")

# Maximum pixel dimension for embedded album art (width or height)
MAX_COVER_PX = 600

# Config / cache files (same folder as this script)
_HERE              = os.path.dirname(os.path.abspath(__file__))
ARTIST_GENRES_FILE = os.path.join(_HERE, "artist_genres.json")   # auto-built cache
ARTIST_GROUPS_FILE = os.path.join(_HERE, "artist_groups.json")   # user-edited mapping

# "Various Artists" variants — never written to albumartist
_VARIOUS = re.compile(r"^various(\s+artists?)?$", re.I)


# ── Persistent caches ─────────────────────────────────────────────────────────

def _load_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Loaded once at startup; saved after each file that modifies them
_artist_genres: dict = _load_json(ARTIST_GENRES_FILE)   # {artist_lower: genre_str}
_artist_groups: dict = _load_json(ARTIST_GROUPS_FILE)   # {artist_name: group_artist}

# Quality tiers (bits, sample_rate_hz)
QUALITY_TIERS = [
    (24, 192000, "Hi-Res 24-bit/192kHz"),
    (24,  96000, "Hi-Res 24-bit/96kHz"),
    (24,  88200, "Hi-Res 24-bit/88.2kHz"),
    (24,  48000, "Hi-Res 24-bit/48kHz"),
    (24,  44100, "Hi-Res 24-bit/44.1kHz"),
    (16,  44100, "CD quality 16-bit/44.1kHz"),
    (16,  48000, "16-bit/48kHz"),
]


# Tags injected by download tools — always removed
_WATERMARK_TAGS = {"encoder", "encoded_by", "encodedby"}
# COMMENT tags are removed only if they contain tool references
_COMMENT_TOOL_PATTERNS = re.compile(r"lucida|downloaded|qobuz\.com|amazon\.com|tidal\.com|deezer|ffmpeg|lavf", re.I)

MUSICBRAINZ_BASE = "https://musicbrainz.org/ws/2"
MB_RATE_LIMIT    = 1.1   # MusicBrainz asks for max 1 req/sec


# ── Watermark cleaner ─────────────────────────────────────────────────────────

def strip_watermarks(audio: FLAC) -> list[str]:
    """
    Remove tool-injected tags (encoder fingerprints, download URLs in comments).
    Returns list of removed tag names.
    """
    removed = []

    # Always remove encoder fingerprint tags
    for key in list(audio.keys()):
        if key.lower() in _WATERMARK_TAGS:
            del audio[key]
            removed.append(key)

    # Remove COMMENT tags that reference download tools
    comments = audio.get("comment") or audio.get("COMMENT") or []
    bad = [c for c in comments if _COMMENT_TOOL_PATTERNS.search(c)]
    if bad:
        clean = [c for c in comments if not _COMMENT_TOOL_PATTERNS.search(c)]
        if clean:
            audio["comment"] = clean
        else:
            try:
                del audio["comment"]
            except KeyError:
                try:
                    del audio["COMMENT"]
                except KeyError:
                    pass
        removed.append(f"comment ({len(bad)} value(s))")

    return removed


# ── MusicBrainz original-date lookup ─────────────────────────────────────────

def mb_original_date(isrc: str) -> str | None:
    """
    Look up the recording's true first-release-date via MusicBrainz ISRC.
    Returns ISO date string (YYYY-MM-DD or YYYY) for the earliest release, or None.
    """
    try:
        r = requests.get(
            f"{MUSICBRAINZ_BASE}/isrc/{isrc}",
            params={"fmt": "json", "inc": "releases"},
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        time.sleep(MB_RATE_LIMIT)
        if r.status_code != 200:
            return None
        recordings = r.json().get("recordings", [])
        dates = [
            rec["first-release-date"]
            for rec in recordings
            if rec.get("first-release-date")
        ]
        if not dates:
            return None
        # Return the earliest date
        return sorted(dates)[0]
    except Exception as e:
        print(f"  MusicBrainz error: {e}")
        return None


# ── iTunes helpers ────────────────────────────────────────────────────────────

def itunes_search(title: str, artist: str) -> dict | None:
    """
    Search iTunes for a track. Returns the best matching result dict or None.
    Response fields we use:
      artistName, collectionName, trackName, releaseDate,
      trackNumber, trackCount, primaryGenreName
    """
    params = {
        "term":    f"{title} {artist}",
        "media":   "music",
        "entity":  "song",
        "limit":   5,
    }
    try:
        r = requests.get(ITUNES_BASE, params=params,
                         headers={"User-Agent": USER_AGENT}, timeout=10)
        r.raise_for_status()
        time.sleep(RATE_LIMIT)
        results = r.json().get("results", [])
    except Exception as e:
        print(f"  iTunes error: {e}")
        return None

    if not results:
        return None

    # Prefer exact title match (case-insensitive)
    title_lower = title.lower()
    for item in results:
        if item.get("trackName", "").lower() == title_lower:
            return item
    return results[0]


def discogs_search(title: str, artist: str) -> dict | None:
    """
    Search Discogs for a release containing this track.
    Returns a simplified dict with the fields we care about, or None.
    """
    params = {
        "q":     f"{title} {artist}",
        "type":  "release",
        "per_page": 3,
    }
    try:
        r = requests.get(f"{DISCOGS_BASE}/database/search",
                         params=params,
                         headers={"User-Agent": USER_AGENT}, timeout=10)
        r.raise_for_status()
        time.sleep(RATE_LIMIT)
        results = r.json().get("results", [])
    except Exception as e:
        print(f"  Discogs error: {e}")
        return None

    if not results:
        return None

    best = results[0]
    year = str(best.get("year", ""))
    genre_list = best.get("genre", []) + best.get("style", [])
    return {
        "album":  best.get("title", ""),
        "year":   year,
        "genre":  "; ".join(genre_list[:2]),
    }


# ── Lyrics helpers ───────────────────────────────────────────────────────────

def _strip_lrc_timestamps(lrc: str) -> str:
    """Convert LRC-format timestamped lyrics to plain text."""
    lines = []
    for line in lrc.splitlines():
        clean = re.sub(r"\[\d+:\d+[\.\d]*\]", "", line).strip()
        if clean:
            lines.append(clean)
    return "\n".join(lines)


def fetch_lyrics(title: str, artist: str) -> tuple[str, str] | tuple[None, None]:
    """
    Try to fetch plain-text lyrics from 6 sources in order.
    Returns (lyrics_text, source_name) or (None, None).
    """
    query = f"{title} {artist}"
    _BROWSER_UA = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # ── 1. LRCLib — keyless, open, 3 M+ tracks ───────────────────────────────
    try:
        r = requests.get(
            "https://lrclib.net/api/search",
            params={"q": query},
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        if r.status_code == 200:
            hits = r.json()
            if hits:
                # Prefer a hit whose title matches exactly
                best = next(
                    (h for h in hits if h.get("trackName", "").lower() == title.lower()),
                    hits[0],
                )
                plain = best.get("plainLyrics", "").strip()
                if plain:
                    return plain, "lrclib"
        time.sleep(RATE_LIMIT)
    except Exception as e:
        print(f"  LRCLib error: {e}")

    # ── 2. lyrics.ovh — keyless REST ─────────────────────────────────────────
    try:
        r = requests.get(
            f"https://api.lyrics.ovh/v1/{urllib.parse.quote(artist)}/{urllib.parse.quote(title)}",
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        if r.status_code == 200:
            lyrics = r.json().get("lyrics", "").strip()
            if lyrics:
                return lyrics, "lyrics.ovh"
        time.sleep(RATE_LIMIT)
    except Exception as e:
        print(f"  lyrics.ovh error: {e}")

    # ── 3. syncedlyrics — Musixmatch → NetEase → Megalobiz ───────────────────
    if syncedlyrics:
        try:
            result = syncedlyrics.search(query, plain_only=True)
            if result and result.strip():
                return result.strip(), "syncedlyrics/plain"
            result = syncedlyrics.search(query)
            if result and result.strip():
                return _strip_lrc_timestamps(result), "syncedlyrics/lrc→plain"
        except Exception as e:
            print(f"  syncedlyrics error: {e}")

    # ── 4. Genius — direct API + page scrape ─────────────────────────────────
    token = os.environ.get("GENIUS_ACCESS_TOKEN")
    if token and BeautifulSoup:
        try:
            r = requests.get(
                "https://api.genius.com/search",
                params={"q": query},
                headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT},
                timeout=10,
            )
            r.raise_for_status()
            time.sleep(RATE_LIMIT)
            hits = r.json().get("response", {}).get("hits", [])
            if hits:
                song_url = hits[0]["result"]["url"]
                page = requests.get(song_url, headers={"User-Agent": _BROWSER_UA}, timeout=10)
                soup = BeautifulSoup(page.text, "html.parser")
                containers = soup.find_all("div", attrs={"data-lyrics-container": "true"})
                if containers:
                    raw = "\n".join(
                        re.sub(r"<br\s*/?>", "\n", str(c.decode_contents()))
                        for c in containers
                    )
                    lyrics = re.sub(r"<[^>]+>", "", raw).strip()
                    lyrics = re.sub(
                        rf"^.*?{re.escape(title)}\s+Lyrics\s*", "", lyrics,
                        flags=re.DOTALL | re.IGNORECASE,
                    ).strip()
                    if lyrics:
                        return lyrics, "genius"
        except Exception as e:
            print(f"  Genius error: {e}")
    elif not token:
        print("  Genius skipped — set GENIUS_ACCESS_TOKEN env var to enable")

    # ── 5. ChartLyrics — keyless SOAP, good for pre-2015 charting hits ───────
    if ChartLyricsClient:
        try:
            client = ChartLyricsClient()
            results = list(client.search_artist_and_song(artist, title))
            if results:
                detail = client.get_lyric(results[0].LyricChecksum, results[0].LyricId)
                if detail and detail.Lyric and str(detail.Lyric).strip():
                    return str(detail.Lyric).strip(), "chartlyrics"
        except Exception as e:
            print(f"  ChartLyrics error: {e}")

    # ── 6. AZLyrics — large English DB, scraper (slow — last resort) ─────────
    if azapi:
        try:
            time.sleep(2)  # AZLyrics is aggressive about rate-limiting
            api = azapi.AZlyrics(accuracy=0.5)
            api.title  = title
            api.artist = artist
            lyrics = (api.getLyrics() or "").strip()
            if lyrics:
                return lyrics, "azlyrics"
        except Exception as e:
            print(f"  AZLyrics error: {e}")

    return None, None


# ── Artwork helpers ───────────────────────────────────────────────────────────

def _resize_image_bytes(data: bytes, max_px: int = MAX_COVER_PX) -> tuple[bytes, int, int]:
    """
    Resize image bytes so neither dimension exceeds max_px.
    Returns (resized_bytes, width, height). Uses LANCZOS resampling.
    If already within limits, returns original bytes unchanged.
    """
    img = Image.open(io.BytesIO(data))
    w, h = img.size
    if w <= max_px and h <= max_px:
        return data, w, h
    img.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    fmt = img.format or "JPEG"
    img.save(buf, format=fmt, quality=90, optimize=True)
    return buf.getvalue(), img.width, img.height


def _itunes_artwork_url(url100: str) -> str:
    """Request 600×600 from iTunes (matches our MAX_COVER_PX cap)."""
    return re.sub(r"\d+x\d+bb(\.\w+)$", rf"{MAX_COVER_PX}x{MAX_COVER_PX}bb\1", url100)


def check_and_fetch_artwork(audio: FLAC, itunes_result: dict | None) -> str | None:
    """
    Enforce the cover art rules:
      1. Must exist (fetch from iTunes if missing).
      2. Must not exceed MAX_COVER_PX × MAX_COVER_PX (resize if larger).
    Original data is replaced only when resizing is needed.
    Returns 'artwork' if the picture was added or changed, None otherwise.
    """
    existing = [p for p in audio.pictures if p.type == 3]

    if existing:
        pic = existing[0]
        raw = pic.data
        try:
            resized, w, h = _resize_image_bytes(raw)
        except Exception as e:
            print(f"  Cover art   : present but unreadable ({e}) — kept as-is")
            return None

        size_kb = len(raw) // 1024
        if resized is raw:
            # Already within limits
            print(f"  Cover art   : present {w}×{h} px ({size_kb} KB) — OK")
            return None
        else:
            # Needs resizing — replace in place
            new_kb = len(resized) // 1024
            # Re-read original dims from the img object (raw was too large)
            orig_img = Image.open(io.BytesIO(raw))
            ow, oh = orig_img.size
            print(f"  Cover art   : {ow}×{oh} px ({size_kb} KB) → resized to {w}×{h} px ({new_kb} KB)")
            audio.clear_pictures()
            pic.data = resized
            pic.width  = w
            pic.height = h
            audio.add_picture(pic)
            return "artwork"

    # ── No cover found — fetch ───────────────────────────────────────────────
    print(f"  Cover art   : MISSING — attempting fetch")

    if itunes_result:
        art_url = _itunes_artwork_url(itunes_result.get("artworkUrl100", ""))
        if art_url:
            try:
                r = requests.get(art_url, timeout=15)
                if r.status_code == 200 and r.content:
                    data, w, h = _resize_image_bytes(r.content)
                    pic = Picture()
                    pic.type   = 3
                    pic.mime   = r.headers.get("Content-Type", "image/jpeg").split(";")[0]
                    pic.desc   = "Cover"
                    pic.data   = data
                    pic.width  = w
                    pic.height = h
                    audio.add_picture(pic)
                    print(f"  Cover art   : fetched from iTunes {w}×{h} px ({len(data)//1024} KB)")
                    return "artwork"
            except Exception as e:
                print(f"  Cover art   : iTunes fetch failed — {e}")

    print(f"  Cover art   : could not fetch — embed manually if needed")
    return None


# ── Genre helpers ─────────────────────────────────────────────────────────────

def mb_artist_genre(artist: str) -> str | None:
    """Look up the top genre tag for an artist from MusicBrainz."""
    try:
        r = requests.get(
            f"{MUSICBRAINZ_BASE}/artist/",
            params={"query": artist, "fmt": "json", "limit": 1},
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        time.sleep(MB_RATE_LIMIT)
        if r.status_code != 200:
            return None
        artists = r.json().get("artists", [])
        if not artists:
            return None
        tags = sorted(artists[0].get("tags", []), key=lambda t: t.get("count", 0), reverse=True)
        if tags:
            return tags[0]["name"].title()
    except Exception as e:
        print(f"  MusicBrainz genre error: {e}")
    return None


def ensure_genre(artist: str, current_genre: str, itunes_genre: str) -> tuple[str, str]:
    """
    Guarantee a non-blank genre. Tries (in order):
      1. existing tag          — already set, keep it
      2. iTunes result         — from the search we already did
      3. artist cache          — genre seen for this artist before
      4. MusicBrainz artist    — live lookup
    Returns (genre_string, source_label). Updates _artist_genres cache in-place.
    """
    key = artist.lower()

    if current_genre:
        # Keep existing; still update cache if empty
        if key not in _artist_genres:
            _artist_genres[key] = current_genre
        return current_genre, "existing"

    if itunes_genre:
        _artist_genres[key] = itunes_genre
        return itunes_genre, "itunes"

    if key in _artist_genres:
        return _artist_genres[key], "cache"

    print(f"  Genre       : empty — querying MusicBrainz")
    mb_genre = mb_artist_genre(artist)
    if mb_genre:
        _artist_genres[key] = mb_genre
        return mb_genre, "musicbrainz"

    return "", "none"


# ── Artist / albumartist helpers ──────────────────────────────────────────────

def resolve_albumartist(artist: str, albumartist: str) -> tuple[str, bool]:
    """
    Return the correct albumartist and whether it was changed.
    Rule: never use 'Various Artists' — use the track artist instead.
    """
    if _VARIOUS.match(albumartist.strip()):
        return artist, True
    return albumartist, False


def apply_artist_group(audio: FLAC, artist: str, albumartist: str) -> str | None:
    """
    If artist_groups.json maps this artist (or albumartist) to a group,
    write ARTISTSORT and ALBUMARTISTSORT so iTunes/Apple Music groups them together.
    Returns the group name if applied, else None.
    """
    group = (_artist_groups.get(artist)
             or _artist_groups.get(albumartist)
             or _artist_groups.get(artist.lower())
             or _artist_groups.get(albumartist.lower()))
    if group:
        audio["artistsort"]      = group
        audio["albumartistsort"] = group
        return group
    return None


# ── Quality check ────────────────────────────────────────────────────────────

def check_quality(audio: FLAC) -> tuple[str, bool]:
    """
    Inspect audio stream specs. Returns (description, is_hires).
    Prints a warning if quality is below 24-bit.
    """
    info = audio.info
    bits   = info.bits_per_sample
    rate   = info.sample_rate
    ch     = info.channels
    ch_str = "mono" if ch == 1 else "stereo" if ch == 2 else f"{ch}ch"

    # Match against known tiers
    label = None
    for (b, r, name) in QUALITY_TIERS:
        if bits == b and rate == r:
            label = name
            break
    if not label:
        label = f"{bits}-bit/{rate//1000}kHz"

    is_hires = bits >= 24
    flag = "✓ Hi-Res" if is_hires else "⚠ CD quality — check if hi-res exists on Qobuz"
    print(f"  Quality     : {label}  {ch_str}  [{flag}]")
    return label, is_hires


# ── Core tagger ───────────────────────────────────────────────────────────────

def fix_file(filepath: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  File : {os.path.basename(filepath)}")

    try:
        audio = FLAC(filepath)
    except Exception as e:
        print(f"  ERROR opening file: {e}")
        return

    def tag(key: str) -> str:
        return (audio.get(key) or [""])[0].strip()

    title  = tag("title")
    artist = tag("artist")

    # ── Quality check ────────────────────────────────────────────────────────
    check_quality(audio)

    # ── Strip watermarks ────────────────────────────────────────────────────
    removed = strip_watermarks(audio)
    if removed:
        print(f"  Removed tags : {', '.join(removed)}")

    missing = [t for t in WANTED_TAGS if not tag(t)]
    if missing:
        print(f"  Missing tags : {', '.join(missing)}")
    else:
        print(f"  All core tags present — will still verify/enrich")

    if not title or not artist:
        print("  SKIP: no title or artist — cannot search.")
        return

    # ── MusicBrainz original date (via ISRC) ────────────────────────────────
    isrc = tag("isrc")
    if isrc:
        print(f"  MusicBrainz : looking up ISRC {isrc}")
        original_date = mb_original_date(isrc)
        if original_date:
            current_date = tag("date")
            current_year = current_date[:4] if current_date else ""
            original_year = original_date[:4]
            if current_year != original_year:
                audio["date"] = original_date
                print(f"  Date fixed  : {current_date!r} → {original_date!r} (MusicBrainz original)")
            else:
                # Year matches — upgrade to full ISO date if we only had a year
                if len(current_date) == 4 and len(original_date) > 4:
                    audio["date"] = original_date
                    print(f"  Date refined: {current_date!r} → {original_date!r} (MusicBrainz)")
                else:
                    print(f"  Date OK     : {current_date!r} matches MusicBrainz original")
        else:
            print(f"  MusicBrainz : no date found for ISRC {isrc}")
    else:
        print(f"  MusicBrainz : no ISRC tag — skipping original-date lookup")

    # ── iTunes lookup ───────────────────────────────────────────────────────
    print(f"  iTunes search: \"{title}\" by {artist}")
    result = itunes_search(title, artist)

    updated = []

    def maybe_set(key: str, value: str, force: bool = False) -> None:
        if not value:
            return
        current = tag(key)
        if force or not current:
            audio[key] = value
            updated.append(f"{key}={value!r}")

    itunes_genre = ""

    if result:
        release_date = result.get("releaseDate", "")
        year         = release_date[:4] if release_date else ""
        album        = result.get("collectionName", "")
        album_artist = result.get("artistName", artist)
        track_no     = str(result.get("trackNumber", ""))
        track_count  = str(result.get("trackCount", ""))
        itunes_genre = result.get("primaryGenreName", "")
        disc_no      = str(result.get("discNumber", ""))
        disc_count   = str(result.get("discCount", ""))

        track_tag = f"{track_no}/{track_count}" if track_no and track_count else track_no
        disc_tag  = f"{disc_no}/{disc_count}"   if disc_no  and disc_count  else disc_no

        print(f"  iTunes result: {album} ({year}) — track {track_tag}")

        maybe_set("album",       album)
        maybe_set("date",        year)
        maybe_set("tracknumber", track_tag)
        maybe_set("discnumber",  disc_tag)

        # ── albumartist — never "Various Artists" ────────────────────────────
        resolved_aa, was_various = resolve_albumartist(artist, album_artist)
        if was_various:
            print(f"  albumartist : 'Various Artists' → '{resolved_aa}' (track artist used)")
        maybe_set("albumartist", resolved_aa)

    else:
        print("  iTunes: no result — trying Discogs fallback")
        disc = discogs_search(title, artist)
        if disc:
            print(f"  Discogs result: {disc['album']} ({disc['year']})")
            maybe_set("album", disc["album"])
            maybe_set("date",  disc["year"])
            itunes_genre = disc["genre"]   # treat Discogs genre same as iTunes for ensure_genre
        else:
            print("  No results from any source.")

        # Fix Various Artists even when iTunes missed
        current_aa = tag("albumartist")
        if current_aa:
            resolved_aa, was_various = resolve_albumartist(artist, current_aa)
            if was_various:
                audio["albumartist"] = resolved_aa
                updated.append(f"albumartist='{resolved_aa}' (was Various Artists)")
                print(f"  albumartist : 'Various Artists' → '{resolved_aa}'")

    # ── Genre — must never be blank ──────────────────────────────────────────
    current_genre = tag("genre")
    final_genre, genre_src = ensure_genre(artist, current_genre, itunes_genre)
    if final_genre and not current_genre:
        audio["genre"] = final_genre
        updated.append(f"genre='{final_genre}' (from {genre_src})")
        print(f"  Genre       : set to '{final_genre}' (source: {genre_src})")
        _save_json(ARTIST_GENRES_FILE, _artist_genres)
    elif not final_genre:
        print(f"  Genre       : ⚠ could not determine — please set manually")
    else:
        if genre_src != "existing":
            print(f"  Genre       : '{current_genre}' (kept; cache updated)")

    # ── Artist grouping (ARTISTSORT / ALBUMARTISTSORT) ───────────────────────
    current_aa = tag("albumartist") or artist
    group = apply_artist_group(audio, artist, current_aa)
    if group:
        updated.append(f"artistsort='{group}' (group)")
        print(f"  Artist group: '{artist}' → grouped under '{group}'")

    # ── Album cover ─────────────────────────────────────────────────────────
    art_key = check_and_fetch_artwork(audio, result)
    if art_key:
        updated.append("artwork=<embedded>")

    # ── Lyrics ──────────────────────────────────────────────────────────────
    existing_lyrics = tag("lyrics")
    if existing_lyrics:
        print(f"  Lyrics  : already present ({len(existing_lyrics)} chars) — skipping")
    else:
        print(f"  Lyrics search: \"{title}\" by {artist}")
        lyrics, source = fetch_lyrics(title, artist)
        if lyrics:
            audio["lyrics"] = lyrics
            updated.append(f"lyrics=<{len(lyrics)} chars from {source}>")
            print(f"  Lyrics  : found via {source} ({len(lyrics)} chars)")
        else:
            print("  Lyrics  : not found in any source")

    if updated:
        audio.save()
        print(f"  Updated : {len(updated)} tag(s)")
        for u in updated:
            print(f"    + {u}")
    else:
        print("  No changes needed — tags already complete.")

    # ── Move to destination folder ───────────────────────────────────────────
    os.makedirs(DEST_FOLDER, exist_ok=True)
    dest_path = os.path.join(DEST_FOLDER, os.path.basename(filepath))
    if os.path.abspath(filepath) != os.path.abspath(dest_path):
        shutil.move(filepath, dest_path)
        print(f"  Moved to: {dest_path}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    files = sys.argv[1:]
    if not files:
        print(__doc__)
        sys.exit(0)

    flac_files = [f for f in files if os.path.isfile(f)]
    if not flac_files:
        print("No valid files found.")
        sys.exit(1)

    print(f"Processing {len(flac_files)} file(s)...")
    for f in flac_files:
        try:
            fix_file(f)
        except KeyboardInterrupt:
            print("\nAborted.")
            sys.exit(0)
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{'─'*60}")
    print("Done.")


if __name__ == "__main__":
    main()
