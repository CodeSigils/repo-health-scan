"""Verify reachable HTTP(S) URLs referenced by docs and skill files.

The URL list lives in docs/evidence-urls.json so the research evidence base has
one machine-readable source of truth. If the doc adds or removes URLs, update
that manifest instead of editing this script's code.

v3 schema adds: status tracking, source_type classification, domain tagging,
last_verified (ISO), versioned_url for versioned references.

Usage:
  python3 scripts/verify-urls.py
  python3 scripts/verify-urls.py --self-test
  python3 scripts/verify-urls.py --summary

Outputs a table of URL -> final status with drift annotations.
Exit code 0 = all URLs match documented expected state.
Exit code 1 = one or more URLs differs from the manifest.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

from _common import ROOT, read_json

MANIFEST_PATH = ROOT / "docs" / "evidence-urls.json"

VALID_STATUS_VALUES = {"active", "retracted", "moved", "deprecated", "unknown"}
VALID_SOURCE_TYPES = {
    "official_docs", "specification", "academic", "community",
    "pinned_snapshot", "versioned_release", "mirror",
}
RETRYABLE_HTTP_STATUSES = frozenset({408, 429, 500, 502, 503, 504})
MAX_JSON_BYTES = 1_000_000
UrlResult = tuple[int | str, bool, str | None]
UrlChecker = Callable[[str, str | None, float], UrlResult]


def load_manifest(path: Path = MANIFEST_PATH) -> tuple[int, str, list[dict[str, Any]]]:
    """Load URL entries from the evidence manifest. Returns (version, description, urls)."""
    try:
        manifest = read_json(path)
    except OSError as exc:
        raise SystemExit(f"FAIL: could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: invalid JSON in {path}: {exc}") from exc

    version = manifest.get("version")
    if version not in (1, 2, 3):
        raise SystemExit(f"FAIL: manifest version must be 1, 2, or 3; got {version}")
    description = manifest.get("description", "")
    urls = manifest.get("urls")
    if not isinstance(urls, list):
        raise SystemExit(f"FAIL: {path} must contain a top-level 'urls' list")
    return version, description, urls


def validate_entry_v1(entry: dict[str, Any]) -> None:
    """Validate one v1 manifest entry."""
    required = ("name", "url", "expected_statuses")
    missing = [key for key in required if key not in entry]
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")
    if not isinstance(entry["name"], str) or not entry["name"].strip():
        raise ValueError("name must be a non-empty string")
    if not isinstance(entry["url"], str) or not entry["url"].startswith(("http://", "https://")):
        raise ValueError("url must be an absolute HTTP(S) URL")
    if not isinstance(entry["expected_statuses"], list) or not entry["expected_statuses"]:
        raise ValueError("expected_statuses must be a non-empty list")
    for status in entry["expected_statuses"]:
        if not isinstance(status, int):
            raise TypeError("expected_statuses must contain integers")


def validate_entry_v3(entry: dict[str, Any]) -> None:
    """Validate one v3 manifest entry. Extends v1 with new fields."""
    validate_entry_v1(entry)

    # status tracking
    status = entry.get("status")
    if status is not None and status not in VALID_STATUS_VALUES:
        raise ValueError(
            f"status must be one of {sorted(VALID_STATUS_VALUES)}; got {status!r}"
        )

    # source_type classification
    source_type = entry.get("source_type")
    if source_type is not None and source_type not in VALID_SOURCE_TYPES:
        raise ValueError(
            f"source_type must be one of {sorted(VALID_SOURCE_TYPES)}; got {source_type!r}"
        )

    # domain_tag (string if present)
    domain_tag = entry.get("domain_tag")
    if domain_tag is not None and not isinstance(domain_tag, str):
        raise ValueError("domain_tag must be a string")

    # last_verified (ISO date format)
    last_verified = entry.get("last_verified")
    if last_verified is not None:
        if not isinstance(last_verified, str):
            raise ValueError("last_verified must be a string")
        try:
            date.fromisoformat(last_verified)
        except ValueError:
            raise ValueError(
                f"last_verified must be ISO date (YYYY-MM-DD); got {last_verified!r}"
            ) from None

    if "versioned_url" in entry and not isinstance(entry["versioned_url"], bool):
        raise ValueError("versioned_url must be a boolean")
    if "content_type" in entry and entry["content_type"] != "json":
        raise ValueError("content_type must be 'json' when present")


def validate_entry(entry: dict[str, Any], version: int = 1) -> None:
    """Validate one manifest entry based on version."""
    if version >= 3:
        validate_entry_v3(entry)
    else:
        validate_entry_v1(entry)


def check_url(
    url: str, content_type: str | None = None, timeout: float = 10
) -> UrlResult:
    """Return (final_status_code, redirected, content_or_error) for one URL.

    When content_type is "json", reads at most ``MAX_JSON_BYTES`` and validates
    the response body. This function makes one request; retry policy belongs in
    ``check_url_with_retries`` so local and CI checks behave the same way.
    """
    request = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "repo-health-and-sync-skill-url-check"},
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            redirected = response.geturl() != url

            if content_type == "json":
                body_bytes = response.read(MAX_JSON_BYTES + 1)
                if len(body_bytes) > MAX_JSON_BYTES:
                    return status, redirected, "JSON_TOO_LARGE"
                try:
                    json.loads(body_bytes.decode("utf-8"))
                    return status, redirected, "VALID"
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return status, redirected, "INVALID_JSON"
            return status, redirected, None

    except urllib.error.HTTPError as exc:
        return exc.code, False, f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return "NETWORK_ERROR", False, str(exc.reason)
    except TimeoutError:
        return "TIMEOUT", False, "timeout"
    except ValueError as exc:
        return "INVALID_URL", False, f"invalid URL: {exc}"


def is_transient_status(status: int | str) -> bool:
    """Return whether a failed URL check can reasonably succeed on retry."""
    return status in RETRYABLE_HTTP_STATUSES or status in {"NETWORK_ERROR", "TIMEOUT"}


def check_url_with_retries(
    url: str,
    content_type: str | None,
    timeout: float,
    attempts: int,
    retry_delay: float,
    *,
    checker: UrlChecker = check_url,
    sleeper: Callable[[float], None] = time.sleep,
) -> UrlResult:
    """Run a bounded retry loop for temporary network and server failures."""
    for attempt in range(1, attempts + 1):
        result = checker(url, content_type, timeout)
        if not is_transient_status(result[0]) or attempt == attempts:
            return result
        print(
            f"Retrying {url} after transient result {result[0]} "
            f"({attempt}/{attempts})...",
            file=sys.stderr,
        )
        sleeper(retry_delay)
    raise AssertionError("retry loop must return during its final attempt")


def classify_status(status: int | str, expected_statuses: list[int]) -> str:
    """Return OK when status matches the manifest, else DRIFT."""
    if isinstance(status, int) and status in expected_statuses:
        return "OK"
    return "DRIFT"


def check_self_test() -> int:
    """Run internal self-tests for the validation logic."""
    # Test classify_status
    assert classify_status(200, [200]) == "OK"
    assert classify_status(404, [200]) == "DRIFT"
    assert classify_status("ERROR", [200]) == "DRIFT"
    assert classify_status(200, [200, 201]) == "OK"
    assert classify_status(201, [200, 201]) == "OK"
    assert is_transient_status(429)
    assert is_transient_status(503)
    assert is_transient_status("NETWORK_ERROR")
    assert not is_transient_status(404)
    assert not is_transient_status("INVALID_URL")
    print("  PASS  classify_status")

    retry_results = iter([("NETWORK_ERROR", False, "offline"), (200, False, None)])
    retry_calls: list[tuple[str, str | None, float]] = []
    retry_delays: list[float] = []

    def fake_check(url: str, content_type: str | None, timeout: float) -> UrlResult:
        retry_calls.append((url, content_type, timeout))
        return next(retry_results)

    result = check_url_with_retries(
        "https://example.test", None, 4, 3, 0,
        checker=fake_check, sleeper=retry_delays.append,
    )
    assert result[0] == 200
    assert len(retry_calls) == 2
    assert retry_delays == [0]
    print("  PASS  bounded transient retry")

    # Test validate_entry (v1)
    try:
        validate_entry({"name": "test", "url": "https://example.com", "expected_statuses": [200]})
        print("  PASS  validate_entry v1 valid")
    except ValueError:
        assert False, "should not fail"

    try:
        validate_entry({"url": "https://example.com"})  # missing name
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry v1 missing field")

    try:
        validate_entry({"name": "test", "url": "https://example.com", "expected_statuses": []})
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry v1 empty statuses")

    try:
        validate_entry({"name": "test", "url": "https://example.com", "expected_statuses": ["200"]})
        assert False, "should have failed"
    except TypeError:
        print("  PASS  validate_entry v1 non-int status")

    # Test validate_entry (v3)
    try:
        validate_entry({
            "name": "test", "url": "https://example.com", "expected_statuses": [200],
            "status": "active", "source_type": "official_docs", "domain_tag": "test",
            "last_verified": "2026-07-27",
        }, version=3)
        print("  PASS  validate_entry v3 valid")
    except ValueError:
        assert False, "should not fail"

    try:
        validate_entry({
            "name": "test", "url": "https://example.com", "expected_statuses": [200],
            "status": "bogus",
        }, version=3)
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry v3 bad status")

    try:
        validate_entry({
            "name": "test", "url": "https://example.com", "expected_statuses": [200],
            "source_type": "bogus",
        }, version=3)
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry v3 bad source_type")

    try:
        validate_entry({
            "name": "test", "url": "https://example.com", "expected_statuses": [200],
            "last_verified": "not-a-date",
        }, version=3)
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry v3 bad date")

    try:
        validate_entry({
            "name": "test", "url": "https://example.com", "expected_statuses": [200],
            "last_verified": "2026-99-99",
        }, version=3)
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry v3 impossible date")

    print("  PASS  verify-urls.py self-tests")
    return 0


def summary_report(entries: list[dict[str, Any]], version: int) -> None:
    """Print a summary report of domain tags and source types."""
    print("\n=== Summary ===")
    domain_counts = Counter(e.get("domain_tag", "untagged") for e in entries)
    source_type_counts = Counter(e.get("source_type", "unclassified") for e in entries)
    status_counts = Counter(e.get("status", "unknown") for e in entries)

    print(f"  Total URLs: {len(entries)}")
    print(f"  Schema version: {version}")
    print("\n  By domain_tag:")
    for tag, count in domain_counts.most_common():
        print(f"    {tag:<30s} {count}")
    print("\n  By source_type:")
    for st, count in source_type_counts.most_common():
        print(f"    {st:<30s} {count}")
    print("\n  By status:")
    for s, count in status_counts.most_common():
        print(f"    {s:<30s} {count}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run internal validation tests")
    parser.add_argument("--summary", action="store_true", help="Print manifest classification summary")
    parser.add_argument("--attempts", type=int, default=3, help="Maximum requests per URL (default: 3)")
    parser.add_argument("--retry-delay", type=float, default=2, help="Seconds between retries (default: 2)")
    parser.add_argument("--timeout", type=float, default=10, help="Per-request timeout in seconds (default: 10)")
    args = parser.parse_args()
    if args.self_test:
        return check_self_test()
    if args.attempts < 1 or args.retry_delay < 0 or args.timeout <= 0:
        parser.error("--attempts must be >= 1, --retry-delay >= 0, and --timeout > 0")

    version, _description, entries = load_manifest()
    summary_mode = args.summary

    print("=== Evidence URL Re-verification ===")
    print(f"Schema version: {version}")
    if version >= 3:
        print(f"{'Name':<30s} {'Status':<8s} {'Expected':<12s} {'Redirected':<9s} {'Content':<12s} {'URL Status':<12s} {'Note':<10s}")
        print("-" * 100)
    else:
        print(f"{'Name':<30s} {'Status':<8s} {'Expected':<12s} {'Redirected':<9s} {'Content':<12s} {'Note':<10s}")
        print("-" * 90)

    drift_found = False
    for entry in sorted(entries, key=lambda item: item["name"].lower()):
        try:
            validate_entry(entry, version)
        except ValueError as exc:
            print(f"  {entry.get('name', '<unnamed>'):<30s} {'-':<8s} {'-':<12s} {'-':<9s} {'-':<12s} MANIFEST: {exc}")
            drift_found = True
            continue

        url_status = entry.get("status", "unknown")

        # Skip retracted/moved/deprecated URLs from live checks (they're expected to be gone)
        if url_status in ("retracted", "moved", "deprecated"):
            if version >= 3:
                print(
                    f"  {entry['name']:<30s} {'SKIP':<8s} {'-':<12s} {'-':<9s} {'-':<12s} {url_status:<12s} (status={url_status})"
                )
            else:
                print(
                    f"  {entry['name']:<30s} {'SKIP':<8s} {'-':<12s} {'-':<9s} {'-':<12s} (status={url_status})"
                )
            continue

        content_type = entry.get("content_type")
        status, redirected, content = check_url_with_retries(
            entry["url"], content_type, args.timeout, args.attempts, args.retry_delay
        )
        expected = entry["expected_statuses"]
        note = classify_status(status, expected)
        if note == "DRIFT":
            drift_found = True

        # Content check trumps status check for JSON endpoints
        content_label = content or "—"
        if content_type == "json" and content == "INVALID_JSON":
            note = "BROKEN"
            drift_found = True

        expected_text = "/".join(str(code) for code in expected)
        marker = "  ← DRIFT" if note == "DRIFT" else ""
        marker = "  ← BROKEN" if note == "BROKEN" else marker

        if version >= 3:
            print(
                f"  {entry['name']:<30s} {status!s:<8s} {expected_text:<12s} "
                f"{redirected!s:<9s} {content_label:<12s} {url_status:<12s} {note:<10s}{marker}"
            )
        else:
            print(
                f"  {entry['name']:<30s} {status!s:<8s} {expected_text:<12s} "
                f"{redirected!s:<9s} {content_label:<12s} {note:<10s}{marker}"
            )

    if drift_found:
        print("\nRESULT: Drift or broken content detected — one or more URLs differ from docs/evidence-urls.json.")
        print("Update the manifest and research doc together after investigating the changed URL state.")
        return 1

    print("\nRESULT: All URLs match documented expected state and content validates OK")

    if summary_mode:
        summary_report(entries, version)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
