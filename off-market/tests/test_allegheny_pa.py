"""Tests for the ``AlleghenyPAAdapter`` orchestrator.

The adapter composes four WPRDC fetchers (parcels + sales + delinquency +
sheriff sales) into enriched ``Parcel`` objects and filters by ``Criteria``.

Tests use ``monkeypatch.setattr`` to inject fake fetchers — NO live network
in unit tests. A single live smoke test (gated on ``RUN_LIVE_TESTS=1``)
confirms the wires connect end-to-end against the live WPRDC API.
"""

from __future__ import annotations

import os
import pathlib
import tempfile
from datetime import date

import pytest

from scripts.county_adapters import allegheny_pa
from scripts.county_adapters.allegheny_pa import AlleghenyPAAdapter
from scripts.county_adapters.wprdc.sales import Sale
from scripts.cache import Cache
from scripts.criteria import Criteria
from scripts.models import Parcel


# ---------- shared canned fixtures ----------

def _canned_parcels() -> list[Parcel]:
    """Three parcels in three zips with varied beds/values, identical schema."""
    return [
        Parcel(
            parcel_id="P-001",
            address="100 MAIN ST, PITTSBURGH, PA 15217",
            owner_name="REGULAR",
            owner_mailing="100 MAIN ST, PITTSBURGH, PA 15217",
            assessed_value=150_000.0,
            beds=3,
            baths=2.0,
            lot_sqft=5000.0,
            year_built=1950,
        ),
        Parcel(
            parcel_id="P-002",
            address="200 OAK AVE, PITTSBURGH, PA 15206",
            owner_name="CORPORATION",
            owner_mailing="999 MARKET ST, NEW YORK, NY 10001",
            assessed_value=300_000.0,
            beds=4,
            baths=2.5,
            lot_sqft=6500.0,
            year_built=1920,
        ),
        Parcel(
            parcel_id="P-003",
            address="50 BIRCH LN, PITTSBURGH, PA 15217",
            owner_name="REGULAR",
            owner_mailing="50 BIRCH LN, PITTSBURGH, PA 15217",
            assessed_value=80_000.0,
            beds=2,
            baths=1.0,
            lot_sqft=3000.0,
            year_built=1965,
        ),
    ]


def _canned_sales() -> dict[str, Sale]:
    return {
        "P-001": Sale(parcel_id="P-001", sale_date=date(2018, 5, 1), sale_price=120_000.0),
        # P-002 has no sale on record.
        "P-003": Sale(parcel_id="P-003", sale_date=date(2022, 9, 15), sale_price=70_000.0),
    }


def _canned_delinquency() -> dict[str, float]:
    return {
        "P-002": 4_500.0,
        # P-001 and P-003 have no liens.
    }


def _canned_sheriff() -> dict[str, date]:
    # Address-keyed (sheriff dataset has no PARID).
    # Key MUST match the address-normalized form of parcel P-002's address.
    from scripts.county_adapters.allegheny_sheriff import normalize_address

    return {
        normalize_address("200 OAK AVE"): date(2025, 3, 15),
    }


@pytest.fixture
def patched_fetchers(monkeypatch):
    """Patch every fetcher the adapter calls into canned data.

    ``fetch_parcels`` honors the ``zips`` kwarg in the same way the real
    CKAN call does (server-side filter on ``PROPERTYZIP``) so adapter
    tests exercise the push-down path. ``fetch_sales`` is filtered the
    same way (sales dataset publishes PROPERTYZIP too). Other fetchers
    accept the kwarg as a no-op for adapter symmetry.
    """

    def _fake_fetch_parcels(**kw):
        zips = kw.get("zips") or None
        parcels = _canned_parcels()
        if not zips:
            return parcels
        zip_set = {str(z).strip() for z in zips}
        return [p for p in parcels if any(z in p.address for z in zip_set)]

    def _fake_fetch_sales(**kw):
        zips = kw.get("zips") or None
        sales = _canned_sales()
        if not zips:
            return sales
        # The canned sales don't carry an address; join through parcel_ids of
        # the pre-zip-filtered canned parcels for fidelity.
        keep_ids = {p.parcel_id for p in _fake_fetch_parcels(zips=zips)}
        return {pid: s for pid, s in sales.items() if pid in keep_ids}

    monkeypatch.setattr(allegheny_pa, "fetch_parcels", _fake_fetch_parcels)
    monkeypatch.setattr(allegheny_pa, "fetch_sales", _fake_fetch_sales)
    monkeypatch.setattr(
        allegheny_pa, "fetch_delinquency", lambda **kw: _canned_delinquency()
    )
    monkeypatch.setattr(
        allegheny_pa, "fetch_sheriff_sales", lambda **kw: _canned_sheriff()
    )


# ---------- behavioral tests ----------

def test_adapter_load_returns_parcels_with_no_criteria(patched_fetchers):
    adapter = AlleghenyPAAdapter()
    parcels = adapter.load(Criteria())
    assert len(parcels) == 3
    ids = {p.parcel_id for p in parcels}
    assert ids == {"P-001", "P-002", "P-003"}


def test_adapter_load_filters_by_zips(patched_fetchers):
    adapter = AlleghenyPAAdapter()
    parcels = adapter.load(Criteria(zips=["15217"]))
    ids = {p.parcel_id for p in parcels}
    assert ids == {"P-001", "P-003"}


def test_adapter_load_filters_by_beds_min(patched_fetchers):
    adapter = AlleghenyPAAdapter()
    parcels = adapter.load(Criteria(beds_min=3))
    ids = {p.parcel_id for p in parcels}
    assert ids == {"P-001", "P-002"}


def test_adapter_load_filters_by_price_max(patched_fetchers):
    adapter = AlleghenyPAAdapter()
    parcels = adapter.load(Criteria(price_max=200_000))
    ids = {p.parcel_id for p in parcels}
    assert ids == {"P-001", "P-003"}


def test_adapter_load_filters_by_lot_sqft_min(patched_fetchers):
    adapter = AlleghenyPAAdapter()
    parcels = adapter.load(Criteria(lot_sqft_min=5500))
    ids = {p.parcel_id for p in parcels}
    assert ids == {"P-002"}


def test_adapter_load_enriches_sales_data(patched_fetchers):
    adapter = AlleghenyPAAdapter()
    parcels = adapter.load(Criteria())
    by_id = {p.parcel_id: p for p in parcels}
    assert by_id["P-001"].last_sale_date == date(2018, 5, 1)
    assert by_id["P-001"].last_sale_price == 120_000.0
    assert by_id["P-003"].last_sale_date == date(2022, 9, 15)


def test_adapter_load_enriches_delinquency(patched_fetchers):
    adapter = AlleghenyPAAdapter()
    parcels = adapter.load(Criteria())
    by_id = {p.parcel_id: p for p in parcels}
    assert by_id["P-002"].tax_owed_usd == 4_500.0


def test_adapter_load_enriches_sheriff_sale(patched_fetchers):
    adapter = AlleghenyPAAdapter()
    parcels = adapter.load(Criteria())
    by_id = {p.parcel_id: p for p in parcels}
    assert by_id["P-002"].sheriff_sale_date == date(2025, 3, 15)


def test_adapter_load_unmatched_parcel_has_none_for_optional_fields(patched_fetchers):
    adapter = AlleghenyPAAdapter()
    parcels = adapter.load(Criteria())
    by_id = {p.parcel_id: p for p in parcels}
    # P-002 has no sale on record
    assert by_id["P-002"].last_sale_date is None
    assert by_id["P-002"].last_sale_price is None
    # P-001 and P-003 have no liens or sheriff sales
    assert by_id["P-001"].tax_owed_usd is None
    assert by_id["P-001"].sheriff_sale_date is None
    assert by_id["P-003"].sheriff_sale_date is None


def test_adapter_load_uses_cache_when_provided(patched_fetchers, monkeypatch):
    """When cache is provided, fetchers should be wrapped through get_or_fetch."""
    call_count = {"parcels": 0, "sales": 0, "delinquency": 0, "sheriff": 0}

    def make_counter(name, original):
        def wrapped(**kw):
            call_count[name] += 1
            return original(**kw)
        return wrapped

    monkeypatch.setattr(
        allegheny_pa, "fetch_parcels", make_counter("parcels", lambda **kw: _canned_parcels())
    )
    monkeypatch.setattr(
        allegheny_pa, "fetch_sales", make_counter("sales", lambda **kw: _canned_sales())
    )
    monkeypatch.setattr(
        allegheny_pa, "fetch_delinquency", make_counter("delinquency", lambda **kw: _canned_delinquency())
    )
    monkeypatch.setattr(
        allegheny_pa, "fetch_sheriff_sales", make_counter("sheriff", lambda **kw: _canned_sheriff())
    )

    with tempfile.TemporaryDirectory() as tmp:
        cache = Cache(root=pathlib.Path(tmp))
        adapter = AlleghenyPAAdapter(cache=cache)
        # First load — should hit fetchers.
        first = adapter.load(Criteria())
        # Second load — should hit cache, not fetchers.
        second = adapter.load(Criteria())
        # Each fetcher was called exactly once.
        for k in call_count:
            assert call_count[k] == 1, f"{k} was called {call_count[k]} times"
        assert len(first) == len(second)


def test_adapter_load_with_no_cache_skips_caching_gracefully(patched_fetchers):
    """cache=None must not crash; fetchers are called directly."""
    adapter = AlleghenyPAAdapter()  # default cache=None
    parcels = adapter.load(Criteria())
    assert len(parcels) == 3


@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="live WPRDC + sheriff fetch")
def test_adapter_load_live_smoke():
    """Smoke test: wires connect against live WPRDC. Don't pin exact counts."""
    adapter = AlleghenyPAAdapter()
    parcels = adapter.load(Criteria(zips=["15217"]))
    # We don't assert non-empty here because live filtering may yield 0 in
    # any individual `limit`-bounded page; just confirm the call returns
    # well-typed output.
    assert isinstance(parcels, list)
    for p in parcels:
        assert isinstance(p, Parcel)
        assert p.parcel_id
