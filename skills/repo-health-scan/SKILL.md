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
  version: "0.4.0"
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

Use this skill before a release, archive, handoff, project revival, unfamiliar-
repository onboarding, or unclear CI failure. Do not use it for a single-file
edit, narrow bug fix, feature implementation, or automatic fixing. Repositories
without git history receive only a filesystem shape summary. The skill reports
findings and does not mutate the repository.

## Step 1: Discover the repo's shape

Run these probes before judging health. Inspect the repository; do not infer its
shape from its name.

```bash
# What languages and tools does this project actually use?
find . -maxdepth 1 -type f \( -name '*.json' -o -name '*.toml' \
  -o -name '*.yaml' -o -name '*.yml' -o -name '*.cfg' -o -name '*file' \
  -o -name 'Dockerfile' -o -name 'Containerfile' \) -print 2>/dev/null

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
find .github/workflows -type f \( -name '*.yml' -o -name '*.yaml' \) 2>/dev/null | sort | head -20
find .github -type f \( -iname '*release*.yml' -o -iname '*release*.yaml' \) 2>/dev/null | sort | head -20
find . -maxdepth 1 -name '*.sh' 2>/dev/null
find scripts/ -type f \( -name '*.py' -o -name '*.sh' \) 2>/dev/null | sort | head -20

# What's the dependency surface? A manifest is not automatically a release
# version source: classify it below before adding it to the profile. In a Git
# repository, include tracked and non-ignored files so .gitignore is respected;
# otherwise use a pruned filesystem scan that avoids dependency, cache, and
# generated trees.
manifest_name() {
  case "${1##*/}" in
    requirements*.txt|Cargo.toml|go.mod|package.json|pyproject.toml|pom.xml|build.gradle)
      printf '%s\n' "$1"
      ;;
  esac
}
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  while IFS= read -r path; do
    manifest_name "$path"
  done < <(git ls-files -co --exclude-standard)
else
  find . \( -path './.git' -o -path '*/node_modules' -o -path '*/vendor' \
    -o -path '*/.venv' -o -path '*/.ruff_cache' -o -path '*/.pytest_cache' \
    -o -path '*/.mypy_cache' -o -path '*/.pyright' -o -path '*/.tox' \
    -o -path '*/.nox' -o -path '*/.cache' -o -path '*/.npm' \
    -o -path '*/.pnpm-store' -o -path '*/.yarn' -o -path '*/dist' \
    -o -path '*/build' \) -prune -o -type f \( \
    -name 'requirements*.txt' -o -name 'Cargo.toml' -o -name 'go.mod' \
    -o -name 'package.json' -o -name 'pyproject.toml' -o -name 'pom.xml' \
    -o -name 'build.gradle' \) -print 2>/dev/null
fi | sort | head -50

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
in its own message; do not combine that message with the dimension plan.
Do not defer either block into a final JSON response: send the profile message,
then a separate dimension-plan message, before running any dimension probe.

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
  branch_commits_outside_base: integer | null
  working_tree_dirty: boolean
  workflow_files: [string]
  release_files: [string]
  verify_refs: boolean
  verify_releases: boolean

inferred:
  repo_type: string
  release_model: string
  risk_context: string
```

Do not run a dimension-specific command before emitting this block. If you
cannot write it, run more discovery probes.

The profile is a machine-readable contract, not a prose summary. The core
fields (`vcs`, languages, package managers, CI, shell/filesystem signals,
version sources, script surface, and shipped payload) are mandatory. Extended
fields are emitted when their probes apply; use `null`, `false`, or `[]` when a
known extended fact is absent.
Keep scalar fields canonical (`vcs: git`, `ci: null` when no CI is present,
`base_ref: null` when no bounded base resolves); put explanations in the
dimension plan or report, not inside scalar values. `workflow_files` and
`workflow_files` contain workflow paths, while `release_files` contain only
paths whose filename or configuration clearly represents release behavior.
Do not classify every CI workflow as a release file. `version_sources` contains only
release-relevant exact paths (or the special `git tag` source) that the version
probe will parse. Do not include a maintainer-only package, test, or tooling
manifest merely because it has a `version` field. If a package is published
independently, include its manifest and state that release model in `inferred`.

## Step 2: Infer what invariants matter

Given the emitted repo profile, ask: what invariants would break if they
drifted?

The candidate catalog below is **non-exhaustive** — not a universal checklist.
Use these built-in dimensions for ordinary audits; add a custom dimension only
when a repository-specific invariant is clearly necessary and explain why it
cannot be represented by a built-in dimension. Every active dimension must cite
`activated_by` evidence from the profile.

Before running any dimension command, emit a `DIMENSION PLAN` that:

- lists each active dimension with one or more exact profile paths in
  `activated_by`;
- lists each inactive dimension with a concrete `skip_reason`; and
- accounts for every candidate dimension in the catalog as active or skipped.

Keep the dimension plan in its own message, after the profile message and
before any dimension-specific command or final report.

Use paths such as `observed.ci` or `inferred.release_model`. A recorded request
or environment flag may also activate a dimension; an unobserved assumption may
not.

For built-in dimensions, prefer these canonical activation paths: history uses
`observed.vcs`; shell correctness uses `observed.shell_files`; version
alignment uses `observed.version_sources`; tag/release integrity uses
`inferred.release_model` only when it names concrete tag/release evidence (or
an observed tag/release file or opt-in flag); commit quality uses
`observed.recent_commits`; CI efficiency uses `observed.ci`; file coverage uses
`observed.gitignore`; attribution drift uses a positive
`observed.branch_commits_outside_base`; and external reference health uses the
true `observed.verify_refs` opt-in. Cross-platform checks additionally require
inferred platform evidence.

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

| Dimension                 | Activated By                                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------------ |
| history_hygiene           | always                                                                                           |
| shell_correctness         | observed.shell_files                                                                             |
| version_alignment         | len(observed.version_sources) ≥ 2                                                                |
| tag_release_integrity     | concrete `inferred.release_model` evidence, observed tags/release files, or verify_releases=true |
| commit_quality            | observed.recent_commits                                                                          |
| ci_efficiency             | observed.ci                                                                                      |
| cross_platform            | observed.shell_files + inferred.platform_requirements                                            |
| attribution_drift         | observed.branch_commits_outside_base > 0                                                         |
| file_coverage             | observed.gitignore                                                                               |
| external_reference_health | env:REPO_HEALTH_VERIFY_REFS=1                                                                    |

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
if ! command -v shellcheck >/dev/null 2>&1; then
  echo "SKIP: shell_correctness requires shellcheck"
else
  shell_files=$(find . -name '*.sh' -not -path '*/node_modules/*' -not -path '*/.git/*' -print)
  if [ -z "$shell_files" ]; then
    echo "SKIP: shell_correctness has no shell files"
  else
    find . -name '*.sh' -not -path '*/node_modules/*' -not -path '*/.git/*' \
      -exec shellcheck {} +
  fi
fi

# Version alignment
# Set VERSION_SOURCES to the exact newline-delimited paths recorded in
# observed.version_sources before running this block. Do not substitute
# root-only defaults: monorepos, skill packs, and language workspaces commonly
# keep version metadata in nested or nonstandard files. The parser handles
# JSON/TOML/CFF/frontmatter/Python assignments and the special git-tag source.
VERSION_SOURCES="$(printf '%s\n' 'path/from/profile' 'another/path/from/profile')"
export VERSION_SOURCES

# The portable Python parser runs through this same shell block so the full
# probe sequence remains copy-pasteable as one command block.
python3 - <<'PY'
import json
import os
import re
import subprocess
from pathlib import Path

def extract(path):
    if path == "git tag":
        result = subprocess.run(
            ["git", "tag", "--list", "v*", "--sort=-version:refname"],
            capture_output=True, text=True, check=False,
        )
        return result.stdout.splitlines()[0].removeprefix("v") if result.stdout.strip() else None
    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError:
        return None
    if file_path.suffix == ".json":
        try:
            value = json.loads(text).get("version")
            return value if isinstance(value, str) else None
        except (json.JSONDecodeError, AttributeError):
            return None
    if file_path.suffix in {".toml", ".tml"}:
        try:
            import tomllib
            data = tomllib.loads(text)
            for section in (data.get("project", {}), data.get("package", {}), data.get("tool", {}).get("poetry", {})):
                if isinstance(section, dict) and isinstance(section.get("version"), str):
                    return section["version"]
        except (ModuleNotFoundError, ValueError):
            return None
    match = re.search(r"(?m)^\s*(?:version|__version__)\s*[:=]\s*[\"']?([^\"'\\s#]+)", text)
    return match.group(1) if match else None

sources = [item for item in os.environ.get("VERSION_SOURCES", "").splitlines() if item and not item.startswith("path/")]
values = {source: extract(source) for source in sources}
unreadable = [source for source, value in values.items() if value is None]
comparable = {source: value.removeprefix("v") for source, value in values.items() if value is not None}
if unreadable:
    print(f"UNREADABLE: {unreadable}")
if len(comparable) < 2:
    print(f"SKIP: fewer than two comparable version sources: {list(comparable)}")
elif len(set(comparable.values())) == 1:
    print(f"PASS: versions aligned across {len(comparable)} sources")
else:
    print(f"DRIFT: version sources disagree: {list(comparable)}")
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
workflow_files=$(find .github/workflows -type f \( -name '*.yml' -o -name '*.yaml' \) 2>/dev/null | sort)
if [ -z "$workflow_files" ]; then
  echo "SKIP: ci_efficiency has no workflow files"
else
  while IFS= read -r workflow; do
    if grep -Eq '^[[:space:]]+paths(-ignore)?:' "$workflow"; then
      echo "PASS: $workflow has path filtering"
    else
      echo "INFO: $workflow has no path filtering"
    fi
  done <<< "$workflow_files"
fi

# Automation identity and authority. A bot actor is not a quality guarantee:
# inspect workflow triggers, explicit permissions, pinned actions, and the
# diff. Treat Dependabot PRs as dependency proposals; their PR workflows use
# read-only tokens and normally cannot access repository secrets. Do not
# recommend auto-merge or permission changes without an observed repository
# policy and a reviewable failure mode.
if [ -f .github/dependabot.yml ]; then
  echo "INFO: Dependabot configuration present; inspect grouping, limits, and covered ecosystems"
fi
grep -RInE '^[[:space:]]*permissions:|^[[:space:]]*(pull_request_target|schedule|workflow_dispatch):|^[[:space:]]*uses:' \
  .github/workflows 2>/dev/null | head -40 || true

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

# Tracked-file credential scan. Print paths/counts only; never print matching
# lines or values. Prefer a project-native scanner when the profile identifies
# one, and skip this heuristic when no grep implementation is available.
if command -v git >/dev/null 2>&1; then
  secret_paths=$(git grep -IlE '(^|[^A-Za-z])(api[_-]?key|secret|token|password|passwd|credential)[[:space:]]*[:=][[:space:]]*[A-Za-z0-9_+/=-]{16,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[oprsu]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|sk-[A-Za-z0-9_-]{20,}' -- . ':!*.lock' 2>/dev/null || true)
  if [ -n "$secret_paths" ]; then
    echo "SECRET-LIKE PATHS: $(printf '%s\n' "$secret_paths" | wc -l | tr -d ' ') tracked file(s) require review"
  else
    echo "No secret-like values detected in tracked files"
  fi
fi

# A match in a scanner, fixture, test, or documentation file may be the
# detector pattern itself rather than a credential. Inspect only the path and
# surrounding non-secret context; if the native scanner passes and no literal
# credential exists, report the result as a heuristic false positive or omit it.

# .gitignore coverage — use Git's matcher so negations are respected
for pat in '.DS_Store' 'node_modules/' '__pycache__/' '.vscode/'; do
  git check-ignore --no-index "$pat" >/dev/null 2>&1 || echo "MISSING: $pat"
done
# Secret-bearing patterns — use git check-ignore to handle negations correctly
for f in .env .env.local .env.production; do
  git check-ignore --no-index "$f" >/dev/null 2>&1 || echo "MISSING: $f (not ignored)"
done
# Ignoring a file does not protect a copy that is already tracked.
tracked_sensitive=$(git ls-files -- .env '.env.*' \
  | grep -Evc '^\.env(\..*)?\.example$' || true)
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

For each active dimension, report what you found. Do not use a pre-defined
severity scale; state the concrete harm and the smallest useful remediation.

If all active dimensions are healthy, report one line such as
`PASS — 4 dimensions checked, all healthy.`

Report blocking findings first, then continue safe read-only checks for remaining
active dimensions. Stop only when the finding requires human remediation before
any further probing is meaningful.

Structured output is an output mode, not a health dimension. Do not include it
in the dimension plan. Emit JSONL only when `REPO_HEALTH_OUTPUT=jsonl` is set;
otherwise use the normal human-readable report. Each JSONL finding must match
the maintainer-side `schemas/repo-health-findings.schema.json` contract and
contain only redacted strings, paths, counts, and confidence values. Emit one
line per finding in blocking → warning → info order; emit no finding lines when
the audit is clean. The schema is not a runtime dependency of the shipped
payload.

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

---

## Optional: Pre-flight contract

Some repos carry a `.repo-health.json` at the root. When present, it overrides
the heuristic discovery in Step 2. Its maintainer-side schema is
`schemas/repo-health-config.schema.json`.

Inspect only settings needed for the plan; do not echo the full file into the
transcript, and redact sensitive values. Merge the settings into the dimension
list. A custom required check replaces the default probe for that dimension.

---

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
  tracked files; and
- automation findings distinguished the bot identity, trigger, permissions,
  and reviewed diff from an assumption that a green bot PR is safe.
