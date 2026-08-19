# JSON Schemas Reference

Versioned schemas for optional automation interfaces. Maintainer-side evidence — not shipped as runtime dependencies.

## Schema Files

| Schema | Purpose | Validates |
|--------|---------|-----------|
| `repo-health-profile.schema.json` | Step 1 REPO PROFILE (observed/inferred) | Eval fixtures, agent output |
| `dimension-plan.schema.json` | Step 2 DIMENSION PLAN (active/skipped) | Eval fixtures, agent output |
| `repo-health-findings.schema.json` | JSONL findings (dimension, finding, harm, remediation, confidence) | `REPO_HEALTH_OUTPUT=jsonl` output |
| `repo-health-config.schema.json` | `.repo-health.json` per-repo override | Pre-flight contract |

## Design Principles

- **Maintainer-side evidence** — schemas live in `schemas/`, validated in CI, not shipped in skill payload
- **Draft 2020-12** — compatible with `jsonschema` Python library
- **Versioned per interface** — each schema independent; no monolithic schema
- **Optional interfaces** — skill works without them; they enable automation when present

## Validation

```bash
# Validate all schemas
python3 -c "
import json, jsonschema
for f in ['schemas/repo-health-profile.schema.json',
          'schemas/dimension-plan.schema.json',
          'schemas/repo-health-findings.schema.json',
          'schemas/repo-health-config.schema.json']:
    jsonschema.Draft202012Validator.check_schema(json.load(open(f)))
    print(f'OK: {f}')
"
```

## Confidence Levels

| Schema | Confidence | Reason |
|--------|------------|--------|
| repo-health-profile | High | Validated against 6 eval fixtures |
| dimension-plan | High | Validated against 6 eval fixtures |
| repo-health-findings | Medium | Only 1 example in skill; no model output validated |
| repo-health-config | Medium | No real `.repo-health.json` files in wild |

See also: `docs/portability-contract.md` §4, roadmap §7.