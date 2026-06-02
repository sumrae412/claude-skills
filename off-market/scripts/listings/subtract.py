"""Subtract actively-listed homes from a candidate-parcel set.

The off-market workflow's premise is "owner hasn't already listed it" —
this module is the single integration point that drops parcels whose
address matches an actively-listed home (per the listings fetcher's
output).

Listings are expected to be a `set[str]` of NORMALIZED street addresses
(per :func:`scripts.listings.address_norm.normalize`). The fetcher
(`scripts.listings.redfin.fetch_listings`) already returns normalized
addresses, so the caller can plumb its output directly into ``listings``
here. We re-normalize the parcels' addresses inside this function so
callers can pass raw `Parcel` objects without pre-processing — at typical
working-set sizes (N ≤ 50K parcels per run) the per-parcel normalize
cost is negligible.
"""

from __future__ import annotations

from scripts.listings.address_norm import normalize
from scripts.models import Parcel


def subtract_listed(parcels: list[Parcel], listings: set[str]) -> list[Parcel]:
    """Return parcels whose normalized address is NOT in `listings`.

    Args:
        parcels: candidate parcels from the upstream county adapter.
        listings: set of NORMALIZED street addresses (caller normalizes
            via :func:`scripts.listings.address_norm.normalize`; the
            listings fetchers in this package already return normalized
            output).

    Returns:
        Filtered parcels in their original input order.

    Empty `listings` → identity (no subtraction performed). Useful for the
    degraded-fetch case where the listings source is hostile/blocked: the
    upstream fetcher returns ``[]``, the caller wraps it as ``set()``, and
    this function passes everything through with a clear "no subtraction"
    semantics.
    """
    if not listings:
        return list(parcels)
    return [p for p in parcels if normalize(p.address) not in listings]
