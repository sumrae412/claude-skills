"""Live integration smoke test for the discover orchestrator.

Gated on ``RUN_LIVE_TESTS=1``. Hits real WPRDC + Redfin endpoints, so it's
slow (30-90s) and subject to upstream availability. Don't pin exact counts
— the underlying data shifts.

Run manually:
    RUN_LIVE_TESTS=1 /opt/homebrew/bin/python3.11 -m pytest \\
        off-market/tests/test_discover_live.py -v
"""

from __future__ import annotations

import os
from datetime import date

import pytest

from scripts.criteria import Criteria
from scripts.discover import discover


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_TESTS") != "1", reason="live discover end-to-end"
)
def test_discover_live_allegheny_small_scope(tmp_path):
    """End-to-end live run, narrowest practical scope.

    Asserts only: doesn't crash, writes three files, returns a well-typed
    result. Tier counts and absolute candidate numbers are NOT pinned —
    they shift with the live data, and the parcels-by-zip filter is
    currently post-fetch (so a small ``parcels_limit`` may yield zero
    in-zip parcels even though the underlying dataset has hundreds).
    The point of this smoke is "the wires connect," not "the rubric
    surfaces N candidates."
    """
    result = discover(
        "allegheny_pa",
        Criteria(zips=["15217"]),
        output_dir=tmp_path,
        use_cache=False,
        as_of=date(2026, 6, 1),
    )

    runs_dir = tmp_path / "runs"
    assert runs_dir.exists(), "runs/ directory not created"
    run_dir = next(runs_dir.iterdir())
    assert (run_dir / "candidates.csv").exists()
    assert (run_dir / "candidates.md").exists()
    assert (run_dir / "health.md").exists()

    # candidates.csv must always have a header row, even on zero candidates.
    csv_text = (run_dir / "candidates.csv").read_text()
    assert "parcel_id" in csv_text

    # Counts must be internally consistent (no negative-after-filter weirdness).
    assert result.parcels_total >= 0
    assert result.parcels_after_listings_filter <= result.parcels_total
    assert result.candidates_kept <= result.candidates_scored
