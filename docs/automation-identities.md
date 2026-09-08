# Automation identities and bot review

This is a maintainer reference for the GitHub App identities that may act in
this repository. It explains authority and review boundaries; it is not a
runtime dependency of the installed skill.

## Current model

| Identity | What it can do here | What it cannot establish |
| --- | --- | --- |
| `dependabot[bot]` | Open scheduled dependency-update pull requests from `.github/dependabot.yml`. | That an update is semantically safe, compatible with this methodology, or ready to merge without review. |
| `github-actions[bot]` | Act through a workflow's `GITHUB_TOKEN`; this repository uses `contents: read` by default. The release job alone has `contents: write` to create a GitHub Release. | Approval, bypass of branch protection, or authority beyond the job's explicit permissions. |
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

## Review rule

For every bot-authored PR:

1. Confirm the actor, changed ecosystem, and whether it is a version or
   security update.
2. Inspect the full diff, including lockfile changes and any altered workflow
   action SHA.
3. Check that required CI is green and that the PR has not changed workflow
   permissions, triggers, or secret use unexpectedly.
4. Merge only a narrow, understood change. Close superseded PRs; GitHub may
   delete the merged branch according to repository settings.

Do not add auto-merge, `pull_request_target`, write permissions for pull
requests, or a workflow that approves its own changes merely to remove this
review step. Each would require a concrete repeated failure mode and a separate
security review.

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
