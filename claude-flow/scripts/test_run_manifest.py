import json
from pathlib import Path

from run_manifest import (
    init_manifest,
    load_manifest,
    record_approval,
    record_command,
    record_review,
    record_verification,
    set_review_base,
)


def _write_state(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "approvals": {},
                "current_phase": {"path": None},
                "capability_matrix": {},
            }
        )
    )


def test_init_manifest_creates_file_and_syncs_state(tmp_path: Path):
    manifest_path = tmp_path / ".claude" / "runs" / "session.json"
    state_path = tmp_path / ".claude" / "workflow-state.json"
    _write_state(state_path)

    manifest = init_manifest(
        manifest_path=manifest_path,
        workflow_path="full",
        task_summary="Improve claude-flow",
        capability_matrix={"test_command": "pytest -q"},
        session_id="session-123",
        state_path=state_path,
    )
    state = json.loads(state_path.read_text())

    assert manifest_path.exists()
    assert manifest["workflow_path"] == "full"
    assert manifest["task_summary"] == "Improve claude-flow"
    assert manifest["capability_matrix"]["test_command"] == "pytest -q"
    assert state["run_manifest_path"] == str(manifest_path)
    assert state["current_phase"]["path"] == "full"
    assert state["capability_matrix"]["test_command"] == "pytest -q"


def test_record_approval_appends_hash_and_syncs_state(tmp_path: Path):
    manifest_path = tmp_path / "run.json"
    state_path = tmp_path / "workflow-state.json"
    _write_state(state_path)
    init_manifest(manifest_path=manifest_path, state_path=state_path)

    approval = record_approval(
        manifest_path=manifest_path,
        kind="requirements",
        content='{"acceptance_criteria":["AC-1"]}',
        state_path=state_path,
    )

    manifest = load_manifest(manifest_path)
    state = json.loads(state_path.read_text())

    assert len(manifest["requirements_approvals"]) == 1
    assert manifest["requirements_approvals"][0]["sha256"] == approval["sha256"]
    assert state["approvals"]["requirements_sha256"] == approval["sha256"]


def test_set_review_base_updates_manifest_and_state(tmp_path: Path):
    manifest_path = tmp_path / "run.json"
    state_path = tmp_path / "workflow-state.json"
    _write_state(state_path)
    init_manifest(manifest_path=manifest_path, state_path=state_path)

    entry = set_review_base(
        manifest_path=manifest_path,
        review_base_sha="abc123",
        source="merge-base",
        base_ref="origin/main",
        state_path=state_path,
    )

    manifest = load_manifest(manifest_path)
    state = json.loads(state_path.read_text())

    assert manifest["review_base_sha"] == "abc123"
    assert manifest["review_base"]["source"] == "merge-base"
    assert entry["base_ref"] == "origin/main"
    assert state["review_base_sha"] == "abc123"


def test_record_verification_review_and_command_append(tmp_path: Path):
    manifest_path = tmp_path / "run.json"
    init_manifest(manifest_path=manifest_path)
    set_review_base(manifest_path=manifest_path, review_base_sha="base456")

    record_verification(
        manifest_path=manifest_path,
        phase="phase-4c",
        status="ok",
        summary={"summary": {"ok": 9, "warnings": 1}},
        plan_file="/tmp/plan.md",
    )
    record_review(
        manifest_path=manifest_path,
        summary={
            "review_budget": "medium",
            "budget_reasons": ["workflow path full defaults to medium"],
            "by_tier": {"1": ["coderabbit"]},
            "budget_skipped": [],
            "conditional_skipped": [],
            "registry_sources": ["bundled"],
        },
        redactions={"redaction_count": 2, "redactions": [{"rule": "password"}]},
        reviewers_run=["coderabbit"],
    )
    record_command(
        manifest_path=manifest_path,
        command="python3 -m pytest -q",
        exit_code=0,
        category="tests",
        cwd="/repo",
    )

    manifest = load_manifest(manifest_path)

    assert manifest["verification_runs"][0]["phase"] == "phase-4c"
    assert manifest["verification_runs"][0]["summary"]["summary"]["ok"] == 9
    assert manifest["review_runs"][0]["review_base_sha"] == "base456"
    assert manifest["review_runs"][0]["redaction_count"] == 2
    assert manifest["review_runs"][0]["reviewers_run"] == ["coderabbit"]
    assert manifest["commands_run"][0]["command"] == "python3 -m pytest -q"
    assert manifest["commands_run"][0]["exit_code"] == 0
