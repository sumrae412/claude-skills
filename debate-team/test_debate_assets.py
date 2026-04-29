from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent


def test_synthesis_and_tier3_guard_against_gold_like_bias():
    synthesis = (SKILL_ROOT / "phases" / "critics-and-synthesis.md").read_text()
    tier3 = (SKILL_ROOT / "phases" / "tier3-and-present.md").read_text()

    for text in (synthesis, tier3):
        lowered = text.lower()
        assert "gold-like" in lowered
        assert "correctness" in lowered
        assert "style preference" in lowered


def test_non_ui_critics_tie_minimality_to_concrete_risk():
    for relative_path in (
        "critics/deepseek-bug-hunter.md",
        "critics/gpt4o-architecture.md",
        "critics/gpt4o-completeness.md",
    ):
        text = (SKILL_ROOT / relative_path).read_text().lower()
        assert "bias guardrail" in text
        assert "concrete" in text
        assert "canonical" in text


def test_ui_critic_keeps_style_findings_domain_grounded():
    text = (SKILL_ROOT / "critics" / "haiku-style-ui.md").read_text().lower()

    assert "bias guardrail" in text
    assert "user-facing" in text
    assert "design-system" in text
    assert "accessibility" in text


def test_calibration_tracks_gold_like_drift():
    text = (SKILL_ROOT / "references" / "critic-calibration.md").read_text()
    lowered = text.lower()

    assert "gold-like bias" in lowered
    assert "not minimal" in lowered
    assert "one prompt change" in lowered
