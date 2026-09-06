"""Run isolated positive and negative Codex skill regressions."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Any

from _common import ROOT as REPO_ROOT
from _common import read_json

SKILL_SOURCE = REPO_ROOT / "skills/repo-health-scan/SKILL.md"
POSITIVE_PROMPT = REPO_ROOT / "evals/codex/positive-prompt.md"
NEGATIVE_PROMPT = REPO_ROOT / "evals/codex/negative-prompt.md"
RESULT_SCHEMA = REPO_ROOT / "evals/codex/positive-result.schema.json"
GRADER = REPO_ROOT / "scripts/grade-codex-transcript.py"
TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


class CodexRunError(RuntimeError):
    """Describe a failed Codex subprocess without losing its failure kind."""

    def __init__(self, message: str, kind: str) -> None:
        super().__init__(message)
        self.kind = kind


def utc_now() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(UTC)


def format_timestamp(value: datetime) -> str:
    """Serialize a UTC timestamp consistently."""
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def codex_version(codex_bin: str) -> str | None:
    """Read the CLI version without failing the regression when unavailable."""
    try:
        result = subprocess.run(
            [codex_bin, "--version"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    version = result.stdout.strip() or result.stderr.strip()
    return version or None


def read_transcript_events(path: Path) -> list[dict[str, Any]]:
    """Read valid JSON objects from a partial or complete JSONL transcript."""
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def event_model(event: dict[str, Any]) -> str | None:
    """Extract a model identifier only when a Codex event exposes one."""
    containers = [event]
    for key in ("thread", "turn", "response", "metadata"):
        value = event.get(key)
        if isinstance(value, dict):
            containers.append(value)
    for container in containers:
        for key in ("model", "model_id", "model_name"):
            value = container.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def summarize_transcript(path: Path) -> dict[str, Any]:
    """Summarize complete or partial Codex events for run observability."""
    events = read_transcript_events(path)
    usage = {field: 0 for field in TOKEN_FIELDS}
    model: str | None = None
    turn_started = False
    turn_completed = False
    in_progress_commands: set[str] = set()
    for event in events:
        event_type = event.get("type")
        turn_started = turn_started or event_type == "turn.started"
        if event_type == "turn.completed":
            turn_completed = True
            event_usage = event.get("usage")
            if isinstance(event_usage, dict):
                for field in TOKEN_FIELDS:
                    value = event_usage.get(field)
                    if isinstance(value, int):
                        usage[field] += value
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") == "command_execution":
            item_id = item.get("id")
            if isinstance(item_id, str):
                if event_type == "item.started":
                    in_progress_commands.add(item_id)
                elif event_type == "item.completed":
                    in_progress_commands.discard(item_id)
        model = model or event_model(event)

    last_event_at = None
    if events and path.is_file():
        last_event_at = format_timestamp(
            datetime.fromtimestamp(path.stat().st_mtime, UTC)
        )
    return {
        "event_count": len(events),
        "last_event_type": events[-1].get("type") if events else None,
        "last_event_at": last_event_at,
        "turn_started": turn_started,
        "turn_completed": turn_completed,
        "command_in_progress": bool(in_progress_commands),
        "model": model,
        "usage": usage if turn_completed else None,
    }


def failure_phase(transcript: dict[str, Any]) -> str:
    """Classify where an incomplete scenario stopped."""
    if not transcript["event_count"] or not transcript["turn_started"]:
        return "startup"
    if transcript["command_in_progress"]:
        return "tool_execution"
    if not transcript["turn_completed"]:
        return "model_inference"
    return "output_capture"


def artifact_paths(output_dir: Path) -> dict[str, str]:
    """List stable artifact paths even when some files were not produced."""
    names = (
        "positive-transcript.jsonl",
        "positive-result.json",
        "positive-stderr.log",
        "negative-transcript.jsonl",
        "negative-result.txt",
        "negative-stderr.log",
        "grade.json",
        "run-summary.json",
    )
    return {Path(name).stem: str(output_dir / name) for name in names}


def new_scenario(transcript: Path, output: Path, stderr_path: Path) -> dict[str, Any]:
    """Create an observable scenario record before execution begins."""
    return {
        "status": "not_started",
        "started_at": None,
        "ended_at": None,
        "duration_seconds": None,
        "failure_phase": None,
        "error": None,
        "transcript_path": str(transcript),
        "output_path": str(output),
        "stderr_path": str(stderr_path),
        "transcript": {
            "event_count": 0,
            "last_event_type": None,
            "last_event_at": None,
            "turn_started": False,
            "turn_completed": False,
            "command_in_progress": False,
            "model": None,
            "usage": None,
        },
    }


def execute_scenario(
    command: list[str],
    transcript: Path,
    output: Path,
    stderr_path: Path,
    timeout_seconds: int,
) -> tuple[dict[str, Any], CodexRunError | None]:
    """Execute one model scenario and retain evidence for every exit path."""
    scenario = new_scenario(transcript, output, stderr_path)
    started_at = utc_now()
    started_clock = monotonic()
    scenario["status"] = "running"
    scenario["started_at"] = format_timestamp(started_at)
    error: CodexRunError | None = None
    try:
        run_codex(command, transcript, stderr_path, timeout_seconds)
    except CodexRunError as exc:
        error = exc
        scenario["status"] = exc.kind
        scenario["error"] = str(exc)
    ended_at = utc_now()
    scenario["ended_at"] = format_timestamp(ended_at)
    scenario["duration_seconds"] = round(monotonic() - started_clock, 3)
    scenario["transcript"] = summarize_transcript(transcript)
    output_is_current = (
        output.is_file() and output.stat().st_mtime >= started_at.timestamp()
    )
    if error is not None:
        scenario["failure_phase"] = failure_phase(scenario["transcript"])
    elif not scenario["transcript"]["turn_completed"] or not output_is_current:
        scenario["status"] = "incomplete"
        scenario["failure_phase"] = failure_phase(scenario["transcript"])
    else:
        scenario["status"] = "completed"
    return scenario, error


def aggregate_usage(scenarios: dict[str, dict[str, Any]]) -> dict[str, int] | None:
    """Add usage from scenarios that emitted turn.completed."""
    total = {field: 0 for field in TOKEN_FIELDS}
    found = False
    for scenario in scenarios.values():
        usage = scenario.get("transcript", {}).get("usage")
        if not isinstance(usage, dict):
            continue
        found = True
        for field in TOKEN_FIELDS:
            value = usage.get(field)
            if isinstance(value, int):
                total[field] += value
    return total if found else None


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    """Write the machine-readable run summary."""
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def run_checked(command: list[str], cwd: Path) -> None:
    """Run a fixture setup command and surface its stderr on failure."""
    result = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"command failed ({' '.join(command)}): {detail}")


def prepare_fixture(root: Path) -> None:
    """Create a small Python repository with one intentional health defect."""
    if root.exists():
        raise FileExistsError(f"fixture path already exists: {root}")
    (root / ".agents/skills/repo-health-scan").mkdir(parents=True)
    (root / ".github/workflows").mkdir(parents=True)
    (root / "src/example").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)

    shutil.copy2(
        SKILL_SOURCE,
        root / ".agents/skills/repo-health-scan/SKILL.md",
    )
    files = {
        "README.md": "# Example Parser\n\nSmall Python parsing library.\n",
        ".gitignore": ".venv/\n__pycache__/\n.pytest_cache/\n",
        "pyproject.toml": (
            "[project]\n"
            'name = "example-parser"\n'
            'version = "0.1.0"\n'
            'requires-python = ">=3.11"\n\n'
            "[tool.uv]\n"
            "package = true\n"
        ),
        "src/example/__init__.py": '"""Example parser package."""\n',
        "src/example/parser.py": (
            '"""Parse a key/value line."""\n\n'
            "def parse_line(value: str) -> tuple[str, str]:\n"
            '    return tuple(value.split("="))\n'
        ),
        "tests/test_parser.py": (
            "from example.parser import parse_line\n\n\n"
            "def test_value_may_contain_separator():\n"
            '    assert parse_line("url=https://example.test?a=1") == (\n'
            '        "url",\n'
            '        "https://example.test?a=1",\n'
            "    )\n"
        ),
        ".github/workflows/ci.yml": (
            "name: ci\n"
            "on: [push]\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v5\n"
            "      - run: uv run pytest\n"
        ),
    }
    for relative, content in files.items():
        (root / relative).write_text(content, encoding="utf-8")

    run_checked(["git", "init", "-b", "main"], root)
    run_checked(["git", "config", "user.name", "Codex Eval"], root)
    run_checked(["git", "config", "user.email", "codex-eval@example.invalid"], root)
    run_checked(["git", "config", "commit.gpgsign", "false"], root)
    run_checked(["git", "add", "."], root)
    run_checked(["git", "commit", "-m", "feat: add example parser"], root)

    # Seed a visible health finding after the clean baseline commit.
    (root / "scratch.txt").write_text(
        "untracked release scratch file\n", encoding="utf-8"
    )


def codex_command(
    codex_bin: str,
    fixture: Path,
    prompt: Path,
    output: Path,
    schema: Path | None = None,
) -> list[str]:
    """Build the controlled non-interactive Codex invocation."""
    command = [
        codex_bin,
        "exec",
        "--json",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "--cd",
        str(fixture),
        "--output-last-message",
        str(output),
    ]
    if schema is not None:
        command.extend(["--output-schema", str(schema)])
    command.append(prompt.read_text(encoding="utf-8"))
    return command


def run_codex(
    command: list[str], transcript: Path, stderr_path: Path, timeout_seconds: int
) -> None:
    """Capture Codex stdout as JSONL and diagnostics separately."""
    transcript.parent.mkdir(parents=True, exist_ok=True)
    with (
        transcript.open("w", encoding="utf-8") as stdout_file,
        stderr_path.open("w", encoding="utf-8") as stderr_file,
    ):
        try:
            result = subprocess.run(
                command,
                cwd=REPO_ROOT,
                stdin=subprocess.DEVNULL,
                stdout=stdout_file,
                stderr=stderr_file,
                text=True,
                check=False,
                timeout=timeout_seconds,
                env=os.environ.copy(),
            )
        except subprocess.TimeoutExpired as exc:
            raise CodexRunError(
                f"Codex exceeded {timeout_seconds}s; see {stderr_path} and {transcript}",
                "timeout",
            ) from exc
    if result.returncode != 0:
        raise CodexRunError(
            f"Codex exited {result.returncode}; see {stderr_path} and {transcript}",
            "failed",
        )


def grade(output_dir: Path) -> int:
    """Run the deterministic grader over both model scenarios."""
    command = [
        sys.executable,
        str(GRADER),
        "--positive-result",
        str(output_dir / "positive-result.json"),
        "--negative-result",
        str(output_dir / "negative-result.txt"),
        "--positive-transcript",
        str(output_dir / "positive-transcript.jsonl"),
        "--negative-transcript",
        str(output_dir / "negative-transcript.jsonl"),
        "--output",
        str(output_dir / "grade.json"),
    ]
    return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode


def run_self_tests() -> int:
    """Verify fixtures, commands, and summaries without a model call."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        fixture = root / "fixture"
        prepare_fixture(fixture)
        assert (
            fixture / ".agents/skills/repo-health-scan/SKILL.md"
        ).is_file()
        assert "uv" in (fixture / "pyproject.toml").read_text(encoding="utf-8")
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=fixture,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert status == "?? scratch.txt\n"
        command = codex_command(
            "codex", fixture, POSITIVE_PROMPT, fixture / "result.json", RESULT_SCHEMA
        )
        assert isinstance(read_json(RESULT_SCHEMA), dict)
        assert command == [
            "codex",
            "exec",
            "--json",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--sandbox",
            "read-only",
            "--cd",
            str(fixture),
            "--output-last-message",
            str(fixture / "result.json"),
            "--output-schema",
            str(RESULT_SCHEMA),
            POSITIVE_PROMPT.read_text(encoding="utf-8"),
        ]

        complete = root / "complete.jsonl"
        complete.write_text(
            "\n".join(
                json.dumps(event)
                for event in (
                    {"type": "thread.started", "model": "test-model"},
                    {"type": "turn.started"},
                    {
                        "type": "item.started",
                        "item": {"id": "cmd-1", "type": "command_execution"},
                    },
                    {
                        "type": "item.completed",
                        "item": {"id": "cmd-1", "type": "command_execution"},
                    },
                    {
                        "type": "turn.completed",
                        "usage": {
                            "input_tokens": 10,
                            "cached_input_tokens": 4,
                            "output_tokens": 3,
                            "reasoning_output_tokens": 1,
                        },
                    },
                )
            )
            + "\n",
            encoding="utf-8",
        )
        complete_summary = summarize_transcript(complete)
        assert complete_summary["turn_completed"] is True
        assert complete_summary["model"] == "test-model"
        assert complete_summary["usage"]["input_tokens"] == 10

        incomplete = root / "incomplete.jsonl"
        incomplete.write_text(
            "\n".join(
                json.dumps(event)
                for event in (
                    {"type": "thread.started"},
                    {"type": "turn.started"},
                    {
                        "type": "item.started",
                        "item": {"id": "cmd-2", "type": "command_execution"},
                    },
                )
            )
            + "\n",
            encoding="utf-8",
        )
        incomplete_summary = summarize_transcript(incomplete)
        assert failure_phase(incomplete_summary) == "tool_execution"
        assert incomplete_summary["usage"] is None

        timed_out = root / "timed-out.jsonl"
        timed_out.write_text(
            "\n".join(
                json.dumps(event)
                for event in (
                    {"type": "thread.started"},
                    {"type": "turn.started"},
                    {
                        "type": "item.completed",
                        "item": {"id": "message-1", "type": "agent_message"},
                    },
                )
            )
            + "\n",
            encoding="utf-8",
        )
        timed_out_summary = summarize_transcript(timed_out)
        assert failure_phase(timed_out_summary) == "model_inference"
        assert timed_out_summary["last_event_type"] == "item.completed"

        scenarios = {
            "positive": {"transcript": complete_summary},
            "negative": {"transcript": timed_out_summary},
        }
        assert aggregate_usage(scenarios) == {
            "input_tokens": 10,
            "cached_input_tokens": 4,
            "output_tokens": 3,
            "reasoning_output_tokens": 1,
        }
    print("PASS: run-codex-regression.py self-tests")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--keep-fixture", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_tests()

    started_at = utc_now()
    started_clock = monotonic()
    timestamp = started_at.strftime("%Y%m%dT%H%M%SZ")
    output_dir = (
        args.output_dir or REPO_ROOT / "artifacts/codex-regression" / timestamp
    ).resolve()
    summary_path = output_dir / "run-summary.json"
    scenarios: dict[str, dict[str, Any]] = {}
    summary: dict[str, Any] = {
        "schema_version": 1,
        "status": "running",
        "failure_phase": None,
        "started_at": format_timestamp(started_at),
        "ended_at": None,
        "duration_seconds": None,
        "codex_cli": {
            "binary": args.codex_bin,
            "version": codex_version(args.codex_bin),
        },
        "model": None,
        "timeout_seconds": args.timeout_seconds,
        "scenarios": scenarios,
        "usage": None,
        "grade": {
            "status": "not_run",
            "exit_code": None,
            "path": str(output_dir / "grade.json"),
        },
        "artifacts": artifact_paths(output_dir),
        "error": None,
    }
    scenarios.update(
        {
            "positive": new_scenario(
                output_dir / "positive-transcript.jsonl",
                output_dir / "positive-result.json",
                output_dir / "positive-stderr.log",
            ),
            "negative": new_scenario(
                output_dir / "negative-transcript.jsonl",
                output_dir / "negative-result.txt",
                output_dir / "negative-stderr.log",
            ),
        }
    )

    temporary: tempfile.TemporaryDirectory[str] | None = None
    if args.fixture_dir is None:
        temporary = tempfile.TemporaryDirectory(prefix="repo-health-codex-eval-")
        fixture = Path(temporary.name) / "fixture"
    else:
        fixture = args.fixture_dir.resolve()
    exit_code = 1
    try:
        prepare_fixture(fixture)
        if args.prepare_only:
            print(f"Prepared Codex regression fixture: {fixture}")
            return 0

        output_dir.mkdir(parents=True, exist_ok=True)

        positive = codex_command(
            args.codex_bin,
            fixture,
            POSITIVE_PROMPT,
            output_dir / "positive-result.json",
            RESULT_SCHEMA,
        )
        scenarios["positive"], scenario_error = execute_scenario(
            positive,
            output_dir / "positive-transcript.jsonl",
            output_dir / "positive-result.json",
            output_dir / "positive-stderr.log",
            args.timeout_seconds,
        )
        if scenario_error is not None:
            summary["failure_phase"] = scenarios["positive"]["failure_phase"]
            raise scenario_error
        negative = codex_command(
            args.codex_bin,
            fixture,
            NEGATIVE_PROMPT,
            output_dir / "negative-result.txt",
        )
        scenarios["negative"], scenario_error = execute_scenario(
            negative,
            output_dir / "negative-transcript.jsonl",
            output_dir / "negative-result.txt",
            output_dir / "negative-stderr.log",
            args.timeout_seconds,
        )
        if scenario_error is not None:
            summary["failure_phase"] = scenarios["negative"]["failure_phase"]
            raise scenario_error
        result = grade(output_dir)
        summary["grade"]["exit_code"] = result
        summary["grade"]["status"] = "passed" if result == 0 else "failed"
        summary["status"] = "passed" if result == 0 else "failed"
        if result != 0:
            summary["error"] = "deterministic grader failed"
            summary["failure_phase"] = "grading"
        exit_code = result
        print(f"Codex regression artifacts: {output_dir}")
    except (FileExistsError, OSError, RuntimeError) as exc:
        summary["status"] = "failed"
        summary["error"] = str(exc)
        if summary["failure_phase"] is None:
            summary["failure_phase"] = "fixture_setup"
        print(f"ERROR: {exc}", file=sys.stderr)
    finally:
        ended_at = utc_now()
        summary["ended_at"] = format_timestamp(ended_at)
        summary["duration_seconds"] = round(monotonic() - started_clock, 3)
        summary["usage"] = aggregate_usage(scenarios)
        summary["model"] = next(
            (
                scenario.get("transcript", {}).get("model")
                for scenario in scenarios.values()
                if scenario.get("transcript", {}).get("model")
            ),
            None,
        )
        if not args.prepare_only:
            output_dir.mkdir(parents=True, exist_ok=True)
            write_summary(summary_path, summary)
        if temporary is not None and not args.keep_fixture:
            temporary.cleanup()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
