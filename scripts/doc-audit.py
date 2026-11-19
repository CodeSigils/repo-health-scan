"""doc-audit.py — Manifest-driven documentation completeness checker.

Reads a JSON manifest declaring required patterns in documentation files
and checks each file against its requirements. Exit 0 if all pass, non-zero
with failure details otherwise.

Usage:
    python3 scripts/doc-audit.py               # default: docs/doc-standards.json
    python3 scripts/doc-audit.py --self-test   # verify manifest + self-integrity

"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit

from _common import read_json

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^]]*]\(([^)\s]+)(?:\s+[^)]*)?\)")
EXTERNAL_SCHEMES = {"data", "http", "https", "mailto", "tel"}


def load_manifest(manifest_path: Path) -> dict:
    """Load and return the JSON manifest as a dict."""
    return read_json(manifest_path)


def check_regex(filepath: Path, pattern: str) -> bool:
    """Return True if pattern (as regex) matches anywhere in filepath."""
    if not filepath.exists():
        return False
    content = filepath.read_text(encoding="utf-8")
    return bool(re.search(pattern, content))


def check_contains_all(filepath: Path, items: list[str]) -> bool:
    """Return True if all items appear as literal substrings in filepath."""
    if not filepath.exists():
        return False
    content = filepath.read_text(encoding="utf-8")
    return all(item in content for item in items)


def check_not_regex(filepath: Path, pattern: str) -> bool:
    """Return True if pattern does not match anywhere in filepath."""
    if not filepath.exists():
        return False
    content = filepath.read_text(encoding="utf-8")
    return not bool(re.search(pattern, content))


def heading_anchors(filepath: Path) -> set[str]:
    """Return GitHub-style anchors for ATX headings in a Markdown file."""
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for line in filepath.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)(?:\s+#+)?$", line)
        if match is None:
            continue
        text = re.sub(r"\[([^]]+)]\([^)]+\)", r"\1", match.group(1))
        slug = re.sub(r"[^\w\- ]", "", text.casefold()).replace(" ", "-")
        slug = re.sub(r"-+", "-", slug).strip("-")
        if not slug:
            continue
        occurrence = counts.get(slug, 0)
        counts[slug] = occurrence + 1
        anchors.add(slug if occurrence == 0 else f"{slug}-{occurrence}")
    return anchors


def tracked_markdown(repo_root: Path) -> list[Path]:
    """Return the repository's Markdown files, preferring the git index.

    An untracked scratch file in a developer checkout is not part of the
    documentation contract, so it must not fail the audit. Outside a git
    work tree (the self-test fixture) fall back to a filesystem walk.
    """
    listed = subprocess.run(
        ["git", "ls-files", "-z", "*.md"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if listed.returncode != 0:
        return sorted(p for p in repo_root.rglob("*.md") if ".git" not in p.parts)
    return [repo_root / name for name in sorted(listed.stdout.split("\0")) if name]


def check_markdown_links(repo_root: Path) -> list[str]:
    """Return invalid repository-relative Markdown link descriptions."""
    errors: list[str] = []
    for source in tracked_markdown(repo_root):
        content = source.read_text(encoding="utf-8")
        for destination in MARKDOWN_LINK_RE.findall(content):
            parsed = urlsplit(destination)
            if parsed.scheme.casefold() in EXTERNAL_SCHEMES or destination.startswith("//"):
                continue
            target_path = unquote(parsed.path)
            target = source.parent / target_path if target_path else source
            resolved = target.resolve()
            try:
                resolved.relative_to(repo_root)
            except ValueError:
                errors.append(f"{source.relative_to(repo_root)}: link escapes repository: {destination}")
                continue
            if not resolved.exists():
                errors.append(f"{source.relative_to(repo_root)}: missing link target: {destination}")
                continue
            if parsed.fragment and resolved.is_file() and resolved.suffix.casefold() == ".md":
                anchor = unquote(parsed.fragment).casefold()
                if anchor not in heading_anchors(resolved):
                    errors.append(f"{source.relative_to(repo_root)}: missing anchor: {destination}")
    return errors


def run_checks(manifest_path: Path, repo_root: Path) -> tuple[int, int]:
    """Run all checks defined in manifest_path against repo_root files.

    Returns (passed: int, failed: int).
    """
    manifest = load_manifest(manifest_path)

    passed = 0
    failed = 0

    for filename, checks in manifest.items():
        filepath = repo_root / filename
        for check in checks:
            cid = check["id"]
            desc = check.get("description", cid)
            ctype = check.get("type", "regex")

            if ctype == "regex":
                ok = check_regex(filepath, check["pattern"])
            elif ctype == "not-regex":
                ok = check_not_regex(filepath, check["pattern"])
            elif ctype == "contains-all":
                ok = check_contains_all(filepath, check["items"])
            else:
                print(f"  FAIL  Doc: {desc} ({cid}) — unknown type '{ctype}'")
                failed += 1
                continue

            if ok:
                print(f"  PASS  Doc: {desc}")
                passed += 1
            else:
                print(f"  FAIL  Doc: {desc} ({cid})")
                failed += 1

    link_errors = check_markdown_links(repo_root)
    if link_errors:
        for error in link_errors:
            print(f"  FAIL  Links: {error}")
        failed += len(link_errors)
    else:
        print("  PASS  Links: repository-relative Markdown targets and anchors")
        passed += 1

    return passed, failed


def self_test() -> int:
    """Validate manifest schema and self-integrity. Exit 0 on success."""
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    manifest_path = repo_root / "docs" / "doc-standards.json"

    if not manifest_path.exists():
        print(f"  FAIL  Self-test: manifest not found at {manifest_path}")
        return 1

    manifest = load_manifest(manifest_path)

    if not isinstance(manifest, dict):
        print("  FAIL  Self-test: manifest must be a JSON object")
        return 1

    for filename, checks in manifest.items():
        if not isinstance(checks, list):
            print(f"  FAIL  Self-test: checks for '{filename}' must be a list")
            return 1
        for check in checks:
            if "id" not in check or "type" not in check:
                print(f"  FAIL  Self-test: check in '{filename}' missing 'id' or 'type'")
                return 1
            if check["type"] in {"regex", "not-regex"}:
                if "pattern" not in check:
                    print(f"  FAIL  Self-test: {check['type']} check '{check['id']}' missing 'pattern'")
                    return 1
                try:
                    re.compile(check["pattern"])
                except re.error as e:
                    print(f"  FAIL  Self-test: {check['type']} check '{check['id']}' invalid: {e}")
                    return 1
            elif check["type"] == "contains-all" and ("items" not in check or not isinstance(check["items"], list)):
                print(f"  FAIL  Self-test: contains-all check '{check['id']}' missing 'items' list")
                return 1

    with TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "target.md").write_text("# Target heading\n", encoding="utf-8")
        (root / "source.md").write_text(
            "[valid](target.md#target-heading)\n[missing target](missing.md)\n"
            "[missing anchor](target.md#missing-heading)\n",
            encoding="utf-8",
        )
        errors = check_markdown_links(root)
        if errors != [
            "source.md: missing link target: missing.md",
            "source.md: missing anchor: target.md#missing-heading",
        ]:
            print("  FAIL  Self-test: Markdown link validation")
            return 1

    print("  PASS  Self-test: doc-audit.py manifest and Markdown link validation valid")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()

    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    manifest_path = repo_root / "docs" / "doc-standards.json"

    if not manifest_path.exists():
        print(f"  FAIL  Manifest not found: {manifest_path}")
        return 1

    passed, failed = run_checks(manifest_path, repo_root)
    print(f"  ({passed}/{passed + failed} doc checks pass)")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
