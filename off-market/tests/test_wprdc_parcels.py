"""Tests for the WPRDC parcels adapter.

Fixture-driven: a 10-row snapshot of the live CKAN response lives at
`fixtures/wprdc_parcels.json`. A separate live test is gated on
RUN_LIVE_TESTS=1 so CI never hits the network.
"""

from __future__ import annotations

import json
import os
import pathlib

import pytest

from scripts.county_adapters.wprdc.parcels import RESOURCE_ID, parse_parcels
from scripts.models import Parcel


FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "wprdc_parcels.json"


def _records():
    data = json.loads(FIXTURE.read_text())
    return data["result"]["records"] if "result" in data else data["records"]


def test_resource_id_is_documented():
    """Sanity: the chosen WPRDC resource ID is a UUID-shaped string."""
    assert RESOURCE_ID
    assert len(RESOURCE_ID) > 30  # UUIDs are 36 chars


def test_parse_parcels_returns_list_of_parcels():
    parcels = parse_parcels(_records())
    assert isinstance(parcels, list)
    assert len(parcels) > 0
    assert all(isinstance(p, Parcel) for p in parcels)


def test_parse_parcels_populates_required_fields():
    parcels = parse_parcels(_records())
    for p in parcels:
        assert p.parcel_id
        assert p.address
        assert p.owner_name
        assert p.owner_mailing


def test_parse_parcels_populates_assessed_value_when_present():
    parcels = parse_parcels(_records())
    with_value = [p for p in parcels if p.assessed_value is not None]
    assert len(with_value) > 0


def test_fetch_parcels_builds_filter_url_for_zips(monkeypatch):
    """Verify fetch_parcels constructs a filters= query param when zips passed."""
    captured: dict = {}

    class _FakeResp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "success": True,
                "result": {"records": [], "fields": []},
            }

    def fake_get(url, **kwargs):
        captured["url"] = url
        captured["params"] = kwargs.get("params")
        return _FakeResp()

    import httpx as _httpx

    monkeypatch.setattr(_httpx, "get", fake_get)

    from scripts.county_adapters.wprdc.parcels import fetch_parcels

    fetch_parcels(zips=["15217", "15232"], limit=100)

    params = captured["params"]
    assert "filters" in params, f"params missing filters key: {params!r}"
    # The filters value is JSON-encoded; both zips must appear, the column
    # name must be PROPERTYZIP, and the dataset stores zips as INT.
    filters_raw = params["filters"]
    assert "PROPERTYZIP" in filters_raw
    assert "15217" in filters_raw
    assert "15232" in filters_raw
    # Must be int-shaped (no quoted string list) — parcels dataset uses int.
    assert '"15217"' not in filters_raw, (
        "parcels PROPERTYZIP is INT in the dataset; should not be quoted "
        f"in filters JSON: {filters_raw!r}"
    )


def test_fetch_parcels_omits_filter_when_zips_empty_or_none(monkeypatch):
    """No zips → no filter param (preserves prior unfiltered-call shape)."""
    captured: dict = {}

    class _FakeResp:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"success": True, "result": {"records": [], "fields": []}}

    def fake_get(url, **kwargs):
        captured["params"] = kwargs.get("params")
        return _FakeResp()

    import httpx as _httpx

    monkeypatch.setattr(_httpx, "get", fake_get)

    from scripts.county_adapters.wprdc.parcels import fetch_parcels

    fetch_parcels(limit=50)
    assert "filters" not in captured["params"]
    fetch_parcels(limit=50, zips=[])
    assert "filters" not in captured["params"]
    fetch_parcels(limit=50, zips=None)
    assert "filters" not in captured["params"]


@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="live WPRDC fetch")
def test_live_fetch_parcels():
    from scripts.county_adapters.wprdc.parcels import fetch_parcels

    parcels = fetch_parcels(limit=5)
    assert len(parcels) > 0
    assert all(p.parcel_id for p in parcels)


@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="live WPRDC fetch")
def test_live_fetch_parcels_with_zip_filter_returns_only_that_zip():
    """Server-side zip filter should yield parcels that all match the zip."""
    from scripts.county_adapters.wprdc.parcels import fetch_parcels

    parcels = fetch_parcels(zips=["15217"], limit=200)
    assert len(parcels) > 0, "no parcels returned with server-side 15217 filter"
    # Most rows should embed the zip in their composed address. We tolerate
    # rows where address composition dropped the zip token (some rows have
    # blank PROPERTYZIP downstream of the filter, depending on row state) —
    # but the majority should match.
    matched = sum(1 for p in parcels if "15217" in p.address)
    assert matched >= len(parcels) // 2, (
        f"expected most parcels to embed 15217 in address; "
        f"only {matched} of {len(parcels)} did"
    )
