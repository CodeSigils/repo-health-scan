"""Grade Codex repo-health regression artifacts deterministically."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from _common import read_json, validate_dimensions

DEFAULT_CONTRACT = Path("evals/cases/repo-health-scan.json")
SEVERITY_ORDER = {"blocking": 0, "warning": 1, "info": 2}
REQUIRED_OBSERVED_FIELDS = {
    "vcs", "languages", "package_managers", "ci", "shell_files", "recent_commits",
    "gitignore", "version_sources", "script_surface", "shipped_payload", "tags_present",
    "base_ref", "branch_commits_outside_base", "working_tree_dirty", "workflow_files",
    "release_files", "verify_refs", "verify_releases",
}
REQUIRED_INFERRED_FIELDS = {"repo_type", "release_model", "risk_context"}


def expected_dimensions(contract: dict[str, Any]) -> set[str]:
    """Derive the candidate dimension set from the deterministic contract."""
    dimensions: set[str] = set()
    for fixture in contract.get("fixtures", []):
        expected = fixture.get("expected", {})
        for key in ("active_dimensions", "skipped_dimensions"):
            for item in expected.get(key, []):
                name = item.get("name")
                if isinstance(name, str):
                    dimensions.add(name)
    return dimensions


def validate_transcript(path: Path, label: str) -> list[str]:
    """Check that a Codex JSONL stream completed without protocol errors."""
    errors: list[str] = []
    event_types: list[str] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(
                f"{label} transcript line {line_number} is invalid JSON: {exc}"
            )
            continue
        event_type = event.get("type")
        if not isinstance(event_type, str):
            errors.append(f"{label} transcript line {line_number} lacks an event type")
            continue
        event_types.append(event_type)
        if event_type in {"error", "turn.failed"}:
            errors.append(f"{label} transcript contains {event_type}")
    if "turn.completed" not in event_types:
        errors.append(f"{label} transcript has no turn.completed event")
    return errors


def grade_positive_transcript(path: Path) -> list[str]:
    """Verify profile content appears before a populated dimension plan."""
    profile_index: int | None = None
    plan_index: int | None = None
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if event.get("type") != "item.completed" or item.get("type") != "agent_message":
            continue
        try:
            result = json.loads(item.get("text", ""))
        except (TypeError, json.JSONDecodeError):
            continue
        events = result.get("events", [])
        for result_event in events:
            if not isinstance(result_event, dict):
                continue
            if result_event.get("type") == "profile" and result_event.get("profile"):
                profile_index = index if profile_index is None else profile_index
            if result_event.get("type") == "dimension_checks" and (
                result_event.get("active_dimensions")
                or result_event.get("skipped_dimensions")
            ):
                plan_index = index if plan_index is None else plan_index
    errors: list[str] = []
    if profile_index is None:
        errors.append("positive transcript has no populated profile event")
    if plan_index is None:
        errors.append("positive transcript has no populated dimension plan event")
    if (
        profile_index is not None
        and plan_index is not None
        and profile_index >= plan_index
    ):
        errors.append(
            "positive transcript does not emit the profile before dimension planning"
        )
    return errors


def grade_negative_transcript(path: Path) -> list[str]:
    """Detect skill reads or health-workflow markers anywhere in a negative run."""
    markers = ("repo-health-scan", "repo-health-and-sync-skill", "repo profile")
    inspected: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if event.get("type") not in {"item.started", "item.completed"}:
            continue
        if item.get("type") == "agent_message":
            inspected.append(str(item.get("text", "")))
        elif item.get("type") == "command_execution":
            inspected.append(str(item.get("command", "")))
    lowered = "\n".join(inspected).lower()
    found = [marker for marker in markers if marker in lowered]
    return [f"negative transcript activates the health skill: {found}"] if found else []


def grade_positive(result: dict[str, Any], dimensions: set[str]) -> list[str]:
    """Grade skill selection, event ordering, evidence, skips, and findings."""
    errors: list[str] = []
    skill = result.get("skill")
    if not isinstance(skill, dict) or skill.get("selected") is not True:
        errors.append("positive run did not select the repo-health skill")
    elif skill.get("name") != "repo-health-scan":
        errors.append(f"positive run selected unexpected skill: {skill.get('name')}")

    events = result.get("events")
    if not isinstance(events, list):
        return errors + ["positive result events must be a list"]
    event_order = [event.get("type") for event in events if isinstance(event, dict)]
    if event_order != ["profile", "dimension_checks", "report"]:
        errors.append(
            "positive events must be ordered profile -> dimension_checks -> report"
        )
        return errors

    profile = events[0].get("profile")
    if not isinstance(profile, dict):
        errors.append("profile event lacks a structured profile")
        profile = {}
    for section in ("observed", "inferred"):
        if not isinstance(profile.get(section), dict) or not profile[section]:
            errors.append(f"profile.{section} must be a non-empty object")
    if isinstance(profile.get("observed"), dict):
        missing = sorted(REQUIRED_OBSERVED_FIELDS - profile["observed"].keys())
        if missing:
            errors.append(f"profile.observed is missing required fields: {missing}")
    if isinstance(profile.get("inferred"), dict):
        missing = sorted(REQUIRED_INFERRED_FIELDS - profile["inferred"].keys())
        if missing:
            errors.append(f"profile.inferred is missing required fields: {missing}")

    plan = events[1]
    active = plan.get("active_dimensions")
    skipped = plan.get("skipped_dimensions")
    if not isinstance(active, list) or not isinstance(skipped, list):
        return errors + ["dimension plan must contain active and skipped lists"]

    errors.extend(validate_dimensions(
        active, skipped, dimensions, profile, check_skip_status=True,
    ))
    if any("active dimension" in e or "skipped dimension" in e or "dimension accounting" in e for e in errors):
        return errors

    findings = events[2].get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("report must contain at least one finding for the seeded defect")
        return errors
    severities: list[int] = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append(f"finding {index} is malformed")
            continue
        severity = finding.get("severity")
        if severity not in SEVERITY_ORDER:
            errors.append(f"finding {index} has invalid severity: {severity}")
        else:
            severities.append(SEVERITY_ORDER[severity])
        for field in ("finding", "harm", "remediation"):
            if not isinstance(finding.get(field), str) or not finding[field].strip():
                errors.append(f"finding {index} lacks {field}")
    if severities != sorted(severities):
        errors.append("findings are not ordered blocking -> warning -> info")
    finding_text = " ".join(
        str(finding.get("finding", ""))
        for finding in findings
        if isinstance(finding, dict)
    ).lower()
    if "scratch.txt" not in finding_text and "dirty" not in finding_text:
        errors.append("report does not identify the seeded dirty-tree defect")
    return errors


def grade_negative(text: str) -> list[str]:
    """Reject accidental repo-health activation for a narrow implementation task."""
    lowered = text.lower()
    markers = ("repo-health-scan", "repo health scan", "repo profile", "dimension plan")
    found = [marker for marker in markers if marker in lowered]
    if found:
        return [f"negative run appears to activate the health skill: {found}"]
    if not text.strip():
        return ["negative run produced no final response"]
    return []


def run_self_tests() -> int:
    """Exercise passing output and representative contract failures."""
    dimensions = {"history_hygiene", "shell_correctness"}
    result = {
        "skill": {
            "selected": True,
            "name": "repo-health-scan",
            "source_path": "SKILL.md",
        },
        "events": [
            {
                "type": "profile",
                "profile": {
                    "observed": {
                        "vcs": "git", "languages": [], "package_managers": [], "ci": None,
                        "shell_files": False, "recent_commits": False, "gitignore": False,
                        "version_sources": [], "script_surface": "none", "shipped_payload": "none",
                        "tags_present": False, "base_ref": None, "branch_commits_outside_base": None,
                        "working_tree_dirty": False, "workflow_files": [], "release_files": [],
                        "verify_refs": False, "verify_releases": False,
                    },
                    "inferred": {"repo_type": "library", "release_model": "none", "risk_context": "routine"},
                },
                "active_dimensions": [],
                "skipped_dimensions": [],
                "findings": [],
            },
            {
                "type": "dimension_checks",
                "profile": None,
                "active_dimensions": [
                    {"name": "history_hygiene", "activated_by": ["observed.vcs"]}
                ],
                "skipped_dimensions": [
                    {
                        "name": "shell_correctness",
                        "status": "SKIP",
                        "skip_reason": "No shell files.",
                    }
                ],
                "findings": [],
            },
            {
                "type": "report",
                "profile": None,
                "active_dimensions": [],
                "skipped_dimensions": [],
                "findings": [
                    {
                        "severity": "warning",
                        "finding": "dirty tree",
                        "harm": "release can include unintended files",
                        "remediation": "remove or commit the file",
                    }
                ],
            },
        ],
    }
    assert grade_positive(result, dimensions) == []
    result["events"][1]["active_dimensions"][0]["activated_by"] = ["observed.missing"]
    assert any(
        "missing profile evidence" in error
        for error in grade_positive(result, dimensions)
    )
    assert grade_negative("Inspect parser.py and change split to rsplit.") == []
    assert grade_negative("Selected repo-health-scan")

    with tempfile.TemporaryDirectory() as directory:
        transcript = Path(directory) / "transcript.jsonl"
        profile_message = {
            "events": [
                {
                    "type": "profile",
                    "profile": {
                        "observed": {
                            "vcs": "git", "languages": [], "package_managers": [], "ci": None,
                            "shell_files": False, "recent_commits": False, "gitignore": False,
                            "version_sources": [], "script_surface": "none", "shipped_payload": "none",
                            "tags_present": False, "base_ref": None, "branch_commits_outside_base": None,
                            "working_tree_dirty": False, "workflow_files": [], "release_files": [],
                            "verify_refs": False, "verify_releases": False,
                        },
                        "inferred": {"repo_type": "library", "release_model": "none", "risk_context": "routine"},
                    },
                }
            ]
        }
        plan_message = {
            "events": [
                {
                    "type": "dimension_checks",
                    "active_dimensions": [{"name": "history_hygiene"}],
                    "skipped_dimensions": [],
                }
            ]
        }
        transcript.write_text(
            "\n".join(
                [
                    json.dumps({"type": "thread.started"}),
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {
                                "type": "agent_message",
                                "text": json.dumps(profile_message),
                            },
                        }
                    ),
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {
                                "type": "agent_message",
                                "text": json.dumps(plan_message),
                            },
                        }
                    ),
                    json.dumps({"type": "turn.completed"}),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        assert validate_transcript(transcript, "test") == []
        assert grade_positive_transcript(transcript) == []
        assert grade_negative_transcript(transcript) == []
    print("PASS: grade-codex-transcript.py self-tests")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--positive-result", type=Path)
    parser.add_argument("--negative-result", type=Path)
    parser.add_argument("--positive-transcript", type=Path)
    parser.add_argument("--negative-transcript", type=Path)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_tests()
    if args.positive_result is None or args.negative_result is None:
        parser.error("--positive-result and --negative-result are required")

    try:
        contract = read_json(args.contract)
        positive = read_json(args.positive_result)
        negative = args.negative_result.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read regression artifact: {exc}", file=sys.stderr)
        return 1

    errors = grade_positive(positive, expected_dimensions(contract))
    errors.extend(grade_negative(negative))
    for path, label in (
        (args.positive_transcript, "positive"),
        (args.negative_transcript, "negative"),
    ):
        if path is not None:
            errors.extend(validate_transcript(path, label))
            if label == "positive":
                errors.extend(grade_positive_transcript(path))
            else:
                errors.extend(grade_negative_transcript(path))

    report = {"passed": not errors, "errors": errors}
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("PASS: Codex model regression contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
