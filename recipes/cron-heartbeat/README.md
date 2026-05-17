# Cron / heartbeat

> Scheduled jobs fail quietly. By the time someone notices, the bill is
> wrong, the report is missing, or the backup is gone.

## Symptoms

- A scheduled report stops arriving.
- A nightly cleanup/billing run/sync silently lapses.
- The job's logs go blank but the app surface looks normal.

## Failure modes

- The scheduler stopped (cron, GitHub Actions schedule, Bubble recurring
  event, Render cron, etc.).
- The job throws but the error is swallowed and never alerted.
- A deploy removed the job definition.
- A job credential quietly expired.
- The job runs but exits 0 without doing anything — config drift.

## Checks

Two monitors that fail differently. Use both.

1. **`heartbeat`** — the job POSTs to a heartbeat URL on **successful**
   completion only. If no ping arrives within `expected_interval_seconds`
   plus a small grace window, the monitor opens an incident. This is the
   classic dead-man's-switch pattern.
2. **`http_keyword` on the output artifact** — fetches the job's output
   (report URL, log file, generated dashboard) and asserts a recent
   timestamp marker is present. Catches the "exits 0 but did nothing" case
   the heartbeat misses.

Both together close the most common failure modes.

## Triage

1. Scheduler dashboard: is the job still listed and enabled?
2. Read the last run's logs for a swallowed exception.
3. Confirm credentials are still valid.
4. Manually trigger the job; confirm output marker updates.
5. Compare current definition against the last known good in source.

## False positives

- First run after a deploy can lag if the schedule offset moved.
- A grace window that's too tight will fire on cold-start delays.

## Alert routing

- **Severity:** ticket.
- **Channel:** on-call platform.
- **Suppress:** scheduled maintenance.
