# Control-justification ledger

> Maintainer-only record. Each recurring control must have a named failure
> mode, evidence, and an explicit cost/coverage decision.

Reviewed: `2026-09-08`
Repository scale: solo maintainer; protected `main`; no mandatory second review.

| Control | Trigger | Failure mode addressed | Evidence | Cost | Decision |
| --- | --- | --- | --- | --- | --- |
| `lint` job | PR, push, schedule, manual | Drift in docs/contracts, unsafe script changes, version mismatch, portability or trust regressions | `scripts/verify.sh`, validators, ShellCheck/Ruff; required on `main` | ~10 min; dependency install | **Retain** as the primary merge gate. |
| `full-verify` job | PR, push, schedule, manual | Fast checks bypassed by workflow or tree-level integration drift | Runs the complete `scripts/verify.sh` after `lint` | ~5 min; serialized after lint | **Retain** because it verifies the aggregate contract. |
| `phase-b-gate` job | PR and push to `main` | Whitespace, dirty-tree, empty-range, or non-conventional authored commits | Caught generated merge-subject false failure; now excludes merge commits in `scripts/check-commit-convention.py` | ~3 min | **Retain**, with merge-commit handling documented and tested. |
| `check-expiry` job | Weekly schedule or manual dispatch | Maintainer references silently exceed their review date | Manual run `34025441454` passed on 2026-09-06; no later scheduled result was observed during the 2026-09-08 audit | ~5 min; external state | **Retain**, but keep out of PR merge gates. |
| `verify-urls` job | Weekly schedule or manual dispatch | Evidence URLs become unavailable or redirect unexpectedly | Local verifier run on 2026-09-08 passed 18/18 URLs; prior manual run `34025441454` passed on 2026-09-06 | ~10 min; transient network failures | **Retain**, retry transient failures, keep out of PR merge gates. |
| Release `verify` job | Version tag push | Tag is not on `main`, or tagged commit lacks successful CI | `.github/workflows/release.yml` checks ancestry and `lint`/`full-verify` | ~10 min per release | **Retain** as supply-chain/release-integrity gate. |
| Release `release` job | After release verification | Duplicate or unsafe GitHub Release creation | Workflow is idempotent for an existing published release and refuses drafts | ~5 min per release | **Retain**; no recurring cost outside releases. |
| Local Codex regression | Manual maintainer evaluation | Model no longer follows profile-first, activation, skip, or finding contracts | Runs 13–15 passed on Codex CLI 0.153.2 | ~2–3 min plus model tokens | **Retain as non-blocking**; run after material payload changes. |

## Review rule

Revisit this ledger when a control fails, causes recurring maintenance friction,
or its protected failure mode no longer exists. Do not add a gate merely because
another repository has one; record the failure mode and evidence first.
