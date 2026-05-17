# Custom domain / DNS cutover

> A DNS edit at 5pm. By morning, half your customers are looking at a parking
> page and the other half are seeing a TLS warning.

## Symptoms

- Customers report "site can't be reached" or wrong content.
- Some see the new site, others still see the old one for hours.
- HTTPS warnings about an unrelated certificate suddenly appear.

## Failure modes

- A/AAAA/CNAME records were edited to point at an origin that isn't serving
  the expected vhost.
- The new origin doesn't have a TLS cert for the cutover domain yet.
- TTL on the old records was too high; propagation is slow and uneven.
- Apex and www records are inconsistent.
- A CDN proxy was disabled/enabled mid-cutover.

## Checks

Four monitors, layered:

1. **`http_status`** on apex — cheap heartbeat.
2. **`http_keyword`** on apex — asserts a unique site marker is present and
   common parking-page strings are absent. Catches "200 but wrong site."
3. **`http_keyword`** on `www.` — asserts apex and www serve the same site.
4. **`ssl`** — confirms TLS cert is valid and has ≥14 days until expiry.

Run during cutover and for at least 48h after to catch slow-propagating
clients.

## Triage

1. `dig +short A {{your-apex-domain}}` and compare to the expected origin.
2. `dig +short CNAME www.{{your-apex-domain}}`.
3. Test via https://www.whatsmydns.net/ to spot uneven propagation.
4. Open the URL in a browser; check the cert Subject and SAN.
5. If using a CDN, confirm the origin pull rule and TLS verify mode.

## False positives

- During an active cutover, some probe regions still hit old records via
  TTL. Annotate the alert with the cutover window.
- CDNs may briefly serve a default page during config pushes.

## Alert routing

- **Severity:** page.
- **Channel:** on-call platform.
- **Suppress:** the explicit cutover window.
