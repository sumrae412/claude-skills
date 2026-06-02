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


@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="live WPRDC fetch")
def test_live_fetch_parcels():
    from scripts.county_adapters.wprdc.parcels import fetch_parcels

    parcels = fetch_parcels(limit=5)
    assert len(parcels) > 0
    assert all(p.parcel_id for p in parcels)
