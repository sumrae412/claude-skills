"""WPRDC tax delinquency (Allegheny County Tax Liens) adapter.

Dataset: "Allegheny County Tax Liens (Filings, Satisfactions, and Current Status)"
  (package `allegheny-county-tax-liens-filed-and-satisfied`)
  https://data.wprdc.org/dataset/allegheny-county-tax-liens-filed-and-satisfied

We pick the COUNTY-level dataset (county-wide coverage) over the more limited
"City of Pittsburgh Property Tax Delinquency" — Allegheny County is the
broader surface and the off-market skill targets the full county.

Resource: "Tax liens with current status (beta) [API-only version]"
  ID: 65d0d259-3e58-49d3-bebb-80dc75f61245

We use the "with current status" view rather than the raw filings table —
each row carries a ``satisfied`` boolean so we can exclude paid-off liens
without joining a second resource. Multiple unsatisfied liens per parcel are
summed; the resulting ``float`` is total currently-owed USD.

Schema columns used: ``pin`` (parcel id), ``amount`` (USD), ``satisfied`` (bool).
"""

from __future__ import annotations

import logging
import os
from typing import Iterable

logger = logging.getLogger(__name__)

RESOURCE_ID = "65d0d259-3e58-49d3-bebb-80dc75f61245"
DATASTORE_URL = "https://data.wprdc.org/api/3/action/datastore_search"


def _to_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_satisfied(value: object) -> bool:
    """CKAN ships ``satisfied`` as a JSON bool, but be defensive about strings."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in ("true", "t", "yes", "y", "1")


def parse_delinquency(records: Iterable[dict]) -> dict[str, float]:
    """Return ``{parcel_id: total_unsatisfied_amount_usd}``.

    Skips: blank/null pins, rows with no amount, and satisfied liens.
    Sums across remaining rows per parcel.
    """
    totals: dict[str, float] = {}
    for rec in records:
        pin = str(rec.get("pin") or "").strip()
        if not pin:
            continue
        if _is_satisfied(rec.get("satisfied")):
            continue
        amount = _to_float(rec.get("amount"))
        if amount is None or amount <= 0:
            continue
        totals[pin] = totals.get(pin, 0.0) + amount
    return totals


def fetch_delinquency(
    limit: int = 10, zips: list[str] | None = None
) -> dict[str, float]:
    """Live CKAN fetch; parses through ``parse_delinquency``.

    ``zips`` is accepted for adapter symmetry but is a NO-OP — the
    tax-liens dataset publishes ``municipality`` / ``ward`` instead of a
    zip column, so server-side zip filtering isn't available. The
    downstream parcel-side filter already restricts the join surface;
    delinquency is post-joined by ``parcel_id``.
    """
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
    return parse_delinquency(payload["result"]["records"])
