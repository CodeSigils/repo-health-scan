# Automation identities and bot review

This is a maintainer reference for the GitHub App identities that may act in
this repository. It explains authority and review boundaries; it is not a
runtime dependency of the installed skill.

## Current model

| Identity | What it can do here | What it cannot establish |
| --- | --- | --- |
| `dependabot[bot]` | Open scheduled dependency-update pull requests from `.github/dependabot.yml`. | That an update is semantically safe, compatible with this methodology, or ready to merge without review. |
| `github-actions[bot]` | Act through a workflow's `GITHUB_TOKEN`; no workflow in this repository requests write access to repository contents, and only `dependency-backlog` adds `pull-requests: write`. | Approval, bypass of branch protection, or authority beyond the job's explicit permissions. |
| Codex regression | Uses an OpenAI API secret only when the feature flag enables the scheduled or manual job; it runs in a read-only sandbox. | A deterministic release gate or permission to change repository state. |

Dependabot-triggered pull-request workflows are treated like fork workflows:
their `GITHUB_TOKEN` is read-only and repository secrets are unavailable.
That reduces exposure, but it does not make an update trustworthy by itself.

## Dependabot policy

The repository has two deliberately narrow weekly update streams:

- GitHub Actions: minor and patch updates are grouped; major updates remain
  individual. At most two update PRs are open.
- `uv`: maintainer tooling updates have one open PR at a time. The lockfile
  makes the exact proposed resolution reviewable.

Both use the `chore(deps)` convention so the normal commit gate accepts bot
commits. Security updates remain a GitHub security feature and are not proof
that ordinary version updates are secure; assess them separately.

`open-pull-requests-limit` is a concurrency cap, not a rate limit: it bounds
how many version-update pull requests are open at once within one update
entry, not how many arrive over time. Entries, keyed by ecosystem and
directory, hold independent budgets, so the two caps never compete. Within
an entry the budget is shared and a group consumes one slot. At the cap
Dependabot opens nothing further, builds no backlog, and waits for the next
scheduled run.

A newer release supersedes instead of queueing. If a version is published
while its pull request is open, that pull request is closed and a new one
opens at the newer version, leaving the open count at the cap even though a
fresh pull request was created. That is the mechanism behind the twelve-day
stall in [MAINTENANCE.md](MAINTENANCE.md), and why a cap that works as
configured does not prevent churn.

`exclude-patterns` ungroups rather than skips. An excluded dependency still
receives individual version-update pull requests, and because `update-types`
filters grouping only, a major release still produces one. Group resolution
carries a documented-versus-implemented discrepancy: GitHub's documentation
places a dependency in the first group it matches, while the updater
implementation resolves the most specific matching group. The two coincide
under one group and diverge under several, so first-match wording is not a
guarantee once groups multiply. A group matching nothing is ignored, and its
members receive individual pull requests instead.

## Review rule

For every bot-authored PR:

1. Confirm the actor, changed ecosystem, and whether it is a version or
   security update.
2. Inspect the full diff, including lockfile changes and any altered workflow
   action SHA.
3. Check that required CI is green and that the PR has not changed workflow
   permissions, triggers, or secret use unexpectedly.
4. Merge only a narrow, understood change, then close any superseded pull
   requests. The merge command deletes the head branch; nothing removes it
   automatically.

Auto-merge is disabled and `delete_branch_on_merge` is off, so a merge keeps
its head branch unless the merge command deletes it. Do not enable auto-merge,
`pull_request_target`, write permissions for pull requests, or a workflow that
approves its own changes merely to remove this review step. Each would require
a concrete repeated failure mode and a separate security review.

## Source and scope notes

GitHub documents that `GITHUB_TOKEN` is an installation token scoped to the
repository and expires with the job. Workflow `permissions` should start at
least privilege and be expanded per job only when necessary. GitHub also
documents that Dependabot workflow runs use read-only tokens and cannot access
secrets. Dependabot grouping and open-PR limits reduce review volume, but
security updates have a distinct configuration and risk path.

Sources:

- [GitHub Actions secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token)
- [Workflow syntax: permissions and Dependabot runs](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Dependabot version updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-version-updates)
- [Customizing Dependabot security updates](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/customizing-dependabot-security-prs)
- [Dependabot configuration options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference)
