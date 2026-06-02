"""Shared street-address normalizer used by listings + county adapters.

This module owns the JOIN KEY semantics for any address-based join in the
off-market pipeline. Both sides of a join (e.g. parcel address vs listing,
parcel address vs sheriff-sale address) MUST be run through :func:`normalize`
so that abbreviation drift ("St" vs "Street", "N" vs "North") doesn't cause
false misses.

The output is a join key, not a display string. It is:
  - lowercase
  - free of punctuation (`. , #`)
  - free of trailing city/state/zip tails
  - free of apartment / unit suffixes (`Apt 4B`, `#4B`, `Unit 4B`)
  - whitespace-collapsed
  - with common street-type and directional abbreviations expanded
    (St→street, Ave→avenue, N→north, etc.) when they appear as standalone
    tokens.

Design notes:
  - Directional expansion is conservative: only the four cardinals N/S/E/W
    are expanded, and only when followed by another whitespace-separated
    token (so a trailing 'N' that might be part of a proper name is left
    alone — see `test_normalize_does_not_expand_trailing_single_letter`).
  - 'SW' / 'NE' / etc. are intentionally NOT expanded — guessing
    'southwest' might be wrong, and the symmetric mismatch is hard to debug.
  - Apt/unit suffix stripping uses a permissive pattern that matches
    "Apt ...", "Unit ...", or "#..." at the end of the string after any
    city-tail strip.
"""

from __future__ import annotations

import re

# Street-type abbreviations expanded to canonical full words. Lowercase
# keys are matched against lowercase tokens after punctuation stripping.
_STREET_ABBREV: dict[str, str] = {
    "st": "street",
    "str": "street",
    "ave": "avenue",
    "av": "avenue",
    "blvd": "boulevard",
    "rd": "road",
    "dr": "drive",
    "ln": "lane",
    "ct": "court",
    "pl": "place",
    "way": "way",
    "pkwy": "parkway",
    "ter": "terrace",
    "cir": "circle",
    "hwy": "highway",
}

# Directional abbreviations — only cardinals. Expanded when followed by
# another whitespace-separated token (see _expand_directionals).
_DIRECTIONALS: dict[str, str] = {
    "n": "north",
    "s": "south",
    "e": "east",
    "w": "west",
}

# Trailing ", CITY, STATE 12345" or ", CITY, STATE 12345-1234" patterns.
# Case-insensitive; STATE is a 2-letter alpha token; CITY may have spaces.
# The state-zip gap accepts ``[,\s]+`` so both ``"... PITTSBURGH, PA 15222"``
# and the WPRDC-published shape ``"... PITTSBURGH, PA, 15222"`` strip cleanly.
_CITY_TAIL_RE = re.compile(
    r",\s*[A-Za-z .]+,\s*[A-Za-z]{2}[,\s]+\d{5}(?:-\d{4})?\s*$"
)

# Apartment / unit suffixes at end of string.
# Matches: "Apt 4B", "Unit 4B", "# 4B", "#4B"
_APT_UNIT_RE = re.compile(
    r"\s+(?:apt|apartment|unit|ste|suite|#)\.?\s*[\w-]+\s*$",
    re.IGNORECASE,
)
# Also a plain trailing "#4B" with no leading space-word.
_HASH_UNIT_RE = re.compile(r"\s*#\s*[\w-]+\s*$")


def _expand_directionals(tokens: list[str]) -> list[str]:
    """Expand cardinal directionals (N/S/E/W) only when NOT the last token.

    Conservative on purpose — a final single-letter 'n' could be part of
    a proper name, not a direction.
    """
    out: list[str] = []
    last_idx = len(tokens) - 1
    for i, tok in enumerate(tokens):
        if i < last_idx and tok in _DIRECTIONALS:
            out.append(_DIRECTIONALS[tok])
        else:
            out.append(tok)
    return out


def _expand_street_types(tokens: list[str]) -> list[str]:
    return [_STREET_ABBREV.get(tok, tok) for tok in tokens]


def normalize(addr: str) -> str:
    """Normalize a free-form street address into a stable JOIN KEY.

    See module docstring for the contract. Examples::

        normalize("123 Elm St, Pittsburgh, PA 15217") → "123 elm street"
        normalize("456 OAK AVE.")                     → "456 oak avenue"
        normalize("789 N. Main Blvd")                 → "789 north main boulevard"
        normalize("100 Elm St Apt 4B")                → "100 elm street"
    """
    if not addr:
        return ""

    s = str(addr)

    # Strip trailing ", CITY, STATE ZIP" tail FIRST (before lowercasing,
    # since the regex is case-insensitive but unambiguous on the original
    # form).
    s = _CITY_TAIL_RE.sub("", s)

    # Strip trailing apt/unit suffix. Try both patterns; whichever matches.
    s = _APT_UNIT_RE.sub("", s)
    s = _HASH_UNIT_RE.sub("", s)

    # Lowercase + drop punctuation that's pure join-key noise.
    s = s.lower()
    s = re.sub(r"[.,#]+", " ", s)

    # Collapse whitespace.
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return ""

    tokens = s.split(" ")
    tokens = _expand_directionals(tokens)
    tokens = _expand_street_types(tokens)
    return " ".join(tokens).strip()
