# Log-pipeline silence

> You only notice the log shipper died when you reach for logs during an
> incident and there are none. This recipe notices first.

## Symptoms

- The log/Issue view stops updating even though the app is clearly serving traffic.
- An incident happens but there are no logs to investigate after the fact.
- The last log line ingested is timestamped hours ago, with no error to explain the gap.

## Failure modes

- The log shipper (Fluent Bit, Promtail, Vector, Grafana Alloy) crashed, OOMed, or was evicted and never rescheduled.
- The shipper auth header / DSN rotated and pushes now 401 silently in a retry loop.
- A CloudWatch subscription filter was deleted, or its destination Lambda lost invoke permission.
- A Loki push endpoint or label change made the shipper drop batches it considers malformed.
- A node pool or namespace change left the DaemonSet without the pods whose logs you cared about.

## Checks

This recipe self-monitors [log
subscriptions](https://nightlamp.app/docs/log-subscriptions) from both ends:

1. **Log stream is still flowing** (`heartbeat`) — treats steady log volume as
   a heartbeat. A healthy app under traffic emits lines continuously; if none
   are fingerprinted into the Issue queue within `expected_interval_seconds`,
   the *pipeline* is the suspect, not the app.
2. **Loki push endpoint accepts a canary line** (`api_canary`) — POSTs one
   canary line via the standard Loki push API and asserts `204`, proving the
   endpoint and auth header are valid. Together the two checks separate "shipper
   is dead" from "endpoint/auth is broken".

Substitute `{{nightlamp_ingest_host}}`, `{{app_id}}`, `{{LOKI_PUSH_TOKEN}}`,
and `{{push_timestamp_ns}}` for your stack. Size the heartbeat interval to
exceed your quietest normal traffic trough.

## Triage

1. Push canary 204 but heartbeat silent? The endpoint is fine — the shipper is
   the problem. Check the shipper pod/agent status and restart count.
2. Push canary fails auth? Rotate/redeploy the shipper credential to match
   Nightlamp's integration settings.
3. CloudWatch path: confirm the subscription filter still exists and the
   destination Lambda has invoke permission.
4. Check recent infra changes — node drains, namespace moves, or DaemonSet
   selector edits that orphaned the target pods.
5. Tail the shipper's own logs for backpressure, dropped batches, or
   malformed-label rejections.

## False positives

- Genuinely low-traffic apps can fall quiet at night — size the interval to the
  quietest real trough, or scope to a busier log stream.
- A deliberate log-level reduction (debug → error only) can cut volume below the
  heartbeat threshold; re-baseline after such changes.

## Alert routing

- **Severity:** ticket.
- **Channel:** on-call platform.
- **Suppress:** scheduled maintenance, planned cluster upgrade.

## Run this continuously

[Nightlamp](https://nightlamp.app/?utm_source=recipes&utm_medium=readme&utm_campaign=log-pipeline-silence)
ingests logs over the [Loki-compatible push API and CloudWatch
subscriptions](https://nightlamp.app/docs/log-subscriptions), fingerprints each
line into the same Issue queue as your SDK events, and watches the stream for
silence — so this recipe runs continuously and tells you the moment you go
blind.
