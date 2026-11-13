# Control-justification ledger

> Maintainer-only record. Each recurring control must have a named failure
> mode, evidence, and an explicit cost/coverage decision.

Reviewed: `2026-10-03`
Repository scale: solo maintainer; `main` accepts administrator direct pushes;
no mandatory second review. The configured local pre-push hook is the
direct-push gate. GitHub required checks and signatures remain PR-merge
protection and post-push evidence because administrator enforcement is disabled.

| Control | Trigger | Failure mode addressed | Evidence | Cost | Decision |
| --- | --- | --- | --- | --- | --- |
| `lint` job | PR, push, schedule, manual | Drift in docs/contracts, unsafe script changes, portability, trust, or duplicated-workflow definitions | `scripts/verify.sh --self-test`, validators, ShellCheck/Ruff, and `check-python-range-parity.py`; required context on `main` | ~10 min timeout, ~12 s actual (run `36846473400`) | **Retain** as the primary CI backstop, pinned to the 3.13 floor. It gates PR merges but not administrator direct pushes. Not a matrix and not a reusable-workflow caller: both rename the reported check, and `main` requires the literal context `lint`. |
| `python-range` job | PR, push, schedule, manual | The payload breaks on a release `requires-python` admits but CI never tests | The Python-sensitive validation set runs against 3.14; the parity checker prevents the duplicated job from silently testing a different command set | ~12 s, in parallel with `lint` | **Retain** as a required context. Checking only the floor leaves `>=3.13` half-promised; like every required context, it gates PR merges but not administrator direct pushes. |
| `full-verify` job | PR, push, schedule, manual | Tree-level integration drift after the required `lint` gate | Runs `scripts/verify.sh --after-lint`, retaining the tree, stale-reference, and full documentation checks without repeating `lint` checks | ~5 min; serialized after lint | **Retain** as a required CI backstop. It is a merge gate for PRs; the local pre-push hook covers direct pushes. |
| `phase-b-gate` job | PR and push to `main` | Whitespace, dirty-tree, empty-range, or non-conventional authored commits | Caught generated merge-subject false failure; now excludes merge commits in `scripts/check-commit-convention.py`; the same range check runs before direct pushes | ~3 min | **Retain** as a required CI backstop, with merge-commit handling documented and tested. |
| `verify-urls` job | Weekly schedule or manual dispatch | Evidence URLs become unavailable or redirect unexpectedly | Local verifier run on 2026-09-08 passed 18/18 URLs; prior manual run `34025441454` passed on 2026-09-06 | ~10 min; transient network failures | **Retain**, retry transient failures, keep out of PR merge gates. |
| Local Codex regression | Manual maintainer evaluation | Model no longer follows profile-first, activation, skip, or finding contracts | Runs 13–15 passed on Codex CLI 0.153.2 | ~2–3 min plus model tokens | **Retain as non-blocking**; run after material payload changes. |

## Review rule

Revisit this ledger when a control fails, causes recurring maintenance friction,
or its protected failure mode no longer exists. Do not add a gate merely because
another repository has one; record the failure mode and evidence first.

## Removed controls

| Control | Removed | Reason |
| --- | --- | --- |
| Release `verify` job | 2026-10-01 | Ran three times for `v0.4.0` while the tag was force-moved between attempts; two of the three runs failed at the step whose purpose was idempotence. Its protected failure mode was a tag-integrity concern that protected `main` already covers more reliably. |
| Release `release` job | 2026-10-01 | Only ran after a release cadence that had already stalled, and the published `v0.4.0` predates the payload rename, so the smoke test it was meant to gate did not gate it. |
| `check-expiry` job | 2026-10-03 | No monitored file declared an expiry date, and `--strict` only emitted missing dates as notes. The control could not detect the stated failure mode; `verify-urls` remains the evidence-staleness control. |

`main` is now the distribution channel. See [MAINTENANCE.md](MAINTENANCE.md) for
what replaced the release procedure.
