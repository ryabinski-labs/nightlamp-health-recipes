# Third-party API canary

> Your app wraps a vendor. The vendor is up — except for you. Or it's down
> and they haven't put it on the status page yet.

## Symptoms

- A customer-facing feature backed by the vendor breaks or feels slow.
- Vendor status page is green but your app is failing.
- Sudden spike in 429 or 5xx from the vendor.

## Failure modes

- Vendor outage not yet on the status page.
- Your account hit a usage or rate limit.
- Vendor changed an API contract (deprecated field, new required header).
- Your API key was rotated or revoked.
- DNS/TLS issue between your origin and the vendor.

## Checks

One `api_canary` per vendor you depend on. Pick an endpoint that is:

- **Cheap** (doesn't bill per call, or bills trivially).
- **Idempotent** (safe to call every 5 minutes forever).
- **Stable** (vendor isn't going to deprecate it).
- **Cheap to assert on** (returns a small, predictable JSON shape).

Good defaults:

| Vendor | Endpoint | Marker |
|---|---|---|
| Stripe | `GET /v1/balance` | `object` |
| Twilio | `GET /2010-04-01/Accounts.json` | `account_sid` |
| OpenAI | `GET /v1/models` | `gpt-` (or whichever model id you depend on) |
| Mapbox | `GET /styles/v1/mapbox/streets-v12` | `version` |

Store the vendor token in your monitoring tool's variable store as
`{{VENDOR_API_TOKEN}}`.

## Triage

1. Check the vendor status page.
2. Hit the canary URL with curl from your machine — auth issue or vendor issue?
3. Inspect the response for deprecation headers or warning fields.
4. On 429: review your usage dashboard; back off or request a raise.
5. Search vendor support/community for ongoing incident chatter.

## False positives

- Vendor maintenance windows for non-critical endpoints can return 503.
- Some vendors throttle per region; the canary may be hitting a hot region.

## Alert routing

- **Severity:** ticket (vendor outages aren't usually your fix).
- **Channel:** on-call integrations.
- **Suppress:** vendor status page incidents, scheduled maintenance.
