import json
import subprocess
import sys
from pathlib import Path

from export_run_timeline import manifest_to_events


SCRIPT = Path(__file__).with_name("export_run_timeline.py")


def _manifest() -> dict:
    return {
        "workflow_version": "2",
        "session_id": "session-123",
        "workflow_path": "lite",
        "task_summary": "Improve workflow observability",
        "review_base_sha": "abc123",
        "capability_matrix": {"test_command": "pytest -q"},
        "last_updated_at": "2026-04-29T12:00:00+00:00",
        "requirements_approvals": [
            {
                "sha256": "req",
                "recorded_at": "2026-04-29T10:00:00+00:00",
                "source": "inline",
            }
        ],
        "plan_approvals": [
            {
                "sha256": "plan",
                "recorded_at": "2026-04-29T10:05:00+00:00",
                "source": "/tmp/plan.md",
            }
        ],
        "verification_runs": [
            {
                "phase": "phase-4c",
                "status": "ok",
                "recorded_at": "2026-04-29T10:10:00+00:00",
            }
        ],
        "review_runs": [
            {
                "recorded_at": "2026-04-29T10:20:00+00:00",
                "review_budget": "low",
                "reviewers_run": ["coderabbit"],
            }
        ],
        "commands_run": [
            {
                "command": "pytest -q",
                "exit_code": 0,
                "recorded_at": "2026-04-29T10:15:00+00:00",
            }
        ],
    }


def test_manifest_to_events_metadata_first_then_chronological_events():
    events = manifest_to_events(_manifest())

    assert [event["sequence"] for event in events] == list(range(len(events)))
    assert events[0]["type"] == "metadata"
    assert events[0]["payload"]["workflow_path"] == "lite"
    assert [event["type"] for event in events[1:]] == [
        "approval",
        "approval",
        "verification_run",
        "command",
        "review_run",
    ]


def test_manifest_to_events_keeps_untimestamped_events_after_timestamped():
    manifest = _manifest()
    manifest["commands_run"].append({"command": "flake8 app/", "exit_code": 1})

    events = manifest_to_events(manifest)

    assert events[-1]["type"] == "command"
    assert events[-1]["timestamp"] is None
    assert events[-1]["payload"]["command"] == "flake8 app/"


def test_cli_writes_jsonl_output(tmp_path: Path):
    manifest_path = tmp_path / "run.json"
    output_path = tmp_path / "timeline.jsonl"
    manifest_path.write_text(json.dumps(_manifest()))

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(manifest_path),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    lines = output_path.read_text().splitlines()
    assert len(lines) == 6
    assert json.loads(lines[0])["type"] == "metadata"


def test_cli_includes_sibling_event_log(tmp_path: Path):
    manifest_path = tmp_path / "run.json"
    event_log_path = tmp_path / "run.events.jsonl"
    output_path = tmp_path / "timeline.jsonl"
    manifest_path.write_text(json.dumps(_manifest()))
    event_log_path.write_text(
        json.dumps(
            {
                "recorded_at": "2026-04-29T10:12:00+00:00",
                "type": "decision",
                "category": "decision",
                "payload": {"summary": "Use append-only continuity events"},
            }
        )
        + "\n"
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(manifest_path),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    events = [
        json.loads(line) for line in output_path.read_text().splitlines()
    ]
    session_events = [
        event for event in events if event["type"] == "session_event"
    ]
    assert session_events[0]["payload"]["category"] == "decision"
    assert session_events[0]["payload"]["payload"]["summary"].startswith("Use")


def test_cli_resolves_configured_relative_event_log_from_manifest_dir(
    tmp_path: Path,
):
    project_dir = tmp_path / "project"
    other_cwd = tmp_path / "other"
    runs_dir = project_dir / ".claude" / "runs"
    manifest_path = runs_dir / "run.json"
    event_log_path = runs_dir / "custom.events.jsonl"
    output_path = tmp_path / "timeline.jsonl"
    other_cwd.mkdir(parents=True)
    runs_dir.mkdir(parents=True)
    manifest = _manifest()
    manifest["event_log_path"] = "custom.events.jsonl"
    manifest_path.write_text(json.dumps(manifest))
    event_log_path.write_text(
        json.dumps(
            {
                "recorded_at": "2026-04-29T10:12:00+00:00",
                "type": "decision",
                "category": "decision",
                "payload": {"summary": "Resolved relative to manifest"},
            }
        )
        + "\n"
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(manifest_path),
            "--output",
            str(output_path),
        ],
        cwd=other_cwd,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    events = [
        json.loads(line) for line in output_path.read_text().splitlines()
    ]
    session_events = [
        event for event in events if event["type"] == "session_event"
    ]
    assert session_events[0]["payload"]["payload"]["summary"] == (
        "Resolved relative to manifest"
    )


def test_cli_reports_missing_manifest(tmp_path: Path):
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(tmp_path / "missing.json"),
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert "manifest not found" in completed.stderr


def test_cli_reports_malformed_manifest(tmp_path: Path):
    manifest_path = tmp_path / "run.json"
    manifest_path.write_text("{not-json")

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manifest",
            str(manifest_path),
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert "not valid JSON" in completed.stderr
