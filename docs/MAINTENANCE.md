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

| Change                                        | Required path                                                                                                                                          |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Docs, CI, schemas, or maintainer scripts      | Make the change, then run the fast verification checklist.                                                                                             |
| `SKILL.md` wording or behavior                | Apply the change, run the fast checklist, then run the local Codex regression.                                                                         |
| Plugin manifest metadata                      | Update `.codex-plugin/plugin.json` when plugin identity changes. `version` is contractually required; it does not track Git tags or GitHub Releases.   |
| Agent support claim                           | Update the relevant compatibility report and portability evidence; do not broaden claims from one runtime.                                             |
| Bot or dependency update                      | Read [automation-identities.md](automation-identities.md), inspect the diff and required checks, then use the fast checklist.                          |
| Change a public support or distribution claim | Update [claim-evidence-matrix.md](claim-evidence-matrix.md) and its owning evidence report in the same change.                                         |

The installed runtime payload is only `skills/repo-health-scan/SKILL.md`.
Maintainer-only evidence/templates live under `docs/references/` and are not
copied into an agent's installed skill directory.

## One-time local setup

Run these once per clone, before the first commit:

```sh
uv sync --locked
git config core.hooksPath .githooks
```

The first command builds the locked environment the verification commands
expect. The second activates the committed `pre-commit` and `pre-push` hooks.
Without it, `core.hooksPath` is unset, `.git/hooks/pre-commit` does not exist,
and git silently runs no hook at all — every commit and push proceeds unchecked
even though the hooks are committed and executable. Nothing in the repository
can fix this: `core.hooksPath` is local git configuration and does not travel
with a clone.

### Direct-push enforcement

This solo-maintainer repository permits administrator pushes to `main`. GitHub
required checks run *after* a push and administrator enforcement is disabled,
so they are evidence and a pull-request merge gate, not a synchronous gate for
an administrator's direct push. Required signatures have the same limitation.

For a configured clone, the local hooks are the direct-push gate:

- `pre-commit` runs Ruff and the portability check.
- `pre-push` validates every outgoing commit subject, then runs
  `bash scripts/verify.sh` before Git sends the ref.

Both hooks are POSIX shell, and both are linted: `verify.sh` sweeps
`.githooks/` alongside `scripts/*.sh`, and each required CI job runs
`shellcheck scripts/*.sh .githooks/*`. Anything added to `.githooks/` is
therefore expected to be shell; if a non-shell hook is ever added
deliberately, those commands change with it.

`--no-verify` deliberately bypasses this local gate and leaves CI as the only
backstop. A fresh clone has no local gate until the setup command above runs.
If this repository gains regular contributors or independent review, switch to
pull requests and require administrator enforcement rather than treating local
hooks as shared protection.

## Commit convention

Every commit must answer what and why. Use this body format:

```text
what: <one-line description of the change>
why:  <reason — design rationale, observed failure, user request, or finding>
```

Subject line: `type(scope): description — summary`; `scope` is optional, and
`!` before the colon marks a breaking change.

Commit subjects and bodies must not include secrets, credentials, access
tokens, private keys, sensitive values, or secret-bearing URLs. Describe the
change generically and redact sensitive identifiers. If a secret may have been
committed, stop before publishing and recommend revocation or rotation; editing
the message or deleting a file does not undo exposure from a commit that was
already shared.

| Type           | When to use                                        |
| :------------- | :------------------------------------------------- |
| `feat:`        | New methodology addition                           |
| `docs:`        | Documentation (README, docs/)                      |
| `refactor:`    | Restructuring, no behaviour change                 |
| `fix:`         | Bug fix in SKILL.md                                |
| `chore:`       | Housekeeping (.gitignore, CI)                      |
| `ci:`          | GitHub Actions or other CI configuration           |
| `test:`        | Tests, fixtures, or evaluation evidence            |
| `chore(deps):` | Dependency bump (dependabot uses this scoped form) |

Subject prefixes are enforced by the local `pre-push` hook and verified again
by CI in the `phase-b-gate` job (`scripts/check-commit-convention.py`). The
hook checks every outgoing commit in the pushed range; CI reports the same
result after the push. Prefixes outside the table above fail either check, so
use only those listed.

The prefixes `what:`, `changelog:`, `sync:`, `flatten:`, and `dev:` were used
historically and are now retired. They are not enforced against existing
history: rewriting past subjects would destroy repository history. Only new
commits going forward are validated.

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

1. **Documentation:** `python3 scripts/doc-audit.py --self-test` and `python3 scripts/doc-audit.py` (the latter also verifies repository-relative Markdown links and anchors)
2. **Agent Skills format:** `uvx --from git+https://github.com/agentskills/agentskills.git@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref skills-ref validate skills/repo-health-scan`
3. **Compatibility evidence policy:** `python3 scripts/check-skills-ref-policy.py .`
4. **No stale refs:** `grep -rn --include='*.md' 'PLAN\\.md\\|PROPOSALS\\.md\\|REPORT\\.md\\|USER-SUGGESTIONS\\.md' . | grep -v '.git/'`
5. **Eval contract:** `python3 scripts/validate-evals.py`
6. **Trust contract:** `python3 scripts/check-trust.py`
7. **Python lint:** `uv run ruff check scripts/ skills/`
8. **Regression grader self-test:** `python3 scripts/grade-codex-transcript.py --self-test`
9. **Shellcheck:** run on any modified shell files.
10. **Final tree:** `git status --porcelain` shows nothing.

The model regression is deliberately outside the fast checklist because it
requires authenticated model access and is nondeterministic. After a material
`SKILL.md` workflow or trigger change, run
`python3 scripts/run-codex-regression.py` locally or dispatch the dedicated
`Codex regression` workflow. Do not make ordinary changes depend on model
availability.

## Automation and bot review

Read [automation-identities.md](automation-identities.md) before changing a
workflow, Dependabot configuration, or a bot-authored pull request. For this
solo repository, the correct default is small, reviewable bot proposals—not
automatic approval or merge. A green dependency PR establishes that the
configured checks passed; it does not establish semantic safety or authorize a
permissions change.

Auto-merge is disabled on this repository, so the prohibition is enforced by
configuration rather than by convention. Merge a reviewed pull request
client-side, which also removes the head branch without depending on repository
settings:

```
gh pr merge <number> --squash --delete-branch
```

Auto-merge was disabled on 2026-10-05. Re-enabling it needs the concrete
repeated failure mode and separate security review that
[automation-identities.md](automation-identities.md) describes, recorded in
[control-justification-ledger.md](control-justification-ledger.md).

See [codex-regression.md](codex-regression.md) for artifacts, grading, and the
current evidence boundary.

### Dependency pull request backlog

Two dependabot pull requests sat mergeable for twelve days in September 2026.
Nothing was red: the checks passed, the pull requests were mergeable, and the
scheduled run reported success. What made the stall invisible is that a stale
pull request produces no failing signal, and Dependabot's
`open-pull-requests-limit` then quietly blocks the next update while reporting
success.

`scripts/check-dependency-backlog.py` closes that gap. On the weekly schedule it
comments on each dependency pull request at or over seven days old and fails the
run. The comment is for whoever reviews the pull request; the non-zero exit is
what notifies the owner, and a failed scheduled run needs no notification
configuration. The comment is rewritten in place through a marker rather than
added again each week.

Run it locally to see the report without posting anything:

```
python3 scripts/check-dependency-backlog.py --days 7
```

Flags: `--post` writes the comment, `--days N` changes the threshold, and
`--repo OWNER/NAME` overrides repository resolution. Exit codes follow the
repository convention: `0` clean, `1` findings, `2` could not run.

Do not add this to the fast verification checklist. It queries the GitHub API, so
it is a scheduled staleness check like `verify-urls.py`,
not a local check. Its `--self-test` is offline and already runs under
`validate-scripts.py`.

## Distribution

This repository does not run a release cadence. `main` is the distribution
channel: clone it, or install from it with the Skills CLI.

```bash
npx skills add CodeSigils/repo-health-scan \
  --skill repo-health-scan --agent codex --copy --yes
```

Use `--agent claude-code` for Claude Code. The install resolves the repository's
default branch, so a merged pull request updates distribution. That is why no
release workflow or historical release/tag marker exists: `skills.sh` indexes
the default branch, so a tag would not change what installers receive.

### Smoke-testing a change

Confirm an install in an isolated temporary directory for each claimed host
after a change to the payload, layout, or install documentation:

```bash
install_dir="$(mktemp -d)"
cd "$install_dir"
npx skills add CodeSigils/repo-health-scan \
  --skill repo-health-scan --agent codex --copy --yes
test "$(find .agents/skills -type f -name SKILL.md | wc -l)" -eq 1
```

Repeat with `--agent claude-code` and verify
that `.claude/skills/` contains exactly one `SKILL.md`. Record the CLI version,
source commit, installed path, and result in the compatibility report.

## How the skill works

The skill runtime is a single SKILL.md with no shipped scripts and no build
process. The `docs/references/` files are maintainer-only and are not installed.
The agent discovers repo characteristics at runtime
using tools already on PATH (`git`, `shellcheck`, `python3`, `gh`).

Changes to the methodology go directly into `skills/repo-health-scan/SKILL.md`.
There is no sync step, no payload regeneration, and no duplicate reference
copies to maintain.

Root `AGENTS.md` is a routing adapter, not a second maintainer guide. It points
repository-health work to `SKILL.md` and repository changes to this file.

## Source ownership

Keep one authoritative home for each kind of information. The root
[README](../README.md) contains the user-facing overview and full repository
tree; this table identifies where maintainers should make changes:

| Concern                                        | Authoritative location                                                  |
| ---------------------------------------------- | ----------------------------------------------------------------------- |
| Runtime audit methodology                      | `skills/repo-health-scan/SKILL.md`                                      |
| Maintainer workflow and distribution procedure | `docs/MAINTENANCE.md`                                                   |
| Architecture decisions                         | `docs/decisions.md`                                                     |
| Portability and compatibility claims           | `docs/portability-contract.md` and `docs/compatibility-reports/`        |
| Public claim-to-evidence mapping               | `docs/claim-evidence-matrix.md`                                         |
| Maintainer evaluation references               | `docs/references/`                                                      |
| Model regression behavior and evidence         | `docs/codex-regression.md` and `evals/`                                 |
| Deterministic validation                       | `scripts/`, `schemas/`, and `.github/workflows/ci.yml`                  |
| Packaging metadata                             | `.codex-plugin/plugin.json`, `CITATION.cff`, and `SKILL.md` frontmatter |

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
