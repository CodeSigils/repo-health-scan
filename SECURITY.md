# Security Policy

Report security issues privately through the
[GitHub Security Advisory](https://github.com/CodeSigils/repo-health-scan/security/advisories/new)
rather than opening a public issue.

Security concerns in this repository include unsafe instructions in the skill
methodology, supply-chain risks in CI tooling, or references to compromised
external resources. Do not include exploit details in public reports.

Issues that do not involve the GitHub Actions workflow (leaked secrets in CI
logs, workflow injection) can be opened as public GitHub issues. Report
CI-related vulnerabilities through the advisory link above.

## Skill Trust Checklist

Maintainers must review this checklist whenever the skill instructions,
fixtures, compatibility evidence, or packaging changes. The enforceable parts
run through `python3 scripts/check-trust.py` in local verification and CI.

- [x] Trigger metadata states both when the skill applies and when it does not.
- [x] Runtime probes are read-only; the skill contains no destructive commands,
  privilege escalation, approval bypasses, or automatic fixes.
- [x] Network access is explicit: release and external-reference queries require
  opt-in environment flags.
- [x] JSONL output is emitted only when `REPO_HEALTH_OUTPUT=jsonl` is set.
- [x] Eval fixtures and recorded compatibility evidence contain no credentials.
- [x] Compatibility claims name the tested agent and exact version.
- [x] The shipped `SKILL.md` payload remains separate from maintainer-only
  scripts, evals, CI, and documentation.
- [x] Report guidance instructs agents to redact credentials, tokens, and
  secrets before including them in findings — flag existence, not values.
- [x] Commit-quality probes emit counts or status only; they do not print or
  persist raw commit subjects or bodies.
- [x] Commit subjects and bodies must not contain credentials, tokens, private
  keys, sensitive values, or secret-bearing URLs.
- [x] `.gitignore` coverage checks account for negations and separately detect
  sensitive environment files that Git already tracks.
- [x] Suspected historical exposure is reported without the value and includes
  revocation or rotation guidance.
- [x] Branch-only history checks discover the configured upstream or remote
  default branch instead of assuming `origin/main`; unavailable bases are skipped.
- [x] Secret-pattern matches are treated as heuristic, and project-native
  scanners or additional sensitive filenames run only when repository evidence activates them.
- [x] CI installs a reviewed, pinned Ruff version rather than an unbounded
  latest release.
- [x] Bot-initiated changes are reviewed as ordinary changes: the actor,
  trigger, explicit token permissions, action pins, and diff are inspected;
  green checks do not grant approval or broaden authority.

## Automation identities

Dependabot and GitHub Actions are separate GitHub App identities with different
authority. Dependabot opens dependency-update pull requests according to
`.github/dependabot.yml`; pull-request workflows it triggers receive a
read-only `GITHUB_TOKEN` and no repository secrets. GitHub Actions workflows
run as `github-actions[bot]` only when a workflow writes with its token, and
their authority is bounded by each workflow's explicit `permissions` block.

This repository does not auto-merge bot pull requests. The release workflow is
the only workflow with `contents: write`, and it may create a GitHub Release
only after tag and CI verification. See [automation-identities.md](docs/automation-identities.md)
for the operational model and review rules.
