# Skill Portability Contract

**Status:** normative maintainer contract

**Scope:** packaging, adapter, validation, and compatibility claims for this
repository. This file is maintainer documentation and is not part of the
shipped skill payload.

## Contract

### 1. Keep one canonical payload

`skills/repo-health-scan/SKILL.md` is the sole source of runtime
methodology. A platform may add metadata, routing, or packaging around that
file, but it must not maintain a second copy of the methodology.

The canonical payload remains free of agent-specific commands, installation
paths, manifest fields, and compatibility claims.

### 2. Make adapters thin and additive

An adapter may:

- point a platform at the canonical skill directory;
- import or route to an existing authoritative instruction file;
- provide platform-required display, discovery, or packaging metadata.

An adapter must not:

- duplicate the audit procedure or maintainer workflow;
- introduce behavior that applies only when the duplicated copy is used;
- imply that successful parsing or discovery proves workflow compatibility.

Create an adapter only after selecting that platform as an active target and
identifying a concrete platform requirement. Prefer imports, paths, and
manifests over copied prose.

### 3. Separate three kinds of evidence

Use these terms consistently:

| Claim                        | Required evidence                                                                                         |
| :--------------------------- | :-------------------------------------------------------------------------------------------------------- |
| **Payload portable**         | The canonical files use the documented skill shape and contain no known platform-only runtime dependency. |
| **Discoverable/installable** | A named platform and version can locate or install the skill through a recorded procedure.                |
| **Workflow verified**        | That platform completes representative positive and negative tasks and satisfies the behavioral contract. |

Evidence for one level does not establish the next. In particular, a shared
directory convention, successful validator, or marketplace listing does not
prove selection, instruction adherence, or equivalent output.

### 4. Validate structure deterministically

Use fast deterministic checks for properties that do not require a model:

- canonical file location and valid frontmatter;
- manifest and routing paths;
- absence of duplicated payload instructions;
- evaluation fixture and schema integrity;
- trust boundaries and version consistency.

Do not use repeated model calls to prove facts that a parser, schema, or file
comparison can establish.

### 5. Certify behavior per runtime

A runtime compatibility report must identify:

- agent/runtime name and exact tested version;
- test date and installation or discovery path;
- whether explicit and implicit selection were tested;
- representative positive and negative tasks;
- raw or reproducible evidence and grading criteria;
- tool, authentication, sandbox, or platform limitations;
- the resulting compatibility status.

Keep model evidence separate from deterministic validation. A material change
to `SKILL.md`, the prompt, grader, or behavioral schema starts a new evidence
baseline; older results remain historical evidence.

Do not extrapolate a successful result to untested agents or later versions.

### 6. Scope automation to demonstrated reuse

Keep runtime-specific runners and graders close to the compatibility report
they support. Extract a generic cross-agent harness only after at least two
repositories require the same input contract, lifecycle, and grading behavior.

Until then, reuse the contract and fixture vocabulary rather than building a
universal runner. Adding a new runtime means adding one thin adapter and one
scoped certification path, not retesting every known agent.

## Compatibility states

Use the narrowest state supported by current evidence:

| State               | Meaning                                                                  |
| :------------------ | :----------------------------------------------------------------------- |
| `candidate`         | The payload appears structurally suitable; runtime behavior is untested. |
| `install_verified`  | Installation or discovery succeeded; workflow behavior is untested.      |
| `workflow_verified` | Representative behavioral tests passed for the recorded runtime version. |
| `limited`           | Testing found a documented runtime or workflow limitation.               |
| `unsupported`       | A known incompatibility prevents the supported workflow.                 |

Avoid `compatible`, `universal`, or `agent-agnostic` without a qualifier. State
the runtime, version, evidence level, and date instead.

## Adding another agent

1. Select the agent as an active compatibility target.
2. Confirm the canonical payload can remain unchanged.
3. Add only the smallest required adapter or setup documentation.
4. Run deterministic packaging and trust checks.
5. Execute representative positive and negative behavioral tests.
6. Record results in `docs/compatibility-reports/<agent>.md`.
7. Update public support claims only to the evidence level achieved.

If step 2 fails, document the incompatibility before changing the portable
methodology. A platform-specific convenience does not by itself justify
expanding the canonical payload.

## Non-goals

This contract does not promise identical outputs across models, installers, or
agent products. It does not require a matrix covering every agent, and it does
not make hosted model evaluation a blocking check for ordinary changes.

The goal is a portable source of truth with explicit, evidence-bounded runtime
support—not universal behavioral equivalence.
