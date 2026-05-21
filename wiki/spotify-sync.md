# Spotify Sync

> After every download session: add the downloaded tracks to the **New Music {year}** playlist,
> then remove them from Liked Songs. Liked Songs is a download queue, not a permanent library.

## Why this step exists

Liked Songs → download queue → FLAC archive → New Music playlist.

Once a track is saved as a tagged FLAC, it leaves Liked Songs and lands in the year's
New Music playlist. This keeps Liked Songs clean (only undownloaded tracks) and lets Apple
Music + Spotify coexist without duplicates.

## Playlist naming rule

`New Music {YYYY}` where YYYY is the year the session runs.
- 2026 session → "New Music 2026"
- 2027 session → "New Music 2027"

One playlist per year, regardless of how many sessions happen that year.

## Step 1 — Get a Spotify access token

> **Note (2026-05-21):** The `get_access_token` endpoint now returns `403 URL Blocked` (Cloudflare
> WAF). Use the fetch-interceptor method below instead.

### Method: fetch interceptor (current working approach)

1. Navigate to `https://open.spotify.com/collection/tracks` in iMac Chrome  
2. Install the interceptor via `javascript_tool`:

```javascript
const origFetch = window.fetch;
window._origFetch = origFetch;
window._capturedToken = null;
window.fetch = function(...args) {
  const url = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');
  const opts = args[1] || {};
  let auth = null;
  try {
    if (opts?.headers) {
      if (typeof opts.headers.get === 'function') auth = opts.headers.get('Authorization');
      else auth = opts.headers['Authorization'] || opts.headers['authorization'];
    }
    if (!auth && args[0] instanceof Request) auth = args[0].headers?.get('Authorization');
  } catch(e) {}
  if (auth && auth.startsWith('Bearer ') && (url.includes('spotify.com') || url.includes('spclient'))) {
    window._capturedToken = auth.replace('Bearer ', '');
    window._spotifyToken = window._capturedToken;
  }
  return origFetch.apply(this, args);
};
'interceptor installed'
```

3. Trigger an SPA navigation to force API calls:

```javascript
window.history.pushState({}, '', '/album/3gr2zAgErmDyi3qDTxoh7b');
window.dispatchEvent(new PopStateEvent('popstate', { state: {} }));
```

4. Wait a moment, then check:

```javascript
window._capturedToken ? 'GOT TOKEN' : 'not yet — scroll the page and try again'
```

Once `window._spotifyToken` is set, proceed to Step 2.

**Important:** Do not make repeated calls to `api.spotify.com` in a tight loop — the token is shared
with the web player and hits a 429 rate limit quickly. Add 500–700ms delays between requests and
run the full sync as a single async function rather than polling step-by-step.

The token lasts ~1 hour. No stored credentials needed — the web player is already logged in.

## Step 2 — Find the playlist ID

```javascript
const year = new Date().getFullYear();
const T = window._spotifyToken;
let allPlaylists = [];
let url = 'https://api.spotify.com/v1/me/playlists?limit=50';
while (url) {
  const page = await fetch(url, {headers: {Authorization: `Bearer ${T}`}}).then(r => r.json());
  allPlaylists = allPlaylists.concat(page.items || []);
  url = page.next;
}
const pl = allPlaylists.find(p => p.name === `New Music ${year}`);
window._playlistId = pl?.id;
pl ? `Found: ${pl.name} (${pl.id})` : `Not found — create it first`;
```

If the playlist doesn't exist yet, create it:

```javascript
const T = window._spotifyToken;
const year = new Date().getFullYear();
const me = await fetch('https://api.spotify.com/v1/me', {headers: {Authorization: `Bearer ${T}`}}).then(r => r.json());
const created = await fetch(`https://api.spotify.com/v1/users/${me.id}/playlists`, {
  method: 'POST',
  headers: {Authorization: `Bearer ${T}`, 'Content-Type': 'application/json'},
  body: JSON.stringify({name: `New Music ${year}`, public: false, description: `Tracks downloaded in ${year}`})
}).then(r => r.json());
window._playlistId = created.id;
`Created: ${created.name} (${created.id})`;
```

## Step 3 — Find Spotify track IDs

For each downloaded track, search by title + artist to get the Spotify URI:

```javascript
const T = window._spotifyToken;
async function findTrackUri(title, artist) {
  const q = encodeURIComponent(`track:${title} artist:${artist}`);
  const res = await fetch(
    `https://api.spotify.com/v1/search?q=${q}&type=track&limit=3`,
    {headers: {Authorization: `Bearer ${T}`}}
  ).then(r => r.json());
  const track = res.tracks?.items?.[0];
  if (!track) { console.warn(`Not found: ${title} — ${artist}`); return null; }
  console.log(`Found: ${track.name} by ${track.artists[0].name} → ${track.uri}`);
  return track.uri;
}

// Fill in the actual track titles and artist name
const downloads = [
  ["Track Title 1", "Artist Name"],
  ["Track Title 2", "Artist Name"],
  // ...
];
const uris = (await Promise.all(downloads.map(([t, a]) => findTrackUri(t, a)))).filter(Boolean);
window._trackUris = uris;
`Found ${uris.length} / ${downloads.length} tracks`;
```

Tip: if a title has extra text (e.g. "Remix - Radio Edit"), search just the base title and
verify the result before proceeding.

## Step 4 — Add to playlist

```javascript
const T = window._spotifyToken;
// Spotify accepts max 100 URIs per request
const chunks = [];
for (let i = 0; i < window._trackUris.length; i += 100)
  chunks.push(window._trackUris.slice(i, i + 100));

for (const chunk of chunks) {
  const res = await fetch(`https://api.spotify.com/v1/playlists/${window._playlistId}/tracks`, {
    method: 'POST',
    headers: {Authorization: `Bearer ${T}`, 'Content-Type': 'application/json'},
    body: JSON.stringify({uris: chunk})
  }).then(r => r.json());
  console.log('Added chunk:', res.snapshot_id || res);
}
`Added ${window._trackUris.length} tracks to playlist`;
```

## Step 5 — Remove from Liked Songs

```javascript
const T = window._spotifyToken;
const ids = window._trackUris.map(u => u.split(':')[2]);
// Spotify accepts max 50 IDs per DELETE
const chunks = [];
for (let i = 0; i < ids.length; i += 50)
  chunks.push(ids.slice(i, i + 50));

for (const chunk of chunks) {
  await fetch('https://api.spotify.com/v1/me/tracks', {
    method: 'DELETE',
    headers: {Authorization: `Bearer ${T}`, 'Content-Type': 'application/json'},
    body: JSON.stringify({ids: chunk})
  });
}
`Removed ${ids.length} tracks from Liked Songs`;
```

## Verification

Open the Spotify app:
1. Liked Songs — the downloaded tracks should be gone
2. New Music {year} — the downloaded tracks should be at the top (added most recently)

## Troubleshooting

| Problem | Fix |
|---|---|
| `get_access_token` returns 403 | Cloudflare WAF blocks it — use fetch interceptor method (Step 1) |
| Token fetch returns 401 | Not logged into open.spotify.com — sign in first |
| Playlist not found | Check exact name spelling including capital N/M; or create it |
| Track not found by search | Try without "(Remix…)" suffix; check artist spelling |
| 403 on playlist add | Check you own the playlist (not a followed one) |
| Rate limit 429 persists >30s | Each 429 response resets the timer. Stop ALL api.spotify.com calls for 70+ seconds, then fire a single async function that does everything with 500ms+ delays between calls. |

## Related

- [download-a-track.md](download-a-track.md) — where this step fits in the full workflow
