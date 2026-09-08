# Claim and evidence matrix

This maintainer reference is the index for public claims. A claim is limited to
the strongest evidence recorded here; a validator, listing, or one runtime
test must not be presented as proof of a stronger claim.

| Claim | Current state | Evidence | Confidence and boundary |
| --- | --- | --- | --- |
| Payload is structurally portable | `SKILL.md` uses the canonical `skills/<name>/SKILL.md` shape and has no known platform-only runtime dependency. | `skills-ref validate`; `scripts/check-portability.py`; [portability contract](portability-contract.md) | High for structural portability. It does not prove selection or equivalent behavior. |
| Skill is discoverable/installable | Skills CLI 1.5.16 discovers `repo-health-scan` from `skills/`; the documented Skills CLI copy procedure is reproducible. | [Codex compatibility report](compatibility-reports/codex.md); README install procedure | High for the recorded CLI procedure; do not extrapolate to an untested client or version. |
| Codex workflow is verified | The profile-first, evidence-linked dimension plan, read-only audit, and finding contract passed representative Codex runs. | [Codex compatibility report](compatibility-reports/codex.md); [regression record](codex-regression.md) | High for the named, recorded Codex version and payload baseline. A material payload change starts a new baseline. |
| Runtime is read-only | The shipped methodology contains no mutation, privilege escalation, or approval bypass and makes network checks opt-in. | `scripts/check-trust.py`; [SECURITY.md](../SECURITY.md); `SKILL.md` completion contract | High for the instruction contract; the agent and host still control tool permissions. |
| Release is integrity-gated | Tagged releases require main ancestry, successful CI jobs, and a clean tagged diff before the release job writes. | `.github/workflows/release.yml`; `scripts/check-version-consistency.py`; [maintaining guide](maintaining.md) | High for this repository’s current workflow. It does not certify arbitrary downstream packaging. |

## Maintenance rule

When a public README, badge, compatibility report, or release note changes a
claim, update the owning row and its evidence source in the same change. If the
evidence is stale, weaken the claim or mark it unresolved; do not silently
refresh dates across unrelated research.
