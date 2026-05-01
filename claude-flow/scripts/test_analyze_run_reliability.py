import json
import subprocess
import sys
from pathlib import Path

from analyze_run_reliability import analyze_event_logs


SCRIPT = Path(__file__).with_name("analyze_run_reliability.py")


def _write_events(path: Path, events: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")


def test_analyze_event_logs_groups_tool_and_subagent_errors(tmp_path: Path):
    first = tmp_path / "runs" / "001.events.jsonl"
    second = tmp_path / "runs" / "002.events.jsonl"
    _write_events(
        first,
        [
            {
                "type": "tool_error",
                "payload": {
                    "tool_name": "rg",
                    "phase": "phase-2",
                    "error_class": "timeout",
                    "expected": True,
                },
            },
            {
                "type": "tool_error",
                "payload": {
                    "tool_name": "grep",
                    "phase": "phase-2",
                    "error_class": "unknown-tool-error",
                    "expected": False,
                },
            },
        ],
    )
    _write_events(
        second,
        [
            {
                "type": "subagent_error",
                "payload": {
                    "subagent_role": "reviewer",
                    "phase": "phase-6",
                    "error_class": "provider-error",
                    "expected": True,
                },
            },
            {"type": "decision", "payload": {"summary": "ignored"}},
        ],
    )

    report = analyze_event_logs([first, second])

    assert report["runs_scanned"] == 2
    assert report["error_events"] == 3
    assert report["unknown_error_count"] == 1
    assert report["by_error_class"][0] == {"key": "provider-error", "count": 1}
    assert {"key": "phase-2", "count": 2} in report["by_phase"]
    assert {"key": "rg", "count": 1} in report["by_tool"]
    assert {"key": "reviewer", "count": 1} in report["by_subagent"]


def test_analyze_event_logs_reports_repeated_failures_and_spikes(
    tmp_path: Path,
):
    first = tmp_path / "runs" / "001.events.jsonl"
    second = tmp_path / "runs" / "002.events.jsonl"
    _write_events(
        first,
        [
            {
                "type": "tool_error",
                "payload": {
                    "tool_name": "rg",
                    "phase": "phase-2",
                    "error_class": "timeout",
                },
            }
        ],
    )
    _write_events(
        second,
        [
            {
                "type": "tool_error",
                "payload": {
                    "tool_name": "rg",
                    "phase": "phase-2",
                    "error_class": "timeout",
                },
            },
            {
                "type": "tool_error",
                "payload": {
                    "tool_name": "rg",
                    "phase": "phase-5",
                    "error_class": "timeout",
                },
            },
        ],
    )

    report = analyze_event_logs([first, second])

    assert report["repeated_failures"]["tools"] == [{"key": "rg", "count": 3}]
    assert report["recent_spikes"] == [
        {
            "dimension": "error_class",
            "key": "timeout",
            "latest_count": 2,
            "previous_max": 1,
        }
    ]


def test_cli_outputs_json_report_for_runs_dir(tmp_path: Path):
    runs_dir = tmp_path / ".claude" / "runs"
    _write_events(
        runs_dir / "session.events.jsonl",
        [
            {
                "type": "tool_error",
                "payload": {
                    "tool_name": "apply_patch",
                    "phase": "phase-5",
                    "error_class": "invalid-arguments",
                },
            }
        ],
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--runs-dir",
            str(runs_dir),
            "--json",
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    report = json.loads(completed.stdout)
    assert report["runs_scanned"] == 1
    assert report["by_tool"] == [{"key": "apply_patch", "count": 1}]


def test_cli_reports_malformed_event_log(tmp_path: Path):
    runs_dir = tmp_path / ".claude" / "runs"
    runs_dir.mkdir(parents=True)
    (runs_dir / "bad.events.jsonl").write_text("{not-json\n")

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--runs-dir",
            str(runs_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert "not valid JSONL" in completed.stderr
