# Download a Track

> Full workflow for downloading a single track as a lossless FLAC using lucida.to + Amazon Music,
> then enriching its metadata.

## Prerequisites

- Claude in Chrome extension installed and connected on the **iMac** (deviceId: `26cadc71-ad91-4608-ab3d-9317c8574292`)
- Valid lucida.to session token (see [token-renewal.md](token-renewal.md))
- The track's Amazon Music ASIN (e.g. `B09Z44CPG6`)
- Python 3.10+ with tag_fixer.py dependencies installed

## Step 0 — Find the ASIN

The Amazon Music ASIN is the alphanumeric ID in the track URL:
`https://music.amazon.com/tracks/B09Z44CPG6` → ASIN = `B09Z44CPG6`

If you only have a Spotify link, search for the track on `music.amazon.com` and copy the ASIN from the URL.

## Step 1 — Select the iMac browser

Via the Claude in Chrome MCP, select the iMac's Chrome:
- **Device:** "Chrome iMac"
- **deviceId:** `26cadc71-ad91-4608-ab3d-9317c8574292`

Never use the laptop browser — downloads land wherever Chrome is running.

## Step 2 — Navigate to lucida.to

Navigate to `https://lucida.to`. If you see "Just a moment...", wait 20–30s for the
Cloudflare challenge to auto-resolve. See [cloudflare-behaviour.md](cloudflare-behaviour.md).

## Step 3 — Inject the download script

Replace `TOKEN_PRIMARY`, `TOKEN_EXPIRY`, `TITLE`, and `ASIN`, then inject via the Chrome extension:

```javascript
(async () => {
  const TOKEN = {"primary": "TOKEN_PRIMARY", "expiry": TOKEN_EXPIRY};
  const title = "TITLE";
  const asin  = "ASIN";

  const init = await fetch('/api/load?url=%2Fapi%2Ffetch%2Fstream%2Fv2', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      url: `https://music.amazon.com/tracks/${asin}?musicTerritory=US`,
      metadata: true, compat: false, private: false, handoff: true,
      account: {type: "country", id: "auto"},
      upload: {enabled: false, service: "pixeldrain"},
      downscale: "original",
      token: TOKEN
    })
  }).then(r => r.json()).catch(e => ({success: false, error: e.message}));

  if (!init.success) { console.error('Init failed:', JSON.stringify(init)); return; }

  const handoff = init.handoff;
  console.log('Handoff:', handoff);

  let successPolls = 0, errPolls = 0;
  for (let i = 0; i < 120; i++) {
    await new Promise(r => setTimeout(r, 2000));
    let poll;
    try {
      poll = await fetch('/api/load?url=' + encodeURIComponent('/api/fetch/request/' + handoff))
               .then(r => r.json());
      successPolls++;
      console.log(`[${i+1}] ${poll.status}: ${poll.message || ''}`);
      if (poll.status === 'completed') break;
      if (!poll.success) { console.error('Poll failed:', JSON.stringify(poll)); return; }
    } catch (e) {
      errPolls++;
      if (i >= 14 && errPolls > successPolls) { console.log('Fallback download'); break; }
    }
  }

  window.location.href = 'https://lucida.to/api/load?url=' +
    encodeURIComponent('/api/fetch/request/' + handoff + '/download');
})();
```

## Step 4 — Wait for the download

Chrome downloads the file to `~/Downloads/`. Check for the new file:

```bash
ls -lt ~/Downloads/*.flac ~/Downloads/*.m4a 2>/dev/null | head -5
```

Typical wait: 15–90 seconds depending on file size and server load.

## Step 5 — Move to destination

```bash
ARTIST="Artist Name"
DEST=~/Downloads/Spotify\ downloads/$ARTIST
mkdir -p "$DEST"
LATEST=$(ls -t ~/Downloads/*.flac ~/Downloads/*.m4a 2>/dev/null | head -1)
mv "$LATEST" "$DEST/"
echo "Moved: $(basename $LATEST) → $DEST/"
```

## Step 6 — Enrich tags and lyrics

```bash
python3 "/Users/whofarted/Claude/Songs Download/tag_fixer.py" \
  ~/Downloads/Spotify\ downloads/"$ARTIST"/*.flac
```

See [tag-fixer-pipeline.md](tag-fixer-pipeline.md) for what this does.

## Multiple tracks

For albums or playlists: do **one track at a time**. After each `window.location.href` navigation
the page reloads and JS state is lost.

Pattern:
1. Inject script → wait → move file
2. Navigate browser back to `https://lucida.to`
3. Repeat from Step 3 for next track
4. After all tracks: run `tag_fixer.py` on the whole folder in one pass

## Troubleshooting

| Problem | See |
|---|---|
| "Just a moment..." | [cloudflare-behaviour.md](cloudflare-behaviour.md) |
| Init `{success: false}` | [token-renewal.md](token-renewal.md) |
| Poll "Failed to fetch" | [error-poll-failed-to-fetch.md](error-poll-failed-to-fetch.md) |
| File downloaded to laptop | [error-download-to-wrong-machine.md](error-download-to-wrong-machine.md) |
| File is `.m4a` not `.flac` | Track has no FLAC on Amazon Music; skip tag_fixer (FLAC only) |

## Related

- [lucida-to-api.md](lucida-to-api.md) — API internals
- [source-quality-guide.md](source-quality-guide.md) — when to prefer Qobuz over Amazon
- [tag-fixer-pipeline.md](tag-fixer-pipeline.md) — enrichment step detail

## Sources

- `raw/session-2026-05-21-jim-noir.md` — workflow validated across 7 Jim Noir tracks
