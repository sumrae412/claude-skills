"""Core data types for the off-market skill.

`Parcel` is the canonical shape every county adapter must yield; downstream
filtering, scoring, and letter generation consume this shape.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

# US 2-letter state followed by optional 5-digit ZIP at the end of the address.
# Anchored to end-of-string (allowing trailing whitespace) so we don't match
# stray two-letter tokens earlier in the string (e.g. street abbreviations).
_STATE_RE = re.compile(r"\b([A-Z]{2})(?:\s+\d{5}(?:-\d{4})?)?\s*$")


def _extract_state(addr: str) -> str | None:
    """Return the 2-letter state token at the end of `addr`, or None."""
    if not addr:
        return None
    m = _STATE_RE.search(addr.strip())
    return m.group(1) if m else None


@dataclass
class Parcel:
    """A single parcel record produced by a county adapter.

    Required fields cover the minimum needed to address an envelope and
    deduplicate; optional fields back the propensity rubric (age, sale recency,
    distress signals).
    """

    parcel_id: str
    address: str
    owner_name: str
    owner_mailing: str

    last_sale_date: date | None = None
    last_sale_price: float | None = None
    assessed_value: float | None = None
    lot_sqft: float | None = None
    beds: int | None = None
    baths: float | None = None
    year_built: int | None = None
    tax_owed_usd: float | None = None
    sheriff_sale_date: date | None = None

    def is_absentee(self) -> bool:
        """True iff the parsed state in `address` differs from `owner_mailing`.

        Conservative: if either side lacks a parseable state token, return
        False rather than flag uncertain cases as absentee.
        """
        addr_state = _extract_state(self.address)
        mail_state = _extract_state(self.owner_mailing)
        if addr_state is None or mail_state is None:
            return False
        return addr_state != mail_state
