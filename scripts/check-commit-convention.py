"""
check-commit-convention.py — Validate commit subject prefixes against the documented convention.

Reads commit subjects from a git revision range and fails if any subject does
not start with an allowed conventional-commit prefix. This is the automated
enforcement half of the "Commit convention" section in docs/maintaining.md.

Usage:
    python3 scripts/check-commit-convention.py                  # check origin/main..HEAD
    python3 scripts/check-commit-convention.py --range A..B     # check an explicit range
    python3 scripts/check-commit-convention.py --self-test      # run internal self-tests
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Callable

# The documented, actively-used subject prefixes. `type(scope):` is also valid,
# e.g. `chore(deps):` from dependabot. The offline historical prefixes
# (what:, changelog:, sync:, flatten:, dev:) are intentionally NOT included;
# they predate the settled convention and, because tag v0.2.0 (commit 74d2082)
# carries a `what:` subject, they are not rewritten.
ALLOWED_PREFIXES = ("feat", "docs", "refactor", "fix", "chore", "ci", "test")

# Special-case subjects that are exempt from prefix rules.
EXEMPT_EXACT = {"Revert", "merge"}
REVERT_RE = re.compile(r"^Revert\s")


def _subject_ok(subject: str) -> bool:
    """Return True if a single commit subject conforms to the convention."""
    s = subject.strip()
    if not s:
        return False
    if REVERT_RE.match(s):
        return True
    # type: or type(scope):  (scope is any alphanumeric + -_ . / )
    if re.match(r"^[a-z]+(\([a-z0-9\-_./]+\))?:\s", s):
        prefix = s.split(":", 1)[0]
        p = prefix.split("(", 1)[0]
        return p in ALLOWED_PREFIXES
    return s in EXEMPT_EXACT


def _git_subjects(rev_range: str) -> list[str]:
    """Return commit subjects for a git revision range via `git log`."""
    proc = subprocess.run(
        ["git", "log", f"{rev_range}", "--format=%s"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git log failed: {proc.stderr.strip()}")
    return [line for line in proc.stdout.splitlines() if line.strip()]


def check_range(
    rev_range: str,
    subjects_getter: Callable[[str], list[str]] = _git_subjects,
) -> list[str]:
    """Validate all subjects in a range. Returns a list of offending subjects."""
    try:
        subjects = subjects_getter(rev_range)
    except RuntimeError as exc:
        return [f"unable to read commit range {rev_range}: {exc}"]
    return [s for s in subjects if not _subject_ok(s)]


def run_self_tests() -> int:
    """Run internal self-tests for the validation logic."""
    cases = [
        ("feat: add audit dimension", True),
        ("docs: update README", True),
        ("refactor: extract helper", True),
        ("fix: correct table formatting", True),
        ("chore: housekeeping", True),
        ("ci: add lint job", True),
        ("test: cover parser", True),
        ("chore(deps): bump ruff to 0.16.3", True),
        ("fix(ci): correct portability path", True),
        ("Revert \"feat: add audit dimension\"", True),
        ("Revert \"docs: update README\"", True),
        # Historical / off-list prefixes must FAIL so future drift is caught.
        ("what: fix table formatting", False),
        ("changelog: tighten entry", False),
        ("sync: sync root scripts", False),
        ("flatten: merge docs", False),
        ("dev: add pre-commit hook", False),
        ("B2: add shellcheck guard", False),
        ("no prefix here", False),
        ("", False),
    ]

    for subject, should_ok in cases:
        result = _subject_ok(subject)
        if result != should_ok:
            status = "OK" if result else "FAIL"
            print(
                f"FAIL: subject {subject!r} → {status} (expected "
                f"{'OK' if should_ok else 'FAIL'})"
            )
            return 1

    print("PASS: check-commit-convention.py self-tests")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate commit subject prefixes against the documented convention"
    )
    parser.add_argument(
        "--range",
        default="origin/main..HEAD",
        help="git revision range to check (default: origin/main..HEAD)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run internal self-tests",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_tests()

    violations = check_range(args.range)
    for v in violations:
        print(f"CONVENTION: {v}", file=sys.stderr)
    if violations:
        print(
            f"BLOCKING: {len(violations)} commit subject(s) violate the "
            "subject convention (see docs/maintaining.md)",
            file=sys.stderr,
        )
        return 1
    print(f"PASS: all commit subjects in {args.range} follow the convention")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
