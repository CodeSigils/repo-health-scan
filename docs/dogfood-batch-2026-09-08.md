# Eight-repository dogfood comparison

| Field | Value |
| --- | --- |
| Date | `2026-09-08` |
| Runtime | `Codex CLI (local)` |
| Purpose | Exercise the profile-first, evidence-activated audit against four CodeSigils repositories and four external repositories. |

The external repositories were temporary depth-one clones. Their shallow
history and absent tags are clone limitations, not findings about project
history or release practice. No external repository was modified.

## Repositories and observations

| Repository | Observed shape | Useful findings or skips |
| --- | --- | --- |
| `zola-skill` | Docs/static-site skill; no CI, tags, or package manifest; shell and tests present | Correctly keeps CI, version, and tag checks out of scope; focuses on shell/test and file-coverage evidence. |
| `skill-discovery` | Python/uv skill repo; three workflows, release workflow, path filtering, pinned actions | Activates CI, release, dependency, and bot-authority review without treating the runtime payload as the whole repository. |
| `zero-md-formatter` | Node package; two workflows, four shell files; clean diff but dirty working tree | Reports the dirty-tree boundary first; CI has no path filters, which is an efficiency observation rather than an automatic failure. Existing user changes were preserved. |
| `py-review-skill` | Python/uv skill repo; four workflows, path filters; local feature branch without upstream | Reports the missing bounded base and avoids inventing attribution conclusions. |
| `psf/requests` | Python project; eight workflows; explicit permissions and pinned actions | Identifies a broad workflow surface and write-capable issue automation for review; shallow history prevents release conclusions. |
| `pallets/click` | Python/uv monorepo with many example manifests; six workflows; empty default permissions and path filters | Correctly treats examples as workspace structure, not independent releases; flags monorepo and publish workflow inspection as relevant. |
| `astral-sh/ruff` | Large Rust/Python/JS monorepo; 20 workflows, 17 shell files, many workspace manifests | Demonstrates proportionate discovery: workflow/path-filter review is active, while every Cargo manifest is not automatically a version source. |
| `github/gitignore` | Template repository; one stale-issue workflow with write permissions; no package manifest or `.gitignore` | Distinguishes an intentional template shape from missing application files and surfaces the workflow authority for review. |

## Effectiveness assessment

The skill was effective at its primary job: selecting the right questions
before probing. It differentiated a simple no-CI skill repository, a dirty
working tree, a feature branch with no upstream, and two large monorepos. It
also made workflow permissions and bot authority visible without recommending
automatic remediation.

The most valuable behavior was not the number of findings; it was avoiding
false findings. In particular, no-CI in `zola-skill`, no `.gitignore` in the
gitignore template, and many manifests in Ruff were treated as contextual
facts rather than universal defects.

## Coverage limits

- The external clones used depth one, so history, tags, and ancestry require a
  follow-up full clone before making release or attribution claims.
- This batch exercised the deterministic methodology manually; it is not a
  new model-regression baseline.
- No repository required a new profile module or runtime payload change.

## Recommendation

Keep the current payload and CI unchanged. Use this batch as comparative
dogfood evidence, and next repeat one external audit from a full clone only if
history or release integrity is the question being evaluated. Otherwise remain
in maintenance mode and collect evidence from real user requests before adding
dimensions or automation.
