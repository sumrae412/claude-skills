import json
from pathlib import Path

import pytest

from lint_skill_metadata import lint_skill_metadata
from lint_skill_security import lint_skill_security
from run_manifest import (
    init_manifest,
    load_manifest,
    record_approval,
    record_event,
)


def test_run_manifest_records_large_unicode_approval(tmp_path: Path):
    manifest_path = tmp_path / "runs" / "session.json"
    init_manifest(manifest_path=manifest_path)
    content = "résumé 任務 🚀\n" + ("x" * (1024 * 1024))

    approval = record_approval(
        manifest_path=manifest_path,
        kind="requirements",
        content=content,
    )
    manifest = load_manifest(manifest_path)

    recorded = manifest["requirements_approvals"][0]
    assert recorded["sha256"] == approval["sha256"]
    assert manifest["requirements_approvals"][0]["size_bytes"] == len(
        content.encode("utf-8")
    )


def test_run_manifest_reports_malformed_json_with_path(tmp_path: Path):
    manifest_path = tmp_path / "bad manifest.json"
    manifest_path.write_text("{not json")

    with pytest.raises(ValueError) as excinfo:
        load_manifest(manifest_path)

    assert str(manifest_path) in str(excinfo.value)
    assert "Invalid JSON" in str(excinfo.value)


def test_record_event_handles_unicode_and_spaces_in_paths(tmp_path: Path):
    manifest_path = tmp_path / "runs with spaces" / "セッション.json"
    init_manifest(manifest_path=manifest_path)

    event = record_event(
        manifest_path=manifest_path,
        event_type="decision",
        category="stress",
        source="test",
        payload={"summary": "unicode path survived", "emoji": "✅"},
    )
    manifest = load_manifest(manifest_path)
    event_log_path = Path(manifest["event_log_path"])
    if not event_log_path.is_absolute():
        event_log_path = manifest_path.parent / event_log_path
    events = [
        json.loads(line)
        for line in event_log_path.read_text().splitlines()
    ]

    assert events == [event]
    assert events[0]["payload"]["emoji"] == "✅"


def test_metadata_lint_rejects_related_skill_traversal_payloads(
    tmp_path: Path,
):
    skill_root = tmp_path / "claude-flow"
    skill_root.mkdir()
    (skill_root / "SKILL.md").write_text(
        """---
name: claude-flow
description: Use when testing path traversal payloads.
version: 1.0.0
metadata:
  hermes:
    tags: [coding]
    related_skills: [../../outside]
---

# Bad
"""
    )

    result = lint_skill_metadata(
        skill_root=skill_root,
        workspace_root=tmp_path,
    )

    assert result["ok"] is False
    assert any("../../outside" in error for error in result["errors"])


def test_security_lint_handles_large_guidance_file(tmp_path: Path):
    skill_root = tmp_path / "claude-flow"
    refs = skill_root / "references"
    refs.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text("# skill\n")
    (skill_root / "README.md").write_text("# readme\n")
    large_doc = ("ordinary guidance\n" * 10000) + "rm -rf /\n"
    (refs / "large.md").write_text(large_doc)

    result = lint_skill_security(skill_root=skill_root)

    assert result["ok"] is False
    assert any("destructive_root_rm" in error for error in result["errors"])
