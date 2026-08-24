# Codex Setup

Status: verified with Codex CLI 0.149.0 on 2026-08-24. The 0.133.0 setup
reproduction remains historical evidence in the compatibility report.

This guide separates repository-local skill authoring from plugin distribution.
The skill itself ships as one `SKILL.md`; the plugin manifest packages that
payload for installation without making maintainer scripts part of the runtime.

## Requirements

- An authenticated Codex CLI installation.
- A clone of this repository.
- A git repository in which to test implicit skill discovery.

Confirm the tested CLI surface:

```bash
codex --version
```

Later Codex versions may remain compatible, but they are not covered by this
recorded test until the compatibility report and regression evidence are
refreshed.

## Repository-Local Skill

Use this path for development or for one repository. Codex scans
`.agents/skills` from the current directory up to the repository root.

```bash
SKILL_REPO=/absolute/path/to/repo-health-and-sync-skill
TARGET_REPO=/absolute/path/to/target-repository

mkdir -p "$TARGET_REPO/.agents/skills"
cp -R "$SKILL_REPO/skills/repo-health-and-sync-skill" \
  "$TARGET_REPO/.agents/skills/"
cd "$TARGET_REPO"
codex
```

Use a symlink instead of `cp -R` during skill development when immediate local
updates are useful. Codex supports symlinked skill folders.

### Verify Discovery

Start a new Codex session in the target repository and use a prompt that does
not name the skill:

```text
Audit this repository before release. Before running repository probes,
identify and read any installed skill relevant to this request. State the
selected skill and summarize its three-step workflow, then stop without
performing the audit or modifying files.
```

The response must select `repo-health-scan`, read its `SKILL.md`, and summarize
Discover -> Infer -> Report. If it does not appear, confirm the path and restart
Codex after changing the skill installation.

## Local Plugin Distribution Test

Use this path to test the packaged plugin. A plugin root is not itself a
marketplace root, so create a small local marketplace containing only the
manifest and shipped skill payload:

```bash
SKILL_REPO=/absolute/path/to/repo-health-and-sync-skill
MARKETPLACE_ROOT="$(mktemp -d)"
PLUGIN_ROOT="$MARKETPLACE_ROOT/plugins/repo-health-and-sync-skill"

mkdir -p "$MARKETPLACE_ROOT/.agents/plugins" "$PLUGIN_ROOT"
cp -R "$SKILL_REPO/.codex-plugin" "$PLUGIN_ROOT/"
cp -R "$SKILL_REPO/skills" "$PLUGIN_ROOT/"

cat >"$MARKETPLACE_ROOT/.agents/plugins/marketplace.json" <<'JSON'
{
  "name": "repo-health-local",
  "interface": {
    "displayName": "Repo Health Local"
  },
  "plugins": [
    {
      "name": "repo-health-and-sync-skill",
      "source": {
        "source": "local",
        "path": "./plugins/repo-health-and-sync-skill"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
JSON

codex plugin marketplace add "$MARKETPLACE_ROOT"
codex plugin add repo-health-and-sync-skill --marketplace repo-health-local
codex plugin list --marketplace repo-health-local
```

The final command must show
`repo-health-and-sync-skill@repo-health-local` as installed and enabled. Run the
implicit discovery prompt above in a new session to verify model activation.
Do not pass `--ignore-user-config` during this check: that diagnostic option
also suppresses installed-plugin configuration from the selected `CODEX_HOME`.

Remove the temporary marketplace after testing. Use
`codex plugin marketplace remove repo-health-local` when the marketplace should
also be removed from Codex configuration.

## Runtime Options

The scan remains read-only by default. Network and structured-output behavior
is opt-in:

| Variable | Effect |
|---|---|
| `REPO_HEALTH_VERIFY_RELEASES=1` | Permit GitHub release queries. |
| `REPO_HEALTH_VERIFY_REFS=1` | Permit external-reference checks. |
| `REPO_HEALTH_OUTPUT=jsonl` | Request JSONL output. |

## Evidence and Sources

- [Codex compatibility report](compatibility-reports/codex.md) records the
  isolated install, implicit discovery, and workflow-conformance results.
- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills) documents
  `.agents/skills`, implicit invocation, and symlink support.
- [OpenAI: Build plugins](https://learn.chatgpt.com/docs/build-plugins)
  documents plugin manifests, marketplace metadata, and CLI marketplace setup.
- [Addy Osmani: agent-skills](https://github.com/addyosmani/agent-skills) is
  comparative evidence for keeping shared skill content separate from focused
  per-agent setup guides and verification instructions.
