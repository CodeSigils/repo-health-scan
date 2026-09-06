# Agent Skills validation policy

Any repository that claims Agent Skills compatibility must provide
reproducible format evidence with the official `skills-ref` validator.

- Repositories with CI must run `skills-ref validate` in CI and pin the
  `agentskills` source to an immutable commit.
- Repositories intentionally without CI must put the same pinned command in a
  manual release gate (normally `docs/release-checklist.md` or
  `docs/maintaining.md`) and record the result with the release evidence.
- The validator checks format and frontmatter conformance; it does not certify
  runtime behavior, safety, or usefulness.

Run the repository policy check from this repository with:

```bash
python3 scripts/check-skills-ref-policy.py /path/to/repository
```

The check is deliberately evidence-oriented: it detects a compatibility claim,
then verifies the appropriate automated or manual path. A repository with no
compatibility claim is not required to carry this evidence.
