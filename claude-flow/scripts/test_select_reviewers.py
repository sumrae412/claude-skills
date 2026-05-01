import json
from pathlib import Path

from select_reviewers import (
    bundled_registry_path,
    infer_review_budget,
    load_registry,
    merge_registry_data,
    select,
)


def test_bundled_registry_exists():
    assert bundled_registry_path().exists()


def test_merge_registry_data_overrides_by_id(tmp_path: Path):
    base = {
        "reviewers": [
            {"id": "coderabbit", "description": "base"},
            {"id": "async-reviewer", "description": "base async"}
        ]
    }
    override = {
        "reviewers": [
            {"id": "coderabbit", "description": "override"},
            {"id": "new-reviewer", "description": "new"}
        ]
    }

    merged = merge_registry_data(base, override)
    reviewers = {reviewer["id"]: reviewer for reviewer in merged["reviewers"]}

    assert reviewers["coderabbit"]["description"] == "override"
    assert reviewers["async-reviewer"]["description"] == "base async"
    assert reviewers["new-reviewer"]["description"] == "new"


def test_load_registry_resolves_relative_paths(tmp_path: Path):
    registry_path = tmp_path / "reviewer-registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "reviewers": [
                    {
                        "id": "curmudgeon-review",
                        "runner_script": "scripts/curmudgeon_review.sh"
                    },
                    {
                        "id": "adversarial-breaker",
                        "persona_file": "scripts/adversarial_breaker_persona.txt"
                    }
                ]
            }
        )
    )

    loaded = load_registry(registry_path)
    reviewers = {reviewer["id"]: reviewer for reviewer in loaded["reviewers"]}

    assert reviewers["curmudgeon-review"]["resolved_runner_script"].endswith(
        "scripts/curmudgeon_review.sh"
    )
    assert reviewers["adversarial-breaker"]["resolved_persona_file"].endswith(
        "scripts/adversarial_breaker_persona.txt"
    )


def test_select_marks_conditional_matches():
    registry = {
        "reviewers": [
            {"id": "always", "tier": "always", "cascade_tier": 1},
            {
                "id": "py-only",
                "tier": "conditional",
                "cascade_tier": 3,
                "file_patterns": ["**/*.py"]
            }
        ]
    }

    result = select(registry, ["app/services/example.py"], Path.cwd(), "high")

    assert result["by_tier"]["1"] == ["always"]
    assert result["by_tier"]["3"] == ["py-only"]


def test_select_matches_impeccable_detector_for_ui_files():
    registry = load_registry(bundled_registry_path())

    result = select(
        registry,
        ["app/templates/dashboard.html"],
        Path.cwd(),
        "medium",
    )

    matched = [
        reviewer["id"]
        for reviewer in result["conditional_matched"]
    ]
    assert "impeccable-detector" in matched
    assert "impeccable-detector" in result["by_tier"]["3"]


def test_select_skips_impeccable_detector_for_backend_only_files():
    registry = load_registry(bundled_registry_path())

    result = select(
        registry,
        ["app/services/calendar.py"],
        Path.cwd(),
        "medium",
    )

    matched = [
        reviewer["id"]
        for reviewer in result["conditional_matched"]
    ]
    assert "impeccable-detector" not in matched


def test_select_respects_review_budget():
    registry = {
        "reviewers": [
            {
                "id": "coderabbit",
                "tier": "always",
                "cascade_tier": 1,
                "min_budget": "low",
            },
            {
                "id": "expensive-reviewer",
                "tier": "always",
                "cascade_tier": 2,
                "min_budget": "high",
            }
        ]
    }

    result = select(registry, ["app/services/example.py"], Path.cwd(), "low")

    assert result["by_tier"]["1"] == ["coderabbit"]
    assert result["budget_skipped"] == [
        {
            "id": "expensive-reviewer",
            "reason": "needs budget high; selected low",
        }
    ]


def test_infer_review_budget_uses_workflow_path_default():
    registry = {"reviewers": []}

    budget, reasons = infer_review_budget(
        registry=registry,
        file_paths=["app/services/example.py"],
        diff_dir=Path.cwd(),
        workflow_path="full",
    )

    assert budget == "medium"
    assert "workflow path full defaults to medium" in reasons


def test_infer_review_budget_escalates_on_high_risk_patterns():
    registry = load_registry(bundled_registry_path())

    budget, reasons = infer_review_budget(
        registry=registry,
        file_paths=["alembic/versions/123_add_column.py"],
        diff_dir=Path.cwd(),
        workflow_path="lite",
    )

    assert budget == "high"
    assert "migration-reviewer signal detected" in reasons
