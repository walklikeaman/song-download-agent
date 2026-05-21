# Song Download Agent — Wiki Index

> LLM-maintained knowledge base. Raw sources live in `raw/`. See `SCHEMA.md` for conventions.

## Process pages

| Page | What it covers |
|---|---|
| [download-a-track.md](download-a-track.md) | Full workflow: select source → lucida.to API → download → move → tag → Spotify sync |
| [tag-fixer-pipeline.md](tag-fixer-pipeline.md) | All tag_fixer.py enrichment steps in order |
| [spotify-sync.md](spotify-sync.md) | Add to New Music {year} playlist + remove from Liked Songs via Spotify Web API |
| [token-renewal.md](token-renewal.md) | How to renew the lucida.to session token |

## Concept pages

| Page | What it covers |
|---|---|
| [lucida-to-api.md](lucida-to-api.md) | Handoff API flow, polling, download URL, CDN behaviour |
| [cloudflare-behaviour.md](cloudflare-behaviour.md) | Why Python/curl fail; what passes; real-browser requirement |
| [genre-pipeline.md](genre-pipeline.md) | 5-source genre chain: iTunes → cache → MusicBrainz → Wikipedia |
| [lyrics-pipeline.md](lyrics-pipeline.md) | 6-source lyrics chain with per-source notes |
| [chrome-extension-setup.md](chrome-extension-setup.md) | iMac vs laptop browser, deviceId, selection |
| [source-quality-guide.md](source-quality-guide.md) | Qobuz > Tidal > Amazon > Deezer priority; never lossy |

## Entity pages

| Page | What it covers |
|---|---|
| [artist-jim-noir.md](artist-jim-noir.md) | Session notes, ASINs, downloaded tracks, tag results |
| [artist-neutral-milk-hotel.md](artist-neutral-milk-hotel.md) | Session notes, ASIN, downloaded track, tag results |
| [artist-dreams-on-tape.md](artist-dreams-on-tape.md) | Session notes, ASINs, downloaded tracks, quirks (bad ASINs, CDN retries) |

## Error pages

| Page | What it covers |
|---|---|
| [error-cloudflare-block.md](error-cloudflare-block.md) | 403 on Python/curl, TLS fingerprinting, solution |
| [error-poll-failed-to-fetch.md](error-poll-failed-to-fetch.md) | Transient CDN "Failed to fetch" errors, fallback logic |
| [error-download-to-wrong-machine.md](error-download-to-wrong-machine.md) | Files landing on laptop instead of iMac |

## Reference pages

| Page | What it covers |
|---|---|
| [ref-tag-fields.md](ref-tag-fields.md) | All FLAC tags written/removed/preserved by tag_fixer.py |
| [ref-config-files.md](ref-config-files.md) | artist_genres.json and artist_groups.json formats |

## Meta

- [_ingest_log.md](_ingest_log.md) — what was ingested and when
- [_lint_report.md](_lint_report.md) — latest lint findings
- [SCHEMA.md](SCHEMA.md) — wiki conventions and page types
