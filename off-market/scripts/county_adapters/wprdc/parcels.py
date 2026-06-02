"""WPRDC parcels (Allegheny County Property Assessments) adapter.

Dataset: "Allegheny County Property Assessments" (package name `property-assessments`)
  https://data.wprdc.org/dataset/property-assessments

Resource: "Property Assessments Parcel Data (for downloads)" — CSV resource
  ID: 9a1c60bd-f9f7-4aba-aeb7-af8c3aaa44e5

We hit CKAN's `datastore_search` API rather than downloading the full CSV; the
full file is ~580K rows and we only ever need filtered slices.

Field-mapping notes
-------------------
The Allegheny assessor's downloadable file does NOT publish individual owner
*names* (privacy-redacted) — only an ``OWNERDESC`` code (e.g. ``REGULAR``,
``CORPORATION``, ``REGULAR-ETUX OR ET VIR``). For ``Parcel.owner_name`` we
populate that code as the best-available identifier; downstream consumers can
join against the Real Estate Portal for the actual name when needed.

``CHANGENOTICEADDRESS1..4`` are the four lines of the "send tax notices here"
mailing address — these ARE published. We concatenate them, trimming each.

Assessed value: we prefer ``COUNTYTOTAL`` (the official assessed value used
for tax billing) over ``FAIRMARKETTOTAL`` (the market estimate). Either may be
zero/None for exempt parcels.

Rooms / age: ``BEDROOMS``, ``FULLBATHS``, ``HALFBATHS``, ``YEARBLT`` are only
populated for residential improved parcels. Bathrooms total = full + 0.5*half.
"""

from __future__ import annotations

import logging
import os
from typing import Iterable

from scripts.models import Parcel

logger = logging.getLogger(__name__)

# Source-of-truth CKAN identifiers. Update both together if the dataset moves.
RESOURCE_ID = "9a1c60bd-f9f7-4aba-aeb7-af8c3aaa44e5"
DATASTORE_URL = "https://data.wprdc.org/api/3/action/datastore_search"


def _clean(value: object) -> str:
    """Trim and stringify; return '' for None/blank."""
    if value is None:
        return ""
    s = str(value).strip()
    return s


def _compose_address(rec: dict) -> str:
    """Build a single-line property address from the WPRDC columns."""
    house = _clean(rec.get("PROPERTYHOUSENUM"))
    frac = _clean(rec.get("PROPERTYFRACTION"))
    street = _clean(rec.get("PROPERTYADDRESS"))
    unit = _clean(rec.get("PROPERTYUNIT"))
    city = _clean(rec.get("PROPERTYCITY"))
    state = _clean(rec.get("PROPERTYSTATE"))
    zip_ = _clean(rec.get("PROPERTYZIP"))

    line1_parts = [p for p in (house, frac, street, unit) if p]
    line1 = " ".join(line1_parts)
    tail_parts = [p for p in (city, state, zip_) if p]
    tail = ", ".join(tail_parts) if tail_parts else ""
    if line1 and tail:
        return f"{line1}, {tail}"
    return line1 or tail


def _compose_owner_mailing(rec: dict) -> str:
    """Join CHANGENOTICEADDRESS1..4 into one line, dropping blanks."""
    parts = []
    for i in range(1, 5):
        v = _clean(rec.get(f"CHANGENOTICEADDRESS{i}"))
        if v:
            parts.append(v)
    return ", ".join(parts)


def _to_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f


def _to_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))  # tolerate "1995.0"-style strings
    except (TypeError, ValueError):
        return None


def _baths(rec: dict) -> float | None:
    full = _to_int(rec.get("FULLBATHS"))
    half = _to_int(rec.get("HALFBATHS"))
    if full is None and half is None:
        return None
    return (full or 0) + 0.5 * (half or 0)


def parse_parcels(records: Iterable[dict]) -> list[Parcel]:
    """Map WPRDC parcel records to ``Parcel`` instances.

    Rows missing any of the required fields (parcel_id, address, owner_name,
    owner_mailing) are skipped — logged at DEBUG, not raised.
    """
    out: list[Parcel] = []
    for rec in records:
        parcel_id = _clean(rec.get("PARID"))
        address = _compose_address(rec)
        owner_name = _clean(rec.get("OWNERDESC"))
        owner_mailing = _compose_owner_mailing(rec)

        if not (parcel_id and address and owner_name and owner_mailing):
            logger.debug(
                "wprdc.parcels: skipping row missing required fields (PARID=%r)",
                parcel_id,
            )
            continue

        assessed = _to_float(rec.get("COUNTYTOTAL"))
        if assessed == 0:
            assessed = None  # treat exempt zeros as "not reported"

        out.append(
            Parcel(
                parcel_id=parcel_id,
                address=address,
                owner_name=owner_name,
                owner_mailing=owner_mailing,
                assessed_value=assessed,
                lot_sqft=_to_float(rec.get("LOTAREA")),
                year_built=_to_int(rec.get("YEARBLT")),
                beds=_to_int(rec.get("BEDROOMS")),
                baths=_baths(rec),
            )
        )
    return out


def fetch_parcels(limit: int = 10) -> list[Parcel]:
    """Live CKAN fetch; parses through ``parse_parcels``.

    Imported lazily so unit tests don't require httpx at import time.
    """
    import httpx  # local import — keeps the test surface offline by default

    # The user's shell exports SSL_CERT_FILE to a path that may not exist on
    # this machine; let httpx fall back to its bundled certifi store when the
    # configured path is missing.
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
    return parse_parcels(payload["result"]["records"])
