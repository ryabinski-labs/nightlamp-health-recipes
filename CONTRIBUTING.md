# Contributing

Thanks for thinking about contributing. Recipes are most useful when they come
from operators who actually hit the failure and remember what they wished they
had monitored.

## What to contribute

**New recipes** for a specific failure mode of a specific kind of app
(Bubble, Lovable, Cursor-built, Webflow, FlutterFlow, custom React/Vue, etc.).
A good recipe targets one *scenario*, not one *check primitive*. "Bubble +
Stripe live webhook" is a scenario. "HTTP status check" is not.

**Updates** to existing recipes when:

- a vendor changes a URL pattern, error code, or required header,
- a new false positive shows up,
- a triage step turns out to be misleading,
- you find a more resilient locator/keyword/threshold.

**Refinements** to alert routing advice, signal noise reduction, or
operator-facing language.

## What we will not merge

- Secrets, API keys, tokens, customer-identifying URLs, screenshots that
  expose customer data, or anything that requires the reader to have
  account-level access to verify.
- Recipes that probe targets you do not operate or have not been authorized
  to probe.
- Probing patterns that could cause harm: high-cadence polling of expensive
  endpoints, abusive retry storms, anything that could trip a rate-limit on a
  shared resource.
- Closed-source vendor-specific configuration that cannot be reproduced
  without a paid account.
- Marketing for unrelated products. Cross-linking to Nightlamp docs/guides is
  fine; we expect it.

## Recipe format

Every recipe lives under `recipes/<slug>/` and contains:

- `README.md` — operator-facing narrative. See an existing recipe for the
  exact section order.
- `nightlamp.recipe.yaml` — machine-readable manifest validated by
  `schemas/recipe.schema.json`.

The manifest must include:

- `id` — kebab-case scenario slug, matching the directory name.
- `scenario` — one short sentence describing the failure.
- `audience` — list from `[bubble, lovable, cursor, webflow, flutterflow,
  no-code, ai-built, generic]`.
- `symptoms` — list of customer-visible symptoms.
- `failure_modes` — list of underlying causes.
- `checks` — one or more monitor definitions using the generic taxonomy
  (`http_status`, `http_keyword`, `ssl`, `tcp`, `api_canary`,
  `browser_journey`, `visual_snapshot`, `heartbeat`).
- `expected_signals` — what a passing/failing run looks like.
- `false_positives` — known reasons the recipe might fire when nothing is
  actually broken.
- `triage` — ordered checklist a human can follow.
- `alert_routing` — who to wake, how loudly, and when to suppress.
- `references` — at least one canonical link.
- `last_reviewed` — ISO date (YYYY-MM-DD).
- `owner` — `maintainers` or a GitHub handle/team.

Placeholders for customer-specific values use `{{double_braces}}`. Sensitive
values must never appear in the manifest; use a placeholder like
`{{LOGIN_PASSWORD}}` and document that the operator should store the secret
in their monitoring tool's variable store.

## Validate locally

```sh
python3 scripts/validate_recipes.py
```

The same validator runs in CI on every PR. PRs cannot merge while validation
fails.

## How to submit

1. Fork the repo and create a branch.
2. Add or update files. One recipe per PR is easier to review than a batch.
3. Run the validator locally.
4. Open a PR using the template. Describe the real-world failure that
   motivated the recipe (anonymized).
5. CI will run validation and required checks. A maintainer will review.

## Quarterly review

Maintainers review every recipe at least once per quarter. The
`last_reviewed` date in the manifest is updated whenever a recipe is checked
end-to-end. If a recipe has not been reviewed in 180 days, it gets a stale
label and may be archived if no maintainer can re-verify it.

## Code of conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
