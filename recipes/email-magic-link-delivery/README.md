# Email magic-link delivery

> The login form works, but the email that lets people *finish* logging in
> never arrives. Auth is down and the page looks fine.

## Symptoms

- Users report "I never got the login email" or "the code never arrived".
- Signups complete but the confirmation email never lands, so accounts stay unverified.
- Support volume spikes around "can't log in" while the login form itself looks fine.

## Failure modes

- The transactional email provider (Postmark, SendGrid, Resend, SES) suspended the account or hit a sending cap.
- A domain/DNS change broke SPF, DKIM, or DMARC, so mail is silently dropped or junked.
- A deploy changed the auth endpoint, the from-address, or the template variable carrying the link.
- The provider API key rotated and the app still uses the old one — sends fail open with a 200.
- The magic-link host moved (custom domain cutover) and links now point at a dead origin.

## Checks

This recipe drives [Nightlamp's AgentDraft email-flow
monitor](https://nightlamp.app/docs/agentdraft-email-flow) — a real round-trip
through a live mailbox, expressed here as two `api_canary` checks:

1. **Request magic link and confirm mailbox delivery** — POSTs a magic-link
   request for a canary address, then polls the AgentDraft QA mailbox for the
   delivered message and asserts the magic-link host appears in the body
   (the `link_present` derived fact).
2. **Email passed SPF/DKIM/DMARC authentication** — asserts the delivered
   message authenticated cleanly, catching the "it arrives but lands in spam"
   case.

Substitute `{{your-app-domain}}`, `{{auth_magic_link_endpoint}}`,
`{{agentdraft_mailbox_domain}}`, `{{agentdraft_mailbox_query_url}}`,
`{{magic_link_host}}`, `{{auth_pass_marker}}`, and `{{AGENTDRAFT_API_TOKEN}}`
for your stack. The mailbox poll uses an AgentDraft API token with
`mailbox:read` + `mailbox:write` scopes.

> **Cadence floor:** email-flow monitors run no faster than every 300s because
> real delivery takes seconds to minutes. Raw links, OTPs, and cookies are never
> stored — only derived facts (`link_present`, auth results).

## Triage

1. Open the AgentDraft QA mailbox; find the canary message and compare its
   receive time to the trigger time.
2. No message? Check the email provider dashboard for bounces, suspensions, or
   a hit sending cap.
3. Message arrived but auth failed? Re-check SPF/DKIM/DMARC DNS for the sending
   domain.
4. Confirm the provider API key in the app is the current one — rotation is the
   most common silent cause.
5. Diff the auth/email template against the last known good deploy; a renamed
   link variable breaks the link without erroring.

## False positives

- Real delivery is bursty; one slow send can lag the 300s window. Add a grace
  cycle before paging.
- Provider sandbox/test mode can route to a suppression list — allowlist the
  canary address.
- A marketing blast to the same domain can warm-throttle transactional mail;
  correlate with provider status.

## Alert routing

- **Severity:** page.
- **Channel:** on-call auth.
- **Suppress:** scheduled maintenance, email provider status-page incident.

## Run this continuously

[Nightlamp](https://nightlamp.app/?utm_source=recipes&utm_medium=readme&utm_campaign=email-magic-link-delivery)
packages the [AgentDraft email-flow monitor](https://nightlamp.app/docs/agentdraft-email-flow),
incident matching, and diagnostic playbooks for no-code and AI-built apps — so
this recipe runs continuously and pages you in plain English when login email
stops landing.
