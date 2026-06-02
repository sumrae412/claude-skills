"""Allegheny County sheriff-sales adapter.

Data-source decision: WPRDC
============================

We checked WPRDC for a structured sheriff-sales dataset BEFORE falling back
to HTML scraping of the sheriff's office website. Result of::

    GET https://data.wprdc.org/api/3/action/package_search?q=sheriff&rows=20

(verified 2026-06-02): package ``sheriff-sales`` ("Allegheny County Sheriff
Sales") exists and exposes 9 CSV resources via the CKAN datastore API:

  - Current Sales Results / Current Bid List / Current Postponement List /
    Current Postponement Sales Results — "current" surfaces (small, ~60-100
    rows each, latest-month focus).
  - Archive Sales Results / Archive Bid List (10,631 rows) / Archive
    Postponement List / Archive Postponement Sales Results — historical
    archives across all months.
  - Sheriff Sales Data Dictionary (PDF).

We pick the **Archive Bid List** (resource ``b4899889-fbf4-43a5-a5ba-ae178fa07347``)
as the canonical source: it is the most comprehensive historical surface and
shares the same schema as the Current Bid List, so any future "current" pull
remains a one-line resource_id swap.

Because WPRDC provides this structured, we skip the documented fallback path
(scraping ``alleghenycountypa.gov/services/sheriff/real-estate-sales/`` for
monthly PDFs/HTML). No web-scraping subprocess is needed for this adapter.

Schema and join key
-------------------

The sheriff dataset does NOT carry ``PARID``. Each row publishes ``Street``,
``City``, ``State``, ``ZIPCode`` (and an unused-by-WPRDC ``Address`` column
that is typically null). Downstream join to ``Parcel.parcel_id`` happens at
the adapter layer by normalizing both sides through ``normalize_address`` and
matching on the resulting key.

Schema columns used: ``Street``, ``ZIPCode``, ``SaleDate``. ``SaleStatus``
is intentionally NOT filtered — POSTPONED, STAYED, ACTIVE, THIRD PARTY all
indicate the parcel is on the sheriff calendar, which is what the propensity
scorer needs. If a caller wants only ACTIVE listings, they can filter the
returned dict.
"""

from __future__ import annotations

import logging
import os
import re
from datetime import date, datetime
from typing import Iterable

logger = logging.getLogger(__name__)

# WPRDC "Archive Bid List" resource — see module docstring for the decision.
RESOURCE_ID = "b4899889-fbf4-43a5-a5ba-ae178fa07347"
DATASTORE_URL = "https://data.wprdc.org/api/3/action/datastore_search"


# Street-type abbreviation table for normalization. Both sides of an
# address-join must collapse to the same canonical form, so we expand
# short forms (ST → STREET, AVE → AVENUE) rather than the other direction.
_STREET_ABBREV = {
    "st": "street",
    "str": "street",
    "ave": "avenue",
    "av": "avenue",
    "rd": "road",
    "dr": "drive",
    "blvd": "boulevard",
    "ln": "lane",
    "ct": "court",
    "pl": "place",
    "ter": "terrace",
    "pkwy": "parkway",
    "hwy": "highway",
    "cir": "circle",
}


def normalize_address(addr: str) -> str:
    """Normalize a free-form street address into a stable join key.

    Lowercase, strip punctuation, collapse whitespace, expand common street
    abbreviations. The output is the JOIN KEY — not a display string.
    """
    if not addr:
        return ""
    s = str(addr).lower()
    # Drop punctuation we don't want as a join-key signal.
    s = re.sub(r"[.,#]+", " ", s)
    # Collapse all whitespace.
    s = re.sub(r"\s+", " ", s).strip()
    # Expand street-type abbreviations only when they appear as standalone tokens.
    tokens = s.split(" ")
    expanded = [_STREET_ABBREV.get(tok, tok) for tok in tokens]
    return " ".join(expanded).strip()


def _parse_date(value: object) -> date | None:
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
    try:
        return datetime.fromisoformat(s).date()
    except ValueError:
        return None


def parse_sheriff_sales(records: Iterable[dict]) -> dict[str, date]:
    """Parse WPRDC sheriff records into ``{normalized_address: sale_date}``.

    Rows missing ``Street`` or ``SaleDate`` are skipped (logged DEBUG).
    Multiple postponements of the same address collapse to the LATEST date —
    consistent with sales.py's "most recent wins" policy.
    """
    out: dict[str, date] = {}
    for rec in records:
        street = str(rec.get("Street") or "").strip()
        if not street:
            continue
        sale_date = _parse_date(rec.get("SaleDate"))
        if sale_date is None:
            logger.debug(
                "allegheny_sheriff: skipping row missing SaleDate (Street=%r)", street
            )
            continue
        key = normalize_address(street)
        if not key:
            continue
        existing = out.get(key)
        if existing is None or sale_date > existing:
            out[key] = sale_date
    return out


def fetch_sheriff_sales(limit: int = 100) -> dict[str, date]:
    """Live WPRDC CKAN fetch; parses through ``parse_sheriff_sales``."""
    import httpx

    cert_path = os.environ.get("SSL_CERT_FILE")
    if cert_path and not os.path.exists(cert_path):
        os.environ.pop("SSL_CERT_FILE", None)

    resp = httpx.get(
        DATASTORE_URL,
        params={
            "resource_id": RESOURCE_ID,
            "limit": limit,
            "sort": "SaleDate desc",
        },
        timeout=60,
    )
    resp.raise_for_status()
    payload = resp.json()
    if not payload.get("success"):
        raise RuntimeError(f"WPRDC datastore_search failed: {payload.get('error')}")
    return parse_sheriff_sales(payload["result"]["records"])
