# Auth / login journey

> The login form renders fine. Submission no longer leads anywhere useful.

## Symptoms

- Login form is visible but submit does nothing or returns a generic error.
- Login succeeds but the post-login redirect lands on a 404 or blank page.
- Customers say "I keep getting kicked back to the login page."

## Failure modes

- Auth endpoint URL or method changed after a deploy.
- Session cookie attributes broke after a domain or SameSite change.
- The post-login redirect target was renamed or deleted.
- Identity provider (Auth0, Clerk, Supabase, Firebase) outage or rate limit.
- A CSRF token surface was removed and the backend now 403s.

## Checks

Two monitors with complementary fidelity:

1. **`browser_journey`** — drives the real form: goto login, fill email, fill
   password (marked sensitive — store in your monitoring tool's variable
   store as `{{LOGIN_PASSWORD}}`), click submit, wait for dashboard URL,
   assert dashboard marker is visible.
2. **`api_canary`** — POSTs credentials to the token endpoint and asserts
   the response contains a token field marker. Catches API-level regressions
   that the browser test might mask with a generic timeout.

Use a dedicated **canary test account** with no real privileges. Do not use
a real customer credential.

## Triage

1. Confirm the canary account is not locked or rate-limited.
2. Compare the auth endpoint to the last known good config.
3. Inspect `Set-Cookie` headers for SameSite/Secure/Domain regressions.
4. Check the identity provider status page.
5. Test login in incognito; capture the network panel through the redirect.

## False positives

- Rate-limit hits if cadence is too aggressive.
- Dashboard marker can change during marketing redesigns. Use a stable
  `data-testid` you control.

## Alert routing

- **Severity:** page.
- **Channel:** on-call auth.
- **Suppress:** scheduled maintenance, identity provider status incidents.
