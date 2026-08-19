---
name: repo-health-scan
description: >-
  Methodology for evaluating any git repository's health at runtime.
  Guides the agent through discover, infer, and report: inspect the
  filesystem and git history, decide which invariants matter for this
  repository, then report findings with concrete harm and remediation.
  Use when asked to audit, review, assess, or check the health of a repo.
  Use before a release, archive, handoff, or onboarding session.
  Use when CI is failing and the cause is unclear.
  Not for single-file edits, narrow bug fixes, or feature implementation.
license: MIT
metadata:
  author: CodeSigils
  version: "0.3.0"
  purpose: project-governance
  tags:
    - git-hygiene
    - methodology
    - runtime-discovery
    - health-audit
    - cross-project
---

# Repo Health Scan

A three-step methodology: discover the repository, infer its local invariants,
then report verified findings. Repository evidence—not a universal
checklist—determines which checks apply.

Four rules govern the scan:

- Let observed repository evidence activate checks; do not bring a universal
  checklist.
- Emit the repo profile and dimension plan before running dimension probes.
- Skip speculative checks: every invariant must trace to a concrete failure.
- Report concrete harm and remediation while keeping sensitive values out of
  commands, transcripts, and findings.

## When to Use

- Before a release, archive, handoff, or project revival
- When onboarding onto an unfamiliar repository
- When CI is failing and the cause is unclear
- After a large batch of AI-assisted commits

## When Not to Use

- For a task scoped to one file, bug, or feature
- For ordinary implementation work when overall repository health is not at issue
- For repositories without git history, except for a filesystem shape summary
- As an automatic fixer; this skill reports but does not mutate the repository

## Step 1: Discover the repo's shape

Run these probes before judging health. Inspect the repository; do not infer its
shape from its name.

```bash
# What languages and tools does this project actually use?
ls *.json *.toml *.yaml *.yml *.cfg 2>/dev/null
ls *file 2>/dev/null
ls Dockerfile Containerfile 2>/dev/null

# What's the commit culture like? Count patterns without printing message text,
# because subjects and bodies can themselves contain credentials.
printf 'recent_commits=%s\n' "$(git rev-list --count --max-count=20 HEAD 2>/dev/null || echo 0)"
printf 'conventional_subjects=%s\n' "$(git log --format='%s' -20 2>/dev/null | grep -Ec '^(feat|fix|docs|chore|refactor|test|ci|build|perf|revert)(\\([^)]*\\))?!?:' || true)"
printf 'informative_bodies=%s\n' "$(git log --format='%b' -5 2>/dev/null | grep -Ec '^(what|why):' || true)"
git status --short --branch
git tag --list 'v*' --sort=-version:refname | head -5
base_ref=$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
if [ -z "$base_ref" ]; then
  base_ref=$(git for-each-ref --format='%(symref:short)' 'refs/remotes/*/HEAD' | sed -n '1p')
fi
printf 'base_ref=%s\n' "${base_ref:-unavailable}"
if [ -n "$base_ref" ] && git rev-parse --verify "$base_ref" >/dev/null 2>&1; then
  printf 'branch_commits_outside_base=%s\n' "$(git rev-list --count "$base_ref"..HEAD)"
fi

# What automation exists?
find .github/workflows -name '*.yml' 2>/dev/null | head -5
find . -maxdepth 1 -name '*.sh' 2>/dev/null
find scripts/ -name '*.py' -o -name '*.sh' 2>/dev/null | head -10

# What's the dependency surface?
find . -maxdepth 2 -name 'requirements*.txt' -o -name 'Cargo.toml' \
  -o -name 'go.mod' -o -name 'package.json' 2>/dev/null | head -10

# Is there a pre-existing health convention?
test -f .repo-health.json && echo ".repo-health.json present" || echo "no .repo-health.json"

# What does the project's .gitignore cover? (respect it when exploring)
test -f .gitignore && echo ".gitignore present" || echo "no .gitignore"

# Did the user or environment opt into a conditional check?
printf 'verify_refs=%s\n' "${REPO_HEALTH_VERIFY_REFS:-0}"
printf 'verify_releases=%s\n' "${REPO_HEALTH_VERIFY_RELEASES:-0}"
```

From this output, form and **emit** a concise structured repo profile before
checking any dimension. Separate observed facts from inferred labels. The
profile must be visible in the transcript as a `REPO PROFILE` block; do not keep
it only in internal reasoning or defer it to the final report. Emit the profile
in its own message; do not combine that message with the dimension plan:

### REPO PROFILE (required structure)

```yaml
observed:
  vcs: git
  languages: [string]
  package_managers: [string]
  ci: string | null
  shell_files: boolean
  recent_commits: boolean
  gitignore: boolean
  version_sources: [string]
  script_surface: string
  shipped_payload: string
  tags_present: boolean
  base_ref: string | null
  verify_refs: boolean
  verify_releases: boolean

inferred:
  repo_type: string
  release_model: string
  risk_context: string
```

Do not run a dimension-specific command before emitting this block. If you
cannot write it, run more discovery probes.

## Step 2: Infer what invariants matter

Given the emitted repo profile, ask: what invariants would break if they
drifted?

The candidate catalog below is **non-exhaustive** — not a universal checklist.
The agent discovers applicable dimensions from this catalog; every active
dimension must cite `activated_by` evidence from the profile. Custom dimensions
are allowed when repo evidence supports a check not in the catalog; they must
still cite `activated_by` evidence.

Before running any dimension command, emit a `DIMENSION PLAN` that:

- lists each active dimension with one or more exact profile paths in
  `activated_by`;
- lists each inactive dimension with a concrete `skip_reason`; and
- accounts for every candidate dimension in the catalog as active or skipped.

Use paths such as `observed.ci` or `inferred.release_model`. A recorded request
or environment flag may also activate a dimension; an unobserved assumption may
not.

```yaml
# DIMENSION PLAN
active:
  - name: shell_correctness
    activated_by: [observed.shell_files]
skipped:
  - name: cross_platform
    skip_reason: no platform or user requirement appears in the profile
```

### Candidate Catalog (non-exhaustive)

| Dimension | Activated By |
|-----------|--------------|
| history_hygiene | always |
| shell_correctness | observed.shell_files |
| version_alignment | len(observed.version_sources) ≥ 2 |
| tag_release_integrity | inferred.release_model exists |
| commit_quality | observed.recent_commits |
| ci_efficiency | observed.ci |
| cross_platform | observed.shell_files + inferred.platform_requirements |
| attribution_drift | observed.branch_commits_outside_base > 0 |
| file_coverage | observed.gitignore |
| external_reference_health | env:REPO_HEALTH_VERIFY_REFS=1 |

Only after emitting the dimension plan, run the smallest command or command
block that answers each active dimension. Do not run probes for skipped
dimensions.

**Blocking behavior is contextual.** When a finding represents a genuine
release blocker (e.g., version drift, secret in tracked file, dirty tree at
release), report it first and **continue safe read-only checks** for remaining
active dimensions — do not stop the audit. Stop only when the finding requires
human remediation before any further probing is meaningful.

Safe to continue after a blocker: history_hygiene, file_coverage, commit_quality.
Pause (may need remediation context): version_alignment, tag_release_integrity, ci_efficiency.
Skip if tools unavailable: cross_platform (needs shellcheck), external_reference_health (needs gh, opt-in).

**Graceful tool absence.** If an expected tool (`shellcheck`, `gh`, `python3`)
is unavailable, skip the dependent dimension with a clear `skip_reason` citing
the missing tool. Do not treat missing tools as failures.

```bash
# History hygiene
if [ -n "$(git status --porcelain)" ]; then
  echo "DIRTY: working tree has uncommitted changes"
else
  echo "CLEAN: working tree has no uncommitted changes"
fi
base_ref=$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
if [ -z "$base_ref" ]; then
  base_ref=$(git for-each-ref --format='%(symref:short)' 'refs/remotes/*/HEAD' | sed -n '1p')
fi
if [ -n "$base_ref" ] && git rev-parse --verify "$base_ref" >/dev/null 2>&1; then
  git rev-list --count "$base_ref"..HEAD
else
  echo "base reference unavailable"
fi

# Shell correctness
find . -name '*.sh' -not -path '*/node_modules/*' -not -path '*/.git/*' \
  -exec shellcheck {} \; 2>&1 | grep -c 'SC[0-9]*:' || true

# Version alignment
python3 - <<'PY'
import json
import pathlib
import re

versions = {}

package_json = pathlib.Path("package.json")
if package_json.exists():
    try:
        data = json.loads(package_json.read_text())
        if isinstance(data.get("version"), str):
            versions["package.json"] = data["version"]
    except Exception as exc:
        versions["package.json"] = f"unreadable:{exc.__class__.__name__}"

def load_toml(path):
    try:
        import tomllib
    except ModuleNotFoundError:
        return None
    try:
        return tomllib.loads(path.read_text())
    except Exception:
        return None

pyproject = pathlib.Path("pyproject.toml")
if pyproject.exists():
    data = load_toml(pyproject)
    version = None
    if data:
        version = data.get("project", {}).get("version")
        version = version or data.get("tool", {}).get("poetry", {}).get("version")
    if not version:
        match = re.search(r'(?m)^version\s*=\s*["\']([^"\']+)["\']', pyproject.read_text())
        version = match.group(1) if match else None
    if version:
        versions["pyproject.toml"] = version

cargo = pathlib.Path("Cargo.toml")
if cargo.exists():
    data = load_toml(cargo)
    version = data.get("package", {}).get("version") if data else None
    if not version:
        text = cargo.read_text()
        package_block = re.search(r'(?ms)^\[package\](.*?)(?:^\[|\Z)', text)
        if package_block:
            match = re.search(r'(?m)^version\s*=\s*["\']([^"\']+)["\']', package_block.group(1))
            version = match.group(1) if match else None
    if version:
        versions["Cargo.toml"] = version

if len(versions) < 2:
    print(f"SKIP: fewer than two version sources found: {versions}")
elif len(set(versions.values())) == 1:
    print(f"PASS: versions aligned: {versions}")
else:
    print(f"DRIFT: {versions}")
PY

# Tag/release integrity
git tag --list 'v*' --sort=-version:refname | head -5
if [ "${REPO_HEALTH_VERIFY_RELEASES:-0}" = "1" ]; then
  gh release list --limit 5 2>/dev/null || echo "GitHub release query failed"
else
  echo "SKIP: GitHub release query requires REPO_HEALTH_VERIFY_RELEASES=1"
fi

# Commit quality (same as Step 1 — already observed)
# Just reach a judgment from what you already read

# CI efficiency
grep -c 'paths:' .github/workflows/*.yml 2>/dev/null && echo "scoped" \
  || echo "unscoped"

# Cross-platform shell
grep -n 'which\|grep -P\|sed -i[^.]' scripts/*.sh 2>/dev/null \
  | head -10 || echo "no patterns found"

# Attribution drift + secret scan. Print counts/status only, never message text.
base_ref=$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
if [ -z "$base_ref" ]; then
  base_ref=$(git for-each-ref --format='%(symref:short)' 'refs/remotes/*/HEAD' | sed -n '1p')
fi
if [ -n "$base_ref" ] && git rev-parse --verify "$base_ref" >/dev/null 2>&1; then
  range="$base_ref..HEAD"
else
  range=""
  echo "SKIP: commit metadata scan requires an upstream or remote-default base"
fi
if [ -n "$range" ]; then
  printf 'coauthored_trailers=%s\n' "$(git log --format='%B' "$range" 2>/dev/null | grep -c '^Co-authored-by:' || true)"
  if git log --format='%B' "$range" 2>/dev/null \
    | grep -Eq '(api[_-]?key|secret|token|password|passwd|credential)[[:space:]]*[:=][[:space:]]*[A-Za-z0-9_-]{20,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[oprsu]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|sk-[A-Za-z0-9_-]{20,}|https?://[^[:space:]/:@]+:[^[:space:]@]+@'; then
    echo "SECRET-LIKE VALUE: commit metadata contains a potential credential"
  else
    echo "No secret-like values detected in commit metadata"
  fi
fi

# .gitignore coverage — use Git's matcher so negations are respected
for pat in '.DS_Store' 'node_modules/' '__pycache__/' '.vscode/'; do
  git check-ignore --no-index "$pat" >/dev/null 2>&1 || echo "MISSING: $pat"
done
# Secret-bearing patterns — use git check-ignore to handle negations correctly
for f in .env .env.local .env.production; do
  git check-ignore --no-index "$f" >/dev/null 2>&1 || echo "MISSING: $f (not ignored)"
done
# Ignoring a file does not protect a copy that is already tracked.
tracked_sensitive=$(git ls-files -- .env '.env.*' | grep -Ev '^\.env(?:\..*)?\.example$' | wc -l)
printf 'tracked_sensitive_env_files=%s\n' "$tracked_sensitive"
```

Secret-pattern matching is heuristic, not proof that a repository is clean. If
the repo profile identifies a project-native secret scanner, prefer its existing
read-only check; use its documented quiet or redacted mode, or capture only its
exit status when output may contain matches. Do not install or configure a new
scanner during an audit. Test additional sensitive filenames such as `.npmrc`
or `.pypirc` only when observed ecosystem evidence makes them relevant, and
report counts or paths, never values.

Run only the commands for dimensions you deemed relevant. Skip the rest.
Do not emit PASS/WARNING/BLOCKING for skipped dimensions — they do not
apply to this repo.

## Step 3: Report findings with judgment, not labels

**Redaction rule:** Never include raw credential values, tokens, keys, or
secret-bearing URLs in findings. Report only:
- Dimension name
- Finding summary (e.g., "hard-coded credential in config.py")
- Concrete harm
- Remediation
- Confidence (0–1)

For each active dimension, report what you found. Do not use a
pre-defined severity scale. Use language that reflects actual harm:

```text
SHELL CORRECTNESS — 3 scripts, 6 warnings
  shellcheck reports SC2086 (unquoted var) in scripts/deploy.sh:17
  This causes silent failure when a path contains spaces.
  Remediation: wrap "$var" consistently. 5-minute fix.

VERSION ALIGNMENT — DRIFT
  package.json says 1.3.0, pyproject.toml says 1.2.0
  Publishing now would release inconsistent metadata.
  Remediation: cross-reference the latest tag and align both files.
```

If all active dimensions are healthy, report one line such as
`PASS — 4 dimensions checked, all healthy.`

Report blocking findings first, then continue safe read-only checks for remaining
active dimensions. Stop only when the finding requires human remediation before
any further probing is meaningful.

Structured output is an output mode, not a health dimension. Do not include it
in the dimension plan. Emit JSONL only when `REPO_HEALTH_OUTPUT=jsonl` is set;
otherwise use the normal human-readable report.

If any finding contains sensitive values (API keys, tokens, passwords,
connection strings, private URLs), **redact the value before including it in
the report**. Flag the presence of a potential secret without exposing the
secret itself — e.g. "a hard-coded credential was found in config.py" not
"API_KEY = sk-1234...".

Credentials, tokens, private keys, sensitive values, and secret-bearing URLs
must not appear in commit subjects or bodies. If secret-like material is found
in tracked files or commit metadata, do not print it. Report only its location
or existence, stop before lower-priority checks, and recommend revocation or
rotation. Adding a path to `.gitignore` or deleting it from the current tree
does not remove historical exposure.

When recommending `.gitignore` changes, preserve existing project-specific and
security rules, prefer targeted additions over wholesale replacement, retain a
sanitized `!.env.example` when used, and avoid broad `*.key` or `*.pem` rules
without checking for intentional public certificates or fixtures. Treat
lockfile policy as an application-versus-library decision, not a generic ignore.

Example JSONL output:
```jsonl
{"dimension":"version_alignment","finding":"pyproject=1.2.0 Cargo=1.1.0","harm":"stale release","remediation":"sync to 1.2.0","confidence":0.95}
```

---

## Optional: Pre-flight contract

Some repos carry a `.repo-health.json` at the root. When present, it
overrides the heuristic discovery in Step 2. Schema:
[`schemas/repo-health-config.schema.json`](../schemas/repo-health-config.schema.json)
(maintainer-side evidence).

```json
{
  "skip": ["shell-correctness"],
  "require": ["custom-consistency-check"],
  "version_sources": ["pyproject.toml"],
  "commit_format": {"type": "conventional", "required_fields": ["what", "why"]}
}
```

Inspect only settings needed for the plan; do not echo the full file into the
transcript, and redact sensitive values. Merge the settings into the dimension
list. A custom required check replaces the default probe for that dimension.

---

## References

- [JSON Schemas Reference](references/json-schemas.md) — versioned schemas for optional interfaces
- [REPO PROFILE Template](references/repo-profile-template.md) — copy-paste template for Step 1
- [Eval Fixtures Reference](references/eval-fixtures.md) — deterministic behavioral contract fixtures

---

## Completion contract

Before delivering the report, confirm that:

- the profile preceded all dimension probes and separates observations from
  inferences;
- the plan accounts for every candidate dimension, cites activation evidence,
  and does not report skipped dimensions as healthy;
- checks and findings concern the shipped repository surface, not unrelated
  maintainer tooling;
- every finding states concrete harm and remediation, with blocking findings
  first;
- JSONL was emitted only when requested;
- secret checks exposed only counts, status, or locations—never raw subjects or
  bodies or sensitive values; and
- sensitive ignore candidates were checked against both ignore rules and
  tracked files.