---
status: maintainer-reference
purpose: Developer workflow guide for maintainers of this skill.
audience: maintainers only — not shipped to skill users.
related: AGENTS.md routes agents to this maintainer reference.
---

# Maintaining the Repo Health Scan Skill

This is the maintainer entry point. Use it for changes to this repository; do
not copy it into repositories that consume the skill.

## Start here

Choose the smallest path that matches the change:

| Change | Required path |
|---|---|
| Docs, CI, schemas, or maintainer scripts | Make the change, then run the fast verification checklist. |
| `SKILL.md` wording or behavior | Apply the change, run the fast checklist, then run the local Codex regression. |
| Release | Align versions, pass CI for the release commit, then follow the release process below. |
| Agent support claim | Update the relevant compatibility report and portability evidence; do not broaden claims from one runtime. |

The installed runtime payload is only `skills/repo-health-and-sync-skill/SKILL.md`.
The adjacent `references/` files are maintainer-only evidence/templates and are
not copied into an agent's installed skill directory.

## Commit convention

Every commit must answer what and why. Use this body format:

```text
what: <one-line description of the change>
why:  <reason — design rationale, observed failure, user request, or finding>
```

Subject line: `type: scope — description`.

Commit subjects and bodies must not include secrets, credentials, access
tokens, private keys, sensitive values, or secret-bearing URLs. Describe the
change generically and redact sensitive identifiers. If a secret may have been
committed, stop before publishing and recommend revocation or rotation; editing
the message or deleting a file does not undo exposure from a commit that was
already shared.

| Type | When to use |
| :--- | :---------- |
| `feat:` | New methodology addition |
| `docs:` | Documentation (README, docs/) |
| `refactor:` | Restructuring, no behaviour change |
| `fix:` | Bug fix in SKILL.md |
| `chore:` | Housekeeping (.gitignore, CI) |
| `ci:` | GitHub Actions or other CI configuration |
| `test:` | Tests, fixtures, or evaluation evidence |
| `chore(deps):` | Dependency bump (dependabot uses this scoped form) |

Subject prefixes are enforced automatically by CI in the `phase-b-gate` job
(`scripts/check-commit-convention.py`), which checks every commit in the pushed
range on `main`. Prefixes outside the table above fail the gate, so use only
those listed.

The prefixes `what:`, `changelog:`, `sync:`, `flatten:`, and `dev:` were used
historically (before 2026-07-13 / v0.2.0) and are now retired. They are not
enforced against existing history: because release tag `v0.2.0` points at
commit `74d2082` whose subject is `what: fix table pipe formatting in Step 2
dimension table`, rewriting past subjects would destroy release history. Only
new commits going forward are validated.

## Change admission gate

Apply this gate before adding methodology, automation, adapters, schemas, or
shared abstractions. It is a maintainer judgment aid, not an automated score.

1. What observed failure or repeated cost motivates the change?
2. Which established specification or first-party implementation was checked?
3. Can an existing mechanism be adopted instead of creating another one?
4. What is the smallest change that addresses the evidence?
5. Has the pattern occurred in two concrete uses before shared infrastructure
   is extracted?
6. What runtime-payload or maintenance complexity will the change add?
7. What evidence will show that the change worked or should be removed?

Use these decision rules:

- No observed problem: defer it. Record project-specific possibilities in the
  roadmap or issue tracker; keep broader research questions in a
  non-authoritative study log.
- An established mechanism fits: adopt it and document only the local choice.
- One concrete use: keep the solution local rather than generalizing it.
- The behavior surface grows: require proportionate evaluation evidence.
- A milestone just completed: consolidate and collect evidence before expanding.

Do not create a proposal database, scoring framework, or validator for this
gate. Revisit that decision only after repeated maintainer failures show that
the human-reviewed checklist is insufficient.

## Fast verification checklist

Run this after every change. The tree-clean check is the final check, after all
edits and generated artifacts have been removed:

1. **Documentation:** `python3 scripts/doc-audit.py --self-test`
2. **No stale refs:** `grep -rn --include='*.md' 'PLAN\\.md\\|PROPOSALS\\.md\\|REPORT\\.md\\|USER-SUGGESTIONS\\.md' . | grep -v '.git/'`
3. **Eval contract:** `python3 scripts/validate-evals.py`
4. **Trust contract:** `python3 scripts/check-trust.py`
5. **Version alignment:** `python3 scripts/check-version-consistency.py`
6. **Python lint:** `uv run ruff check scripts/ skills/`
7. **Regression grader self-test:** `python3 scripts/grade-codex-transcript.py --self-test`
8. **Shellcheck:** run on any modified shell files.
9. **Final tree:** `git status --porcelain` shows nothing.

The model regression is deliberately outside the fast checklist because it
requires authenticated model access and is nondeterministic. After a material
`SKILL.md` workflow or trigger change, run
`python3 scripts/run-codex-regression.py` locally or dispatch the dedicated
`Codex regression` workflow. Do not make ordinary changes depend on model
availability.

See [codex-regression.md](codex-regression.md) for artifacts, grading, and the
current evidence boundary.

## Release process

Releases are created by `.github/workflows/release.yml` from a pushed semantic
version tag. The workflow is intentionally gated before it writes a GitHub
Release:

1. Align the `SKILL.md`, plugin manifest, citation metadata, and release tag
   versions with `python3 scripts/check-version-consistency.py`.
2. Commit and push the release change to `main`; wait for the `ci` workflow to
   pass for that exact commit.
3. Create and push the version tag (use the repository's normal signing policy
   when creating tags):

   ```bash
   git tag -a vX.Y.Z -m "release: vX.Y.Z"
   git push origin vX.Y.Z
   ```

4. The release workflow verifies that the tag is reachable from `main`, finds
   a successful `ci` run for the tagged commit, and checks the tagged diff for
   whitespace errors.
5. After the preflight succeeds, it creates the GitHub Release with generated
   notes. Categories and excluded labels are defined in `.github/release.yml`.

Do not create the GitHub Release manually before the preflight completes. A tag
that does not point into `main` or lacks a successful CI run is rejected.

## How the skill works

The skill runtime is a single SKILL.md with no shipped scripts and no build
process. The adjacent references are maintainer-only and are not installed.
The agent discovers repo characteristics at runtime
using tools already on PATH (`git`, `shellcheck`, `python3`, `gh`).

Changes to the methodology go directly into `skills/repo-health-and-sync-skill/SKILL.md`.
There is no sync step, no payload regeneration, and no duplicate reference
copies to maintain.

Root `AGENTS.md` is a routing adapter, not a second maintainer guide. It points
repository-health work to `SKILL.md` and repository changes to this file.

## Source ownership

Keep one authoritative home for each kind of information. The root
[README](../README.md) contains the user-facing overview and full repository
tree; this table identifies where maintainers should make changes:

| Concern | Authoritative location |
|---|---|
| Runtime audit methodology | `skills/repo-health-and-sync-skill/SKILL.md` |
| Maintainer workflow and release procedure | `docs/maintaining.md` |
| Architecture decisions | `docs/decisions.md` |
| Portability and compatibility claims | `docs/portability-contract.md` and `docs/compatibility-reports/` |
| Model regression behavior and evidence | `docs/codex-regression.md` and `evals/` |
| Deterministic validation | `scripts/`, `schemas/`, and `.github/workflows/ci.yml` |
| Packaging metadata | `.codex-plugin/plugin.json`, `CITATION.cff`, and `SKILL.md` frontmatter |

Do not copy guidance between these locations. Link to the owning document
instead; this is the primary defense against documentation drift.

## Common pitfalls

1. **Speculative checks.** A methodology addition needs an observed failure
   or a documented ecosystem pattern, not "seems useful."
2. **Over-instruction.** The methodology should be compact enough that the agent
   can read and apply it in one pass. If the SKILL.md grows significantly,
   trim the methodology back rather than adding reference files. Trust the
   agent's judgment for details; the methodology teaches *how to decide*,
   not *what to check*.
3. **Ecosystem drift.** The tools on PATH change over time. Verify that
   detection commands in SKILL.md still work against current tool versions.
4. **Platform-specific commands in a portable methodology.** Do not add
   Hermes-specific commands (`skill_view`, `hermes skills`) or agent-specific
   config paths to the skill payload. Track platform packaging and behavior in
   compatibility reports instead.
