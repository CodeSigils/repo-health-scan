# Maintainer docs — not shipped to skill users

This directory documents the project's architecture decisions and research
evidence. It is not part of the skill runtime — users who install this
skill do not receive these files.

The installed runtime payload is a single `SKILL.md`. This directory contains
maintainer-only procedures, contracts, evidence, and research; none of these
files are runtime dependencies of the installed skill.

## Choose the right document

| If you need to…                                | Read…                                                                                                                   |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Make or review a repository change             | [maintaining.md](maintaining.md)                                                                                        |
| Understand why the architecture looks this way | [decisions.md](decisions.md)                                                                                            |
| Install or test the Codex plugin               | [codex-setup.md](codex-setup.md)                                                                                        |
| Run the model regression harness               | [codex-regression.md](codex-regression.md)                                                                              |
| Record a real-project dogfood audit            | [dogfood-audit-template.md](dogfood-audit-template.md)                                                                  |
| Justify recurring CI and release controls      | [control-justification-ledger.md](control-justification-ledger.md)                                                      |
| Check an agent compatibility claim             | [compatibility-reports/codex.md](compatibility-reports/codex.md) and [portability-contract.md](portability-contract.md) |
| Understand the research behind a decision      | [research.md](research.md)                                                                                              |
| Use maintainer-only evaluation references      | [references/](references/)                                                                                              |
| Plan a repository or skill-directory rename    | [rename-plan.md](rename-plan.md)                                                                                        |

## Normal maintainer path

1. Read [maintaining.md](maintaining.md) and make the smallest evidence-backed
   change.
2. Run the fast verification commands listed there.
3. If `SKILL.md` behavior or trigger boundaries changed, run the optional local
   Codex regression.
4. For a release, follow the tagged-release procedure in `maintaining.md`.

The root [README](../README.md) is the user-facing overview. `AGENTS.md` is
only a routing layer; it points maintainers here and does not duplicate these
procedures.

## Documentation model

The files use four deliberately different roles:

- **How-to:** `maintaining.md`, `codex-setup.md`, and `codex-regression.md`
  explain how to perform maintainer tasks.
- **Reference:** `portability-contract.md` and
  `compatibility-reports/` define claim levels and recorded runtime evidence.
- **Explanation:** `decisions.md` explains architectural choices; `research.md`
  records the evidence behind them.
- **Automation data:** `doc-standards.json` and `evidence-urls.json` are
  machine-maintained inputs for CI, not prose guides.

Keep procedures out of decision records, keep current support claims out of
research notes, and update the index above when a new document type is added.
