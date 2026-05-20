---
name: song-download
description: >
  Download hi-res lossless audio (FLAC) from lucida.to using Amazon Music as the
  source, then enrich the file's metadata and lyrics with tag_fixer.py.
  After every run, automatically update the wiki (wiki/ pages + WIKI.md changelog)
  and commit + push to GitHub so the knowledge base learns from each session.
  Use this skill whenever the user asks to download a song, album, or track —
  especially when they mention an artist name, song title, Spotify link, Amazon
  ASIN, or says things like "rip this", "get me this track", "download in FLAC",
  "add to my library", or "tag this file". Also trigger when the user asks to
  run tag_fixer on already-downloaded files.
---

# Song Download Agent

Three-step pipeline: **download via lucida.to** → **enrich tags + lyrics** → **update wiki + commit**.

The third step is not optional. Every run teaches the system: new artists, new errors, new
patterns — all go into the wiki so the next run starts smarter.

---

## Quick reference

| Thing | Value |
|---|---|
| iMac Chrome deviceId | `26cadc71-ad91-4608-ab3d-9317c8574292` |
| Chrome browser name | "Chrome iMac" |
| lucida.to base | `https://lucida.to` |
| Download lands in | `~/Downloads/` |
| Final destination | `~/Downloads/Spotify downloads/{Artist}/` |
| tag_fixer.py | `/Users/whofarted/Claude/Songs Download/tag_fixer.py` |
| Wiki directory | `/Users/whofarted/Claude/Songs Download/wiki/` |
| Flat wiki | `/Users/whofarted/Claude/Songs Download/WIKI.md` |
| GitHub repo | `walklikeaman/song-download-agent` (branch: main) |

---

## Step 0 — Before you start

### Get the lucida.to session token

```bash
grep -A1 'TOKEN' /tmp/playwright_download.py 2>/dev/null
# Check expiry: python3 -c "import datetime; print(datetime.datetime.fromtimestamp(EXPIRY))"
```

If expired: tell the user → lucida.to → sign in → DevTools → Application → Local Storage → copy token.

### Find the Amazon Music ASIN

ASIN is the alphanumeric ID in `https://music.amazon.com/tracks/{ASIN}`.
If you only have a Spotify link, search `music.amazon.com` for the track.

### Select the iMac browser

```
mcp__Claude_in_Chrome__select_browser  deviceId: "26cadc71-ad91-4608-ab3d-9317c8574292"
```

Never use the laptop browser — downloads land on whichever machine Chrome is running on.

---

## Step 1 — Download via lucida.to

Do **one track at a time**. After each `window.location.href` the page reloads and JS state is lost.

### 1a. Navigate to lucida.to

Navigate to `https://lucida.to`. If "Just a moment..." appears (Cloudflare), wait 20–30s — it
auto-resolves in a real browser. Do NOT use Python/curl at any point.

### 1b. Inject and run the download script

Replace `TOKEN_PRIMARY`, `TOKEN_EXPIRY`, `TITLE`, `ASIN`, then inject via `mcp__Claude_in_Chrome__javascript_tool`:

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
      downscale: "original", token: TOKEN
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

### 1c. Wait for download, then move to destination

```bash
ARTIST="Artist Name"
DEST=~/Downloads/Spotify\ downloads/$ARTIST
mkdir -p "$DEST"
LATEST=$(ls -t ~/Downloads/*.flac ~/Downloads/*.m4a 2>/dev/null | head -1)
mv "$LATEST" "$DEST/" && echo "Moved: $(basename $LATEST)"
```

For multiple tracks: navigate back to `https://lucida.to` between each one and re-inject.

---

## Step 2 — Tag enrichment

```bash
python3 "/Users/whofarted/Claude/Songs Download/tag_fixer.py" \
  ~/Downloads/Spotify\ downloads/"$ARTIST"/*.flac
```

Runs in one pass over the whole folder. Handles: watermark removal, MusicBrainz ISRC date,
iTunes/Discogs metadata, genre pipeline (iTunes → cache → MusicBrainz → Wikipedia),
cover art, lyrics (6 sources), artist subfolder move.

---

## Step 3 — Update wiki and commit  ← ALWAYS DO THIS

This step is how the system learns. After every session — even one track — update the knowledge
base so future runs start with more context.

### 3a. Update wiki pages

For each thing that happened this session, update the relevant page in
`/Users/whofarted/Claude/Songs Download/wiki/`:

| If this happened | Update this page |
|---|---|
| New artist downloaded | Create or update `artist-{name}.md` with tracks, ASINs, quality, genre results |
| New error encountered | Create `error-{description}.md` with symptom, root cause, fix |
| tag_fixer result was interesting | Update `tag-fixer-pipeline.md` or `genre-pipeline.md` |
| Token renewed | Note the new expiry range in `token-renewal.md` |
| New workaround discovered | Update the relevant concept or error page |

Cross-link aggressively. If a new artist page mentions the poll error fallback, link to
`error-poll-failed-to-fetch.md`. If a new error page describes a known Cloudflare variant,
link to `cloudflare-behaviour.md`.

### 3b. Add to the ingest log

Append a row to `wiki/_ingest_log.md`:

```markdown
| YYYY-MM-DD | Session: {artist} download | {N} | {one-line summary of what happened and what was new} |
```

### 3c. Add to the WIKI.md changelog

Append to the changelog table at the bottom of `WIKI.md`:

```markdown
| YYYY-MM-DD | {What was done this session — new artist, new error encountered, new pattern discovered} |
```

### 3d. Commit and push

```bash
cd "/Users/whofarted/Claude/Songs Download"
git add wiki/ WIKI.md
# Also stage artist_genres.json if it was updated (it's gitignored, so use -f)
git commit -m "Session YYYY-MM-DD: {artist} — {brief summary}

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
git push origin main
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "Just a moment..." | Wait 20–30s. Never use Python/curl. |
| Init `{success: false}` | Token expired — renew at lucida.to → DevTools → Local Storage |
| Poll `{success: false}` with error | Track unavailable on Amazon Music US — try Qobuz URL |
| "Failed to fetch" on all polls | Transient CDN — fallback fires after 30s, usually works |
| File on laptop, not iMac | Wrong browser — re-run `select_browser` with iMac deviceId |
| `.m4a` instead of `.flac` | No FLAC on Amazon Music — skip tag_fixer (FLAC only) |
| Page navigated away mid-poll | CDN returned HTML — re-navigate to lucida.to, fresh rip |

---

## Source quality priority

Prefer: **Qobuz** (24-bit/192kHz) > **Tidal** (24-bit/96kHz) > **Amazon** (24-bit) > **Deezer** (16-bit)  
Never: Soundcloud (lossy MP3).  
Amazon is the default (ASIN-based URLs). Switch to Qobuz when quality matters.
