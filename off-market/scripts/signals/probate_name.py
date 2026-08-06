"""Probate-name-pattern signal.

Matches if `owner_name` contains "Estate of " (leading), "Heirs of"
(anywhere, word-bounded), or ", Deceased" (trailing). Case-insensitive.

Corporate / trust names are EXCLUDED even when a probate pattern is
present — an LLC named "Estate Realty LLC" is not a probate estate, and
"John Doe Family Trust" is estate-planning structure, not a probate signal.
"""
from __future__ import annotations

import re

from scripts.models import Parcel
from scripts.signals import SignalResult

_PROBATE_PATTERNS = [
    re.compile(r"^Estate of\b", re.IGNORECASE),
    re.compile(r"\bHeirs of\b", re.IGNORECASE),
    re.compile(r",\s*Deceased\s*$", re.IGNORECASE),
]

# Word-bounded corporate / trust tokens. "Trust" is excluded here because
# "John Doe Family Trust" is an estate-planning structure, not a probate
# signal — different mailing / contact mechanics.
_CORPORATE_PATTERNS = [
    re.compile(r"\bLLC\b", re.IGNORECASE),
    re.compile(r"\bInc\b", re.IGNORECASE),
    re.compile(r"\bRealty\b", re.IGNORECASE),
    re.compile(r"\bHoldings\b", re.IGNORECASE),
    re.compile(r"\bCorp\b", re.IGNORECASE),
    re.compile(r"\bPartners\b", re.IGNORECASE),
    re.compile(r"\bTrust\b", re.IGNORECASE),
    re.compile(r"\bLP\b", re.IGNORECASE),
]


def score(parcel: Parcel) -> SignalResult:
    """Score the probate-name-pattern signal for `parcel`."""
    name = parcel.owner_name
    if any(p.search(name) for p in _CORPORATE_PATTERNS):
        return SignalResult(matched=False, weight=0, reason="")
    if any(p.search(name) for p in _PROBATE_PATTERNS):
        return SignalResult(matched=True, weight=20, reason="probate_name_pattern")
    return SignalResult(matched=False, weight=0, reason="")
