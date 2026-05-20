# Chrome Extension Setup

> Which browser to use, how to select it, and why it matters.

## Overview

The "Claude in Chrome" extension connects Claude to a running Chrome browser, allowing JavaScript
injection, navigation, and page reads. Multiple Chrome instances can be connected simultaneously —
one per device. It's critical to always select the **iMac's** Chrome, not the laptop's.

## Connected browsers

| Name | Device | deviceId | Use |
|---|---|---|---|
| "Chrome iMac" | iMac (whofarted) | `26cadc71-ad91-4608-ab3d-9317c8574292` | ✅ Always use this for downloads |
| "ChatGPT Atlas" | Laptop (walklikeaman) | different | ❌ Downloads land on laptop — wrong machine |

## Why it matters

When Chrome downloads a file via `window.location.href`, it saves to **that computer's**
`~/Downloads/` folder. If the laptop's Chrome is selected, files land on the laptop and
have to be transferred manually. Always verify the correct browser is selected before injecting
download scripts.

## How to select the iMac browser

Using the Claude in Chrome MCP tool `mcp__Claude_in_Chrome__select_browser`:
- **deviceId:** `26cadc71-ad91-4608-ab3d-9317c8574292`

Or verify which is selected with `mcp__Claude_in_Chrome__list_connected_browsers`.

## Verifying the right browser is active

After selecting, check the page title or URL by taking a screenshot or reading the page — the
iMac's Chrome tabs will reflect what's open on the iMac, not the laptop.

## Related

- [download-a-track.md](download-a-track.md) — uses this browser for all downloads
- [error-download-to-wrong-machine.md](error-download-to-wrong-machine.md) — what happens when wrong browser is used

## Sources

- `raw/session-2026-05-21-jim-noir.md` — discovered during Jim Noir download session (first 3 tracks went to laptop)
