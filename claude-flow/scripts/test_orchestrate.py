import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

import orchestrate
import run_manifest


def _init_state(state_path: Path, manifest_path: Path) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "approvals": {},
                "current_phase": {"path": "full"},
                "capability_matrix": {},
                "run_manifest_path": str(manifest_path),
            }
        )
    )


def test_discover_manifest_path_uses_state_when_no_explicit(tmp_path: Path):
    manifest_path = tmp_path / ".claude" / "runs" / "session.json"
    state_path = tmp_path / ".claude" / "workflow-state.json"
    _init_state(state_path, manifest_path)

    resolved = orchestrate.discover_manifest_path(tmp_path, None)

    assert resolved == manifest_path


def test_discover_manifest_path_errors_when_state_missing(tmp_path: Path):
    with pytest.raises(SystemExit):
        orchestrate.discover_manifest_path(tmp_path, None)


def test_status_from_summary_classifies_counts():
    assert orchestrate.status_from_summary({"summary": {"missing": 1}}) == "fail"
    assert orchestrate.status_from_summary({"summary": {"errors": 1}}) == "fail"
    assert orchestrate.status_from_summary({"summary": {"warnings": 1}}) == "warning"
    assert orchestrate.status_from_summary({"summary": {"ok": 5}}) == "ok"


def _make_completed(stdout: str, returncode: int) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=["verify_plan"], returncode=returncode, stdout=stdout, stderr=""
    )


def test_cmd_verify_plan_records_warning_status(tmp_path: Path, capsys):
    manifest_path = tmp_path / "run.json"
    state_path = tmp_path / ".claude" / "workflow-state.json"
    _init_state(state_path, manifest_path)
    run_manifest.init_manifest(manifest_path=manifest_path, state_path=state_path)

    plan_file = tmp_path / "plan.md"
    plan_file.write_text("Modify: `app/main.py`\n")

    fake_summary = {
        "plan_file": str(plan_file),
        "summary": {"ok": 0, "missing": 0, "warnings": 1, "errors": 0},
        "warnings": [{"path": "app/main.py", "message": "stale"}],
    }
    with patch.object(
        subprocess,
        "run",
        return_value=_make_completed(json.dumps(fake_summary), 0),
    ):
        exit_code = orchestrate.main(
            [
                "verify-plan",
                str(plan_file),
                "--manifest",
                str(manifest_path),
                "--project-root",
                str(tmp_path),
            ]
        )

    assert exit_code == 0
    manifest = run_manifest.load_manifest(manifest_path)
    assert manifest["verification_runs"][-1]["status"] == "warning"
    assert manifest["verification_runs"][-1]["plan_file"] == str(plan_file)
    out = capsys.readouterr().out
    assert "verify-plan" in out and "warning" in out


def test_cmd_verify_plan_uses_manifest_from_state(tmp_path: Path):
    manifest_path = tmp_path / "run.json"
    state_path = tmp_path / ".claude" / "workflow-state.json"
    _init_state(state_path, manifest_path)
    run_manifest.init_manifest(manifest_path=manifest_path, state_path=state_path)

    plan_file = tmp_path / "plan.md"
    plan_file.write_text("Modify: `app/main.py`\n")

    fake_summary = {
        "plan_file": str(plan_file),
        "summary": {"ok": 1, "missing": 0, "warnings": 0, "errors": 0},
    }
    with patch.object(
        subprocess,
        "run",
        return_value=_make_completed(json.dumps(fake_summary), 0),
    ):
        exit_code = orchestrate.main(
            [
                "verify-plan",
                str(plan_file),
                "--project-root",
                str(tmp_path),
            ]
        )

    assert exit_code == 0
    manifest = run_manifest.load_manifest(manifest_path)
    assert manifest["verification_runs"][-1]["status"] == "ok"


def test_cmd_verify_plan_propagates_failure_exit_code(tmp_path: Path):
    manifest_path = tmp_path / "run.json"
    run_manifest.init_manifest(manifest_path=manifest_path)

    plan_file = tmp_path / "plan.md"
    plan_file.write_text("Modify: `missing/file.py`\n")

    fake_summary = {
        "summary": {"ok": 0, "missing": 1, "warnings": 0, "errors": 0},
    }
    with patch.object(
        subprocess,
        "run",
        return_value=_make_completed(json.dumps(fake_summary), 1),
    ):
        exit_code = orchestrate.main(
            [
                "verify-plan",
                str(plan_file),
                "--manifest",
                str(manifest_path),
                "--project-root",
                str(tmp_path),
            ]
        )

    assert exit_code == 1
    manifest = run_manifest.load_manifest(manifest_path)
    assert manifest["verification_runs"][-1]["status"] == "fail"


def test_cmd_resolve_review_base_persists_to_manifest_and_state(tmp_path: Path):
    manifest_path = tmp_path / "run.json"
    state_path = tmp_path / ".claude" / "workflow-state.json"
    _init_state(state_path, manifest_path)
    run_manifest.init_manifest(manifest_path=manifest_path, state_path=state_path)

    fake_resolution = {
        "review_base_sha": "deadbeef",
        "source": "merge-base",
        "base_ref": "origin/main",
    }
    with patch.object(
        orchestrate.resolve_review_base,
        "resolve_review_base",
        return_value=fake_resolution,
    ):
        exit_code = orchestrate.main(
            [
                "resolve-review-base",
                "--manifest",
                str(manifest_path),
                "--project-root",
                str(tmp_path),
                "--state-file",
                str(state_path),
            ]
        )

    assert exit_code == 0
    manifest = run_manifest.load_manifest(manifest_path)
    state = json.loads(state_path.read_text())
    assert manifest["review_base_sha"] == "deadbeef"
    assert manifest["review_base"]["source"] == "merge-base"
    assert manifest["review_base"]["base_ref"] == "origin/main"
    assert state["review_base_sha"] == "deadbeef"


def test_cmd_scrub_diff_writes_scrubbed_and_redactions(tmp_path: Path):
    diff = tmp_path / "diff.patch"
    diff.write_text("Authorization: Bearer abcdef123456\nother\n")
    output = tmp_path / "scrubbed.diff"

    exit_code = orchestrate.main(
        [
            "scrub-diff",
            str(diff),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    scrubbed_text = output.read_text()
    assert "Bearer [REDACTED]" in scrubbed_text
    redactions_path = output.with_suffix(output.suffix + ".redactions.json")
    redactions_payload = json.loads(redactions_path.read_text())
    assert redactions_payload["redaction_count"] >= 1
    assert any(
        item["rule"] == "bearer_token"
        for item in redactions_payload["redactions"]
    )


def test_cmd_scrub_diff_honors_explicit_redactions_path(tmp_path: Path):
    diff = tmp_path / "diff.patch"
    diff.write_text("password = supersecret\n")
    output = tmp_path / "scrubbed.diff"
    redactions = tmp_path / "custom-redactions.json"

    exit_code = orchestrate.main(
        [
            "scrub-diff",
            str(diff),
            "--output",
            str(output),
            "--redactions-output",
            str(redactions),
        ]
    )

    assert exit_code == 0
    payload = json.loads(redactions.read_text())
    assert payload["redaction_count"] >= 1
