# Changelog

All notable changes to this project are documented here. The format is loosely
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

### Added

- Initial public release scaffold: README, license, contributing guide, code
  of conduct, security policy, support policy, maintainers list.
- Recipe manifest schema (`schemas/recipe.schema.json`) and local validator
  (`scripts/validate_recipes.py`).
- CI workflows: PR validation, recipe schema validation, and OSS compliance
  checks.
- First batch of scenario recipes: `bubble-stripe-live-webhook`,
  `checkout-path`, `auth-login-journey`, `lead-form-delivery`,
  `custom-domain-dns-cutover`, `ssl-expiry`, `cron-heartbeat`,
  `third-party-api-canary`, `homepage-visual-regression`,
  `webhook-response-code-drift`.
