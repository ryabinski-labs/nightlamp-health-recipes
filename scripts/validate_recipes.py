#!/usr/bin/env python3
"""Validate every recipe in this repo against the recipe schema.

Usage:
    python3 scripts/validate_recipes.py [--repo PATH]

Exits non-zero if any recipe is missing a manifest, fails schema validation,
has a manifest id that does not match its directory name, contains an obvious
secret pattern, or is missing the README symptom/triage sections.

Designed to run locally and in CI without network access. The only third-party
dependency is `pyyaml` (loaded lazily so an environment without it gets a
helpful message).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SECRET_PATTERNS = [
    (re.compile(r"(?i)sk_live_[a-z0-9]{8,}"), "looks like a live Stripe secret key"),
    (re.compile(r"(?i)rk_live_[a-z0-9]{8,}"), "looks like a live Stripe restricted key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "looks like an AWS access key id"),
    (re.compile(r"(?i)bearer\s+[a-z0-9._-]{20,}"), "looks like a Bearer token"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "contains a private key block"),
    (re.compile(r"(?i)password\s*[:=]\s*[\"']?[^\s\"']{4,}"), "contains a plaintext password assignment"),
]

REQUIRED_README_HEADINGS = ["symptoms", "triage", "checks"]


def load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except ImportError:
        sys.stderr.write(
            "validate_recipes.py: PyYAML is required. Install with: pip install pyyaml\n"
        )
        sys.exit(2)
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_schema(repo: Path) -> dict[str, Any]:
    schema_path = repo / "schemas" / "recipe.schema.json"
    if not schema_path.exists():
        raise SystemExit(f"missing schema: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_against_schema(manifest: Any, schema: dict[str, Any]) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        sys.stderr.write(
            "validate_recipes.py: jsonschema is required. Install with: pip install jsonschema\n"
        )
        sys.exit(2)
    validator = jsonschema.Draft202012Validator(schema)
    return [
        f"{'/'.join(str(p) for p in err.absolute_path) or '<root>'}: {err.message}"
        for err in validator.iter_errors(manifest)
    ]


def scan_for_secrets(text: str) -> list[str]:
    findings: list[str] = []
    for pattern, label in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(f"{label} at offset {match.start()}: {match.group(0)[:40]!r}")
    return findings


def readme_section_check(readme: str) -> list[str]:
    lowered = readme.lower()
    missing = []
    for heading in REQUIRED_README_HEADINGS:
        if f"## {heading}" not in lowered and f"### {heading}" not in lowered:
            missing.append(heading)
    return missing


def iter_recipes(repo: Path) -> Iterable[Path]:
    recipes_dir = repo / "recipes"
    if not recipes_dir.exists():
        return []
    return sorted(p for p in recipes_dir.iterdir() if p.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Repository root (default: cwd)")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    schema = load_schema(repo)
    recipes = list(iter_recipes(repo))

    if not recipes:
        sys.stderr.write(f"no recipes found under {repo / 'recipes'}\n")
        return 1

    errors: list[str] = []
    for recipe_dir in recipes:
        slug = recipe_dir.name
        manifest_path = recipe_dir / "nightlamp.recipe.yaml"
        readme_path = recipe_dir / "README.md"

        if not manifest_path.exists():
            errors.append(f"{slug}: missing nightlamp.recipe.yaml")
            continue
        if not readme_path.exists():
            errors.append(f"{slug}: missing README.md")

        manifest = load_yaml(manifest_path)
        if not isinstance(manifest, dict):
            errors.append(f"{slug}: manifest is not a YAML mapping")
            continue

        schema_errors = validate_against_schema(manifest, schema)
        for e in schema_errors:
            errors.append(f"{slug}: schema: {e}")

        manifest_id = manifest.get("id")
        if manifest_id != slug:
            errors.append(
                f"{slug}: manifest id ({manifest_id!r}) does not match directory name"
            )

        manifest_text = manifest_path.read_text(encoding="utf-8")
        for s in scan_for_secrets(manifest_text):
            errors.append(f"{slug}: manifest secret-scan: {s}")

        if readme_path.exists():
            readme_text = readme_path.read_text(encoding="utf-8")
            for s in scan_for_secrets(readme_text):
                errors.append(f"{slug}: readme secret-scan: {s}")
            missing_headings = readme_section_check(readme_text)
            for h in missing_headings:
                errors.append(f"{slug}: README is missing '## {h}' section")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"\n{len(errors)} validation error(s) across {len(recipes)} recipe(s).")
        return 1

    print(f"ok: {len(recipes)} recipe(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
