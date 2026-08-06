"""Long-tenure + high-equity signal.

Matches if the owner has held ≥20 years AND equity_pct ≥ 60% of assessed value.
Both legs are required — either alone is too weak.

equity_pct = (assessed_value - last_sale_price) / assessed_value

Missing any required field (last_sale_date, last_sale_price, assessed_value)
or negative equity (last_sale_price >= assessed_value) → matched=False.
"""
from __future__ import annotations

from datetime import date

from scripts.models import Parcel
from scripts.signals import SignalResult


def score(parcel: Parcel, *, as_of: date | None = None) -> SignalResult:
    """Score the long-tenure + high-equity signal for `parcel`."""
    if (
        parcel.last_sale_date is None
        or parcel.last_sale_price is None
        or parcel.assessed_value is None
        or parcel.assessed_value <= 0
    ):
        return SignalResult(matched=False, weight=0, reason="")

    today = as_of if as_of is not None else date.today()
    years_owned = today.year - parcel.last_sale_date.year - (
        1 if (today.month, today.day) < (parcel.last_sale_date.month, parcel.last_sale_date.day) else 0
    )

    equity_pct = (parcel.assessed_value - parcel.last_sale_price) / parcel.assessed_value

    if years_owned < 20 or equity_pct < 0.60:
        return SignalResult(matched=False, weight=0, reason="")

    return SignalResult(
        matched=True,
        weight=10,
        reason=f"long_tenure_high_equity:{years_owned}",
    )
