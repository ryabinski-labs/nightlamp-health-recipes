# Security Policy

## Scope

This repository contains health-check recipes (YAML manifests and Markdown
documentation). It does not ship runtime code that processes untrusted input
in production. Security concerns most relevant here:

- Recipe content that could direct a reader to probe a target they do not
  operate.
- CI workflows that could leak repository tokens or be exploited via a
  malicious PR.
- Recipe validator scripts in `scripts/` and `.github/scripts/`.

## Reporting a Vulnerability

Please **do not** open a public issue for security reports.

- Email: **cigan1@gmail.com**
- Subject line: `[security] nightlamp-health-recipes: <short summary>`

Include:

- A description of the issue and the impact you observed.
- Steps to reproduce, ideally with a minimal failing input.
- Any suggested mitigation.

We will acknowledge receipt within **5 business days** and aim to provide a
fix or mitigation plan within **30 days** for confirmed issues.

## Disclosure

We follow coordinated disclosure. Once a fix is ready, we will publish a
release note in [`CHANGELOG.md`](CHANGELOG.md) and credit the reporter
unless they prefer to remain anonymous.

## Supported Versions

This repository does not version recipes individually. The `main` branch is
the supported version. Security-impacting changes will be reflected in the
changelog and tagged in a release.
