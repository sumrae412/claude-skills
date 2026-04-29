import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def test_workflow_profiles_cover_expected_paths():
    profiles = json.loads((SKILL_ROOT / "workflow-profiles.json").read_text())
    expected = {
        "bug",
        "fast",
        "plan",
        "clone",
        "lite",
        "audit",
        "explore",
        "full",
    }

    assert set(profiles["paths"]) == expected


def test_workflow_profiles_define_default_review_budget():
    profiles = json.loads((SKILL_ROOT / "workflow-profiles.json").read_text())

    for profile in profiles["paths"].values():
        assert profile["review_budget_default"] in {"low", "medium", "high"}


def test_workflow_profiles_reference_real_phase_files():
    profiles = json.loads((SKILL_ROOT / "workflow-profiles.json").read_text())
    phases_dir = SKILL_ROOT / "phases"

    for profile in profiles["paths"].values():
        for phase in profile["phases"]:
            phase_file = phases_dir / f"{phase}-implementation.md"
            if phase == "phase-1":
                phase_file = phases_dir / "phase-1-discovery.md"
            elif phase == "phase-2":
                phase_file = phases_dir / "phase-2-exploration.md"
            elif phase == "phase-3":
                phase_file = phases_dir / "phase-3-requirements.md"
            elif phase == "phase-4":
                phase_file = phases_dir / "phase-4-architecture.md"
            elif phase == "phase-4c":
                phase_file = phases_dir / "phase-4c-verification.md"
            elif phase == "phase-4d":
                phase_file = phases_dir / "phase-4d-skeletons.md"
            elif phase == "phase-5":
                phase_file = phases_dir / "phase-5-implementation.md"
            elif phase == "phase-5.5":
                phase_file = phases_dir / "phase-5.5-reflection.md"
            elif phase == "phase-6":
                phase_file = phases_dir / "phase-6-quality.md"

            assert phase_file.exists(), phase


def test_audit_profile_is_read_only_and_skips_phase_5():
    profiles = json.loads((SKILL_ROOT / "workflow-profiles.json").read_text())
    audit = profiles["paths"]["audit"]

    assert audit["mutation_allowed"] is False
    assert "phase-5" not in audit["phases"]


def test_bundled_registry_has_single_tier_one_reviewer():
    registry = json.loads((SKILL_ROOT / "reviewer-registry.json").read_text())
    tier_one = [
        reviewer["id"]
        for reviewer in registry["reviewers"]
        if reviewer["cascade_tier"] == 1
    ]

    assert tier_one == ["coderabbit"]


def test_bundled_registry_always_reviewers_respect_early_exit():
    registry = json.loads((SKILL_ROOT / "reviewer-registry.json").read_text())

    for reviewer in registry["reviewers"]:
        if reviewer["tier"] != "always":
            continue
        if reviewer["id"] == "coderabbit":
            assert reviewer["cascade_tier"] == 1
        else:
            assert reviewer["cascade_tier"] >= 2


def test_bundled_registry_reviewers_define_min_budget():
    registry = json.loads((SKILL_ROOT / "reviewer-registry.json").read_text())

    for reviewer in registry["reviewers"]:
        assert reviewer["min_budget"] in {"low", "medium", "high"}


def test_phase_6_reference_docs_exist():
    assert (SKILL_ROOT / "references" / "phase-6-review-operations.md").exists()
    assert (SKILL_ROOT / "references" / "phase-6-design-review.md").exists()


def test_run_manifest_and_capability_refs_exist():
    assert (SKILL_ROOT / "references" / "run-manifest.md").exists()
    assert (SKILL_ROOT / "references" / "project-capability-matrix.md").exists()
    assert (SKILL_ROOT / "scripts" / "run_manifest.py").exists()


def test_llm_judge_prompts_guard_against_gold_like_bias():
    persona = (SKILL_ROOT / "scripts" / "adversarial_breaker_persona.txt").read_text()
    phase_6 = (SKILL_ROOT / "phases" / "phase-6-quality.md").read_text()
    schema = (
        SKILL_ROOT / "references" / "reviewer-registry-schema.md"
    ).read_text()

    for text in (persona, phase_6, schema):
        lowered = text.lower()
        assert "correctness" in lowered
        assert "minimality" in lowered
        assert "gold" in lowered
        assert "tiebreaker" in lowered
