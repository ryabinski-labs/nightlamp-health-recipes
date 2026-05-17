# Checkout path

> The buy page itself goes wrong. Every minute it's down is lost revenue.

## Symptoms

- Customers report a blank page on the buy/checkout URL.
- The checkout button doesn't respond, or the spinner never resolves.
- The page renders but the payment iframe never appears.

## Failure modes

- A recent deploy changed the route path or removed the page.
- A third-party script (Stripe.js, analytics, fonts) is blocking render.
- The page now requires login and is redirecting anonymous users away.
- A CSP or CORS change broke the payment SDK iframe.
- The page is 200ing but the body is a friendly "we'll be right back" placeholder.

## Checks

Three monitors, increasing fidelity:

1. **`http_status`** — cheap heartbeat that the URL exists.
2. **`http_keyword`** — asserts the payment SDK marker appears and a
   maintenance string does not. Catches the "200 but actually broken" case.
3. **`browser_journey`** — clicks the buy button on a product page and
   asserts the payment iframe becomes visible. Catches client-side breakage
   that the keyword check misses.

Substitute `{{your-app-domain}}`, `{{checkout_path}}`,
`{{product_path}}`, `{{buy_button_label}}`, `{{payment_sdk_marker}}` (e.g.
`js.stripe.com`), and `{{payment_iframe_host}}` for your stack.

## Triage

1. Open the checkout page in incognito. Does the SDK iframe render?
2. Check the browser console for blocked-script errors.
3. Compare the current URL to the last known good route; check recent deploys.
4. If the maintenance keyword fired, you're up but in maintenance mode —
   confirm intentional.
5. Roll back the last deploy if failure correlates with deploy time.

## False positives

- Payment SDK can lag during marketing campaigns; raise cadence with a grace
  window before paging.
- Browser journey can fail when the button label changes for a locale or
  A/B test variant. Update the locator.

## Alert routing

- **Severity:** page.
- **Channel:** on-call revenue.
- **Suppress:** scheduled maintenance, payment provider status page incident.
