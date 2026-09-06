# `repo-health-scan` Growth Roadmap

**Status:** Codex-first development

**Last reconciled:** 2026-09-06

This roadmap is based on the current repository, recorded compatibility tests,
official platform documentation, and the research sources listed below. It
separates completed foundation work, ordered Codex follow-ups, and deferred
cross-agent expansion so completed tasks do not remain disguised as open work.

---

## 1. Product Direction

`repo-health-scan` is a read-only methodology for terminal-capable coding
agents. It discovers repository shape, infers relevant invariants, and reports
concrete harm and remediation without applying a universal checklist.

Its primary value is as an **agent reasoning protocol**: it makes discovery,
dimension selection, skip decisions, and reporting observable. It is not a
general-purpose scanner and does not replace tests, linters, dependency or
security scanners, package-manager checks, or an experienced maintainer's
repository knowledge. Its highest-value contexts are unfamiliar repositories,
release and handoff audits, and AI-assisted maintenance that benefits from a
repeatable review structure.

The three-step contract is now observable in Codex:

1. Discover and emit a structured repository profile.
2. Select dimensions using explicit evidence from that profile.
3. Report only relevant findings with concrete harm and remediation.

Codex is the only active compatibility target. Other agents remain potential
targets, not verified support claims.

Current product assessment:

- The profile-first and evidence-linked planning contract is useful and
  differentiates the skill from a generic health checklist.
- The payload was consolidated from 492 to 415 lines while retaining inline
  probes and the complete security contract. Its remaining size is dominated by
  operational examples rather than repeated rationalizations and checklists.
- The ten dimensions behave as an evidence-activated candidate catalog. Calling
  the method "not a checklist" without that qualification overstates the
  distinction.
- The skill is useful guidance, not an executable guarantee. Agent-interpreted
  `.repo-health.json` and JSONL interfaces need tighter contracts before they
  should be treated as stable automation surfaces.
- Profile growth is not the next milestone. Core clarity, fixture diversity,
  regression observability, and reliability take precedence.

---

## 2. Evidence Baseline

| Evidence                                                                                                                                                                                                                                                                  | Decision Supported                                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| OpenAI plugin documentation requires `.codex-plugin/plugin.json` and supports a plugin-root-relative `skills` path.                                                                                                                                                       | Keep Codex packaging separate from the portable `SKILL.md` payload.                                                                                                      |
| OpenAI skill documentation describes metadata-first discovery and progressive disclosure.                                                                                                                                                                                 | Keep trigger language precise and the loaded skill concise.                                                                                                              |
| The 2026-07-13 isolated Codex transcript selected the unnamed skill prompt and loaded the installed payload.                                                                                                                                                              | Treat implicit Codex discovery as verified for CLI 0.133.0.                                                                                                              |
| The 2026-07-13 conformance retest emitted the profile and evidence-linked dimension plan before health checks.                                                                                                                                                            | Treat the core Codex workflow as verified and preserve it with deterministic evals.                                                                                      |
| Current Codex skill validation rejects the blanket `compatibility` frontmatter field.                                                                                                                                                                                     | Record compatibility per agent instead of declaring `compatibility: all`.                                                                                                |
| GitHub documents `GH_TOKEN` for GitHub CLI API access in Actions and SSH/GPG/S/MIME for commit or tag signing.                                                                                                                                                            | Keep CI API authorization separate from git provenance policy.                                                                                                           |
| Repository-context research warns that excess context can increase cost or reduce task performance.                                                                                                                                                                       | Consolidate the existing payload before adding fields or modules; any later profile growth requires strict evidence and budgets.                                         |
| Addy Osmani's `agent-skills` keeps shared `SKILL.md` workflows alongside substantial repository-level `AGENTS.md` and `CLAUDE.md` instructions, per-agent setup guides, and separate platform manifests. Its root `plugin.json` is identified as an Antigravity manifest. | Reuse the source-ownership principle, not a presumed universal three-file contract. Add only adapters required by a selected platform and keep their scope explicit.     |
| The AGENTS.md specification describes one repository instruction file consumed by Codex, Cursor, OpenCode, GitHub Copilot, and other agents.                                                                                                                              | Use a concise root `AGENTS.md` for repository routing without treating its presence as runtime compatibility evidence.                                                   |
| Skills CLI 1.5.16 discovers `skills/<name>/SKILL.md` directly and lists Codex, Cursor, OpenCode, GitHub Copilot, and Hermes installation targets. An isolated local `--list` check found exactly `repo-health-scan` without root `plugin.json`.                           | Treat skills CLI discovery as verified independently of agent execution; do not add duplicate root metadata for this path.                                               |
| Skills CLI 1.5.16 again discovered `repo-health-scan` from the published repository with `npx skills add CodeSigils/repo-health-and-sync-skill --list`.                                                                                                                   | Keep the `skills/<directory>/SKILL.md` layout, document the skills.sh install form, and verify copied installs for each claimed host.                                    |
| Claude Code reads `CLAUDE.md`, not `AGENTS.md`, and officially supports importing `AGENTS.md` with `@AGENTS.md`.                                                                                                                                                          | If Claude Code becomes active, use an import adapter instead of duplicating repository instructions.                                                                     |
| Official Codex non-interactive guidance documents `codex exec --json`, ephemeral sessions, explicit sandboxes, and machine-readable output schemas.                                                                                                                       | Use raw JSONL locally and a schema-constrained final result for deterministic grading.                                                                                   |
| Official Codex GitHub Action guidance keeps the API key behind a proxy and supports read-only execution on trusted triggers.                                                                                                                                              | Retain the official Action as optional infrastructure for maintainers with API-key billing; never make it a prerequisite for local evaluation or repository exploration. |
| Two local regressions passed with 153,545 and 136,050 input tokens; a third produced partial model output and timed out after 15 minutes.                                                                                                                                 | Treat model cost and stalls as product evidence, improve run observability, and do not expand the instruction surface yet.                                               |

Primary sources and research, accessed 2026-07-12 or 2026-07-13:

- https://learn.chatgpt.com/docs/build-plugins
- https://learn.chatgpt.com/docs/build-skills
- https://developers.openai.com/codex/noninteractive
- https://developers.openai.com/codex/github-action
- https://docs.github.com/en/actions/tutorials/authenticate-with-github_token
- https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits
- https://github.com/addyosmani/agent-skills
- https://agents.md/
- https://github.com/vercel-labs/skills
- https://code.claude.com/docs/en/memory
- https://arxiv.org/abs/2607.01456
- https://arxiv.org/abs/2605.11418
- https://arxiv.org/abs/2607.00911
- https://arxiv.org/abs/2606.17819
- https://arxiv.org/abs/2602.11988
- https://arxiv.org/abs/2606.14066

---

## 3. Current State

### Verified

| Area                       | Evidence                                                                                                                                                                                  |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Skill schema               | Current Codex skill validator passes. Frontmatter contains supported fields only.                                                                                                         |
| Codex packaging            | The v0.3.0 plugin manifest validates. The recorded isolated marketplace installation is historical v0.2.0 evidence and should not be described as a reproduced v0.3.0 install.            |
| Codex discovery            | An unnamed release-audit prompt selected `repo-health-scan` and loaded the installed skill.                                                                                               |
| Codex workflow             | The isolated retest emitted the profile and complete dimension plan before probes; all active checks cited profile evidence.                                                              |
| Codex setup                | The focused guide was reproduced from a clean isolated `CODEX_HOME`; the historical v0.2.0 plugin installation and implicit discovery passed.                                             |
| Final reporting            | The full audit produced a structured final profile, concrete harm, remediation, and correct payload/tooling classification.                                                               |
| Probe correctness          | Dirty-tree, TOML/JSON version parsing, attribution range, and command-block examples were corrected and smoke-tested.                                                                     |
| Runtime boundary           | The shipped payload is one `SKILL.md`; Python and shell scripts are maintainer-only.                                                                                                      |
| Repository routing         | Root `AGENTS.md` routes health-audit intent to `SKILL.md`, routine maintenance to `docs/maintaining.md`, and explicitly excludes narrow implementation work.                              |
| Skills CLI discovery       | Skills CLI 1.5.16 found exactly `repo-health-scan` from the local `skills/` tree with `npx --yes skills add <repo> --list`; no root manifest was required.                                |
| skills.sh distribution     | README documents `npx skills add` for Codex and Claude Code; the skills.sh badge and install smoke matrix remain lightweight distribution evidence.                                       |
| Eval contract              | `evals/cases/repo-health-scan.json` covers positive/negative triggers, this skill pack, and a Python library using `uv`.                                                                  |
| Eval validation            | `scripts/validate-evals.py` enforces profile-first ordering, activation evidence, skip reasons, fixture diversity, and the complete observed profile field set.                           |
| Security and trust         | `scripts/check-trust.py` enforces bounded triggers, read-only instructions, opt-in network/output behavior, credential hygiene, versioned compatibility evidence, and payload separation. |
| Secret scanning            | Skill scans `.gitignore`, commit metadata, and tracked files for heuristic secret patterns; output is limited to counts/paths and includes a redaction guard.                             |
| Audit hardening            | Repository audits streamlined; coverage gaps closed; portability scanner fixed; expiry checker wired. Evidence: commits `1aef227`, `a54272b`, `988322d`.                                  |
| Release consistency        | The checker validates `SKILL.md`, plugin metadata, `CITATION.cff`, tags, and GitHub releases. Strict CI queries use a read-only job token.                                                |
| CI and merge governance    | CI runs on every pull request without path filters; `lint`, `full-verify`, and `phase-b-gate` are required on `main`, with one approval, conversation resolution, and signed commits.     |
| Release workflow hardening | Tagged releases verify the exact CI commit and required jobs; reruns are idempotent when a GitHub Release already exists.                                                                 |
| Repository verification    | Script self-tests, Ruff, ShellCheck, documentation audit, plugin validation, skill validation, and diff checks pass independently.                                                        |
| Evidence URL tracking      | `docs/evidence-urls.json` upgraded to v3 schema with status, source_type, domain_tag, and last_verified fields. All 11 URLs verified reachable.                                           |
| Local model regression     | Ten Codex runs are recorded: seven passes, one timeout, and two deterministic grading failures. Run 10 passed the revised payload on Codex CLI 0.149.0.                                   |

### Remaining Gaps

| Gap                                                                                                                                      | Consequence                                                                                                                             | Priority |
| ---------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Ten local runs are recorded, but the payload changed across recent runs and several were same-session.                                   | The 70% historical pass rate is diagnostic; the current 0.149.0 payload has one passing run and needs time-separated repeated evidence. | High     |
| `.repo-health.json` and JSONL are optional maintainer-side contracts.                                                                    | Schemas and graders now enforce profile completeness and redacted finding shape; cross-agent runtime conformance remains unverified.    | Low      |
| Deterministic fixtures cover six repository shapes, including a monorepo, docs product, missing tools, no `origin/main`, and dirty tree. | Broader real-world model evidence is still needed beyond deterministic fixtures.                                                        | Medium   |
| Current-version marketplace installation has not been reproduced in the compatibility report.                                            | Resolved: v0.3.0 installation evidence is recorded separately from historical v0.2.0 evidence.                                          | Resolved |
| Scheduled URL checks can fail when upstream references drift or are unavailable.                                                         | Keep URL verification scheduled/manual, retry transient failures, and do not make it a pull-request merge gate.                         | Ongoing  |

The hosted Codex Action is not a product gap. It requires API-key billing, which
is separate from the ChatGPT subscription used by the current maintainer's
authenticated local Codex CLI. Keep the workflow available as an optional path,
but do not use its unverified status to block local development, cloning, skill
discovery, or profile scaling.

### Current Decision Gate

The initial five-run evidence set is recorded and reviewed, but it is not a
stable baseline for one payload. An observed secret-exposure risk justified a
security change during the former freeze, and run 4 then exposed a JSONL versus
dimension ambiguity that was corrected before run 5. Freeze further
model-facing changes while collecting time-separated repeats of the hardened
payload. Maintainer documentation and fixes that preserve model-facing inputs
may continue.

The required sequence is:

1. **Completed:** record and review the initial five runs, preserving the
   timeout, grading failure, runtime, and token evidence.
2. Collect time-separated repeated runs for the hardened payload without
   changing model-facing inputs.
3. Consolidate the core methodology and contextual blocking behavior only if
   the baseline review supports proceeding.
4. Establish a fresh repeated baseline for the consolidated payload.
5. Formalize optional output contracts, broaden deterministic fixtures, and
   only then hold the profile-module go/no-go review.

Completing a baseline is an evidence gate, not an automatic instruction to
implement the next item. Any failed or stalled run must remain in the record and
inform the review.

---

## 4. Completed Milestone: Codex Workflow Conformance

**Result:** `workflow_verified` on Codex CLI 0.133.0.

`SKILL.md` now gives Step 1 and Step 2 an observable handoff:

- Require the agent to emit the structured `observed`/`inferred` profile before
  running any dimension-specific command.
- Require every active dimension to name at least one profile signal that
  activated it.
- Require an explicit skip reason for every candidate dimension that lacks
  activation evidence.
- Keep cross-platform checks inactive unless the profile contains a platform or
  user requirement.
- Keep attribution checks inactive when there are no commits outside the base
  branch or no attribution policy is present.
- Preserve read-only behavior and the distinction between shipped payload and
  maintainer-only tooling.

The isolated implicit Codex audit and its environment, prompt, selected skill,
profile event, dimension plan, findings, and deviations are recorded in
`docs/compatibility-reports/codex.md`.

Acceptance evidence:

- Implicit discovery still selects `repo-health-scan`.
- A structured profile appears in the transcript before the first dimension
  probe.
- Every active dimension cites profile evidence.
- Dimensions without evidence are skipped before probing.
- Findings retain concrete harm and remediation.
- No repository files are modified by the audit.
- The compatibility report status is `workflow_verified`.

---

## 5. Release Milestone and Ordered Follow-up

### 5.1 Completed: Release Current Codex Work

**Result:** `v0.3.0` published on 2026-07-13.

- Updated `SKILL.md`, `.codex-plugin/plugin.json`, and `CITATION.cff` together.
- Confirmed README describes the released behavior, Codex compatibility status,
  opt-in interfaces, and repository shape.
- Created a signed release commit and a new signed `v0.3.0` tag without moving
  `v0.2.0`.
- Published the matching GitHub release.
- Reran strict consistency and the full repository verifier successfully.

Acceptance met: local metadata, tag, GitHub release, and released plugin payload
all identify version `0.3.0`.

### 5.2 Implemented: Model-Driven Regression Harness

**Local result:** nine runs recorded on Codex CLI 0.133.0 through 2026-07-16:
six passes, one timeout, and two deterministic grading failures. The current
hardened payload has one passing run; see `docs/codex-regression.md` for the
full evidence and same-session caveat.

The harness now includes:

- An isolated Python/`uv` fixture with positive and negative prompts.
- A local `codex exec --json` runner that captures raw event streams and final
  responses while enforcing read-only, ephemeral execution.
- A deterministic grader for selection, raw profile/plan ordering,
  `activated_by` evidence, complete dimension accounting, skip behavior,
  seeded finding quality, severity ordering, and negative non-selection.
- A separate manual/weekly GitHub workflow using the official Codex Action and
  read-only safety strategy.
- Artifact and reliability documentation in `docs/codex-regression.md`.

First-run assertions:

- Positive skill selection and negative non-selection passed.
- The populated profile preceded the populated dimension plan.
- Every active dimension cited a valid profile path.
- All ten candidate dimensions were active or explicitly skipped.
- The seeded dirty-tree finding named the defect, harm, and remediation.

Local regression is the primary reliability path because it can use the current
maintainer's authenticated Codex CLI. The hosted workflow remains an optional
`pending_first_run` path for a future maintainer with API-key billing. Keep the
deterministic JSON eval as the fast CI layer and do not make ordinary pull
requests depend on model availability.

### 5.3 Implemented: Minimal Repository Routing

Root `AGENTS.md` now acts only as a repository adapter:

- It scopes itself to agents maintaining this source repository.
- It routes repository-health and release-readiness intent to the canonical
  `SKILL.md`.
- It preserves negative triggers for narrow fixes, feature work, single-file
  edits, and routine code review.
- It routes contributor workflow to `docs/maintaining.md` rather than copying
  commands or conventions.

An isolated skills CLI 1.5.16 check found exactly `repo-health-scan` directly
from `skills/`. This verifies repository discovery by that CLI, not execution,
automatic selection, or instruction adherence in any additional agent.

---

## 6. Deferred Work

These items are intentionally outside the current Codex-first milestone:

| Item                                                          | Resume When                                                                                                        |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Gemini, Claude Code, OpenCode, Cursor, or Hermes verification | Codex workflow conformance and setup are stable.                                                                   |
| Root `plugin.json` for Antigravity                            | Antigravity becomes an active target and its native manifest contract is tested.                                   |
| `CLAUDE.md` import adapter                                    | Claude Code becomes an active target; use `@AGENTS.md` unless verified Claude-specific instructions are necessary. |
| Additional per-agent setup guides and compatibility reports   | The relevant agent is selected as an active target and tested directly.                                            |
| `repo-sync` companion skill                                   | Scan findings and the human approval boundary are stable.                                                          |
| Organization-wide scanner and dashboard                       | Single-repository JSONL behavior is executable and evaluated, not only instructional.                              |
| Generic CI integration guide                                  | A real agent runtime and failure policy are selected.                                                              |
| Hosted Codex Action activation                                | A maintainer has API-key billing and wants scheduled GitHub-hosted model runs.                                     |
| `CHANGELOG.md`                                                | Release cadence makes a changelog more useful than GitHub release notes alone.                                     |

No deferred item should appear in README as verified support before its own
fixture or compatibility report exists. Apply the claim levels, thin-adapter
boundary, and runtime certification requirements in
`docs/portability-contract.md`; do not substitute a universal agent matrix for
per-target evidence.

---

## 7. Core Consolidation Gate and Deferred Profile Scaling

**Status:** profile modules are explicitly deferred.

The initial five-run evidence set does not automatically unlock profile modules,
especially because it spans payload changes. Before adding any module, complete
these gates in order:

1. **Completed:** regression observability records CLI and model identity when
   available, elapsed time, usage, last-event time, failure phase, and preserved
   first-attempt outcomes. This shipped in commit `f21214c`.
2. **Completed with caveat:** five runs now record observability and failure
   phases, but runs 4 and 5 were same-session and straddled a payload fix; treat
   them as diagnostic evidence rather than a stable repeated baseline.
3. Consolidate the core methodology while preserving the verified three-step
   contract. Target a 30-50% payload reduction where it can be achieved without
   weakening trigger boundaries, read-only behavior, profile-first ordering,
   activation evidence, skip accounting, or finding quality.
4. Describe the dimension table as a non-exhaustive candidate catalog, allow
   evidence-backed custom dimensions, make blocking contextual to the audit,
   continue safe read-only checks after finding a blocker, and state graceful
   behavior when an expected tool is unavailable.
5. Formalize small versioned contracts for the profile, dimension plan, JSONL
   findings, and `.repo-health.json`; keep schemas and validators as
   maintainer-side evidence rather than shipped runtime dependencies. **Done:**
   profile completeness, dimension accounting, and redacted finding fields are
   now enforced by the validators.
6. Add deterministic fixtures for a monorepo, documentation product, missing
   tools, no `origin/main`, and an intentionally dirty non-release workflow.
   **Done:** all six shapes are represented in the eval contract.
7. Because consolidation changes `SKILL.md`, establish a fresh repeated model
   baseline for the revised payload. Do not carry the v0.3.0 pass rate forward
   as proof of the new behavior.
8. Hold a documented go/no-go review for profile modules. The default outcome
   is continued deferral unless observed repository failures show that the
   compact core cannot represent necessary evidence.

The following design is retained for possible future use; it is not an approved
implementation milestone.

Keep the mandatory profile small:

```yaml
observed:
  languages:
  ci:
  package_managers:
  script_surface:
  shipped_payload:

inferred:
  repo_type:
  release_model:
  risk_context:
```

Activate optional modules only from Step 1 evidence:

| Module     | Activation Evidence                                                 | Maximum Fields |
| ---------- | ------------------------------------------------------------------- | -------------: |
| `release`  | Tag, changelog, registry, container, or release workflow.           |              6 |
| `agent`    | Skill, plugin manifest, or agent instruction file.                  |              6 |
| `monorepo` | Workspace manifest or multiple packages/services.                   |              6 |
| `security` | Security policy, scanning, permissions, secrets, or signing policy. |              6 |
| `docs`     | Documentation is the product or handoff risk is active.             |              6 |

Profile rules:

- Core profile target: 8-10 fields; hard cap: 12.
- Optional module target: 4 fields; hard cap: 6.
- Every optional field carries one evidence path or command result.
- Confidence is `observed`, `inferred-high`, `inferred-low`, or `unknown`.
- Unknown is valid; never invent a value to activate a check.
- Modules add questions, not mandatory PASS/FAIL dimensions.

If the later go/no-go review approves profile scaling, implement one module at a
time in the canonical `SKILL.md`, deterministic fixtures and validators, and
the model grader. Each module needs an observed activation use case, its own
field budget, and fresh regression evidence. Do not implement all five as one
surface expansion.

---

## 8. Priority Queue

| Order | Action                                                                                                                                                                      |                                     Effort | Impact |
| ----: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -----------------------------------------: | ------ |
|     1 | Collect time-separated local regression runs for the hardened payload without changing model-facing inputs. Preserve all first-attempt outcomes.                            |             Observation over multiple runs | High   |
|     2 | Review the hardened-payload pass rate, failure phases, runtime, token use, and evidence quality.                                                                            |                                    0.5 day | High   |
|     3 | If that review supports proceeding, consolidate `SKILL.md`, clarify the candidate-catalog and contextual-blocking contracts, and preserve the verified three-step behavior. |                                   1-2 days | High   |
|     4 | Establish a fresh repeated model baseline for the consolidated payload; do not reuse earlier rates as proof.                                                                |             Observation over multiple runs | High   |
|     5 | Formalize the optional interfaces and broaden deterministic fixture coverage against the stable consolidated contract.                                                      |                                   1-2 days | High   |
|     6 | Decide whether profile modules are justified. Keep them deferred by default; if approved, implement and evaluate one module at a time.                                      | Review, then 0.5-1 day per approved module | Medium |

Optional, unordered infrastructure: activate the hosted Codex Action only if a
maintainer later has API-key billing and wants GitHub-hosted scheduling. It is
not required to complete this queue. Non-Codex agent verification remains
deferred under Section 6 rather than competing with the Codex reliability path.

Completed foundation:

- Added regression run metadata, failure-phase reporting, and preserved-attempt
  summaries without changing the model-facing regression inputs (`f21214c`).
- Corrected methodology probes and structured profile.
- Added trigger-aware skill anatomy and valid Codex plugin packaging.
- Verified local plugin installation and implicit Codex discovery.
- Captured the first full workflow transcript and deviations.
- Verified profile-first Codex workflow conformance in an isolated read-only run.
- Added and executed the security/trust checklist as a local and CI gate.
- Reconciled README with Codex-only evidence and documented opt-in behavior.
- Added the focused Codex setup guide and reproduced it from an isolated home.
- Added deterministic eval fixtures and validation.
- Fixed dirty-tree verification.
- Enforced local/tag/release version consistency with strict CI API behavior.
- Removed unsupported blanket compatibility metadata.
- Published signed release `v0.3.0` with aligned skill, plugin, citation, tag,
  and GitHub Release versions.
- Added and locally verified the non-blocking Codex model regression runner,
  deterministic grader, isolated fixture, and trusted-trigger hosted workflow.
- Added runner-only timing, usage, last-event, artifact, and failure-phase
  summaries without changing model-facing regression inputs.
- Added a minimal root `AGENTS.md` that routes to canonical sources without
  duplicating methodology or maintainer instructions.
- Verified skills CLI 1.5.16 discovers the single skill directly from
  `skills/` without a root `plugin.json`.
- Added secret scanning: `.gitignore` secret pattern detection, commit body
  secret scanning, and report redaction guard (`92d7481`, `fa0b8f9`).
- Hardened repository audits: streamlined audit flow, closed coverage gaps,
  pinned `setup-python`, fixed portability scanner, wired expiry checker
  (`1aef227`, `a54272b`, `988322d`).
- Hardened CI and release governance: removed path-filter bypasses, moved commit
  convention checks into pull requests, required exact CI jobs for tags, made
  release reruns idempotent, and enabled protected-main requirements (`#6`–`#8`).
- Reconciled runtime-payload documentation: `SKILL.md` is installed; moved
  maintainer-only references from `skills/.../references/` to
  `docs/references/` so Skills CLI cannot package them as runtime resources.
- Added skills.sh badge and explicit Skills CLI installation guidance; kept the
  public skill name `repo-health-scan` while preserving the repository's
  existing directory name for backwards-compatible local installs.
- Completed `.gitignore` coverage: added `.hermes/`, `.gemini/`, `tmp/`,
  `.cache/`, `*.log`, virtualenv patterns (`5a01331`–`9575140`).
- Replaced dead NousResearch URL with canonical `github/gitignore`
  `Agents.gitignore` (`cb13205`).
- Upgraded `docs/evidence-urls.json` from v1 to v3 schema with status
  tracking, source_type classification, domain tagging, and ISO
  `last_verified` dates (`2402213`).

---

## 9. Constraints

1. The scan remains read-only and never becomes the fixer.
2. Repository evidence selects checks; the dimension table is a non-exhaustive
   candidate catalog, not a universal checklist.
3. Maintainer scripts never become required runtime payload implicitly.
4. Instruction-level JSONL and `.repo-health.json` remain labelled as contracts,
   not executable features.
5. Compatibility and installability claims require per-agent fixtures or
   reports.
6. External-facing decisions use current primary sources and record access
   dates; purely local command fixes use local tests.
7. API authorization and git provenance remain separate controls.
8. Profile growth remains frozen until core consolidation, expanded fixtures,
   and a fresh model baseline pass a documented go/no-go review.
9. Human approval separates scan findings from any future synchronization or
   repair workflow.
10. Repository instruction adapters improve source-checkout routing but do not
    establish installation, selection, or behavioral compatibility.
11. A material `SKILL.md` change starts a new behavioral evidence baseline;
    results for an older payload remain historical evidence only.
12. Cross-agent support follows `docs/portability-contract.md`: one canonical
    payload, thin platform adapters, deterministic structural checks, and
    compatibility claims certified per named runtime and version.
13. Keep the repository directory name `skills/repo-health-scan/`
    stable until the staged migration in [docs/rename-plan.md](docs/rename-plan.md)
    is approved; `repo-health-scan` remains the public skill identifier. A
    GitHub repository rename is a separate remote operation and must not be
    conflated with the local package-directory rename.

---

## 10. Near-Term Repository Shape

```text
repo-health-scan/
├── .codex-plugin/
│   └── plugin.json
├── .github/
│   ├── dependabot.yml              # github-actions auto-update
│   └── workflows/
│       ├── ci.yml                  # Deterministic CI pipeline
│       └── codex-regression.yml    # Non-blocking model evaluation
├── AGENTS.md                       # repository routing only
├── CITATION.cff
├── LICENSE
├── README.md
├── SECURITY.md
├── pyproject.toml                  # non-package maintainer environment
├── uv.lock                         # exact transitive dependency lock
├── repo-health-skill-roadmap.md
├── skills/
│   └── repo-health-scan/
│       └── SKILL.md
├── evals/
│   └── cases/
│       └── repo-health-scan.json
├── docs/
│   ├── codex-setup.md              # verified Codex setup
│   ├── references/                  # maintainer-only evidence and templates
│   ├── portability-contract.md     # cross-agent claim and adapter rules
│   ├── maintaining.md
│   ├── decisions.md
│   └── compatibility-reports/
│       └── codex.md
└── scripts/                        # maintainer-only validation
    ├── check-expiry.py
    ├── check-portability.py
    ├── check-trust.py
    ├── check-version-consistency.py
    ├── doc-audit.py
    ├── extract-tests.py
    ├── grade-codex-transcript.py
    ├── run-codex-regression.py
    ├── validate-evals.py
    ├── validate-scripts.py
    ├── verify.sh
    └── verify-urls.py
```
