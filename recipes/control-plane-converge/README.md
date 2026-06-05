# Control-plane self-convergence

> A reconcile loop fails as an *absence*, not an error. The box stays up and
> serves the last-applied config while drift quietly accumulates — until the
> next deploy fails in a confusing way.

## Symptoms

- Config drift on a reconciled host goes unreconciled until a deploy needs it.
- The convergence timer dies and nobody notices until a change is required.
- Converge runs and exits 0 but never applies the desired state.

## Failure modes

- The convergence timer (e.g. a systemd timer) stopped or was masked.
- `ansible-pull` (or the reconcile step) throws on git/SSM/network, but the
  error is swallowed and never alerted.
- A bad commit fails config validation; converge rolls back but keeps failing.
- The node's secret-reader credential expired, so secrets can't be fetched.
- The timer fires but convergence is a silent no-op — drift accumulates.

## Checks

Three monitors that fail differently. The first two are the core of the recipe.

1. **`heartbeat`** — a push-based dead-man's switch
   ([docs](https://nightlamp.app/docs/heartbeat-monitors)). The key idea: the
   job pings its unique `heartbeat_ping_url` **only after a health-gated
   success** — every vhost's `/healthz` returns 200:

   ```bash
   # converge.sh, after ansible-pull applies desired state:
   if curl -fsS https://api.example.com/healthz >/dev/null; then
     write_converge_status ok=true last_success="$(date -Is)" config_rev="$(git rev-parse HEAD)"
     curl -fsS -X POST "$HEARTBEAT_PING_URL"      # only on success
   else
     write_converge_status ok=false
     # no ping → Nightlamp opens an incident at ~1.5x the interval
   fi
   ```

   A failed or rolled-back converge withholds the ping. Pinging on *every* timer
   fire would hide exactly the rollback you want to catch.
2. **`http_keyword` on the converge-status artifact** — fetches a small JSON
   document the node serves (`{"ok":true,"last_success":"…","config_rev":"…"}`)
   and asserts `"ok":true`, which is only true when `last_success` is recent.
   Catches the "timer ran, exited 0, did nothing" case the heartbeat misses.
3. **`http_status` on `/healthz`** — external liveness, independent of the
   converge loop.

## Triage

1. Is the convergence timer active and not masked?
2. Read the last converge run's logs for a swallowed git/SSM/network error.
3. Fetch the converge-status artifact; compare `last_success` and `config_rev`.
4. If a bad commit triggered a rollback, revert it and let converge re-apply.
5. Confirm the node's secret-reader credential is still valid.

## False positives

- A long but legitimate converge can lag the heartbeat if the grace window is
  too tight.
- A deliberate maintenance stop fires unless the monitor is paused
  (`paused_until`).

## Alert routing

- **Severity:** ticket.
- **Channel:** on-call platform.
- **Suppress:** scheduled maintenance.

## Run this continuously

[Nightlamp](https://nightlamp.app/?utm_source=recipes&utm_medium=readme&utm_campaign=control-plane-converge)
packages these monitors, incident matching, and diagnostic playbooks — so this
recipe runs continuously and pages you in plain English the first interval the
reconcile loop stops succeeding. See the full write-up:
[Control-plane self-convergence guide](https://nightlamp.app/guides/control-plane-self-convergence).
