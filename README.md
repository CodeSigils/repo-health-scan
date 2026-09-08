# Repo Health Scan

[![CI](https://github.com/CodeSigils/repo-health-scan/actions/workflows/ci.yml/badge.svg)](https://github.com/CodeSigils/repo-health-scan/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/CodeSigils/repo-health-scan?label=release)](https://github.com/CodeSigils/repo-health-scan/releases)
[![skills.sh](https://skills.sh/b/codesigils/repo-health-scan)](https://skills.sh/codesigils/repo-health-scan/repo-health-scan)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Repo Health Scan** — audits any git repository for release readiness,
maintenance drift, and handoff health. The agent discovers the repo's
shape, infers what invariants matter, and reports findings with concrete
harm and remediation.

This skill handles pre-release audits, unfamiliar-repo onboarding,
dormant-repo revival, CI failure triage, and AI-assisted commit review.
Works on any git repository — Python, Rust, shell, docs-only, or monorepo.

It does **not** ship hardcoded checklists, runtime scripts, or reference
files. Pair it with
[`repo-architecture-skill`](https://github.com/CodeSigils/repo-architecture-skill)
for skill-repository structure, payload, and distribution boundaries, and with
[`py-review-skill`](https://github.com/CodeSigils/py-review-skill) for
dedicated Python code review.

The shipped payload is one `SKILL.md` — no agent-specific commands or
paths — so it works with any terminal-capable coding agent. It is
agentskills.io-compatible.

**Compatibility status:** Codex CLI 0.149.0 is the only verified agent target.
The `SKILL.md` payload is designed to be portable, but other agents are not
supported claims until they have their own recorded compatibility tests.

---

## How it works

1. **Load the skill** via your agent's skill system.
2. **Point the agent at a repo** (any git repo, any language, any ecosystem).
3. The agent runs three steps — discover → infer → report — and reports
   what it finds with judgment proportional to actual harm.

See [SKILL.md](skills/repo-health-scan/SKILL.md) for the full three-step procedure.

---

## Candidate Dimensions

The agent activates only relevant checks from this catalog — not a universal checklist:

| Dimension                 | Activated When                               |
| ------------------------- | -------------------------------------------- |
| History hygiene           | Always (cheap, universal)                    |
| Shell correctness         | Any `.sh` files exist                        |
| Version alignment         | ≥2 version sources found                     |
| Tag/release integrity     | Any tags exist                               |
| Commit quality            | Commits on this branch                       |
| CI efficiency             | CI config exists                             |
| Cross-platform            | `.sh` files + macOS/BSD user evidence        |
| Attribution drift         | Commits outside upstream/remote-default base |
| File coverage             | `.gitignore` exists                          |
| External reference health | `REPO_HEALTH_VERIFY_REFS=1` set              |

*Not a checklist — the agent may add custom dimensions when repo evidence supports them.*

---

## Install

Clone this repo and make the skill discoverable:

```bash
git clone --filter=blob:none https://github.com/CodeSigils/repo-health-scan
```

For skills.sh-compatible installation, use the Skills CLI and select the
portable skill for the target agent:

```bash
npx skills add CodeSigils/repo-health-scan \
  --skill repo-health-scan --agent codex --copy --yes
```

Use `--agent claude-code` for Claude Code. The repository is indexed by the
`skills/<directory>/SKILL.md` layout; no npm package or root `SKILL.md` is
required. The skills.sh detail page is
`https://skills.sh/codesigils/repo-health-scan/repo-health-scan`; the repository
landing page is `https://skills.sh/codesigils/repo-health-scan`. The badge
currently reports one indexed skill/install; skills.sh may show a dash on the
individual skill page until its per-skill history is populated.

For repository-local Codex use, place the skill under `.agents/skills/`:

```bash
mkdir -p .agents/skills
cp -r skills/repo-health-scan .agents/skills/
```

Codex discovers repository skills from `.agents/skills/`. For reusable
distribution, this repository includes `.codex-plugin/plugin.json`. The tested
repository-local and marketplace procedures are in the
[Codex setup guide](docs/codex-setup.md); exact test evidence is recorded in the
[Codex compatibility report](docs/compatibility-reports/codex.md).

Other agents may be able to consume the portable `SKILL.md`, but installation,
discovery, and workflow behavior remain unverified. Platform-specific setup
instructions will be added only with a matching compatibility report. The
[skill portability contract](docs/portability-contract.md) defines the claim
levels and evidence required before support is advertised.

---

## What this repo does NOT include

| Excluded                | Reason                                                                                                                       |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Hardcoded checklists    | The agent discovers what to check from the repo itself, not from a pre-written table.                                        |
| Reference files         | Every fact the skill needs is discovered at runtime (tools on PATH, repo state, filesystem).                                 |
| Shipped runtime scripts | The agent uses `git`, `shellcheck`, `python3`, `gh`, and whatever else is on PATH.                                           |
| Install scripts         | Every platform provides native skill consumption paths. A script would compete and drift.                                    |
| Platform adapter files  | User-side setup only. The repo ships only `skills/repo-health-scan/SKILL.md`.                                                |
| Runtime plugin code     | The Codex plugin manifest points at the skill directory; it does not add runtime scripts, hooks, MCP servers, or connectors. |

---

## Dependencies

None shipped with the skill payload. The skill expects the agent to have
access to general-purpose tools already on PATH: `git`, `shellcheck`,
`python3`, and optionally `gh`. If a tool is absent, the agent skips that
dimension and reports the gap.

The Python and shell files under `scripts/` are maintainer-only checks for
this repository's CI and documentation. They are not installed as skill
runtime helpers and should not be copied into `skills/repo-health-scan/`.

The optional [Codex model regression](docs/codex-regression.md) runs positive
and negative prompts against an isolated fixture. It is manual or scheduled,
uses a read-only sandbox, and does not block ordinary pull requests.

---

## Per-project configuration

Add a `.repo-health.json` at the repo root to override the agent's
heuristic discovery — declare which checks to skip, which version sources
to use, or a custom consistency check.

Optional behavior is explicit:

| Variable                        | Effect                                                       |
| ------------------------------- | ------------------------------------------------------------ |
| `REPO_HEALTH_VERIFY_RELEASES=1` | Allow the GitHub release query for tag/release integrity.    |
| `REPO_HEALTH_VERIFY_REFS=1`     | Allow network checks for external references.                |
| `REPO_HEALTH_OUTPUT=jsonl`      | Emit automation-oriented JSONL instead of the normal report. |

---

## Skill Payload — What Ships to the User

Only the `skills/` directory is the runtime payload. Everything else is
development infrastructure — scripts, CI, docs, evals, plugin manifests.

```text
skills/
└── repo-health-scan/
    └── SKILL.md      # 3-step methodology — discover, infer, report
```

The runtime payload is one file: `SKILL.md`. Maintainer-only evidence and
templates live under `docs/references/`; they are not copied into an agent's
installed skill directory and are not runtime dependencies.
The methodology contains inline command examples the agent executes using
`git`, `shellcheck`, `python3`, `gh` already on PATH. Copy only
`skills/repo-health-scan/` to your agent's skill directory (see
Install above).

---

## Project structure

```text
├── .github/
│   ├── dependabot.yml               # Weekly GitHub Actions updates
│   ├── release.yml                  # Generated release-note categories
│   └── workflows/
│       ├── ci.yml                    # Deterministic CI pipeline
│       ├── codex-regression.yml      # Non-blocking model evaluation
│       └── release.yml               # Validated GitHub release creation
├── .codex-plugin/
│   └── plugin.json                   # Codex plugin manifest
├── .gitattributes                    # Git text normalization and Linguist overrides
├── .gitignore                        # Python, OS, and editor artifact ignore rules
├── AGENTS.md                         # Repository-level agent routing
├── CITATION.cff                      # Citation metadata for academic reference
├── LICENSE                           # MIT license text
├── pyproject.toml                    # Non-package maintainer environment
├── uv.lock                           # Exact transitive dependency lock
├── README.md                         # Project documentation and usage guide
├── repo-health-skill-roadmap.md      # Development roadmap and future plans
├── SECURITY.md                       # Security policy and vulnerability reporting
├── schemas/                          # Versioned JSON schemas for optional interfaces
│   ├── dimension-plan.schema.json
│   ├── repo-health-config.schema.json
│   ├── repo-health-findings.schema.json
│   └── repo-health-profile.schema.json
├── docs/                             # Maintainer documentation
│   ├── README.md                     # Document index and navigation
│   ├── codex-setup.md                # Verified Codex repository-local and plugin setup
│   ├── codex-regression.md           # Non-blocking model regression harness docs
│   ├── portability-contract.md       # Cross-agent portability guarantees
│   ├── compatibility-reports/
│   │   └── codex.md                  # Compatibility evidence for Codex CLI
│   ├── maintaining.md                # Release and maintenance procedures
│   ├── automation-identities.md       # Bot authority and review boundaries
│   ├── decisions.md                  # Architecture decision records
│   ├── evidence-urls.json            # External URL inventory for verification
│   ├── research.md                   # Design research and ecosystem analysis
│   └── doc-standards.json            # Documentation quality and style rules
├── evals/
│   ├── cases/
│   │   └── repo-health-scan.json     # Local behavioral contract for the skill
│   └── codex/                        # Model prompts and output schema for regressions
│       ├── negative-prompt.md        # Prompt that should trigger skip behavior
│       ├── positive-prompt.md        # Prompt that should trigger full scan
│       └── positive-result.schema.json  # Expected output schema for positive case
├── scripts/                          # CI-only tooling (not shipped)
│   ├── check-expiry.py               # Scans for expired doc and config references
│   ├── check-portability.py          # Validates no agent-specific references in skills
│   ├── check-trust.py                # Validates security and trust contract
│   ├── check-version-consistency.py  # Checks version alignment across manifests and tags
│   ├── doc-audit.py                  # Manifest-driven doc completeness checker
│   ├── extract-tests.py              # Extracts test fixtures from script docstrings
│   ├── grade-codex-transcript.py     # Grades Codex regression artifacts deterministically
│   ├── run-codex-regression.py       # Runs isolated Codex skill regressions
│   ├── validate-evals.py             # Validates eval contract structure
│   ├── validate-scripts.py           # Validates script quality conventions
│   ├── verify.sh                     # Repository structure consistency check
│   └── verify-urls.py                # Checks external URL references are reachable
├── skills/
│   └── repo-health-scan/
│       └── SKILL.md                  # The shipped runtime skill
├── docs/
│   └── references/                   # Maintainer-only evidence and templates
```

---

## Design principles

**The repo tells you what it needs.** Do not bring expectations. Every
repo is different — the methodology discovers the shape before forming
judgments.

**Every invariant traces to a concrete failure.** If you cannot describe
the harm a broken invariant would cause, the check is speculative. Skip it.

**Run once, observe broadly.** One `ls`, one `find`, one `git log`
should give you the repo's shape. Do not chain five commands to
confirm what the first two already showed.

**Write the profile before the checks.** If you don't know the repo's
languages, tools, commit culture, and CI system, you cannot meaningfully
assess its health. Step 1 is not optional.

**The right number of checks is the one the repo needs, not the
one the skill defines.**

**Audit without leaking.** Secret checks emit counts, status, or locations —
never raw credential values or unredacted commit-message contents. Ignored and
tracked state are separate: `.gitignore` cannot protect a file already in Git.

---

## See also

- [Codex compatibility report](docs/compatibility-reports/codex.md) — tested
  version, installation evidence, and workflow results
- [Codex setup guide](docs/codex-setup.md) — repository-local and plugin setup
- [Codex model regression](docs/codex-regression.md) — isolated runner, grader,
  and non-blocking workflow
- [Skill portability contract](docs/portability-contract.md) — canonical
  payload, thin adapters, and per-runtime certification
- [Growth roadmap](repo-health-skill-roadmap.md) — verified scope and ordered
  follow-ups
- [Maintainer guide](docs/maintaining.md) — repository verification and release
  workflow
- [CodeSigils/agents-markdown-formatter](https://github.com/CodeSigils/agents-markdown-formatter) — GFM/MDX formatter with structural guards

---

## License

MIT — see [LICENSE](LICENSE).
