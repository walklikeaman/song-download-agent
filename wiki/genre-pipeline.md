# Genre Pipeline

> How tag_fixer.py ensures every track has a genre tag. Five sources tried in order.

## Rule

Genre must never be blank. The pipeline tries sources in order and stops at the first hit.
Once a genre is found for an artist, it's cached in `artist_genres.json` and reused for all
future tracks by that artist — no API calls needed.

## Pipeline

```
existing tag
    │ hit → done
    ▼ miss
iTunes primaryGenreName (from the track search already done)
    │ hit → cache it + done
    ▼ miss
artist_genres.json cache (genre found in a previous session)
    │ hit → done
    ▼ miss
MusicBrainz artist tags (crowd-voted, sorted by vote count)
    │ hit → cache it + done
    ▼ miss
Wikipedia infobox (| genre = field from artist's article)
    │ hit → cache it + done
    ▼ miss
⚠ warn, leave blank
```

## Source details

### 1. Existing tag
Already in the FLAC. Wins unconditionally. Still seeds the cache if it wasn't there.

### 2. iTunes `primaryGenreName`
Free byproduct of the iTunes metadata search that runs for every track anyway.
Apple's genre taxonomy is broad (e.g., "Alternative", "Electronic") — reliable for
mainstream artists.

### 3. artist_genres.json cache
Auto-built file in the same folder as `tag_fixer.py`. Maps `artist_lower → genre_string`.
The cache is updated whenever a new genre is found from any source below. Edit manually to
seed or correct genres before processing.

### 4. MusicBrainz artist tags
Live API call to `musicbrainz.org/ws/2/artist/?query={artist}`. Returns crowd-voted genre
tags sorted by vote count. Top tag is used, title-cased.

**Known issue on this network:** MusicBrainz is blocked at the TLS level. When this happens,
the call times out silently and the pipeline continues to Wikipedia.

### 5. Wikipedia infobox
Searches Wikipedia for `"{artist} musician"`, fetches the top result's wikitext, and parses
the `| genre = [[Genre]]` infobox field.

```python
# Regex used:
re.search(r"\|\s*genre\s*=([^\n|{}]{1,200})", wikitext, re.IGNORECASE)
# Extracts from: [[Pop music|Pop]], [[Indie pop]]
# Returns: "Pop" (first genre listed)
```

Handles both wikilink format (`[[Link|Display]]`) and plain text. No API key required.

## Cache file format

`artist_genres.json` (gitignored — personal cache, not committed):

```json
{
  "jim noir": "Alternative",
  "radiohead": "Alternative Rock",
  "fink": "Folk"
}
```

Keys are lowercased artist names. Values are the genre string as it will be written to the tag.

## Related

- [tag-fixer-pipeline.md](tag-fixer-pipeline.md) — where genre fits in the full pipeline
- [ref-config-files.md](ref-config-files.md) — artist_genres.json format

## Sources

- `WIKI.md` (original flat wiki, ingested 2026-05-21)
- `tag_fixer.py` — `ensure_genre()` and `wikipedia_genre()` functions
