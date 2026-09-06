# Real-project dogfood audit

> Maintainer-only template. This report is evidence about one audit execution,
> not a compatibility or safety certification.

Date: `YYYY-MM-DD`
Auditor/runtime: `<agent and version>`
Repository: `<owner/name>`
Source revision: `<commit or unavailable>`
Working tree: `clean | dirty | uncommitted prototype`

## Repository profile

Record observed facts before interpreting them. Use `null`, `false`, or `[]`
when a field is known to be absent.

```yaml
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
  working_tree_dirty: false
  workflow_files: []
  release_files: []
  tool_availability: {}
inferred:
  repo_type: ""
  release_model: ""
  risk_context: ""
```

## Dimension plan

List every candidate dimension as active or skipped. Every active dimension
needs an exact profile path; every skipped dimension needs a concrete reason.

```yaml
active: []
skipped: []
```

## Checks and evidence

| Dimension | Commands or sources | Result | Evidence paths / limitations |
| --- | --- | --- | --- |
|  |  |  |  |

## Findings

For each finding, state the concrete harm and a proportionate remediation. Do
not include secrets, raw commit bodies, or sensitive provider content.

| Finding | Harm | Remediation | Confidence |
| --- | --- | --- | --- |
|  |  |  |  |

## Outcome

- Useful findings: `<yes/no; why>`
- False positives or missed checks: `<details>`
- Tool-absence or environment limits: `<details>`
- Module gap requiring follow-up: `<none or evidence>`
- Reopen decision: `<no / specific next experiment>`
