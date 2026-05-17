# Bubble + Stripe live webhook

> Test mode worked. You flipped to live. Now real customers pay and nothing
> happens on your side.

## Symptoms

- Test mode Stripe events trigger the Bubble workflow; live events do not.
- Stripe dashboard says "Succeeded" (2xx) but the workflow never ran.
- Customers complete checkout but receive no email, no account, no thing.

## Failure modes

- The Stripe endpoint URL still contains `/version-test`.
- The Stripe endpoint URL points at `/initialize` (the one-time detection route).
- Test keys, live keys, and webhook signing secrets are mixed.
- The expected event type (e.g. `checkout.session.completed`) is not subscribed.
- The Bubble backend workflow requires authentication that Stripe is not sending.
- The domain changed after launch and the Stripe endpoint still points at the old one.
- The workflow does too much before returning 2xx; Stripe retries fire duplicates.

## Checks

See [`nightlamp.recipe.yaml`](nightlamp.recipe.yaml). Two monitors:

1. **`http_keyword`** — POST a benign probe to the live webhook workflow and
   assert the response does not contain `version-test`. Catches the single
   most common Bubble misconfiguration in seconds.
2. **`api_canary`** — read the most recent stored Stripe event row. If the
   newest row is older than your expected event interval, live events are not
   landing.

Replace `{{your-app-domain}}`, `{{stripe_live_workflow_slug}}`,
`{{STRIPE_SIGNATURE_PROBE}}`, and `{{BUBBLE_API_TOKEN}}` with your values.
Store the token and signature placeholders in your monitoring tool's variable
store, never in the manifest.

## Triage

1. Stripe dashboard → Developers → Webhooks. Confirm the endpoint URL does
   not contain `/version-test` or `/initialize`.
2. Confirm the live signing secret matches the one stored in the Bubble
   workflow.
3. Confirm the event type subscribed in Stripe matches what the workflow
   listens for.
4. Send a test event from Stripe → Webhooks → "Send test webhook" and watch
   the Bubble logs.
5. Confirm the API entry point does not require authentication, or that
   Stripe is configured to send it.
6. If the custom domain changed recently, update the Stripe endpoint URL.

## False positives

- Stripe sends bursts; a quiet hour at 03:00 UTC is not always a failure.
- The `api_canary` token may itself rotate; a 401 on that monitor doesn't
  mean payment is broken.

## Alert routing

- **Severity:** page.
- **Channel:** on-call for payments.
- **Suppress:** during scheduled maintenance windows or when Stripe's status
  page reports an incident.

## See also

- [Bubble Stripe webhook guide on Nightlamp](https://nightlamp.app/guides/bubble-stripe-webhook-failures)
- [Stripe webhooks docs](https://docs.stripe.com/webhooks)
