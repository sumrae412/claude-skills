"""Tests for the WPRDC sales adapter.

Fixture lives at ``fixtures/wprdc_sales.json`` (10-row CKAN snapshot).
"""

from __future__ import annotations

import json
import os
import pathlib
from datetime import date

import pytest

from scripts.county_adapters.wprdc.sales import (
    RESOURCE_ID,
    Sale,
    parse_sales,
)


FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "wprdc_sales.json"


def _records():
    data = json.loads(FIXTURE.read_text())
    return data["result"]["records"] if "result" in data else data["records"]


def test_resource_id_is_documented():
    assert RESOURCE_ID
    assert len(RESOURCE_ID) > 30  # UUIDs are 36 chars


def test_parse_sales_returns_dict_keyed_by_parcel():
    sales = parse_sales(_records())
    assert isinstance(sales, dict)
    assert len(sales) > 0
    for parcel_id, sale in sales.items():
        assert isinstance(parcel_id, str)
        assert isinstance(sale, Sale)
        assert sale.parcel_id == parcel_id
        assert isinstance(sale.sale_date, date)
        assert isinstance(sale.sale_price, float)


def test_parse_sales_keeps_only_most_recent_per_parcel():
    # Synthetic multi-sale fixture — two sales on PARID-X, older first.
    synth = [
        {
            "PARID": "PARID-X",
            "SALEDATE": "2010-05-01",
            "PRICE": 50000,
        },
        {
            "PARID": "PARID-X",
            "SALEDATE": "2022-08-15",
            "PRICE": 175000,
        },
        {
            "PARID": "PARID-Y",
            "SALEDATE": "2018-01-10",
            "PRICE": 80000,
        },
    ]
    sales = parse_sales(synth)
    assert set(sales.keys()) == {"PARID-X", "PARID-Y"}
    assert sales["PARID-X"].sale_date == date(2022, 8, 15)
    assert sales["PARID-X"].sale_price == 175000.0
    assert sales["PARID-Y"].sale_date == date(2018, 1, 10)


def test_parse_sales_skips_rows_missing_date_or_price():
    synth = [
        {"PARID": "P1", "SALEDATE": "", "PRICE": 100},  # no date
        {"PARID": "P2", "SALEDATE": "2020-01-01", "PRICE": None},  # no price
        {"PARID": "P3", "SALEDATE": "2020-01-01", "PRICE": 99000},
    ]
    sales = parse_sales(synth)
    assert set(sales.keys()) == {"P3"}


@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="live WPRDC fetch")
def test_live_fetch_sales():
    from scripts.county_adapters.wprdc.sales import fetch_sales

    sales = fetch_sales(limit=10)
    assert len(sales) > 0
    for parcel_id, sale in sales.items():
        assert parcel_id
        assert sale.sale_date
