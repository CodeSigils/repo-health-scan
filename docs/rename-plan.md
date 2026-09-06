---
status: maintainer-reference
purpose: Plan and evidence for separating the repository name from the public skill name.
audience: maintainers only — not shipped to skill users.
---

# Repository and skill-name migration plan

## Current state (2026-09-06)

| Concern                 | Current value                                                                                                         | Compatibility meaning                                                                      |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| GitHub repository       | `CodeSigils/repo-health-scan` (renamed from `repo-health-and-sync-skill`)                                             | Canonical remote source used by clone, Skills CLI, badges, schemas, and release workflows. |
| Skills CLI directory    | `skills/repo-health-scan/`                                                                                            | Discovered skill directory.                                                                |
| Public skill identifier | `repo-health-scan`                                                                                                    | `SKILL.md` frontmatter name and `--skill` selector.                                        |
| Codex plugin            | `repo-health-and-sync-skill`                                                                                          | Separate plugin identity; not the Skills CLI skill name.                                   |
| Skills CLI discovery    | Passed; exactly `repo-health-scan` found                                                                              | Directory and public identifier now match.                                                 |
| skills.sh page          | Detail route and repository landing route respond; landing page lists one skill and one total install | Badge and installation metadata are live; individual detail-page install history may still show `–`. |

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

This target is now implemented. It was a clarity improvement, not a
prerequisite for skills.sh compatibility.

## Migration record

### Local rename — completed 2026-09-06

The payload directory was renamed to `skills/repo-health-scan/`. Scripts,
fixtures, documentation, schemas, and compatibility paths were updated. The
repository verification suite passed.

### Remote rename — completed 2026-09-06

The GitHub repository was renamed to `CodeSigils/repo-health-scan`, local
`origin` was updated, and canonical URLs were repaired. Follow-up checks:

1. Confirm no GitHub Actions workflow calls this repository as an action.
2. Verify old and new clone URLs, release/tag links, and security links.
3. For future clones, use:

   ```bash
   git remote set-url origin https://github.com/CodeSigils/repo-health-scan.git
   git remote -v
   ```

4. Do not recreate the old repository name, because that can consume GitHub's
   redirect.

## Acceptance

- Skills CLI lists exactly `repo-health-scan` from the new repository URL.
- Codex and Claude Code isolated installs contain the expected `SKILL.md`.
- No stale old repository or directory URLs remain outside this migration note.
- CI, release verification, security links, and schema identifiers use the
  canonical repository URL.
- A compatibility report records source commit, CLI version, host, installed
  path, and result.
