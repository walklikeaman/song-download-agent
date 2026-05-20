# Lyrics Pipeline

> Six sources tried in order. First hit wins. Existing LYRICS tag is never overwritten.

## Chain

```
LRCLib → lyrics.ovh → syncedlyrics → Genius → ChartLyrics → AZLyrics
  #1          #2            #3           #4           #5           #6
```

## Source details

| # | Source | Key? | Strength | Weakness |
|---|--------|------|----------|----------|
| 1 | **LRCLib** | No | 3M+ tracks, open-source, no rate limit | Misses very new/obscure tracks |
| 2 | **lyrics.ovh** | No | Good French coverage | Unmaintained, occasionally slow |
| 3 | **syncedlyrics** | No (community token) | Best Asian/Chinese via NetEase | Musixmatch returns 30% snippets on some tracks |
| 4 | **Genius** | Free token | Largest English DB; hip-hop, pop, rock | New tracks may be untranscribed; slow scrape |
| 5 | **ChartLyrics** | No | Stable legacy SOAP service | Sparse — best for pre-2015 chart hits only |
| 6 | **AZLyrics** | No | Enormous English catalog; rock, metal, pop | Aggressive rate-limiting; 2s delay enforced |

## Genius setup

Genius requires a free API token. Without it, source #4 is silently skipped.

```bash
# Get token: https://genius.com/api-clients → New API Client
echo 'export GENIUS_ACCESS_TOKEN="your_token"' >> ~/.zshrc
source ~/.zshrc
```

## Known real-world results

- **Fink — Wishing For Blue Sky:** Only AZLyrics had it (2026 release, no other source had transcriptions yet)
- **Most tracks:** LRCLib hits on first try

## syncedlyrics stdout noise

The `syncedlyrics` library prints its own errors to stdout (Megalobiz connection refused, etc.).
This is internal library behaviour and harmless — the chain continues regardless.

## Related

- [tag-fixer-pipeline.md](tag-fixer-pipeline.md) — where lyrics fits in the full pipeline

## Sources

- `WIKI.md` — original flat wiki
- `tag_fixer.py` — `get_lyrics()` function
