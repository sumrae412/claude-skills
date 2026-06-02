"""Tests for outreach letter drafting helpers."""

from pathlib import Path

from scripts.outreach import (
    CandidateBrief,
    load_candidates,
    render_outreach_brief,
    write_letter_file,
)


def test_load_candidates_returns_top_n_sorted_by_score(tmp_path):
    csv = tmp_path / "candidates.csv"
    csv.write_text(
        "parcel_id,address,owner_name,owner_mailing,propensity_total,tier,reasons\n"
        "1,A Address,REGULAR,A Mailing,50,high_priority,absentee:FL\n"
        "2,B Address,REGULAR,B Mailing,80,act_this_week,sheriff_sale:2026-08-01\n"
        "3,C Address,REGULAR,C Mailing,20,worth_a_letter,probate_name_pattern\n"
    )
    cands = load_candidates(csv, top=2)
    assert len(cands) == 2
    assert cands[0].score == 80
    assert cands[1].score == 50


def test_render_brief_contains_all_signal_reasons():
    cand = CandidateBrief(
        address="123 ELM ST",
        mailing="999 BEACH RD",
        score=60,
        tier="high_priority",
        reasons=("sheriff_sale:2026-08-01", "absentee:FL"),
    )
    voice = "## Tone\nWarm, direct."
    brief = render_outreach_brief(cand, voice)
    assert "sheriff_sale:2026-08-01" in brief
    assert "absentee:FL" in brief


def test_render_brief_warns_about_owner_name_code():
    cand = CandidateBrief(
        address="x", mailing="y", score=50, tier="high_priority", reasons=()
    )
    brief = render_outreach_brief(cand, "voice")
    assert "owner_name" in brief.lower() or "generic salutation" in brief.lower()


def test_write_letter_file_sanitizes_address(tmp_path):
    cand = CandidateBrief(
        address="123 ELM ST, PITTSBURGH, PA, 15217",
        mailing="x",
        score=50,
        tier="high_priority",
        reasons=(),
    )
    body = "# To the homeowner at 123 Elm\n\nHello..."
    path = write_letter_file(cand, body, tmp_path)
    assert path.exists()
    assert path.parent.name == "letters"
    # Filename should not contain spaces or commas
    assert " " not in path.name
    assert "," not in path.name


def test_load_candidates_handles_empty_csv(tmp_path):
    csv = tmp_path / "empty.csv"
    csv.write_text(
        "parcel_id,address,owner_name,owner_mailing,propensity_total,tier,reasons\n"
    )
    assert load_candidates(csv, top=10) == []
