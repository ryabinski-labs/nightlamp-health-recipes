# bolt-deployed-app-health

> Your bolt.new app works in the editor but breaks the moment it hits Netlify.

## Symptoms

- Blank or white screen on the live Netlify URL while the editor preview is fine.
- Supabase data does not load; rows return empty or 403.
- Webhooks return 401 after deploy.
- App broke after forking or duplicating the project.
- A secret key is visible in the browser network tab.

## Failure modes

- Env vars set in the Bolt editor were never added to the Netlify site.
- The Bolt-created Supabase database was never claimed in the Supabase dashboard.
- Forking created a new Netlify site; the custom domain still points at the old one.
- Webhook JWT verification is on and the deployed function rejects the signature.
- A Supabase secret or Stripe key is bundled in the client build.

## Checks

Five monitors cover the main Netlify-handoff failure modes:

1. ** — live URL responds.** Proves the Netlify URL and your custom domain answer at all.
2. ** — real content rendered.** Loads the deployed app and asserts a meaningful element exists — catches blank-screen and missing-env-var failures.
3. ** — Supabase data readable.** Reads through the Supabase-backed API as a signed-in user; exposes unclaimed databases and RLS-empty tables.
4. ** — webhook endpoint accepts a probe.** Catches JWT-verification rejection before your payment provider gives up retrying.
5. ** — custom-domain certificate valid.** Confirms the TLS cert for your custom domain before it expires.

## Triage

1. Open the live URL in incognito; read the browser console.
2. Netlify dashboard → Site settings → Environment variables: every var the app needs exists.
3. Supabase: Settings → Applications — Bolt connected? Database claimed?
4. Netlify deploy log: did the last publish build succeed?
5. If forked recently: look for a NEW Netlify site; move env vars and custom domain to it.
6. RLS: verify policies grant real users access (empty lists usually mean missing policies).
7. Rotate any key found in client network requests and move the call server-side.

## Run this continuously

[Nightlamp](https://nightlamp.app/?utm_source=recipes&utm_medium=readme&utm_campaign=bolt-deployed-app-health) packages these monitors for no-code and AI-built apps — so you get the diagnosis (which variable, which connection, which deployment) when the live site diverges from the editor.

Companion guide: [Bolt app broken after deploy?](https://nightlamp.app/guides/bolt-app-broken)
