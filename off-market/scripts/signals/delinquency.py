"""Tax-delinquency signal.

Matches if `tax_owed_usd` is not None and > 0. Weight scales with amount:
  weight = min(5 + 0.5 * (owed / 1000), 25)

Floor 5 (presence of any owed tax is a soft signal); cap 25 prevents one
runaway delinquent from dominating the rubric.
"""
from __future__ import annotations

from scripts.models import Parcel
from scripts.signals import SignalResult


def score(parcel: Parcel) -> SignalResult:
    """Score the tax-delinquency signal for `parcel`."""
    owed = parcel.tax_owed_usd
    if owed is None or owed <= 0:
        return SignalResult(matched=False, weight=0, reason="")
    weight = min(5 + 0.5 * (owed / 1000), 25)
    return SignalResult(
        matched=True,
        weight=weight,
        reason=f"tax_delinquent:${int(owed)}",
    )
