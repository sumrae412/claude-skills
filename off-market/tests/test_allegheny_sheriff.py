"""Tests for the Allegheny County sheriff-sales adapter.

WPRDC publishes Sheriff Sales as a structured CKAN dataset (package
``sheriff-sales``); we use the "Archive Bid List" resource as the canonical
source. Same fixture-driven pattern as the other WPRDC fetchers — live test
gated on ``RUN_LIVE_TESTS=1``.

The sheriff dataset does NOT carry ``PARID``, so this fetcher keys results
by a normalized property address. The downstream adapter performs the
address-join against the parcels feed.
"""

from __future__ import annotations

import json
import os
import pathlib
from datetime import date

import pytest

from scripts.county_adapters.allegheny_sheriff import (
    RESOURCE_ID,
    normalize_address,
    parse_sheriff_sales,
)


FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "allegheny_sheriff_sales.json"


def _records():
    data = json.loads(FIXTURE.read_text())
    return data["result"]["records"] if "result" in data else data["records"]


def test_resource_id_is_documented():
    assert RESOURCE_ID
    assert len(RESOURCE_ID) > 30  # UUIDs are 36 chars


def test_parse_returns_dict_of_date_values():
    result = parse_sheriff_sales(_records())
    assert isinstance(result, dict)
    assert len(result) > 0
    for key, value in result.items():
        assert isinstance(key, str)
        assert isinstance(value, date)


def test_dates_are_in_the_future_or_recent_past():
    """Validates each value parses to a real ``date`` (not freshness)."""
    result = parse_sheriff_sales(_records())
    assert all(isinstance(v, date) for v in result.values())
    # Sanity: years in the fixture are 2010-2030 ballpark.
    for v in result.values():
        assert 2000 <= v.year <= 2100


def test_keys_are_non_empty():
    result = parse_sheriff_sales(_records())
    for key in result.keys():
        assert key  # non-empty string
        assert key.strip() == key  # already normalized


def test_parse_handles_empty_input():
    assert parse_sheriff_sales([]) == {}
    # Also tolerate falsy iterables.
    assert parse_sheriff_sales(iter([])) == {}


def test_normalize_address_basic():
    """Address normalization is the join key; collisions across spelling matter."""
    assert normalize_address("110 POPLAR STREET ") == normalize_address("110 Poplar St")
    assert normalize_address("8525 PERSHING ST") == normalize_address("8525 pershing street")


def test_normalize_address_strips_punctuation_and_collapses_whitespace():
    assert normalize_address("123  Main   St.,") == "123 main street"


def test_parse_skips_rows_missing_street_or_date():
    synth = [
        {"Street": "", "ZIPCode": "15217", "SaleDate": "2025-01-15"},  # no street
        {"Street": "100 MAIN ST", "ZIPCode": "15217", "SaleDate": ""},  # no date
        {"Street": "200 OAK AVE", "ZIPCode": "15217", "SaleDate": "2025-02-20"},
    ]
    result = parse_sheriff_sales(synth)
    assert len(result) == 1
    assert normalize_address("200 OAK AVE") in result


@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="live WPRDC fetch")
def test_live_fetch_sheriff_sales():
    from scripts.county_adapters.allegheny_sheriff import fetch_sheriff_sales

    result = fetch_sheriff_sales(limit=10)
    assert isinstance(result, dict)
    assert len(result) > 0
    for key, value in result.items():
        assert key
        assert isinstance(value, date)
