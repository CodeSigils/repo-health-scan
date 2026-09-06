---
status: maintainer-reference
purpose: Plan and evidence for separating the repository name from the public skill name.
audience: maintainers only — not shipped to skill users.
---

# Repository and skill-name migration plan

## Current state (2026-09-06)

| Concern                 | Current value                                                             | Compatibility meaning                                                                      |
| ----------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| GitHub repository       | `CodeSigils/repo-health-scan` (renamed from `repo-health-and-sync-skill`) | Canonical remote source used by clone, Skills CLI, badges, schemas, and release workflows. |
| Skills CLI directory    | `skills/repo-health-scan/`                                                | Discovered skill directory.                                                                |
| Public skill identifier | `repo-health-scan`                                                        | `SKILL.md` frontmatter name and `--skill` selector.                                        |
| Codex plugin            | `repo-health-and-sync-skill`                                              | Separate plugin identity; not the Skills CLI skill name.                                   |
| Skills CLI discovery    | Passed; exactly `repo-health-scan` found                                  | The mismatch is supported and does not require a rename.                                   |

The previous claim that a remote rename would break installs was inaccurate.
GitHub redirects clone, fetch, push, and web traffic after a repository rename.
Local clones should still update `origin`, and workflows that invoke this
repository as an action need separate review because action references are not
redirected.

## Recommended target

```text
repository: repo-health-scan
skill directory: skills/repo-health-scan/
skill name: repo-health-scan
plugin name: repo-health-and-sync-skill (retain until a separate plugin migration)
```

This is a clarity improvement, not a prerequisite for skills.sh compatibility.

## Staged migration

### 1. Prepare locally (no remote mutation)

1. Create a branch from an up-to-date `main`.
2. Rename `skills/repo-health-and-sync-skill/` to `skills/repo-health-scan/`.
3. Update every source, test, fixture, documentation, plugin path, and
   compatibility report that refers to the directory. Keep repository URLs
   unchanged in this phase.
4. Run Skills CLI discovery and isolated Codex and Claude Code installs. Assert
   the selected name is `repo-health-scan`, exactly one `SKILL.md` is installed,
   and no maintainer references are included.
5. Run full verification and a Codex regression. Treat this as a packaging
   change and start a fresh compatibility baseline.

### 2. Merge the local rename

Merge only after required CI checks pass. Do not publish a release or change
the GitHub repository name in the same pull request; this keeps failures
attributable and permits a straightforward revert.

### 3. Rename the GitHub repository (remote mutation)

After the local rename is released or explicitly accepted:

1. Confirm no GitHub Actions workflow calls this repository as an action.
2. Rename the repository in GitHub settings to `repo-health-scan` (**completed
   2026-09-06**).
3. Immediately update local clones:

   ```bash
   git remote set-url origin https://github.com/CodeSigils/repo-health-scan.git
   git remote -v
   ```

4. Update badges, release and security links, schema `$id` URLs, Skills CLI
   examples, plugin metadata, and compatibility reports.
5. Verify old and new clone URLs, the skills.sh page, release/tag links, and
   both host install smoke tests. Do not recreate the old repository name,
   because that can consume GitHub's redirect.

## Acceptance

- Skills CLI lists exactly `repo-health-scan` from the new repository URL.
- Codex and Claude Code isolated installs contain the expected `SKILL.md`.
- No stale old repository or directory URLs remain outside this migration note.
- CI, release verification, security links, and schema identifiers use the
  canonical repository URL.
- A compatibility report records source commit, CLI version, host, installed
  path, and result.
