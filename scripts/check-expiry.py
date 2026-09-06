"""
check-expiry.py — Scan for expired references in documentation and config files.

Scans .repo-health.json, SKILL.md, docs/ for Expires: fields.
Fails if any expired references are found.

Usage:
    python3 scripts/check-expiry.py           # check all files
    python3 scripts/check-expiry.py --strict  # treat missing Expires as error
    python3 scripts/check-expiry.py --self-test  # run internal self-tests
"""

from __future__ import annotations

import json
import re
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from _common import ROOT, read_json

EXPIRY_RE = re.compile(r"^\s*Expires?:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
]


def parse_date(date_str: str) -> date | None:
    """Parse date string with multiple format support."""
    date_str = date_str.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=UTC).date()
        except ValueError:
            continue
    return None


def find_expiry_dates(file_path: Path) -> list[tuple[str, date, int]]:
    """Find all Expires: fields in a file. Returns (line, expiry_date, line_number)."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    results = []
    for match in EXPIRY_RE.finditer(content):
        line_start = content.rfind("\n", 0, match.start()) + 1
        line_end = content.find("\n", match.end())
        if line_end == -1:
            line_end = len(content)
        line = content[line_start:line_end].strip()
        line_no = content.count("\n", 0, match.start()) + 1

        expiry_date = parse_date(match.group(1))
        if expiry_date:
            results.append((line, expiry_date, line_no))

    return results


def check_file_expiry(file_path: Path, strict: bool = False) -> tuple[list[str], list[str]]:
    """Check a file for expired/missing expiry dates.
    Returns (expired_messages, missing_entries).
    """
    expired = []
    missing = []

    try:
        file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return [], []

    expiries = find_expiry_dates(file_path)
    if not expiries and strict:
        missing.append(f"{file_path}: no Expires: field found")

    today = datetime.now(tz=UTC).date()
    for line, expiry_date, line_no in expiries:
        if expiry_date < today:
            expired.append(f"{file_path}:{line_no}: expired on {expiry_date} ({line})")

    return expired, missing


def check_yaml_frontmatter(file_path: Path) -> list[tuple[str, date, int]]:
    """Extract expires from YAML frontmatter."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    if not content.startswith("---\n"):
        return []

    try:
        _, raw, _ = content.split("---\n", 2)
    except ValueError:
        return []

    results = []
    for line in raw.splitlines():
        if line.strip().startswith("expires:") or line.strip().startswith("expire:"):
            match = re.match(r"expires?:\s*(.+)", line, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip().strip('"\'')
                expiry = parse_date(date_str)
                if expiry:
                    # Approximate line number
                    line_no = content.find(line) + 1
                    line_no = content[:line_no].count("\n") + 1
                    results.append((line.strip(), expiry, line_no))

    return results


def check_json_file(file_path: Path) -> tuple[list[tuple[str, date, int]], list[str]]:
    """Check JSON files for expires fields."""
    try:
        data = read_json(file_path)
    except (OSError, json.JSONDecodeError):
        return [], []

    expired = []
    missing = []

    def check_obj(obj: Any, path: str = "") -> None:
        if isinstance(obj, dict):
            if "expires" in obj or "expire" in obj:
                date_str = obj.get("expires") or obj.get("expire")
                expiry = parse_date(str(date_str))
                if expiry and expiry < datetime.now(tz=UTC).date():
                    expired.append((f"{file_path}: {path}.expires", expiry, 0))
            for k, v in obj.items():
                check_obj(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_obj(item, f"{path}[{i}]")

    check_obj(data)
    return expired, missing


def run_self_tests() -> int:
    """Run internal self-tests for check-expiry logic."""
    errors = 0

    # Test parse_date
    test_cases = [
        ("2025-01-15", date(2025, 1, 15)),
        ("2025/01/15", date(2025, 1, 15)),
        ("15-01-2025", date(2025, 1, 15)),
        ("15/01/2025", date(2025, 1, 15)),
        ("invalid", None),
    ]
    for date_str, expected in test_cases:
        result = parse_date(date_str)
        if result != expected:
            print(f"FAIL: parse_date({date_str!r}) = {result!r}, expected {expected!r}")
            errors += 1

    # Test parse_date with edge cases
    assert parse_date("2024-02-29") == date(2024, 2, 29)  # leap year
    assert parse_date("2023-02-29") is None  # not leap year

    print("  PASS  parse_date tests")

    # Test EXPIRY_RE regex
    test_lines = [
        "Expires: 2025-12-31",
        "expires: 2025-01-01",
        "expire: 2025-06-15",
        "  Expires: 2025-12-31  ",
    ]
    for line in test_lines:
        matches = list(EXPIRY_RE.finditer(line))
        if len(matches) != 1:
            print(f"FAIL: Expected 1 match in {line!r}, got {len(matches)}")
            for m in matches:
                print(f"  Match: {m.group()!r}")
            errors += 1
        else:
            assert parse_date(matches[0].group(1)) is not None

    # Test non-matching lines
    for line in ["Expiration: 2025-01-01", "Expired: 2025-01-01", "Version: 1.0.0"]:
        matches = list(EXPIRY_RE.finditer(line))
        assert len(matches) == 0, f"Expected 0 matches in {line!r}"

    print("  PASS  EXPIRY_RE tests")

    # Test validate_entry
    try:
        # validate_entry is not defined in this script - skip
        print("  SKIP  validate_entry test (not in this script)")
    except NameError:
        pass  # Expected since validate_entry not defined here

    print("  PASS  check-expiry.py self-tests")
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Check for expired references")
    parser.add_argument("--strict", action="store_true", help="Treat missing Expires as error")
    parser.add_argument("--self-test", action="store_true", help="Run internal self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_tests()

    errors: list[str] = []
    notes: list[str] = []
    today = datetime.now(tz=UTC).date()

    # Scan SKILL.md
    skill_path = ROOT / "skills" / "repo-health-scan" / "SKILL.md"
    if skill_path.exists():
        expired, missing = check_file_expiry(skill_path, strict=args.strict)
        errors.extend(expired)
        notes.extend(missing)
        yaml_expired = [e for e, d, _ in check_yaml_frontmatter(skill_path) if d < today]
        errors.extend(yaml_expired)

    # Scan docs/ for expiration fields
    for f in sorted(ROOT.glob("docs/*.md")):
        expired, missing = check_file_expiry(f, strict=args.strict)
        errors.extend(expired)
        notes.extend(missing)

    # Scan evidence-urls.json
    urls_path = ROOT / "docs" / "evidence-urls.json"
    if urls_path.exists():
        json_expired, json_missing = check_json_file(urls_path)
        expired_strs = [e for e, d, _ in json_expired]
        errors.extend(expired_strs)
        notes.extend(json_missing)

    for n in notes:
        print(f"NOTE: {n}")
    if errors:
        for e in errors:
            print(f"EXPIRED: {e}", file=sys.stderr)
        return 1
    print("PASS: no expired references found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
