# Token Renewal

> How to get a fresh lucida.to session token when the current one expires.

## Token format

```json
{"primary": "GdRfswkwpErPuot3YXXJPIF1F9c", "expiry": 1779373132}
```

`expiry` is a Unix timestamp. Check with: `date -j -f "%s" 1779373132 "+%Y-%m-%d %H:%M"` (macOS)
or `python3 -c "import datetime; print(datetime.datetime.fromtimestamp(1779373132))"`.

Tokens last roughly a few days to a week.

## How to renew

1. Open `https://lucida.to` in the **iMac's Chrome** (must be a real browser session)
2. Sign in if prompted
3. Open DevTools: `⌘ + Option + I` → Application tab → Local Storage → `https://lucida.to`
4. Look for a key containing `token` or `session` — copy the value
5. Or: navigate to the lucida.to Settings page if a "Copy token" button exists
6. Update the token value in the download script before injecting

## When to renew

The `init` POST will return `{"success": false}` with an auth-related error message when the
token is expired. If the init call fails and the track is definitely available, check the token
first.

## Storing the token

The token is not stored in any tracked file (it's a credential). When starting a new session,
check `/tmp/playwright_download.py` for the most recent token used:

```bash
grep -A2 'TOKEN' /tmp/playwright_download.py 2>/dev/null
```

## Related

- [lucida-to-api.md](lucida-to-api.md) — how the token is used in API calls
- [download-a-track.md](download-a-track.md) — where to substitute the token

## Sources

- `raw/session-2026-05-21-jim-noir.md`
