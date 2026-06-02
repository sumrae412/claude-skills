"""Absentee-owner signal.

Matches if the owner's mailing city OR state differs from the property's
city/state. More inclusive than `Parcel.is_absentee()` (which only compares
state) — captures landlords who live in the same state but a different city.

Conservative on unparseable inputs: if either address fails to yield a
`(city, state)` tuple, return matched=False rather than guess.
"""
from __future__ import annotations

import re

from scripts.models import Parcel
from scripts.signals import SignalResult

# Match ", City, ST" near end of address. City is letters/spaces/periods/hyphens;
# state is 2 uppercase letters; optional ZIP follows. Anchored to end-of-string
# (allowing trailing whitespace).
_CITY_STATE_RE = re.compile(
    r",\s*([A-Za-z][A-Za-z .\-]*?)\s*,\s*([A-Z]{2})(?:\s+\d{5}(?:-\d{4})?)?\s*$"
)


def _extract_city_state(addr: str) -> tuple[str, str] | None:
    if not addr:
        return None
    m = _CITY_STATE_RE.search(addr.strip())
    if not m:
        return None
    return (m.group(1).strip().lower(), m.group(2))


def score(parcel: Parcel) -> SignalResult:
    prop = _extract_city_state(parcel.address)
    mail = _extract_city_state(parcel.owner_mailing)
    if prop is None or mail is None:
        return SignalResult(matched=False, weight=0, reason="")
    if prop[0] == mail[0] and prop[1] == mail[1]:
        return SignalResult(matched=False, weight=0, reason="")
    return SignalResult(matched=True, weight=10, reason=f"absentee:{mail[1]}")
