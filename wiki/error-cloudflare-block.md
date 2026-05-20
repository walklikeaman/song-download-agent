# Error: Cloudflare Block

> lucida.to returns 403 or shows "Just a moment..." — automated request was detected.

## Symptoms

- Python `requests.get("https://lucida.to/...")` returns HTTP 403
- `curl_cffi` with Chrome TLS impersonation returns 403
- Playwright browser shows "Just a moment..." and never resolves
- Error in console: `cf_clearance` cookie present but requests still fail

## Root cause

Cloudflare fingerprints the full browser context simultaneously — TLS JA3 signature, HTTP/2 frame
order, JavaScript `navigator.webdriver`, browsing history, cookies, and behavioural signals.
No automated approach can replicate all of these. See [cloudflare-behaviour.md](cloudflare-behaviour.md).

## Solution

Use the **iMac's real Chrome browser** via the Claude in Chrome extension. The extension runs JS
in an existing, human-used Chrome context that passes all Cloudflare checks.

1. Select the iMac browser (deviceId: `26cadc71-ad91-4608-ab3d-9317c8574292`)
2. Navigate to `https://lucida.to`
3. If "Just a moment..." appears, wait 20–30s — it auto-resolves in a real browser
4. Inject the download script

## What NOT to try

- Python `requests` + `cf_clearance` cookie — fails; cookie alone isn't enough
- `curl_cffi` TLS impersonation — passes TLS check, fails JS/behaviour checks
- Playwright headless or headed with real Chrome profile — still detected

## Related

- [cloudflare-behaviour.md](cloudflare-behaviour.md) — full explanation of why automation fails
- [chrome-extension-setup.md](chrome-extension-setup.md) — how to set up the real browser
