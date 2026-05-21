# Ingest Log

| Date | Source | Pages touched | Summary |
|---|---|---|---|
| 2026-05-21 | `WIKI.md` (flat wiki, v1) | 12 (initial creation) | Converted monolithic WIKI.md into structured wiki pages: download workflow, tag pipeline, genre/lyrics chains, quality guide, tag reference, config files |
| 2026-05-21 | Session transcript: Jim Noir download (2026-05-21) | 5 | Added: cloudflare-behaviour.md, chrome-extension-setup.md, artist-jim-noir.md, error-poll-failed-to-fetch.md, error-download-to-wrong-machine.md — all from direct observation during the download session |
| 2026-05-21 | Skills: song-download v2 + llm-wiki v1 | 2 | song-download skill updated: added Step 3 (post-run wiki update + commit). llm-wiki skill created. Both versioned in skills/. Skill now mandates: update wiki → log → changelog → commit after every run |
| 2026-05-21 | Session transcript: Jim Noir Eanie Meany download (2026-05-21 session 2) | 1 | Downloaded missing 8th Jim Noir track: "Eanie Meany (Fatboy Slim Remix - radio edit)" via Qobuz GB. Updated artist-jim-noir.md with session 2 details, quirks (bad ASIN, Qobuz US 404, ZIP extraction). Confirmed all 8 liked tracks now downloaded. |
| 2026-05-21 | New rule: Spotify sync step | 4 | Added spotify-sync.md. Updated download-a-track.md (Step 7), index.md (new process page), WIKI.md (Step 3 section + changelog), skills/song-download.md (Step 3 Spotify sync + Step 4 wiki/commit). Rule: Liked Songs = download queue; downloaded tracks → New Music {year} playlist → removed from Liked Songs. |
