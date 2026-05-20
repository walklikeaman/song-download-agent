# lucida.to API

> How the lucida.to download backend works — the handoff pattern, polling, CDN download trigger.

## Overview

lucida.to exposes a proxy API at `/api/load` that wraps its internal fetch pipeline. All calls
go through this single endpoint; the actual destination URL is passed as a query parameter.
This is what allows the browser to make cross-origin calls without CORS errors — everything
routes through the same origin.

## Auth

A session token is required. It's a JSON object embedded in the request body:

```json
{"primary": "GdRfswkwpErPuot3YXXJPIF1F9c", "expiry": 1779373132}
```

`expiry` is a Unix timestamp. Tokens last roughly a few days. See [token-renewal.md](token-renewal.md).

## Step 1 — Initiate fetch (POST)

```
POST /api/load?url=%2Fapi%2Ffetch%2Fstream%2Fv2
Content-Type: application/json

{
  "url": "https://music.amazon.com/tracks/{ASIN}?musicTerritory=US",
  "metadata": true,
  "compat": false,
  "private": false,
  "handoff": true,
  "account": {"type": "country", "id": "auto"},
  "upload": {"enabled": false, "service": "pixeldrain"},
  "downscale": "original",
  "token": {"primary": "...", "expiry": ...}
}
```

**Success response:**
```json
{"success": true, "handoff": "d89baca4"}
```

**Failure response:**
```json
{"success": false, "error": "..."}
```

Common failure causes: expired token, track not available in the specified territory.

## Step 2 — Poll for completion (GET)

```
GET /api/load?url=%2Fapi%2Ffetch%2Frequest%2F{handoff}
```

Returns status updates while the backend fetches and transcodes:

```json
{"success": true, "status": "processing", "message": "Fetching track..."}
{"success": true, "status": "completed", "message": ""}
```

**Poll interval:** Every 2 seconds. Typical completion: 20–90s.

### Handling transient fetch errors

The poll endpoint occasionally returns network errors ("Failed to fetch") that are NOT real failures
— the backend is still processing. Handle these with:

```javascript
try {
  poll = await fetch(...).then(r => r.json());
  successPolls++;
  if (poll.status === 'completed') break;
} catch (e) {
  errPolls++;
  // After ~30s with mostly errors, attempt download anyway
  if (i >= 14 && errPolls > successPolls) { break; }
}
```

See [error-poll-failed-to-fetch.md](error-poll-failed-to-fetch.md) for the full pattern.

## Step 3 — Trigger download (navigate)

```javascript
window.location.href = 'https://lucida.to/api/load?url=' +
  encodeURIComponent('/api/fetch/request/' + handoff + '/download');
```

**Why `window.location.href` instead of `fetch()`:**
The CDN redirect goes to `katze.lucida.to` or `maus.lucida.to` — a different subdomain.
A `fetch()` call gets an opaque CORS response and cannot retrieve the binary.
`window.location.href` is a plain navigation — the browser follows the redirect and downloads the
file because the response has `Content-Disposition: attachment`.

## Important: page reload after navigation

When `window.location.href` triggers the download, the page navigates. If the CDN returns HTML
(e.g., an error page), the lucida.to page is replaced and all JS variables are lost. Even on
success, Chrome may navigate away briefly.

**Rule:** Do one track at a time. Re-inject the download script for each track after navigating
back to `https://lucida.to`.

## Source URL formats supported

| Service | URL format |
|---|---|
| Amazon Music track | `https://music.amazon.com/tracks/{ASIN}?musicTerritory=US` |
| Spotify track | `https://open.spotify.com/track/{id}` |
| Qobuz album | `https://www.qobuz.com/album/...` |
| Tidal track | `https://tidal.com/browse/track/{id}` |

## Related

- [cloudflare-behaviour.md](cloudflare-behaviour.md) — why this must run in a real browser
- [token-renewal.md](token-renewal.md) — when and how to get a new token
- [error-poll-failed-to-fetch.md](error-poll-failed-to-fetch.md) — handling poll errors
- [download-a-track.md](download-a-track.md) — full workflow using this API

## Sources

- `raw/session-2026-05-21-jim-noir.md` — observed directly during Jim Noir download session
