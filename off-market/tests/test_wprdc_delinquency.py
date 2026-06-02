"""Tests for the WPRDC tax delinquency adapter.

Fixture lives at ``fixtures/wprdc_delinquency.json`` (10-row CKAN snapshot).
"""

from __future__ import annotations

import json
import os
import pathlib

import pytest

from scripts.county_adapters.wprdc.delinquency import RESOURCE_ID, parse_delinquency


FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "wprdc_delinquency.json"


def _records():
    data = json.loads(FIXTURE.read_text())
    return data["result"]["records"] if "result" in data else data["records"]


def test_resource_id_is_documented():
    assert RESOURCE_ID
    assert len(RESOURCE_ID) > 30


def test_parse_delinquency_returns_dict_of_floats():
    delinq = parse_delinquency(_records())
    assert isinstance(delinq, dict)
    assert len(delinq) > 0
    for parcel_id, amount in delinq.items():
        assert isinstance(parcel_id, str)
        assert parcel_id  # non-empty
        assert isinstance(amount, float)
        assert amount > 0  # only owed amounts are kept


def test_parse_delinquency_sums_multiple_liens_per_parcel():
    synth = [
        {"pin": "P1", "amount": 100.0, "satisfied": False},
        {"pin": "P1", "amount": 250.50, "satisfied": False},
        {"pin": "P2", "amount": 75.0, "satisfied": False},
    ]
    delinq = parse_delinquency(synth)
    assert delinq["P1"] == 350.50
    assert delinq["P2"] == 75.0


def test_parse_delinquency_excludes_satisfied_liens():
    synth = [
        {"pin": "P1", "amount": 100.0, "satisfied": True},   # paid off
        {"pin": "P1", "amount": 50.0, "satisfied": False},
        {"pin": "P2", "amount": 200.0, "satisfied": True},   # fully satisfied
    ]
    delinq = parse_delinquency(synth)
    assert delinq == {"P1": 50.0}


def test_parse_delinquency_skips_blank_parcel_ids():
    synth = [
        {"pin": "", "amount": 100.0, "satisfied": False},
        {"pin": None, "amount": 50.0, "satisfied": False},
        {"pin": "P1", "amount": 25.0, "satisfied": False},
    ]
    delinq = parse_delinquency(synth)
    assert delinq == {"P1": 25.0}


@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="live WPRDC fetch")
def test_live_fetch_delinquency():
    from scripts.county_adapters.wprdc.delinquency import fetch_delinquency

    delinq = fetch_delinquency(limit=10)
    assert len(delinq) > 0
    for parcel_id, amount in delinq.items():
        assert parcel_id
        assert amount > 0
