"""Snapshot stability test for the outreach brief.

Locks in the exact text of ``render_outreach_brief()`` for a canonical
``CandidateBrief``, so future prompt edits show up as visible diffs. If the
brief shape changes (sections added, wording shifted), the test fails — the
author updates the snapshot with intent.
"""

import pathlib

from scripts.outreach import CandidateBrief, render_outreach_brief

CANONICAL = CandidateBrief(
    address="123 ELM ST, PITTSBURGH, PA, 15217",
    mailing="999 BEACH RD, MIAMI, FL, 33101",
    score=50,
    tier="high_priority",
    reasons=("sheriff_sale:2026-08-01", "absentee:FL", "long_tenure_high_equity:25"),
    optional_user_note="Blue craftsman with the porch swing on the corner of Elm and 5th.",
)

CANONICAL_VOICE = """## Tone
Warm, specific. Not salesy.
## Sentence cadence
Short declaratives. Avg ~12 words.
"""

SNAPSHOT_PATH = pathlib.Path(__file__).parent / "fixtures" / "outreach_brief_snapshot.txt"


def test_render_outreach_brief_matches_snapshot():
    actual = render_outreach_brief(CANONICAL, CANONICAL_VOICE)
    expected = SNAPSHOT_PATH.read_text()
    assert actual == expected, (
        "Prompt brief drifted. Update snapshot with:\n"
        "  pathlib.Path(__file__).parent / 'fixtures' / 'outreach_brief_snapshot.txt'"
        "\nThen confirm intent before committing."
    )
