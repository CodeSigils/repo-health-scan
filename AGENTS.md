# Repository Instructions

> **Scope:** These instructions apply to agents maintaining this repository.
> They are not part of the reusable skill payload and should not be copied into
> repositories being audited.

## Intent Routing

- For repository-health, release-readiness, maintenance-drift, archive,
  handoff, or onboarding audits, read and follow
  [`skills/repo-health-scan/SKILL.md`](skills/repo-health-scan/SKILL.md).
- Do not invoke the skill for ordinary feature implementation, a narrow bug
  fix, a single-file edit, or a routine code review without a repository-health
  question.
- For changes to this repository, follow
  [`docs/maintaining.md`](docs/maintaining.md).

## Source Ownership

- `SKILL.md` owns the audit methodology and trigger boundaries.
- `docs/maintaining.md` owns contributor workflow and verification commands.
- Compatibility reports own agent-specific support claims.

Keep this file as a routing layer. Link to the owning source instead of
restating its instructions.
