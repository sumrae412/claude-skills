"""End-to-end tests for the Stage 1 ``discover`` orchestrator.

The orchestrator composes the county adapter + listings subtractor + propensity
scorer + output writers. Tests monkeypatch the adapter and the listings
fetcher so no live network is hit. A separate ``test_discover_live.py``
(gated on ``RUN_LIVE_TESTS=1``) hits the real adapter end-to-end.

Assertions are STRUCTURAL — header rows, file existence, ordering — not
byte-exact snapshots, so cosmetic changes to the writers don't break tests.
"""

from __future__ import annotations

import csv
from datetime import date

import pytest

from scripts import discover as discover_mod
from scripts.criteria import Criteria
from scripts.discover import DiscoverResult, discover
from scripts.models import Parcel


# ---------- canned fixtures ----------


def _fake_parcels() -> list[Parcel]:
    """Five parcels: 4 fire signals strong enough to stay above tier=dropped.

    Signal weights (from references/propensity-rubric.md):
      sheriff_sale:40, delinquency:5-25, absentee:10, long_tenure_equity:10.
    Tier thresholds: dropped<15, worth_a_letter<40, high_priority<70, act≥70.

    To survive `tier != dropped` (≥15) we stack signals so absentees also
    carry tenure equity, and the delinquency parcel has a real lien (≥20k).
    """
    return [
        Parcel(
            # long_tenure_high_equity (1995 sale, 73% equity) = 10pts → dropped.
            parcel_id="P-001",
            address="100 MAIN ST, PITTSBURGH, PA 15217",
            owner_name="REGULAR",
            owner_mailing="100 MAIN ST, PITTSBURGH, PA 15217",
            assessed_value=150_000.0,
            last_sale_date=date(1995, 5, 1),
            last_sale_price=40_000.0,
            year_built=1950,
        ),
        Parcel(
            # Absentee FL (+10) + long_tenure_high_equity (+10) = 20 → worth_a_letter.
            parcel_id="P-002",
            address="200 OAK AVE, PITTSBURGH, PA 15217",
            owner_name="CORPORATION",
            owner_mailing="999 BEACH RD, MIAMI, FL 33101",
            assessed_value=300_000.0,
            last_sale_date=date(1990, 1, 1),
            last_sale_price=50_000.0,
            year_built=1920,
        ),
        Parcel(
            # sheriff_sale (+40) = 40 → high_priority.
            parcel_id="P-003",
            address="50 BIRCH LN, PITTSBURGH, PA 15217",
            owner_name="REGULAR",
            owner_mailing="50 BIRCH LN, PITTSBURGH, PA 15217",
            assessed_value=80_000.0,
            sheriff_sale_date=date(2026, 8, 1),
            year_built=1965,
        ),
        Parcel(
            # No signals — dropped.
            parcel_id="P-004",
            address="400 ELM ST, PITTSBURGH, PA 15217",
            owner_name="REGULAR",
            owner_mailing="400 ELM ST, PITTSBURGH, PA 15217",
            assessed_value=200_000.0,
            last_sale_date=date(2024, 1, 1),
            year_built=2010,
        ),
        Parcel(
            # tax_owed 25k → weight 5 + 12.5 = 17.5 → worth_a_letter.
            parcel_id="P-005",
            address="500 PINE ST, PITTSBURGH, PA 15217",
            owner_name="REGULAR",
            owner_mailing="500 PINE ST, PITTSBURGH, PA 15217",
            assessed_value=120_000.0,
            tax_owed_usd=25_000.0,
            year_built=1955,
        ),
    ]


class _FakeAdapter:
    """Fake adapter that returns canned parcels regardless of criteria.

    Real adapters apply criteria themselves; we mimic that by zip-filtering.
    """

    def __init__(self, cache=None):
        self.cache = cache

    def load(self, criteria: Criteria, *, as_of=None) -> list[Parcel]:
        parcels = _fake_parcels()
        if criteria.zips:
            parcels = [p for p in parcels if any(z in p.address for z in criteria.zips)]
        return parcels


def _empty_listings(zip_code: str, *, throttle_seconds: float = 0.0) -> list[str]:
    return []


@pytest.fixture
def patched_discover(monkeypatch):
    """Replace the adapter registry + listings fetcher with fakes."""
    monkeypatch.setitem(discover_mod._ADAPTER_REGISTRY, "allegheny_pa", _FakeAdapter)
    monkeypatch.setattr(discover_mod, "fetch_listings", _empty_listings)


# ---------- tests ----------


def test_discover_writes_all_three_files(patched_discover, tmp_path):
    discover(
        "allegheny_pa",
        Criteria(zips=["15217"]),
        output_dir=tmp_path,
        use_cache=False,
        as_of=date(2026, 6, 1),
    )

    run_dir = tmp_path / "runs" / "2026-06-01-allegheny_pa"
    assert (run_dir / "candidates.csv").exists()
    assert (run_dir / "candidates.md").exists()
    assert (run_dir / "health.md").exists()

    csv_text = (run_dir / "candidates.csv").read_text()
    assert "parcel_id" in csv_text  # header row present
    assert "propensity_total" in csv_text
    assert "tier" in csv_text

    md_text = (run_dir / "candidates.md").read_text()
    assert "# " in md_text  # at least one H1

    health = (run_dir / "health.md").read_text()
    assert "Run health" in health
    assert "Parcels" in health


def test_discover_returns_result_struct(patched_discover, tmp_path):
    result = discover(
        "allegheny_pa",
        Criteria(),
        output_dir=tmp_path,
        use_cache=False,
        as_of=date(2026, 6, 1),
    )
    assert isinstance(result, DiscoverResult)
    assert result.parcels_total == 5
    # P-001 (10) and P-004 (0) drop below 15; P-002, P-003, P-005 stay.
    assert result.candidates_kept == 3
    assert len(result.output_files) == 3


def test_discover_unknown_county_raises(tmp_path):
    with pytest.raises((KeyError, ValueError), match="county|mars_xx"):
        discover("mars_xx", Criteria(), output_dir=tmp_path)


def test_discover_orders_csv_by_score_desc(patched_discover, tmp_path):
    discover(
        "allegheny_pa",
        Criteria(zips=["15217"]),
        output_dir=tmp_path,
        use_cache=False,
        as_of=date(2026, 6, 1),
    )
    run_dir = tmp_path / "runs" / "2026-06-01-allegheny_pa"
    with (run_dir / "candidates.csv").open() as f:
        rows = list(csv.DictReader(f))
    # First non-dropped row should have the highest propensity_total.
    kept = [r for r in rows if r["tier"] != "dropped"]
    totals = [float(r["propensity_total"]) for r in kept]
    assert totals == sorted(totals, reverse=True)
    # Sheriff sale parcel (P-003) should be first — 40 pts is the loudest signal.
    assert kept[0]["parcel_id"] == "P-003"


def test_discover_no_zip_skips_listings(patched_discover, tmp_path, monkeypatch):
    """When criteria.zips is empty, listings fetch is skipped entirely."""
    calls: list[str] = []

    def _spy_fetch(zip_code, **kw):
        calls.append(zip_code)
        return []

    monkeypatch.setattr(discover_mod, "fetch_listings", _spy_fetch)
    discover(
        "allegheny_pa",
        Criteria(),  # no zips
        output_dir=tmp_path,
        use_cache=False,
        as_of=date(2026, 6, 1),
    )
    assert calls == []


def test_discover_subtracts_listed_addresses(patched_discover, tmp_path, monkeypatch):
    """If a parcel's address shows up as an active listing, it's subtracted."""
    from scripts.listings.address_norm import normalize as _norm

    # Pre-list P-001 — it should drop out of candidates.
    listed = {_norm("100 MAIN ST")}
    monkeypatch.setattr(
        discover_mod, "fetch_listings", lambda z, **kw: list(listed)
    )

    result = discover(
        "allegheny_pa",
        Criteria(zips=["15217"]),
        output_dir=tmp_path,
        use_cache=False,
        as_of=date(2026, 6, 1),
    )
    assert result.parcels_total == 5
    assert result.parcels_after_listings_filter == 4
    run_dir = tmp_path / "runs" / "2026-06-01-allegheny_pa"
    with (run_dir / "candidates.csv").open() as f:
        rows = list(csv.DictReader(f))
    ids = {r["parcel_id"] for r in rows}
    assert "P-001" not in ids


def test_discover_empty_parcels_writes_files(patched_discover, tmp_path, monkeypatch):
    """Empty parcel list → still writes three files cleanly."""

    class _EmptyAdapter:
        def __init__(self, cache=None):
            pass

        def load(self, criteria, *, as_of=None):
            return []

    monkeypatch.setitem(discover_mod._ADAPTER_REGISTRY, "allegheny_pa", _EmptyAdapter)

    result = discover(
        "allegheny_pa",
        Criteria(),
        output_dir=tmp_path,
        use_cache=False,
        as_of=date(2026, 6, 1),
    )
    run_dir = tmp_path / "runs" / "2026-06-01-allegheny_pa"
    assert (run_dir / "candidates.csv").exists()
    assert (run_dir / "candidates.md").exists()
    assert (run_dir / "health.md").exists()
    assert result.parcels_total == 0
    assert result.candidates_kept == 0
