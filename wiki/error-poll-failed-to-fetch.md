# Error: Poll "Failed to fetch"

> The polling loop throws network errors on every iteration but the track may still be processing.

## Symptoms

```
[3] fetch error (Failed to fetch) — errPolls=3
[4] fetch error (Failed to fetch) — errPolls=4
...
```

Console shows mostly errors, no `status: completed` ever seen.

## Root cause

Transient network issue between the browser and lucida.to's CDN (katze/maus subdomain).
The backend may still be processing the track successfully — the poll errors do **not** mean
the fetch itself failed.

## The fallback logic

The download script handles this automatically:

```javascript
} catch (e) {
  errPolls++;
  // After 30s with mostly errors, try the download anyway
  if (i >= 14 && errPolls > successPolls) {
    console.log('Fallback: attempting download despite poll errors');
    break;  // exits loop, proceeds to window.location.href
  }
}
```

After ~30 seconds of mostly-error polls (14+ iterations), the script breaks out of the poll loop
and attempts the download directly. If the backend finished processing, the file downloads
normally. If not, Chrome gets an error page instead of a binary — in that case, start fresh.

## When the fallback fails

If `window.location.href` navigates to an error page (HTML instead of binary file download):

1. Navigate back to `https://lucida.to`
2. Start a fresh rip with the same ASIN — generate a new handoff
3. Wait for at least one successful poll before attempting the download

## Real example

A.M Jazz (B08232C9NQ), first attempt: all 30+ polls returned errors. Fallback triggered but the
handoff `d89baca4` had never completed — got an error page. Second attempt with fresh handoff
succeeded normally.

## Related

- [lucida-to-api.md](lucida-to-api.md) — poll endpoint details
- [download-a-track.md](download-a-track.md) — full script with error handling

## Sources

- `raw/session-2026-05-21-jim-noir.md` — observed during A.M Jazz download
