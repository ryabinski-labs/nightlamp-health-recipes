# Nightlamp Health-Check Recipes

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-1f6feb.svg)](LICENSE)
[![Recipes](https://img.shields.io/badge/recipes-10-17202a.svg)](#available-recipes)
[![Validate recipes](https://github.com/GipsyChef/nightlamp-health-recipes/actions/workflows/validate-recipes.yml/badge.svg)](https://github.com/GipsyChef/nightlamp-health-recipes/actions/workflows/validate-recipes.yml)
[![Run on Nightlamp](https://img.shields.io/badge/run%20on-Nightlamp-1f6feb.svg)](https://nightlamp.app/recipes?utm_source=recipes&utm_medium=readme&utm_campaign=badge)

**[Browse the recipes &rarr;](https://nightlamp.app/recipes?utm_source=recipes&utm_medium=readme&utm_campaign=top_cta)** — scenario-specific monitors and triage for the silent failures in no-code &amp; AI-built apps.

Open-source recipes for the failure modes that bite no-code and AI-built apps:
checkout, webhook, auth, DNS/SSL, cron, lead forms, third-party APIs, and visual
regressions. Copy a recipe, set up the checks, and know what to look at first
when something goes wrong.

These recipes are organized by **scenario** (the thing that actually breaks),
not by check primitive. Each one tells you:

- the symptom a customer reports,
- the likely failure modes,
- the Nightlamp monitor(s) to set up (with concrete YAML),
- the signals you should expect to see,
- common false positives,
- a short triage checklist for the on-call human,
- and where to route the alert.

You can use the recipes with any synthetic-monitoring tool — the YAML is
human-readable and the checks are intentionally generic. They run best inside
[Nightlamp](https://nightlamp.app), which packages the monitors, incident
matching, and diagnostic playbooks for you.

## The problem these recipes solve

Generic uptime monitoring tells you the homepage returns 200. It does not
tell you that the checkout button stopped working, that the Stripe live
webhook silently went to `/version-test`, that the nightly cron job exits
clean without doing anything, or that the cert on the subdomain you
launched a year ago is about to expire. Those are the failures that lose
money and trust — and they require scenario-specific recipes, not just more
HTTP checks. This repo collects those recipes for operators who do not have
the time or background to invent each one from scratch.

## Who this is for

- **No-code founders** running Bubble, Lovable, Cursor-built, Webflow,
  FlutterFlow, or similar production apps with no dedicated SRE.
- **Small teams** that just shipped a fragile flow and want to know it broke
  before the customer does.
- **Operators** maintaining cron jobs, webhooks, and third-party integrations
  that fail silently.

## Repository layout

```
recipes/
  <scenario>/
    README.md                 # symptom, failure modes, triage, alerting
    nightlamp.recipe.yaml     # machine-readable manifest (monitors + metadata)
schemas/
  recipe.schema.json          # JSON schema for the manifest
scripts/
  validate_recipes.py         # local validator (runs in CI too)
.github/
  ISSUE_TEMPLATE/
    recipe-request.yml
    recipe-bug.yml
  workflows/
    validate-recipes.yml
CONTRIBUTING.md
CODE_OF_CONDUCT.md
SECURITY.md
MAINTAINERS.md
LICENSE                       # Apache-2.0
CHANGELOG.md
```

## Available recipes

| Scenario | When it bites | Recipe |
|---|---|---|
| Bubble + Stripe live webhook | Switching Stripe to live mode silently drops `checkout.session.completed`. | [`bubble-stripe-live-webhook`](recipes/bubble-stripe-live-webhook/) |
| Checkout path | The Buy button page goes blank, slow, or 500s right before payment. | [`checkout-path`](recipes/checkout-path/) |
| Auth / login journey | Login form renders but submission no longer redirects. | [`auth-login-journey`](recipes/auth-login-journey/) |
| Lead form delivery | Form posts succeed but the lead never lands in the CRM/sheet/email. | [`lead-form-delivery`](recipes/lead-form-delivery/) |
| Custom domain / DNS cutover | A DNS edit moved customers to a misconfigured origin. | [`custom-domain-dns-cutover`](recipes/custom-domain-dns-cutover/) |
| SSL certificate expiry | The cert quietly expires on a subdomain you forgot existed. | [`ssl-expiry`](recipes/ssl-expiry/) |
| Cron / heartbeat | A scheduled job stops running and no one notices for a week. | [`cron-heartbeat`](recipes/cron-heartbeat/) |
| Third-party API canary | A vendor (Stripe, Twilio, OpenAI, Mapbox) degrades or rate-limits you. | [`third-party-api-canary`](recipes/third-party-api-canary/) |
| Homepage visual regression | A theme/CSS deploy makes the landing page render blank or broken. | [`homepage-visual-regression`](recipes/homepage-visual-regression/) |
| Webhook response-code drift | An inbound webhook starts returning 2xx but no longer does the work. | [`webhook-response-code-drift`](recipes/webhook-response-code-drift/) |

## Installation and setup

There is nothing to compile or install to use a recipe. The "install" is:
clone or copy the recipe folder, replace the `{{placeholder}}` values with
your domain and identifiers, and create the listed monitors in your tool of
choice.

To run the local validator (only needed if you are editing recipes):

```sh
git clone https://github.com/GipsyChef/nightlamp-health-recipes.git
cd nightlamp-health-recipes
python3 -m pip install pyyaml jsonschema
python3 scripts/validate_recipes.py
```

**Prerequisites for editing recipes:** Python 3.10+, `pyyaml`, `jsonschema`.
No runtime is required to simply read and copy a recipe.

**Supported platforms:** Recipes are platform-neutral YAML and Markdown. They
work on macOS, Linux, and Windows. Recipes name monitor types in a generic
taxonomy (see below) so they can be used with Nightlamp, Checkly, Grafana
Synthetic Monitoring, Prometheus `blackbox_exporter`, Upptime, or any other
tool that supports the equivalent check primitives.

## Quickstart: use a recipe with Nightlamp

1. Open the recipe's `nightlamp.recipe.yaml`.
2. Replace `{{...}}` placeholders with your domain, paths, and any non-secret
   identifiers.
3. Create one monitor per `checks[*]` entry in Nightlamp (or import via the
   monitor JSON paste field — most check types map 1:1 to monitor fields).
4. Copy the **Triage** section from `README.md` into your runbook so the
   on-call has a starting checklist.

## Quickstart: use a recipe with any other tool

The manifest names monitor types using a generic taxonomy:

- `http_status` — periodic HTTP check, status code assertion
- `http_keyword` — periodic HTTP check, body keyword assertion
- `ssl` — TLS certificate expiry/validity
- `tcp` — TCP port reachability
- `api_canary` — multi-step API request sequence with assertions
- `browser_journey` — Playwright-style click/fill/assert flow
- `visual_snapshot` — rendered page snapshot diff
- `heartbeat` — inbound ping; alert on absence

Map these to whatever check primitive your tool offers
(Checkly browser/API/heartbeat checks, Grafana SM, Prometheus `blackbox_exporter`,
Upptime, etc.).

## Contributing

We welcome:

- **New recipes** for failure modes you have actually hit.
- **Updates** to existing recipes when a vendor behavior, URL, or workaround
  changes.
- **Refinements** to triage steps, alert routing, or false-positive notes.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the recipe format, validation
rules, and what we won't merge (secrets, customer-identifying details, unsafe
probing patterns).

## Governance and support

- License: [Apache-2.0](LICENSE).
- Maintainers: [`MAINTAINERS.md`](MAINTAINERS.md).
- Security disclosure: [`SECURITY.md`](SECURITY.md).
- Code of conduct: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
- Recipes are reviewed quarterly. Each one has a `last_reviewed` date in its
  manifest.

This is a community knowledge base. Nightlamp the product is the easiest way
to run, alert on, and learn from these recipes continuously — but the recipes
themselves are yours to use, fork, and adapt.
