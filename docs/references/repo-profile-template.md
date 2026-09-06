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
  shipped_payload: ""
  tags_present: false
  base_ref: null
  branch_commits_outside_base: null
  working_tree_dirty: false
  workflow_files: []
  release_files: []
  verify_refs: false
  verify_releases: false

inferred:
  repo_type: ""
  release_model: ""
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
| `version_sources` | File paths with version fields | `["pyproject.toml", "SKILL.md"]` |
| `script_surface` | `find scripts/`, root `*.sh` | `"maintainer-only Python + shell"` |
| `shipped_payload` | Skill discovery | `"single SKILL.md"` |
| `tags_present` | `git tag --list 'v*'` | `true` / `false` |
| `branch_commits_outside_base` | bounded base comparison | integer or `null` |
| `working_tree_dirty` | `git status --porcelain` | `true` / `false` |
| `workflow_files` | `.github/workflows/` recursive discovery | relative paths |
| `release_files` | release workflows/manifests | relative paths |
| `base_ref` | `@{upstream}` or remote default | `"origin/main"` or `null` |
| `verify_refs` | `REPO_HEALTH_VERIFY_REFS` | `true` / `false` |
| `verify_releases` | `REPO_HEALTH_VERIFY_RELEASES` | `true` / `false` |

### Inferred (judgment from observed)

| Field | Derived From | Example |
|-------|--------------|---------|
| `repo_type` | languages, package_managers, script_surface | `"skill-pack"`, `"library"`, `"monorepo"`, `"documentation"` |
| `release_model` | tags_present, CI, package_managers | `"git tags"`, `"PyPI package"`, `"independent packages"` |
| `risk_context` | tags_present, recent_commits, CI | `"pre-release"`, `"routine review"`, `"active development"` |

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
  version_sources: ["skills/repo-health-scan/SKILL.md", ".codex-plugin/plugin.json", "CITATION.cff", "git tag"]
  script_surface: "maintainer-only Python + shell"
  shipped_payload: "single SKILL.md"
  tags_present: true
  base_ref: "origin/main"
  verify_refs: false
  verify_releases: false

inferred:
  repo_type: "skill-pack"
  release_model: "git tag plus Codex plugin"
  risk_context: "pre-release"
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
  shipped_payload: "library"
  tags_present: false
  base_ref: "origin/main"
  verify_refs: false
  verify_releases: false

inferred:
  repo_type: "library"
  release_model: "PyPI package"
  risk_context: "routine review"
```
