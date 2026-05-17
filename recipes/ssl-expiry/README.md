# SSL certificate expiry

> Your apex cert is auto-renewing. The subdomain you launched 14 months ago
> and forgot about is not.

## Symptoms

- Browsers show "your connection is not private."
- API clients fail handshake with `NET::ERR_CERT_DATE_INVALID` or x509 errors.
- Slack/Stripe/Twilio webhooks stop firing.

## Failure modes

- Auto-renewal stopped (ACME challenge failing, expired email on the account).
- Cert was issued for the wrong SAN list; the subdomain you care about isn't
  covered.
- A CDN edge is serving a stale cert that hasn't been refreshed.
- A DNS change broke ACME http-01 validation on the renewal attempt.

## Checks

One `ssl` monitor per hostname you care about. Don't try to be clever with
one wildcard check — wildcards can cover the apex but not API subdomains,
and vice versa. List each host explicitly.

Default threshold: **21 days** before expiry. Anything lower than that and
you don't have time to debug a stuck renewal.

## Triage

```sh
openssl s_client -servername {{host}} -connect {{host}}:443 </dev/null 2>/dev/null \
  | openssl x509 -noout -dates -subject -ext subjectAltName
```

1. Confirm the SAN list covers the failing hostname.
2. Check the issuer; if auto-renewal, read the renewal logs.
3. If ACME http-01, confirm `/.well-known/acme-challenge/` is reachable.
4. Force a renewal. Clear CDN/edge caches.

## False positives

- A cert that just renewed may appear "old" on a CDN edge for a few minutes.
- Hosts behind SNI can legitimately serve different certs per Host header —
  test with `-servername` explicitly.

## Alert routing

- **Severity:** ticket (21 days is plenty of warning).
- **Channel:** on-call platform.
- **Suppress:** scheduled cert renewal window.
