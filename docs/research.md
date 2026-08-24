# Research — Repo Health Scan (v0.3.0)

**Purpose:** Evidence base that informed the current methodology design.
Contains ecosystem survey data, cross-platform consumption patterns, and
research findings. This file is the reference for *what was found*,
not *what was built* — decisions are in `docs/decisions.md`.

---

## 1. 17-project survey (ecosystem patterns)

17 top-starred projects across 9 language ecosystems inspected for: directory
structure, branch naming, tags, commit style, CI organization, scripts
directory, agent config files, agent instruction files, CHANGELOG approach,
and .gitattributes usage. This data shaped the methodology's design principles
(runtime discovery, proportionate checking).

### Survey snapshot

| Ecosystem | Projects | Shared traits |
| :-------- | :------- | :------------ |
| Go (3) | golang/go, kubernetes, prometheus | No agent configs; `.github/` for CI; commit styles vary within ecosystem |
| JS/TS (4) | react, vscode, next.js, express | **100% agent config adoption** — only ecosystem where all projects commit them |
| Python (3) | django, ansible, numpy | Most diverse CI platforms (GitHub, Azure, CircleCI); 1/3 has agent config |
| Ruby (2) | rails, Homebrew | Homebrew is reference for CI workflow organization (14 separate files) |
| Rust (1) | rust-lang/rust | Built-in toolchain formatting (rustfmt); no agent config |
| C/C++ (2) | torvalds/linux, nodejs | `.clang-format` universal; no agent configs |
| Shell (2) | ohmyzsh, nvm | **ohmyzsh has zero tags** — proves absence of tags is not a defect |

### Key findings

**KF1 — No single commit convention dominates.** 10 distinct commit styles
across 17 projects. Conventional Commits is the plurality (29%) but not the
majority. Homebrew explicitly rejects conventional commits via CI workflow.
The methodology teaches agents to observe the repo's actual commit style
before forming judgments — not to enforce one convention universally.

**KF2 — 29% of top projects commit agent configs.** 5/17 commit `.claude/`,
`.cursor/`, `.codex/`, `.agents/`, or `.vscode/` configs. JS/TS leads at
100% adoption. These are instruction files — committed, not gitignored.

**KF3 — Zero tags is a valid project state.** ohmyzsh (188k stars) has no
tags and no releases. The only actionable tag problem is *stale* tags, not
*absent* tags.

**KF4 — .gitattributes is the most common cross-platform mechanism.** 13/17
(76%) use `.gitattributes` for line-ending control. This is more common
than any shell portability pattern.

**KF5 — Pre-commit/husky/lefthook are NOT widely adopted.** Only 1/17
(apache/spark) uses pre-commit. Projects rely on EditorConfig (53%) →
ecosystem formatters → CI-based linting. Enforcement happens at CI time,
not commit time.

**KF6 — Formatters are universal.** Every project in the survey uses at
least one formatter/linter. The question is *which* formatter, not *whether*.
Built-in toolchain formatters (gofmt, rustfmt) require no config; external
formatters (prettier, black, clang-format) need installation.

---

## 2. Agent instruction ecosystem

Canonical instruction file per platform — relevant to portability:

| Tool | Canonical file | Scoped extension |
| :--- | :------------- | :--------------- |
| Anthropic Claude Code | `CLAUDE.md` | `.claude/rules/`, `@path` imports |
| OpenAI Codex | `AGENTS.md` | `AGENTS.override.md` |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md` |
| Cursor | `.cursorrules` | `.cursor/` community rules |

**Key principle:** Do not multiply authoritative instruction surfaces without
a clear maintenance or scope reason. Every additional file creates another
place where guidance can become duplicated, stale, or contradictory.

---

## 3. Cross-platform portability — verified patterns

All patterns validated against shellcheck rules — relevant to the
methodology's detection commands:

| Pattern | Shellcheck rule | Priority |
| :------ | :-------------- | :------ |
| `which` → `command -v` | SC2230 | High |
| `grep -P` → `grep -E` | SC3028 | High |
| `sed -i` (no backup) | SC2001 | High |
| `echo` with escapes | SC3028 | High |
| `#!/bin/bash` → `#!/usr/bin/env bash` | SC2001 | Medium |
| `\012` octal | Niche | Low — rare CI failure |
| `find -exit` → `-exec` | SC2001 | Medium |
| `flock` → `mkdir .lock \|\| exit 1` | SC2001 | Medium |

**Patterns identified as common but not actionable at methodology level:**
`[[ ]]` (SC3010), `source` vs `.` (SC2039), `pushd`/`popd` (SC2164),
`readlink -f`, GNU `mktemp` flags, `${var/pattern/replacement}` (SC2001),
`let` (SC2250). The methodology teaches agents to check for these when
cross-platform compatibility is declared; it does not enforce them
universally.

---

## 4. Co-author guard research

Two distinct enforcement families, same mechanism:

- **Proactive trailer rejection** — block unauthorized `*-by:` attribution
  before it reaches the commit log. Rare direction.
- **DCO enforcement** — Linux kernel, DCO App (337★), CNCF ecosystem:
  enforce *presence* of `Signed-off-by`, not rejection of unauthorized
  trailers.

Both use the same architecture: policy documentation → local commit-msg hook →
shared checker script → CI gate. No surveyed project uses hook-only or CI-only
for enforcement that matters. The current methodology teaches agents to check
for unauthorized `Co-authored-by:` trailers via `git log --format="%B"`,
eliminating the need for a shipped Python checker script. (Note: the earlier
`check-commit-trailers.py` script that this replaced was removed from the
repository; git-log-based detection is the sole approach.)

---

## 5. .gitignore patterns — official vs practice

**Official github/gitignore/Global/Agents.gitignore (canonical) directs:**

- **Ignore** (local state only): `.aider.*.history`, `.claude/*.local.json`,
  `.claude/**/*.log`, `CLAUDE.local.md`, `gemini-debug.log`, `.gemini-clipboard/`
- **Commit** (all commented out): `AGENTS.md`, `.codex/`, `.claude/`,
  `.cursorrules`, `.cursor/`, `GEMINI.md`, `WARP.md`,
  `.github/copilot-instructions.md`

**Practice from survey:** 47% of projects commit AGENTS.md, 24% commit
CLAUDE.md. No project gitignores agent instruction files. The official
template confirms this: instruction files are intentionally committed,
local variants go in .gitignore.

---

## 6. Script naming conventions (from open-source survey)

| Prefix | Purpose | Frequency |
| :----- | :------ | :-------- |
| `check-*` / `verify-*` | Validation and consistency | Ubiquitous |
| `build-*` | Compilation and packaging | Ubiquitous |
| `install-*` | Installation and setup | Common |
| `deploy-*` / `sync-*` | Deployment | Common |
| `run-*` / `start-*` | Execution and service | Very common |
| `test-*` | Testing | Ubiquitous |
| `lint-*` / `format-*` | Code quality | Very common |
| `release-*` / `publish-*` | Release management | Common |
| `clean-*` | Cleanup | Common |
| `setup-*` / `init-*` | First-time setup | Common |

Standard location: `scripts/` directory. Names lowercase-dash-separated.
Consistent prefixes enable tab-completion grouping.

---

## 7. Ecosystem structural survey (v0.2.0 motivation)

Survey of 6 major agent skill collection repos — the primary evidence that
led to the single-SKILL.md methodology design:

| Repo | Stars | Skills | Root refs/ | Root scripts/ | Shipped scripts | Payload sync |
|------|-------|--------|-----------|--------------|----------------|--------------|
| addyosmani/agent-skills | 68K+ | 25 | 0 | 0 | 0 | No |
| openai/skills | — | ~20 | 0 | 0 | 0 | No |
| anthropics/claude-plugins-official | ~31K | 29+ | 0 | 0 | 0 | No |
| wondelai/skills | 1.5K | 50 | 0 | ~2 | 0 | No |
| cybersecurity-skills | 22.8K | 817 | 0 | 2 | 0 | No |
| OpenMontage | 27.6K | 253 | 0 | ~50 | 0 | No |

**Key finding: Zero ecosystem repos ship reference files or wrapper scripts
in their skill payloads.** In those surveyed repositories, the installed skill
payload is the agent-facing surface; maintainer-only repository tooling is a
separate concern.
No build step, no sync script, no manifest.

### Consumption paths (no build step needed)

| Platform | Discovery path | Cross-agent path? |
|----------|---------------|------------------|
| Hermes | `external_dirs` → `skills/*/SKILL.md` | No — does not document `.agents/skills/` |
| Claude Code | `.claude/skills/` directory walk | No |
| Codex CLI | `.agents/skills/` directory walk | **Yes** — verified by the current setup guide |
| Gemini CLI | `.agents/skills/` (user/workspace) | **Yes** — explicitly documented |
| Cursor | `.cursor/rules/` glob match | No — uses rules format |

**Survey finding (2026-07-12):** `.agents/skills/` was the only cross-agent path
explicitly endorsed by a platform vendor in the sources inspected (Gemini CLI).
This is a historical survey result, not a guarantee about later platform
versions. The methodology remains suitable for platforms that can run `git`,
`shellcheck`, `python3`, and `gh`, subject to per-agent certification.

---

## 8. Primary research sources

- **agent-concepts-study** (https://github.com/CodeSigils/agent-concepts-study): 6 study notes on
  instruction boundaries, proportionate anti-drift, duplicate guidance, and
  research-practice loops; plus the 2026-07-12 structural diversity note
  that directly motivated the v0.2.0 redesign
- **skill-discovery/hub-marketplace-research.md**: ecosystem survey of 7
  marketplaces, 42 client platforms, 3-layer discovery model
- **skill-repo-architecture/repo-architecture-patterns.md**: structural
  benchmarks from 6 major collections
- **cross-ecosystem-skill-research skill**: platform vendor docs survey,
  repo architecture patterns
- **github/gitignore** (175k★): `Global/Agents.gitignore` — official agent
  artifact template
- **shellcheck wiki**: SC2001, SC2230, SC2039, SC3010, SC3028, SC2164, SC2250
- **DCO App**: github.com/dcoapp/app (337★) — Signed-off-by enforcement bot
- **Linux kernel DCO v1.1**: docs.kernel.org — origin of Signed-off-by
  trailer convention

---

## 9. Secret handling in repository audits (v0.3.0 addition)

**Finding:** Repository audits that print content from commit metadata or
configuration files risk exposing credentials present in messages, config, or
ignored files. Detection should return counts, status, or locations without
echoing matching values.

**Evidence:**
- Common secret patterns in commit messages: `api_key=sk-...`, `password=...`, `token=...` (observed in public corpuses)
- `.gitignore` grep checks produce false negatives when negation patterns exist (`!.env.local`) — `git check-ignore --no-index` correctly respects gitignore semantics
- Agent skill payloads that instruct "report findings with concrete harm" need an explicit redaction rule to prevent secret leakage in audit output

**Mitigation implemented in methodology:**
1. Commit-metadata secret scan for assignment-style secrets, known token
   prefixes, private-key headers, and credential-bearing URLs; emit status only,
   never raw subjects, bodies, or matching values.
2. `.gitignore` secret-pattern check via `git check-ignore --no-index` so
   negations are handled correctly.
3. Separate tracked-file check for sensitive environment filenames because
   `.gitignore` does not affect files already in Git.
4. Secret redaction plus revocation/rotation guidance for possible historical
   exposure.
5. Red Flag and Verification checklist items that prohibit raw commit-metadata
   output and require tracked-file awareness.
6. Bounded branch-history checks resolve the current upstream or remote default
   instead of assuming `origin/main`; no-base repositories skip rather than scan
   all history.
7. Pattern matching is explicitly heuristic. Existing project-native scanners
   and ecosystem-specific sensitive filenames are used only when discovery
   identifies them.

**Open question:** Whether opt-in `REPO_HEALTH_VERIFY_REFS=1` external URL checks should also scan response bodies for secret patterns.

---

## 10. Documentation architecture (2026-08-24)

**Finding:** Maintainer documentation is easier to navigate when each page has
one job: teach a task, define a contract, explain a decision, or preserve
evidence. Mixing those jobs makes current instructions compete with historical
context and increases drift.

**Applied pattern:** The docs index routes maintainers by task, while
`maintaining.md` owns the workflow. `portability-contract.md` owns normative
claims, compatibility reports own runtime evidence, and `decisions.md` and
`research.md` remain explanatory/history surfaces. Machine-readable JSON files
stay clearly labeled as CI inputs rather than user documentation.

**Sources:**

- [Diátaxis: Start here](https://diataxis.fr/start-here/) — separates tutorials,
  how-to guides, reference, and explanation.
- [GitHub: Setting guidelines for repository contributors](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors)
  — documents conventional contributor-guidance placement and discoverability.

This is a navigation and ownership pattern, not a requirement to create a
large documentation site or to split short, cohesive pages unnecessarily.

The 2026-08-24 dogfood audit also validated two runtime guardrails: release
alignment must distinguish published metadata from maintainer-only package
metadata, and heuristic secret matches need native-scanner/context review to
avoid flagging detector source code as a credential.
