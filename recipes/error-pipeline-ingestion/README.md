# Error-pipeline ingestion

> The scariest monitoring failure is the one where monitoring itself broke.
> A deploy drops the SDK, the DSN rotates — and now real exceptions raise no
> alerts at all.

## Symptoms

- Customers report errors that your dashboards never showed.
- The Issue queue goes suspiciously quiet right after a deploy, even under normal traffic.
- "We have monitoring" but the last ingested event is hours or days old.

## Failure modes

- A deploy removed or reordered the SDK init, so exceptions are never captured.
- The DSN rotated and the app still ships events to the old write-only credential.
- A bundler/tree-shaking change dropped the `@sentry/*` client from the production build.
- An egress/firewall or CSP `connect-src` change blocks the store endpoint.
- Sampling was cranked to near-zero, dropping events before they leave the client.

## Checks

This recipe self-monitors the [Sentry-compatible SDK
integration](https://nightlamp.app/docs/sdk-integration) — it proves errors
*could* be reported, rather than waiting to discover they can't:

1. **Canary event is accepted by the ingestion endpoint** — POSTs a canary
   event to the DSN store endpoint and asserts `200`. Because the DSN is a
   write-events-only credential, a 200 proves the whole write path (credential
   + network + endpoint) is alive. The event is tagged `level=info` /
   `environment=monitoring` so production alert rules ignore it.
2. **App build still references the ingestion DSN** — for client-side SDKs,
   asserts the production bundle still contains the ingest host, catching a
   tree-shake or dropped init *before* a real exception goes unreported. Skip
   for server-only SDKs.

Substitute `{{dsn_key}}`, `{{nightlamp_ingest_host}}`, `{{app_id}}`,
`{{release}}`, `{{your-app-domain}}`, and `{{built_bundle_path}}` for your
stack.

## Triage

1. Re-run the canary by hand against the store endpoint — a non-200 isolates
   the break to the write path.
2. Compare the deployed DSN to the value in Nightlamp's integration settings;
   rotation is the usual cause.
3. Grep the production bundle/source map for the ingest host to confirm the SDK
   init survived the build.
4. Check CSP `connect-src` and any egress firewall for the ingest host.
5. In the Issue queue, confirm alert rules exist
   ([`new_issue` / `threshold` / `regression`](https://nightlamp.app/docs/alert-rules))
   and are scoped to the right environment.

## False positives

- The canary event itself appears in the Issue queue — filter it by
  `environment=monitoring` so it never pages.
- A short ingest-endpoint maintenance window can 5xx briefly; allow one grace
  cycle.

## Alert routing

- **Severity:** ticket (escalate to page if paired with a traffic spike).
- **Channel:** on-call platform.
- **Suppress:** scheduled maintenance.

## Run this continuously

[Nightlamp](https://nightlamp.app/?utm_source=recipes&utm_medium=readme&utm_campaign=error-pipeline-ingestion)
ingests [SDK error events](https://nightlamp.app/docs/sdk-integration), groups
them into Issues, and applies [alert rules](https://nightlamp.app/docs/alert-rules) —
so this recipe runs continuously and tells you the moment your error pipeline
goes dark.
