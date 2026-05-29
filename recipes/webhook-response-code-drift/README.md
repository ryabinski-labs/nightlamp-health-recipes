# Webhook response-code drift

> The webhook returns 200. It also stopped doing the work last Tuesday. No
> one noticed because everything looked green.

## Symptoms

- Sender (Stripe, GitHub, Slack, custom) records successful delivery.
- The downstream side-effect (DB row, email, notification) doesn't happen.
- Handler logs show it ran but exited early with no error.

## Failure modes

- A `try/except` now swallows the exception and returns 200.
- The sender renamed a required field; the handler ignores the new shape.
- Handler 200s immediately and enqueues the work; the worker is stuck.
- A feature flag disables the side-effect but the handler still 200s.
- A schema migration added a `NOT NULL` column the handler doesn't populate;
  the insert fails silently because the failure path returns 200.

## Checks

The trick: a 200 from the handler is not enough proof. You need to read the
side-effect.

1. **`api_canary` two-step.** POST a canary event with a unique `run_id`,
   then GET the side-effect surface for that `run_id`. The GET is the proof.
2. **`http_keyword` on a `/meta` endpoint** (optional). Asserts the handler
   advertises its current contract version. Catches silent contract changes
   between deploys.

Use an internal read token (`{{INTERNAL_READ_TOKEN}}`) stored in your
monitoring tool's variable store. The canary lookup endpoint should be
behind that token and should only return rows tagged as canary.

## Triage

1. Search logs for the canary `run_id`.
2. If POST 200 but GET fails: find the silent except, the disabled feature
   flag, or the failing insert.
3. Read the handler diff since the last known-good deploy.
4. Replay a recent failed canary in the queue/worker and watch.
5. Confirm the handler's interpretation of the event shape matches what the
   sender currently sends.

## False positives

- Worker delays of minutes can fool a tight two-step canary. Either delay
  the GET, or extend cadence and run the GET separately on a longer interval.
- If the queue is paused intentionally, suppress.

## Alert routing

- **Severity:** page.
- **Channel:** on-call integrations.
- **Suppress:** scheduled maintenance, intentional queue pauses.

## Run this continuously

[Nightlamp](https://nightlamp.app/?utm_source=recipes&utm_medium=readme&utm_campaign=webhook-response-code-drift) packages these monitors, incident matching, and diagnostic playbooks for no-code and AI-built apps — so this recipe runs continuously and pages you in plain English when the contract changes.
