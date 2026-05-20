# Source Quality Guide

> Priority order for choosing a music source on lucida.to. Always prefer lossless, always prefer hi-res.

## Priority order

| Priority | Source | Max quality | Notes |
|---|---|---|---|
| 1 | **Qobuz** | 24-bit / 192kHz FLAC | Best available quality; largest hi-res catalog |
| 2 | **Tidal** | 24-bit / 96kHz FLAC | Good hi-res option |
| 3 | **Amazon Music** | 24-bit / 48kHz FLAC | Good for newer releases |
| 4 | **Deezer** | 16-bit / 44.1kHz FLAC | CD quality only — use only if above unavailable |
| ✗ | **Soundcloud** | 128–320 kbps MP3 | Lossy — never use for music collection |

## Rules

- **Never accept MP3, AAC, or any lossy format.** The download button should always show FLAC.
- If all sources only have 16-bit/44.1kHz (CD quality), that is the master — no hi-res exists for this track. tag_fixer.py will show `⚠ CD quality` but this is expected.
- Verify the format shown on lucida.to before clicking download. If it shows MP3/AAC, switch sources.

## Amazon Music as primary (practical note)

For convenience, Amazon Music is the default source in the download scripts (ASIN-based URLs are
easy to construct). Qobuz is theoretically better but requires a separate URL lookup. When
quality matters and time allows, prefer Qobuz.

## Related

- [download-a-track.md](download-a-track.md) — step 2 covers source selection
- [tag-fixer-pipeline.md](tag-fixer-pipeline.md) — quality check step reports what you got

## Sources

- `WIKI.md` — original flat wiki
