# Lead form delivery

> The form says "thanks!" The CRM stays empty. Marketing dollars vanish.

## Symptoms

- Form shows a green success message but the lead never lands in the CRM,
  sheet, or inbox.
- Sales reports a quiet week that doesn't match marketing traffic.
- The form POST returns 200, but the destination shows nothing new.

## Failure modes

- A Zap / Make / n8n workflow paused or ran out of tasks.
- The destination API key rotated; the integration still uses the old one.
- A reCAPTCHA or honeypot change silently drops valid submissions as spam.
- The form route was renamed; the success message stayed hardcoded.
- The CRM webhook URL changed during a CRM migration.

## Checks

Two monitors. The first proves the form accepts data. The second proves the
data actually arrived downstream.

1. **`api_canary` — form POST.** Submits a canary lead with a recognizable
   email like `canary@your-domain-canary.com` and asserts the success marker
   appears in the response.
2. **`api_canary` — destination check.** Queries the destination (CRM API,
   Sheet, etc.) and asserts the canary email appears in a recent record.

Use a canary email domain you own and do not use elsewhere — this keeps it
easy to filter and recognize, and prevents accidentally polluting real sales
outreach.

## Triage

1. Search the destination for the canary email address.
2. Open the Zap/Make/n8n history; look for failed runs or paused workflows.
3. Confirm the destination API token is still valid.
4. Submit a manual test from incognito; watch the network panel for the
   form POST and any tracking calls.
5. Check spam quarantine if delivery is by email.

## False positives

- Anti-spam services may classify the canary as junk if cadence is too high
  or the email domain looks new.
- Destinations that batch ingestion (CRMs, data warehouses) may have a
  multi-minute lag. Set the destination cadence ≥ slowest batching window.

## Alert routing

- **Severity:** ticket (not page — marketing-ops can handle next-morning).
- **Channel:** marketing-ops.
- **Suppress:** scheduled maintenance windows.

## Run this continuously

[Nightlamp](https://nightlamp.app/?utm_source=recipes&utm_medium=readme&utm_campaign=lead-form-delivery) packages these monitors, incident matching, and diagnostic playbooks for no-code and AI-built apps — so this recipe runs continuously and pages you in plain English when the contract changes.

Companion guide: [Your form says “Thanks!” but the lead never arrives](https://nightlamp.app/guides/form-submits-but-no-lead).
