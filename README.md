# Nightlamp Health-Check Recipes

> Copy-paste monitoring recipes for the failure modes that quietly break
> no-code and AI-built apps — checkout, webhooks, auth, DNS/SSL, cron, lead
> forms, third-party APIs, and visual regressions.

[![Validate Recipes](https://github.com/GipsyChef/nightlamp-health-recipes/actions/workflows/validate-recipes.yml/badge.svg)](https://github.com/GipsyChef/nightlamp-health-recipes/actions/workflows/validate-recipes.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Recipes](https://img.shields.io/badge/recipes-13-success.svg)](#available-recipes)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Tool-agnostic](https://img.shields.io/badge/works%20with-any%20synthetic%20monitor-orange.svg)](#use-a-recipe-with-any-other-tool)

**The problem:** generic uptime monitoring tells you the homepage returns
`200`. It doesn't tell you the checkout button stopped working, the Stripe live
webhook silently went nowhere, or the cert on a forgotten subdomain expires next
week. This repo is built for no-code founders and small teams: each recipe
catches one money-losing failure mode and gives your on-call a triage checklist,
so you can fix it before customers notice.

Each recipe is a self-contained folder: a plain-English runbook plus a
machine-readable [`nightlamp.recipe.yaml`](schemas/recipe.schema.json) you can
copy into Nightlamp, Checkly, Grafana, Prometheus `blackbox_exporter`, or any
tool that speaks the same check primitives. **No install, no runtime, no
lock-in.**

---

## At a glance

| | |
|---|---|
| **What it is** | A library of 13 scenario-specific monitoring recipes (runbook + YAML manifest each). |
| **Who it's for** | No-code founders and small teams running production apps without a dedicated SRE. |
| **What you get** | Concrete monitors to set up, expected signals, false positives, a triage checklist, and alert routing — per failure mode. |
| **Cost to start** | Copy a folder, swap in your domain, create the listed monitors. ~5 minutes per recipe. |
| **License** | [Apache-2.0](LICENSE) — fork and adapt freely. |

### Use this if…

- You shipped a flow on **Bubble, Lovable, Cursor, Webflow, FlutterFlow**, or
  similar, and want to know it broke *before the customer tells you*.
- You run **cron jobs, webhooks, or third-party integrations** that can fail
  silently.
- You want a **triage checklist** ready in the runbook, not invented at 2am.

### Probably not for you if…

- You only need basic "is the homepage up?" uptime checks — any free uptime
  tool covers that.
- You have a full SRE/observability team with bespoke synthetic tests already.
- You need a hosted monitoring product out of the box — these are the *recipes*;
  [Nightlamp](https://nightlamp.app) is one way to run them continuously.

---

## Contents

- [Available recipes](#available-recipes)
- [Quickstart](#quickstart)
  - [With Nightlamp](#use-a-recipe-with-nightlamp)
  - [With any other tool](#use-a-recipe-with-any-other-tool)
- [What's in a recipe](#whats-in-a-recipe)
- [Repository layout](#repository-layout)
- [Editing & validating recipes](#editing--validating-recipes)
- [Contributing](#contributing)
- [Governance and support](#governance-and-support)

---

## Available recipes

| Scenario | When it bites | Recipe |
|---|---|---|
| 💳 Bubble + Stripe live webhook | Switching Stripe to live mode silently drops `checkout.session.completed`. | [`bubble-stripe-live-webhook`](recipes/bubble-stripe-live-webhook/) |
| 🛒 Checkout path | The Buy button page goes blank, slow, or 500s right before payment. | [`checkout-path`](recipes/checkout-path/) |
| 🔐 Auth / login journey | Login form renders but submission no longer redirects. | [`auth-login-journey`](recipes/auth-login-journey/) |
| 📥 Lead form delivery | Form posts succeed but the lead never lands in the CRM/sheet/email. | [`lead-form-delivery`](recipes/lead-form-delivery/) |
| 🌐 Custom domain / DNS cutover | A DNS edit moved customers to a misconfigured origin. | [`custom-domain-dns-cutover`](recipes/custom-domain-dns-cutover/) |
| 🔒 SSL certificate expiry | The cert quietly expires on a subdomain you forgot existed. | [`ssl-expiry`](recipes/ssl-expiry/) |
| ⏰ Cron / heartbeat | A scheduled job stops running and no one notices for a week. | [`cron-heartbeat`](recipes/cron-heartbeat/) |
| 🔄 Control-plane self-convergence | The reconcile loop dies, silently no-ops, or rolls back and drift goes unreconciled. | [`control-plane-converge`](recipes/control-plane-converge/) |
| 🔌 Third-party API canary | A vendor (Stripe, Twilio, OpenAI, Mapbox) degrades or rate-limits you. | [`third-party-api-canary`](recipes/third-party-api-canary/) |
| 🖼️ Homepage visual regression | A theme/CSS deploy makes the landing page render blank or broken. | [`homepage-visual-regression`](recipes/homepage-visual-regression/) |
| 🔁 Webhook response-code drift | An inbound webhook starts returning 2xx but no longer does the work. | [`webhook-response-code-drift`](recipes/webhook-response-code-drift/) |
| ✉️ Email magic-link delivery | The login email or OTP stops arriving, so customers can't get in. | [`email-magic-link-delivery`](recipes/email-magic-link-delivery/) |
| 🚨 Error-pipeline ingestion | A deploy drops the SDK or rotates the DSN, so exceptions raise no alerts. | [`error-pipeline-ingestion`](recipes/error-pipeline-ingestion/) |
| 📡 Log-pipeline silence | The log shipper or CloudWatch subscription dies and you go blind. | [`log-pipeline-silence`](recipes/log-pipeline-silence/) |

Recipes are organized by **scenario** (the thing that actually breaks), not by
check primitive — so you start from the symptom your customer reports.

---

## Quickstart

There's nothing to compile or install to *use* a recipe. The whole flow is:
**read the runbook → copy the YAML → swap in your values → create the monitors.**

### Use a recipe with Nightlamp

1. Open the recipe's `nightlamp.recipe.yaml` (e.g. [`recipes/ssl-expiry/nightlamp.recipe.yaml`](recipes/ssl-expiry/nightlamp.recipe.yaml)).
2. Replace `{{...}}` placeholders with your domain, paths, and non-secret identifiers.
3. Create one monitor per `checks[*]` entry in Nightlamp (or paste the monitor
   JSON — most check types map 1:1 to monitor fields).
4. Copy the **Triage** section from the recipe `README.md` into your runbook so
   on-call has a starting checklist.

✅ **Expected result:** within one check cadence you have live monitors that
fail *specifically* on the failure mode — not just on a downed homepage — and a
written triage path for whoever gets paged.

### Use a recipe with any other tool

The manifest names monitor types using a generic taxonomy, so they map onto any
synthetic-monitoring tool:

| Type | What it does |
|---|---|
| `http_status` | Periodic HTTP check, status-code assertion |
| `http_keyword` | Periodic HTTP check, body keyword assertion |
| `ssl` | TLS certificate expiry / validity |
| `tcp` | TCP port reachability |
| `api_canary` | Multi-step API request sequence with assertions |
| `browser_journey` | Playwright-style click/fill/assert flow |
| `visual_snapshot` | Rendered page snapshot diff |
| `heartbeat` | Inbound ping; alert on absence |

Map these onto Checkly browser/API/heartbeat checks, Grafana Synthetic
Monitoring, Prometheus `blackbox_exporter`, Upptime, or whatever you already run.

**Supported platforms:** recipes are platform-neutral YAML + Markdown and work
on macOS, Linux, and Windows.

---

## What's in a recipe

Every recipe folder gives the on-call human a complete story:

- **Symptom** — what the customer actually reports.
- **Failure modes** — the likely root causes, ranked.
- **Checks** — the exact monitor(s) to set up, with concrete YAML.
- **Expected signals** — what pass and fail look like.
- **False positives** — what looks broken but isn't.
- **Triage** — a short checklist for whoever gets paged.
- **Alert routing** — severity, channel, and when to suppress.

---

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
  ISSUE_TEMPLATE/             # recipe-request, recipe-bug, ...
  workflows/                  # recipe validation + OSS compliance
```

---

## Editing & validating recipes

You only need this if you're *editing* a recipe — reading and copying one needs
nothing installed.

```sh
git clone https://github.com/GipsyChef/nightlamp-health-recipes.git
cd nightlamp-health-recipes
python3 -m pip install pyyaml jsonschema
python3 scripts/validate_recipes.py
```

**Prerequisites:** Python 3.10+, `pyyaml`, `jsonschema`. The same validator runs
in CI on every pull request.

---

## Contributing

We welcome:

- **New recipes** for failure modes you've actually hit.
- **Updates** when a vendor behavior, URL, or workaround changes.
- **Refinements** to triage steps, alert routing, or false-positive notes.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the recipe format, validation rules,
and what we won't merge (secrets, customer-identifying details, unsafe probing
patterns).

---

## Governance and support

- **License:** [Apache-2.0](LICENSE) — yours to use, fork, and adapt.
- **Maintainers:** [`MAINTAINERS.md`](MAINTAINERS.md)
- **Security disclosure:** [`SECURITY.md`](SECURITY.md)
- **Code of conduct:** [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- **Support boundaries:** [`SUPPORT.md`](SUPPORT.md)
- Recipes are reviewed quarterly; each has a `last_reviewed` date in its manifest.

This is a community knowledge base. The recipes are yours to run anywhere —
[Nightlamp](https://nightlamp.app/?utm_source=recipes&utm_medium=readme&utm_campaign=root_readme)
is the easiest way to run, alert on, and learn from them continuously.
