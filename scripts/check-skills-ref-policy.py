"""Enforce the skills-ref evidence policy for Agent Skills repositories."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

PINNED_SOURCE = re.compile(r"agentskills\.git@[0-9a-f]{40}", re.IGNORECASE)
VALIDATE_COMMAND = re.compile(r"skills-ref\s+validate", re.IGNORECASE)
CLAIM = re.compile(
    r"agent\s+skills|agentskills\.io|skills\.sh|claude\s+code\s+skill|codex\s+skill",
    re.IGNORECASE,
)
CI_NAMES = {".gitlab-ci.yml", ".gitlab-ci.yaml", "azure-pipelines.yml", "Jenkinsfile"}
MANUAL_FILES = {
    "CONTRIBUTING.md",
    "README.md",
    "docs/release-checklist.md",
    "docs/maintaining.md",
    "docs/README.md",
}


def _text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _skill_paths(root: Path) -> list[Path]:
    paths = sorted(root.glob("skills/*/SKILL.md"))
    direct = root / "SKILL.md"
    if direct.is_file():
        paths.append(direct)
    return paths


def _claim_files(root: Path) -> list[Path]:
    files = [root / "README.md", root / "AGENTS.md", root / "SECURITY.md"]
    files.extend(sorted((root / "docs").glob("**/*.md")) if (root / "docs").is_dir() else [])
    return [p for p in files if p.is_file() and CLAIM.search(_text(p))]


def _ci_files(root: Path) -> list[Path]:
    workflow_dir = root / ".github" / "workflows"
    files = sorted(workflow_dir.glob("*.y*ml")) if workflow_dir.is_dir() else []
    files.extend(root / name for name in CI_NAMES if (root / name).is_file())
    return files


def audit(root: Path) -> list[str]:
    """Return policy violations for one repository root."""
    skills = _skill_paths(root)
    claims = _claim_files(root)
    if not claims:
        return []
    errors: list[str] = []
    if not skills:
        errors.append("Agent Skills compatibility is claimed but no SKILL.md was found")
        return errors

    ci = _ci_files(root)
    ci_text = "\n".join(_text(path) for path in ci)
    if ci:
        if not VALIDATE_COMMAND.search(ci_text):
            errors.append("CI exists but does not run 'skills-ref validate'")
        elif not PINNED_SOURCE.search(ci_text):
            errors.append("CI runs skills-ref but does not pin the agentskills source to a commit")
    else:
        manual = [root / name for name in MANUAL_FILES if (root / name).is_file()]
        manual_text = "\n".join(_text(path) for path in manual)
        if not VALIDATE_COMMAND.search(manual_text):
            errors.append(
                "no CI found; add a pinned 'skills-ref validate' command to the manual release gate"
            )
        elif not PINNED_SOURCE.search(manual_text):
            errors.append("manual gate runs skills-ref but does not pin the agentskills source to a commit")
    return errors


def run_self_tests() -> list[str]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "skills" / "demo").mkdir(parents=True)
        (root / "skills" / "demo" / "SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")
        (root / "README.md").write_text("This is Agent Skills compatible.\n", encoding="utf-8")
        (root / ".github" / "workflows").mkdir(parents=True)
        command = (
            "uvx --from git+https://github.com/agentskills/agentskills.git@"
            "0123456789abcdef0123456789abcdef01234567#subdirectory=skills-ref "
            "skills-ref validate skills/demo\n"
        )
        workflow = root / ".github" / "workflows" / "ci.yml"
        workflow.write_text(command, encoding="utf-8")
        if audit(root):
            return ["valid pinned CI fixture was rejected"]
        workflow.write_text("skills-ref validate skills/demo\n", encoding="utf-8")
        if not audit(root):
            return ["unpinned CI fixture was accepted"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="*", type=Path, default=[Path(".")])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        errors = run_self_tests()
    else:
        errors = []
        for root in args.roots:
            errors.extend(f"{root}: {error}" for error in audit(root.resolve()))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: Agent Skills compatibility claims have skills-ref evidence")
    return 0


if __name__ == "__main__":
    sys.exit(main())
