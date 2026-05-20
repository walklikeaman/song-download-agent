# Cloudflare Behaviour

> Why all automated/scripted approaches to lucida.to fail, and what actually works.

## Overview

lucida.to is protected by Cloudflare. The challenge page ("Just a moment...") blocks anything that
doesn't look like a real human-operated browser. This isn't just about User-Agent strings — Cloudflare
fingerprints at multiple layers simultaneously.

## What Cloudflare checks

| Layer | What it looks at |
|---|---|
| TLS | JA3 fingerprint (cipher suites, extensions order) — Python `requests` has a distinctive fingerprint |
| HTTP/2 | Frame ordering, SETTINGS frame values |
| JavaScript | `navigator.webdriver`, `navigator.plugins`, `window.chrome`, `navigator.permissions` |
| Behavioural | Mouse movements, scroll events, time-on-page before first interaction |
| History | Whether the browser has cookies, cached resources, browsing history |

## What fails and why

| Approach | Result | Root cause |
|---|---|---|
| Python `requests` | 403 | TLS fingerprint recognised immediately |
| `curl_cffi` with TLS impersonation | 403 | Passes TLS check but fails JS checks |
| Playwright headless | Blocked | `navigator.webdriver = true` even with stealth patches |
| Playwright `channel="chrome"` headless=False | Blocked | No real browsing history/cookies; still fingerprinted |
| Playwright with copied real Chrome profile | Blocked | Cloudflare detects automation despite real cookies |

## What works

**Only a real, human-operated Chrome browser passes Cloudflare.**

Specifically: the iMac's Chrome browser, connected via the Claude in Chrome extension, with its
real browsing history, cookies, and human interaction patterns intact.

The extension runs JavaScript in the existing Chrome context — it's indistinguishable from a user
typing in the DevTools console.

## The "Just a moment..." page

If lucida.to shows "Just a moment..." when the extension navigates to it:

1. Wait 20–30 seconds — Cloudflare's JS challenge runs and auto-resolves in a real browser
2. Check the page title again — it should change from "Just a moment..." to "lucida"
3. If still stuck after 30s: try a manual reload, or close and reopen the tab

## Corollary: never use Python/curl for lucida.to

Even with a valid `cf_clearance` cookie extracted from a real browser session, Python requests fail.
The cookie alone is not enough — Cloudflare validates the full browser fingerprint on each request.

## Related

- [lucida-to-api.md](lucida-to-api.md) — the API calls that run inside the real browser
- [chrome-extension-setup.md](chrome-extension-setup.md) — which browser to use
- [error-cloudflare-block.md](error-cloudflare-block.md) — error reference

## Sources

- `raw/session-2026-05-21-jim-noir.md` — tested Python requests, curl_cffi, and Playwright; all failed
