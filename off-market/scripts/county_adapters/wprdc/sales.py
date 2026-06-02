"""WPRDC sales (Allegheny County Property Sale Transactions) adapter.

Dataset: "Allegheny County Property Sale Transactions" (package `real-estate-sales`)
  https://data.wprdc.org/dataset/real-estate-sales

Resource: "Property Sales Transactions" — the cross-year CSV (all years combined,
NOT the per-year breakouts like "2012 Property Sales Transactions").
  ID: 5bbe6c55-bce6-4edb-9d04-68edeb6bf7b1

Schema columns used: ``PARID``, ``SALEDATE`` (YYYY-MM-DD ISO), ``PRICE``.

We collapse multi-sale parcels to the MOST RECENT sale; downstream consumers
only need a single ``(last_sale_date, last_sale_price)`` to score recency.
Older transactions stay in WPRDC if a future caller needs them — re-fetch with
a date filter.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable

logger = logging.getLogger(__name__)

RESOURCE_ID = "5bbe6c55-bce6-4edb-9d04-68edeb6bf7b1"
DATASTORE_URL = "https://data.wprdc.org/api/3/action/datastore_search"


@dataclass(frozen=True)
class Sale:
    """A single property sale: parcel id, date, price (USD)."""

    parcel_id: str
    sale_date: date
    sale_price: float


def _parse_date(value: object) -> date | None:
    """WPRDC sales emit ISO ``YYYY-MM-DD``; tolerate a few common variants."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    # ISO with time component
    try:
        return datetime.fromisoformat(s).date()
    except ValueError:
        return None


def _to_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_sales(records: Iterable[dict]) -> dict[str, Sale]:
    """Return ``{parcel_id: Sale}`` keeping only the most recent sale per parcel.

    Rows missing ``PARID``, ``SALEDATE``, or ``PRICE`` are skipped (logged DEBUG).
    """
    best: dict[str, Sale] = {}
    for rec in records:
        parcel_id = str(rec.get("PARID") or "").strip()
        sale_date = _parse_date(rec.get("SALEDATE"))
        price = _to_float(rec.get("PRICE"))

        if not parcel_id or sale_date is None or price is None:
            logger.debug(
                "wprdc.sales: skipping row missing required fields (PARID=%r, "
                "SALEDATE=%r, PRICE=%r)",
                parcel_id,
                rec.get("SALEDATE"),
                rec.get("PRICE"),
            )
            continue

        sale = Sale(parcel_id=parcel_id, sale_date=sale_date, sale_price=price)
        existing = best.get(parcel_id)
        if existing is None or sale.sale_date > existing.sale_date:
            best[parcel_id] = sale
    return best


def fetch_sales(limit: int = 10) -> dict[str, Sale]:
    """Live CKAN fetch; parses through ``parse_sales``."""
    import httpx

    cert_path = os.environ.get("SSL_CERT_FILE")
    if cert_path and not os.path.exists(cert_path):
        os.environ.pop("SSL_CERT_FILE", None)

    resp = httpx.get(
        DATASTORE_URL,
        params={"resource_id": RESOURCE_ID, "limit": limit},
        timeout=60,
    )
    resp.raise_for_status()
    payload = resp.json()
    if not payload.get("success"):
        raise RuntimeError(f"WPRDC datastore_search failed: {payload.get('error')}")
    return parse_sales(payload["result"]["records"])
