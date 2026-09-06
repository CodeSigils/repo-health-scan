# Decisions — Repo Health Scan (v0.3.0)

This decision record also captures post-release maintenance decisions; the
release version in the title identifies the methodology baseline, not a claim
that every entry was made before the release.

**Purpose:** Records the design decisions that shaped the current methodology.
The skill itself is `skills/repo-health-scan/SKILL.md`. Research
evidence that informed these decisions is in `docs/research.md`.

---

## Methodology over checklist

**Decision:** Ship a three-step methodology (discover repo shape → infer what
invariants matter → verify at runtime). Do not ship a hardcoded B-phase
checklist.

**Why:** Every repo is different. A 200K-line monorepo with 5 package managers
needs different checks than a 12-line shell script. The agent decides what to
check based on what the repo profile reveals, not from a lookup table. This
matches every major ecosystem repo (addyosmani/agent-skills, openai/skills,
wondelai/skills) — none ship checklists.

**Evidence:** Ecosystem survey of 6 top-starred skill collections; study note
on 6 cross-project patterns (§ Methodology over Collection).

---

## Runtime discovery over reference tables

**Decision:** Do not ship reference tables as part of the runtime skill
payload. The agent discovers repository facts at runtime using tools on PATH.

**Why:** The v0.1.0 design shipped 14 reference files as lookup tables for
detection heuristics, portability patterns, and co-author guard procedures.
These went stale as tools, paths, and conventions evolved. Runtime discovery
uses the repo's actual filesystem state and the tools on PATH — it stays
current between maintainer edits. Self-proving drift: the agentskills.io
Showcase page cycled 404→200→404 within 4 hours. A reference file claiming
it was 404 would have been wrong within hours.

**Evidence:** Hub marketplace research (skill-discovery docs); skill-discovery
durable findings § drift self-proof.

---

## No runtime scripts in the payload

**Decision:** The runtime payload uses general-purpose tools directly (`git`,
`shellcheck`, `python3`, `gh`) rather than requiring wrapper scripts. The
repository may still contain maintainer-only scripts for CI, schema validation,
documentation audits, and regression grading.

**Why:** The v0.1.0 design shipped a Python checker for commit trailers and
commit body format, plus a shared verification script. Those runtime helpers
duplicated functionality already available via `git log`, `shellcheck`, and
`python3`. Keeping the distinction explicit lets maintainers test and package
the project without making those helpers a dependency of the installed skill.

**Evidence:** Ecosystem structural survey (2026-07-12 study note). All 6
surveyed repos ship zero runtime scripts.

---

## Portability Is Verified Per Agent

**Decision:** Keep the skill methodology free of agent-specific commands and
config paths, but do not declare blanket compatibility in `SKILL.md`
frontmatter. Record installation and workflow evidence in per-agent
compatibility reports.

**Why:** The methodology uses only `find`, `git`, `shellcheck`, `python3`, `gh`,
and standard shell commands, so terminal-capable coding agents are plausible
targets. Discovery, packaging, tool availability, and
instruction-following behavior vary by agent. Portability of the text does not
prove end-to-end support.

**Evidence:** The current Codex skill validator rejects `compatibility` as an
unsupported frontmatter key. Codex installation, implicit discovery, and
workflow behavior are tracked in `docs/compatibility-reports/codex.md`; other
agents remain unverified.

The normative claim levels, adapter boundary, and evidence requirements are
defined in `docs/portability-contract.md`.

---

## CI API Authentication Is Separate From Commit Signing

**Decision:** Pass the job-scoped `${{ github.token }}` to GitHub CLI as
`GH_TOKEN` for release queries. Keep SSH commit and tag signing as a separate
provenance policy.

**Why:** `gh release list` calls the GitHub API and needs API authorization.
An SSH signature proves who signed a git object; it does not authorize API
requests. The workflow grants only `contents: read`, which is sufficient for
the read-only release query and keeps the token scoped to the job.

**Evidence:** GitHub's `GITHUB_TOKEN` authentication guide explicitly configures
GitHub CLI through `GH_TOKEN`. GitHub's signing documentation describes SSH as
a mechanism for cryptographically signing commits and tags. Sources accessed
2026-07-13:

- https://docs.github.com/en/actions/tutorials/authenticate-with-github_token
- https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits

---

## Single-file payload

**Decision:** `skills/repo-health-scan/SKILL.md` is the only runtime
payload file. Maintainer documentation, references, schemas, CI configuration, and test
scripts remain in the repository but are not required by an installed skill.

**Why:** A methodology that fits in one file is consumed immediately — the
agent reads it once and applies it. Multi-file runtime payloads add loading
overhead and create another drift surface. The repository therefore keeps
supporting material for maintainers while installing only the portable
`SKILL.md`.

**Evidence:** Structural survey of 6 CodeSigils repos vs 6 ecosystem repos
(2026-07-12 study note). The ecosystem consistently ships minimal payloads.

---

## Proportionate checking

**Decision:** The agent checks only dimensions that the repo profile reveals
as relevant. No universal checklist, no mandatory PASS/FAIL for every step.

**Why:** Running a version-alignment check on a repo with no version sources
wastes agent context and produces false negatives. Running a CI-efficiency
check on a repo with no CI config is noise. The methodology's Step 1
(discover shape) gates Step 2 (infer invariants) — only dimensions that
the repo profile shows as active are checked.

**Evidence:** v0.1.0 B0 principle "detect, don't enforce." Observed during
dogfooding: the old B-phase would emit WARNINGs for dimensions that didn't
apply, consuming the agent's attention on noise.

---

## Judgment over labels

**Decision:** The agent reports findings with context and harm assessment,
not pre-defined PASS/WARNING/BLOCKING labels.

**Why:** The old architecture used a fixed severity scale (PASS / WARNING /
BLOCKING) that couldn't account for project context. A loose `.gitignore`
in a solo personal project is less harmful than the same issue in a
multi-contributor open-source repo. The methodology's Step 3 instructs
the agent to use language that reflects actual harm ("This causes silent
failure when...") rather than a severity class that repeats on every report.

**Evidence:** Observed during dogfooding: B-phase reports would flag the
same items as WARNING regardless of the repo's stage or audience, wasting
the maintainer's attention on items that didn't need action.

## v0.3.0 consolidation and later contract hardening

**Decision:** Keep the methodology profile-first and proportionate while
making the observable runtime contract explicit. The current contract requires
core profile fields, allows extended fields when evidence exists, requires
activation evidence for dimensions, and supports redacted JSONL findings.

**Why:** Regression runs showed that an implicit profile shape was too fragile:
models could omit the evidence needed to justify a dimension or invent paths.
The explicit contract improves grading and audit reproducibility without turning
the skill into a universal checklist.

**Changes:**

- Added core/extended profile fields and exact-path evidence rules.
- Added schema-backed dimension-plan and findings contracts.
- Kept network and release verification opt-in and read-only.
- Added portable version-source parsing guidance and explicit tool-absence skips.
- Restricted version alignment to release-relevant metadata and accepted
  unquoted CFF/YAML version values.
- Used Git's tracked/non-ignored file set for manifest discovery, with a
  pruned filesystem fallback for non-Git repositories; release-file evidence
  remains separate from ordinary CI workflows.
- Treated scanner/test/fixture matches as heuristic candidates until native
  scanner results and non-secret context confirm a credential.
- Recorded Codex runtime certification separately from the release version.

The v0.1.0 B-phase design and its shipped helper/reference files remain
historical and are available in git history. Current repository structure and
validation commands are documented in `docs/maintaining.md` and `README.md`.

---

## Defer profile modules by default

**Decision:** Do not add release, agent, monorepo, security, or documentation
profile modules to the runtime payload yet.

**Why:** The consolidated core already expresses the observed repository
shapes, and three clean, time-separated runs (13–15) passed on Codex CLI
0.153.2. No captured failure requires module-specific fields or checks. Adding
modules now would increase prompt surface and maintenance cost without an
evidence-backed user benefit.

**Reopen when:** A real audit failure shows that the core profile cannot
represent necessary evidence, or a repeatable use case demonstrates that one
module materially improves finding quality. Any approved module must be added
alone with a bounded field budget, deterministic fixture, validator coverage,
and a fresh regression baseline.
