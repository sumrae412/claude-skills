"""Sheriff-sale-scheduled signal.

The loudest signal in the rubric (weight 40). Matches if a sheriff sale is
scheduled today or in the future — past auctions are excluded (the sale
already happened; outreach is too late).
"""
from __future__ import annotations

from datetime import date

from scripts.models import Parcel
from scripts.signals import SignalResult


def score(parcel: Parcel, *, as_of: date | None = None) -> SignalResult:
    sale_date = parcel.sheriff_sale_date
    if sale_date is None:
        return SignalResult(matched=False, weight=0, reason="")
    today = as_of if as_of is not None else date.today()
    if sale_date < today:
        return SignalResult(matched=False, weight=0, reason="")
    return SignalResult(
        matched=True,
        weight=40,
        reason=f"sheriff_sale:{sale_date.isoformat()}",
    )
