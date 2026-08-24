---
status: maintainer-reference
purpose: Developer workflow guide for maintainers of this skill.
audience: maintainers only — not shipped to skill users.
related: AGENTS.md routes agents to this maintainer reference.
---

# Maintaining the Repo Health Scan Skill

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

## Verification checklist

Before marking work done, run through in order:

1. **Tree clean** — `git status --porcelain` shows nothing
2. **Doc audit passes** — `python3 scripts/doc-audit.py --self-test`
3. **No stale refs** — `grep -rn --include='*.md' 'PLAN\\.md\\|PROPOSALS\\.md\\|REPORT\\.md\\|USER-SUGGESTIONS\\.md' . | grep -v '.git/'` returns nothing
4. **Shellcheck clean** — on any modified `.sh` files
5. **Eval contract valid** — `python3 scripts/validate-evals.py`
6. **Trust contract valid** — `python3 scripts/check-trust.py`
7. **Versions aligned** — `python3 scripts/check-version-consistency.py`
8. **Python lint clean** — `python3 -m ruff check scripts skills`

The model regression is deliberately outside this required fast checklist.
After a material `SKILL.md` workflow or trigger change, run
`python3 scripts/run-codex-regression.py` locally or dispatch the dedicated
`Codex regression` workflow. Do not make ordinary changes depend on model
availability.

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

The skill is a single SKILL.md with no shipped scripts, no reference files,
and no build process. The agent discovers repo characteristics at runtime
using tools already on PATH (`git`, `shellcheck`, `python3`, `gh`).

Changes to the methodology go directly into `skills/repo-health-and-sync-skill/SKILL.md`.
There is no sync step, no payload regeneration, and no duplicate reference
copies to maintain.

Root `AGENTS.md` is a routing adapter, not a second maintainer guide. It points
repository-health work to `SKILL.md` and repository changes to this file.

## Project structure

```text
├── .github/
│   ├── dependabot.yml              # Weekly GitHub Actions updates
│   ├── release.yml                 # Generated release-note categories
│   └── workflows/
│       ├── ci.yml
│       ├── codex-regression.yml    # Scheduled/manual non-blocking model evaluation
│       └── release.yml             # Validated generated release creation
├── .codex-plugin/plugin.json      # Codex distribution manifest
├── .gitignore
├── .gitattributes
├── AGENTS.md                      # Repository-level agent routing
├── CITATION.cff
├── LICENSE
├── README.md
├── SECURITY.md
├── docs/                          # Maintainer docs (not shipped)
│   ├── README.md
│   ├── codex-regression.md
│   ├── codex-setup.md
│   ├── compatibility-reports/
│   │   └── codex.md
│   ├── evidence-urls.json
│   ├── portability-contract.md      # cross-agent claim and adapter rules
│   ├── maintaining.md
│   ├── decisions.md
│   ├── research.md
│   └── doc-standards.json
├── evals/
│   └── cases/
│       └── repo-health-scan.json  # Local behavioral contract
├── scripts/                       # CI-only tooling (not shipped)
│   ├── _common.py                 # Shared utilities (ROOT, read_json, validate_dimensions)
│   ├── check-expiry.py
│   ├── check-portability.py
│   ├── check-trust.py
│   ├── check-version-consistency.py
│   ├── doc-audit.py
│   ├── extract-tests.py
│   ├── grade-codex-transcript.py
│   ├── run-codex-regression.py
│   ├── validate-evals.py
│   ├── validate-scripts.py
│   ├── verify-urls.py
│   └── verify.sh
└── skills/
    └── repo-health-and-sync-skill/
        └── SKILL.md               # The entire skill
```

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
