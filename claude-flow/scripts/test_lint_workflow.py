import json
from pathlib import Path

from lint_workflow import lint_workflow


def _valid_profiles() -> dict:
    return {
        "paths": {
            "bug": {"phases": ["phase-1"], "mutation_allowed": True},
            "fast": {"phases": ["phase-1"], "mutation_allowed": True},
            "plan": {
                "phases": ["phase-1", "phase-4c", "phase-5", "phase-5.5", "phase-6"],
                "mutation_allowed": True,
            },
            "clone": {
                "phases": ["phase-1", "phase-4c", "phase-5", "phase-5.5", "phase-6"],
                "mutation_allowed": True,
            },
            "lite": {
                "phases": [
                    "phase-1",
                    "phase-2",
                    "phase-3",
                    "phase-4",
                    "phase-4c",
                    "phase-5",
                    "phase-5.5",
                    "phase-6",
                ],
                "mutation_allowed": True,
            },
            "audit": {
                "phases": ["phase-1", "phase-2", "phase-3", "phase-4", "phase-6"],
                "mutation_allowed": False,
            },
            "explore": {"phases": ["phase-1"], "mutation_allowed": True},
            "full": {
                "phases": [
                    "phase-1",
                    "phase-2",
                    "phase-3",
                    "phase-4",
                    "phase-4c",
                    "phase-4d",
                    "phase-5",
                    "phase-5.5",
                    "phase-6",
                ],
                "mutation_allowed": True,
            },
        },
        "phase_transitions": [
            {"from": "phase-1", "to": "phase-4c"},
            {"from": "phase-4", "to": "phase-4c"},
            {"from": "phase-4c", "to": "phase-4d"},
            {"from": "phase-4c", "to": "phase-5"},
        ],
    }


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _build_min_skill_root(tmp_path: Path) -> Path:
    skill_root = tmp_path / "claude-flow"
    _write_text(skill_root / "SKILL.md", "# skill\n")
    _write_text(skill_root / "README.md", "# readme\n")
    _write_text(skill_root / "phases" / "phase-3-requirements.md", "# p3\n")
    _write_text(skill_root / "phases" / "phase-4-architecture.md", "# p4\n")
    _write_text(skill_root / "phases" / "phase-4c-verification.md", "# p4c\n")
    _write_text(skill_root / "phases" / "phase-6-quality.md", "# p6\n")
    _write_text(skill_root / "references" / "memory-injection.md", "# mem\n")
    _write_text(skill_root / "references" / "lookup-detectors.md", "# lookups\n")
    _write_text(
        skill_root / "references" / "subagent-driven-development.md", "# sdd\n"
    )
    _write_text(skill_root / "references" / "run-manifest.md", "# run manifest\n")
    _write_text(
        skill_root / "references" / "project-capability-matrix.md",
        "# capability matrix\n",
    )
    _write_text(
        skill_root / "workflow-profiles.json",
        json.dumps(_valid_profiles(), indent=2),
    )
    _write_text(skill_root / "scripts" / "run_manifest.py", "# helper\n")
    return skill_root


def test_lint_workflow_passes_on_current_repo():
    repo_root = Path(__file__).resolve().parents[2]

    result = lint_workflow(
        skill_root=repo_root / "claude-flow",
        project_root=repo_root,
        include_review_base=True,
    )

    assert result["errors"] == []


def test_lint_workflow_flags_stale_active_doc_patterns(tmp_path: Path):
    skill_root = _build_min_skill_root(tmp_path)
    _write_text(
        skill_root / "phases" / "phase-3-requirements.md",
        "python3 skills/claude-flow/scripts/audit_phase3_questions.py --json\n",
    )
    _write_text(
        skill_root / "phases" / "phase-6-quality.md",
        "git diff --name-only HEAD~1\n",
    )

    result = lint_workflow(
        skill_root=skill_root,
        project_root=tmp_path,
        include_review_base=False,
    )

    assert result["ok"] is False
    assert any("legacy skill script prefix" in error for error in result["errors"])
    assert any("hardcoded HEAD~1 review base" in error for error in result["errors"])


def test_lint_workflow_flags_phase_drift_and_missing_reference_assets(
    tmp_path: Path,
):
    skill_root = _build_min_skill_root(tmp_path)
    profiles = _valid_profiles()
    profiles["paths"]["plan"]["phases"] = ["phase-1", "phase-5", "phase-6"]
    profiles["phase_transitions"] = [{"from": "phase-1", "to": "phase-5"}]
    _write_text(
        skill_root / "workflow-profiles.json",
        json.dumps(profiles, indent=2),
    )
    (skill_root / "references" / "run-manifest.md").unlink()

    result = lint_workflow(
        skill_root=skill_root,
        project_root=tmp_path,
        include_review_base=False,
    )

    assert result["ok"] is False
    assert any("path 'plan' phases drifted" in error for error in result["errors"])
    assert any(
        "missing phase transition phase-4 -> phase-4c" in error
        for error in result["errors"]
    )
    assert any("run-manifest reference missing" in error for error in result["errors"])


def test_lint_workflow_flags_missing_run_manifest_helper(tmp_path: Path):
    skill_root = _build_min_skill_root(tmp_path)
    (skill_root / "scripts" / "run_manifest.py").unlink()

    result = lint_workflow(
        skill_root=skill_root,
        project_root=tmp_path,
        include_review_base=False,
    )

    assert result["ok"] is False
    assert any("run-manifest helper missing" in error for error in result["errors"])
