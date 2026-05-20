# Error: Download Lands on Wrong Machine

> Files appear in the laptop's ~/Downloads/ instead of the iMac's.

## Symptoms

- Files appear in `/Users/walklikeaman/Downloads/` (laptop)
- iMac `~/Downloads/` has no new files after a download
- User shows a Finder screenshot with files on a different machine

## Root cause

The wrong Chrome browser was selected. The Claude in Chrome extension can connect to Chrome on
multiple machines. When the laptop's Chrome ("ChatGPT Atlas") was selected instead of the iMac's
("Chrome iMac"), all downloads were triggered in the laptop's browser — files landed on the laptop.

## Solution

Re-select the iMac browser before running any download scripts:

- **Device:** "Chrome iMac"
- **deviceId:** `26cadc71-ad91-4608-ab3d-9317c8574292`

Use `mcp__Claude_in_Chrome__select_browser` with this deviceId.

## Prevention

At the start of every download session, verify the selected browser is the iMac's Chrome. The
deviceId is stable — it won't change between sessions unless the extension is reinstalled.

## Related

- [chrome-extension-setup.md](chrome-extension-setup.md) — browser selection details
- [download-a-track.md](download-a-track.md) — step 1 covers browser selection

## Sources

- `raw/session-2026-05-21-jim-noir.md` — first 3 Jim Noir tracks went to laptop; discovered mid-session
