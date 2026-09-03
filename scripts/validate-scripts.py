"""Validate script quality for repo-health scripts."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

# Regex matching a standalone self-test entry point. Must stay in sync with
# REQUIRED_PATTERNS below so discovery and validation agree on what counts.
SELF_TEST_RE = re.compile(r"def (?:do_self_test|run_self_tests|check_self_test|self_test)\(")

ALL_SCRIPTS = sorted(
    p.name for p in SCRIPTS_DIR.iterdir()
    if p.is_file() and (p.suffix in (".py", ".sh")) and not p.name.startswith("_")
)

REQUIRED_PATTERNS = [
    (SELF_TEST_RE.pattern, "missing --self-test function"),
    (r"if __name__ == \"__main__\"", "missing main entry point"),
]

FORBIDDEN_PATTERNS = [
    (r"except:\s*$", "bare except: clause"),
    (r"except Exception:\s*pass", "catch-all pass"),
    (r"subprocess\.run\([^)]*shell=True", "shell=True without justification"),
]

SHELL_SCRIPTS = {"verify.sh"}


def _py_scripts_with_self_test() -> list[str]:
    """Auto-discover Python scripts that declare a self-test entry point.

    Excludes the current harness module, which declares `run_self_tests` but
    must not be invoked by itself (that would recurse into this very loop).
    """
    self_name = Path(__file__).name
    return sorted(
        p.name
        for p in SCRIPTS_DIR.iterdir()
        if p.is_file()
        and p.suffix == ".py"
        and p.name != self_name
        and not p.name.startswith("_")
        and SELF_TEST_RE.search(p.read_text(encoding="utf-8"))
    )


def check_script(script_path: Path) -> list[str]:
    """Check a single script for quality issues."""
    errors = []
    content = script_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Skip Python-specific checks for shell scripts
    if script_path.suffix == ".sh":
        if not lines[0].startswith("#!/usr/bin/env bash"):
            errors.append(f"{script_path.name}: missing #!/usr/bin/env bash shebang")
        if "set -euo pipefail" not in content:
            errors.append(f"{script_path.name}: missing 'set -euo pipefail'")
        return errors

    # Python script checks
    for pattern, msg in REQUIRED_PATTERNS:
        if not re.search(pattern, content):
            errors.append(f"{script_path.name}: {msg}")

    for pattern, msg in FORBIDDEN_PATTERNS:
        if re.search(pattern, content):
            errors.append(f"{script_path.name}: {msg}")

    # Check for encoding on open() calls (but not urllib.request.urlopen)
    open_calls = re.findall(r"open\([^)]+\)", content)
    for call in open_calls:
        for i, line in enumerate(lines, 1):
            if call in line:
                # Skip if this is urllib.request.urlopen
                if "urllib.request.urlopen" in line or "urllib.request.Request" in line:
                    break
                if "encoding=" not in line and "rb" not in line and "wb" not in line:
                    errors.append(f"{script_path.name}:{i}: open() missing encoding=")
                break

    # Shebangs are intentionally omitted (EXE001)
    if lines[0].startswith("#!"):
        errors.append(f"{script_path.name}: unexpected shebang — scripts are invoked via python3")

    return errors


def run_self_tests() -> list[str]:
    """Run --self-test on all scripts that declare it and verify they pass."""
    errors = []
    for script in _py_scripts_with_self_test():
        script_path = SCRIPTS_DIR / script
        if not script_path.exists():
            continue
        result = subprocess.run(
            [sys.executable, str(script_path), "--self-test"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            errors.append(f"{script}: self-test failed: {result.stderr}")
    return errors


def check_all_scripts() -> list[str]:
    """Check all scripts for quality issues."""
    all_errors = []
    for script in ALL_SCRIPTS:
        script_path = SCRIPTS_DIR / script
        if script_path.exists():
            all_errors.extend(check_script(script_path))
    return all_errors


def main() -> int:
    all_errors = []

    # Check all scripts
    all_errors.extend(check_all_scripts())

    # Run self-tests
    all_errors.extend(run_self_tests())

    if all_errors:
        for error in all_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("OK: all script validations passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
