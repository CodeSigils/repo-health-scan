# Codex Compatibility Report

Status: `workflow_verified`

Date: 2026-07-13

## Scope

This report verifies Codex plugin packaging, local marketplace installation,
implicit skill discovery, and the full model-driven workflow for
`repo-health-and-sync-skill`. A 2026-07-13 conformance retest selected the skill
without naming it, emitted the profile and evidence-linked dimension plan before
health checks, reported concrete harm and remediation, and remained read-only.

## Sources

Accessed 2026-07-13:

- https://learn.chatgpt.com/docs/build-plugins
- https://learn.chatgpt.com/docs/build-skills

Evidence used:

- OpenAI plugin docs require `.codex-plugin/plugin.json`.
- OpenAI plugin docs show `skills` as a plugin-root-relative path such as
  `"./skills/"`.
- OpenAI skills docs describe progressive disclosure: Codex starts from skill
  `name`, `description`, and path before loading full `SKILL.md`.

## Environment

```text
codex-cli 0.133.0
repo: CodeSigils/repo-health-and-sync-skill
plugin: repo-health-and-sync-skill
plugin version: 0.2.0
isolated CODEX_HOME: $CODEX_HOME
temporary marketplace root: $TMPDIR/repo-health-marketplace
activation CODEX_HOME: $TMPDIR/repo-health-codex-eval-20260713
audit fixture: clean local clone at $TMPDIR/repo-health-audit-fixture
execution mode: ephemeral, read-only sandbox
```

The install test used an isolated `CODEX_HOME` under the workspace so the user's
real Codex configuration was not modified.

## Setup Guide Reproduction

The `docs/codex-setup.md` procedure was reproduced on 2026-07-13 with a new
isolated `CODEX_HOME`, a new local marketplace, and an empty git repository.
Marketplace registration, plugin installation, and listing reported
`repo-health-and-sync-skill@repo-health-local` as installed, enabled, and
version `0.2.0`.

An unnamed release-audit prompt then selected `repo-health-scan`, read
`SKILL.md` from the isolated plugin cache, summarized Discover -> Infer ->
Report, and stopped without repository probes or file changes. A diagnostic run
with `--ignore-user-config` did not see the installed plugin, so the setup guide
warns against that option during plugin verification.

## Commands

Validate plugin manifest against the local Codex plugin validator:

```bash
python3 "$CODEX_PLUGIN_VALIDATOR" \
  "$REPO_ROOT"
```

Result:

```text
Plugin validation passed: $REPO_ROOT
```

Register the temporary local marketplace:

```bash
env CODEX_HOME="$CODEX_HOME" \
  codex plugin marketplace add "$TMPDIR/repo-health-marketplace"
```

Result:

```text
Added marketplace `repo-health-local` from `$TMPDIR/repo-health-marketplace`.
Installed marketplace root: $TMPDIR/repo-health-marketplace
```

Install the plugin from that marketplace:

```bash
env CODEX_HOME="$CODEX_HOME" \
  codex plugin add repo-health-and-sync-skill --marketplace repo-health-local
```

Result:

```text
Added plugin `repo-health-and-sync-skill` from marketplace `repo-health-local`.
Installed plugin root: $CODEX_HOME/plugins/cache/repo-health-local/repo-health-and-sync-skill/0.2.0
```

Confirm installed status:

```bash
env CODEX_HOME="$CODEX_HOME" \
  codex plugin list --marketplace repo-health-local
```

Result:

```text
repo-health-and-sync-skill@repo-health-local  installed, enabled  0.2.0
```

Confirm installed payload:

```text
.codex-plugin/plugin.json
skills/repo-health-and-sync-skill/SKILL.md
```

## Activation Tests

### Implicit Discovery

The first prompt omitted the skill name so that selection depended on the
installed skill metadata:

```text
Audit this repository before release. Before running repository probes,
identify and read any installed skill relevant to this request. State the
selected skill and summarize its three-step workflow, then stop without
performing the audit or modifying files.
```

Transcript excerpt:

```text
I'll use the repo health scan skill because this is a release-readiness
repository audit request.

Selected skill: repo-health-and-sync-skill:repo-health-scan.
```

Codex then read `SKILL.md` from the installed plugin cache and summarized the
Discover -> Infer -> Report workflow without running repository probes. This
verifies description-driven discovery for this prompt on Codex CLI 0.133.0.

### Full Workflow Retest

The conformance prompt omitted the skill name, combining implicit discovery and
workflow validation in one isolated run:

```text
Audit this repository before release. Before running repository probes,
identify and read any installed skill relevant to this request. Do not modify
files. Emit the structured observed/inferred repository profile before
selecting health dimensions. For every candidate dimension, cite the profile
evidence that activates it or give a skip reason, then report findings with
concrete harm and remediation.
```

## Workflow Result

| Requirement | Result | Evidence |
|---|---|---|
| Select and load the installed skill | Pass | Codex selected `repo-health-scan` from the unnamed prompt and read its installed `SKILL.md` before repository inspection. |
| Produce an observed/inferred profile | Pass | A distinct `REPO PROFILE` transcript event separated observed facts from inferred labels. |
| Write the profile before dimension checks | Pass | The profile and `DIMENSION PLAN` appeared before the first health-check command. |
| Cite activation evidence | Pass | All seven active dimensions named one or more exact profile paths in `activated_by`. |
| Skip unsupported dimensions before probing | Pass | Cross-platform, attribution drift, and external-reference checks had explicit reasons and were not probed. |
| Explain concrete harm and remediation | Pass | The release-verification limitation included its concrete consequence and a specific rerun procedure. |
| Distinguish payload from maintainer tooling | Pass | The profile identified `SKILL.md` as shipped payload and `scripts/` as maintainer-only. |
| Preserve read-only behavior | Pass | No repository files changed; the run used Codex's read-only sandbox. |

The active dimensions were history hygiene, shell correctness, version
alignment, tag/release integrity, commit quality, CI efficiency, and file
coverage. The audit found the local dimensions healthy. It could not verify the
GitHub release because the clean local clone intentionally had a filesystem
remote; the report described the resulting evidence gap and the strict command
to rerun from a GitHub-backed clone. CI already executes that strict check with
its read-only job token.

## Deviations and Follow-up

No workflow acceptance criterion failed. The model additionally recorded
structured output as skipped because JSONL was not requested; this was
conservative and did not trigger an extra probe or finding.

The subsequent security review changed the release probe so `gh release list`
now requires `REPO_HEALTH_VERIFY_RELEASES=1`. The recorded transcript remains
the ordering and activation-evidence test; current network opt-in behavior is
enforced deterministically by `scripts/check-trust.py`.

Full workflow conformance is also represented by the local contract at
`evals/cases/repo-health-scan.json`, which asserts:

- A structured observed/inferred profile appears before any dimension probe.
- Every selected dimension cites the profile signal that activated it.
- Every candidate dimension is active or explicitly skipped before probing.

`python3 scripts/validate-evals.py` checks the contract structure, ordering
requirements, profile evidence references, complete dimension accounting, and
both skill-pack and non-skill fixtures. It does not run Codex or grade free-form
model output; repeat the transcript test when `SKILL.md` behavior changes
materially.

## Notes

Directly adding this repository as a marketplace failed because a plugin root is
not a marketplace root. The working local marketplace layout was:

```text
$TMPDIR/repo-health-marketplace/
├── .agents/plugins/marketplace.json
└── plugins/repo-health-and-sync-skill/
    ├── .codex-plugin/plugin.json
    └── skills/repo-health-and-sync-skill/SKILL.md
```

Using a symlink from the temporary marketplace plugin path back to this checkout
caused recursive copying because the isolated `CODEX_HOME` lived under the
workspace. The successful test used a minimal non-recursive temp copy containing
only `.codex-plugin/` and `skills/`.

---

## v0.3.0 Marketplace Installation Evidence (2026-08-19)

The v0.3.0 plugin manifest was validated and installed from a clean isolated
`CODEX_HOME` on 2026-08-19 to provide installation evidence for the released
version:

```bash
# Validate v0.3.0 plugin manifest
python3 "$CODEX_PLUGIN_VALIDATOR" \\
  "$REPO_ROOT"
```

Result:
```text
Plugin validation passed: $REPO_ROOT
```

The v0.3.0 plugin manifest (`./.codex-plugin/plugin.json`) identifies version
`0.3.0`, matching the `SKILL.md` frontmatter, `CITATION.cff`, git tag `v0.3.0`,
and GitHub release `v0.3.0`. This completes the installation evidence for the
current released version.

## Runtime freshness note (2026-08-24)

The local Codex CLI currently reports `codex-cli 0.149.0`. The
`workflow_verified` claim above remains scoped to the recorded `0.133.0`
execution evidence; the newer installed version has not yet received a new
model-regression certification run. This distinction prevents a version
observation from being mistaken for a behavioral compatibility result.
