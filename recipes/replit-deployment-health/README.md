# replit-deployment-health

> Works in the editor. Breaks at the deployed URL — or just goes to sleep.

## Symptoms

- App is unreachable or shows a "This Repl is sleeping" page on the free plan.
- App works in the Replit editor but fails at the custom domain.
- Secrets are present in the Secrets tab but undefined at runtime after a restart.
- Database queries fail after a cold start.
- App starts on the wrong port and returns connection refused.

## Failure modes

- Free-plan Replits sleep after inactivity; the first wake takes 10–30 seconds.
- Secrets in the Secrets tab are not auto-exported to deployed static builds.
- App binds to  instead of ; external traffic is rejected.
- Custom domain CNAME or A record drifted after a Replit deployment switch.
- Database connection string expired or rotated.

## Checks

Four monitors cover the main deployment failure modes:

1. ** — deployed URL responds.** Confirms the Replit deployment URL and custom domain answer (with wake-up timeout for free plan).
2. ** — real content rendered.** Loads the live app with a generous timeout and asserts a meaningful element exists.
3. ** — database-backed endpoint returns data.** Calls a health or data endpoint to confirm the DB connection is alive after restarts.
4. ** — custom-domain certificate valid.** Confirms the TLS cert for your custom domain.

## Triage

1. Open the app URL in a browser and wait 30 seconds — if it wakes, use Replit Deployments to avoid free-plan sleeping.
2. Check the Replit Secrets tab: every secret the code reads must be there.
3. Confirm the app binds to  on the correct port ( env var, usually 3000).
4. Custom domain: verify the CNAME or A record still points to Replits deployment endpoint.
5. Database: test the connection string directly to confirm it has not rotated.

## Run this continuously

[Nightlamp](https://nightlamp.app/?utm_source=recipes&utm_medium=readme&utm_campaign=replit-deployment-health) packages these monitors for no-code and AI-built apps.

Companion guide: [Replit app unreachable or broken?](https://nightlamp.app/guides/replit-app-broken)
