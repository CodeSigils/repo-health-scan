# REPO PROFILE Template

Copy this template when emitting the Step 1 profile. Fill in all fields; use `null` or `[]` when not applicable.

```yaml
# REPO PROFILE
observed:
  vcs: git
  languages: []
  package_managers: []
  ci: null
  shell_files: false
  recent_commits: false
  gitignore: false
  version_sources: []
  script_surface: ""
  reliability_audit_requested: false
  shipped_payload: ""
  base_ref: null
  branch_commits_outside_base: null
  working_tree_dirty: false
  workflow_files: []
  verify_refs: false

inferred:
  repo_type: ""
  risk_context: ""
```

## Field Guide

### Observed (direct from probes)

| Field | Source | Example |
|-------|--------|---------|
| `vcs` | Always git | `git` |
| `languages` | `ls`, file extensions | `["Python", "TypeScript", "Markdown"]` |
| `package_managers` | `pyproject.toml`, `package.json`, etc. | `["uv", "npm"]` |
| `ci` | `.github/workflows/`, `.gitlab-ci.yml` | `"GitHub Actions"` or `null` |
| `shell_files` | `find . -name '*.sh'` | `true` / `false` |
| `recent_commits` | `git rev-list --count --max-count=20 HEAD` | `true` if >0 |
| `gitignore` | `test -f .gitignore` | `true` / `false` |
| `version_sources` | Parseable paths inside one distribution boundary | `["pyproject.toml", "src/pkg/__init__.py"]` |
| `script_surface` | `find scripts/`, root `*.sh` | `"maintainer-only Python + shell"` |
| `reliability_audit_requested` | Explicit user request for reliability or test-gap analysis | `true` / `false` |
| `shipped_payload` | Skill discovery | `"single SKILL.md"` |
| `branch_commits_outside_base` | bounded base comparison | integer or `null` |
| `working_tree_dirty` | `git status --porcelain` | `true` / `false` |
| `workflow_files` | `.github/workflows/` recursive discovery | relative paths |
| `base_ref` | `@{upstream}` or remote default | `"origin/main"` or `null` |
| `verify_refs` | `REPO_HEALTH_VERIFY_REFS` | `true` / `false` |

### Inferred (judgment from observed)

| Field | Derived From | Example |
|-------|--------------|---------|
| `repo_type` | languages, package_managers, script_surface | `"skill-pack"`, `"library"`, `"monorepo"`, `"documentation"` |
| `risk_context` | recent_commits, working_tree_dirty, CI | `"routine review"`, `"active development"` |

## Example: Skill Pack

```yaml
observed:
  vcs: git
  languages: ["Markdown", "Python", "shell"]
  package_managers: ["pip"]
  ci: "GitHub Actions"
  shell_files: true
  recent_commits: true
  gitignore: true
  version_sources: [".codex-plugin/plugin.json"]
  script_surface: "maintainer-only Python + shell"
  reliability_audit_requested: false
  shipped_payload: "single SKILL.md"
  base_ref: "origin/main"
  verify_refs: false

inferred:
  repo_type: "skill-pack"
  risk_context: "routine review"
```

## Example: Python Library (uv)

```yaml
observed:
  vcs: git
  languages: ["Python"]
  package_managers: ["uv"]
  ci: "GitHub Actions"
  shell_files: false
  recent_commits: true
  gitignore: true
  version_sources: ["pyproject.toml", "src/example/__init__.py"]
  script_surface: "none"
  reliability_audit_requested: false
  shipped_payload: "library"
  base_ref: "origin/main"
  verify_refs: false

inferred:
  repo_type: "library"
  risk_context: "routine review"
```
