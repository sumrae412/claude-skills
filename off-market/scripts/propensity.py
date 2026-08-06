"""Propensity scorer — composes signal modules into a 0-105 score with tier label.

The rubric is canonical in `references/propensity-rubric.md`. This module is the
ONLY place the signals are composed; never compose signals ad hoc in other modules.

Fair housing: this module MUST NOT reference any field name in FORBIDDEN_FIELDS
(see references/fair-housing.md). A static AST test enforces this.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from scripts.models import Parcel
from scripts.signals import SignalResult
from scripts.signals import absentee, tenure_equity, delinquency, sheriff_sale, probate_name


# Signal registry — order is rubric order from references/propensity-rubric.md.
# Each entry: (signal_module, label_for_debug).
_SIGNALS = (
    (sheriff_sale, "sheriff_sale"),
    (delinquency, "delinquency"),
    (probate_name, "probate_name"),
    (absentee, "absentee"),
    (tenure_equity, "tenure_equity"),
)


@dataclass(frozen=True)
class PropensityScore:
    total: float        # 0..105 (open scale; not capped at 100)
    reasons: tuple[str, ...]  # ordered list of reason codes from matched signals
    tier: str           # "dropped" | "worth_a_letter" | "high_priority" | "act_this_week"


def tier_for(total: float) -> str:
    """Return the rubric tier for a total score."""
    if total < 15:
        return "dropped"
    if total < 40:
        return "worth_a_letter"
    if total < 70:
        return "high_priority"
    return "act_this_week"


def score(parcel: Parcel, *, as_of: Optional[date] = None) -> PropensityScore:
    """Compose all signal modules into a single propensity score."""
    if as_of is None:
        as_of = date.today()
    total = 0.0
    reasons: list[str] = []
    for signal_mod, _label in _SIGNALS:
        # Each signal takes (parcel, as_of=...) or (parcel,) — pass as_of universally
        # via kwargs; signals without an `as_of` param will reject. We dispatch by
        # introspection-free convention: signals that need as_of accept it as a kwarg.
        try:
            result: SignalResult = signal_mod.score(parcel, as_of=as_of)
        except TypeError:
            result = signal_mod.score(parcel)
        if result.matched:
            total += result.weight
            reasons.append(result.reason)
    return PropensityScore(
        total=total,
        reasons=tuple(reasons),
        tier=tier_for(total),
    )
