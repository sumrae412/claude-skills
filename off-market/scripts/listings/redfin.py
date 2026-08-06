"""Redfin listings fetcher — used to subtract actively-listed homes from
the candidate pool.

Source choice (verified 2026-06-02 against zip 15217 Squirrel Hill, Pittsburgh):
  - **Redfin**: chosen. Returned HTTP 200 with no CAPTCHA/robot wall, body
    contains a JS-embedded React state assignment with addresses in the
    form ``streetLine\\":{\\"value\\":\\"<addr>\\"`` (escaped JSON inside a
    `<script>` block). ~73 listings on the test page. Polite rate-limited
    fetches are tolerated.
  - Zillow: NOT tried — known to aggressively block scrapers; would be
    the next fallback.
  - Realtor.com: NOT tried.

If Redfin starts blocking, ``fetch_listings`` returns ``[]`` (not raise)
and logs a warning so the orchestrator can degrade to "no subtraction,
all parcels remain candidates" instead of crashing.

Output addresses are NORMALIZED via :func:`scripts.listings.address_norm.normalize`
so the listings set can be passed directly to :func:`scripts.listings.subtract.subtract_listed`.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any

import httpx

from scripts.listings.address_norm import normalize

logger = logging.getLogger(__name__)

# Browser-like headers — Redfin (like most modern frontends) returns a
# different / smaller response without a recognizable User-Agent.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# The per-zip page embeds React state as a literal JS assignment that
# contains escaped-JSON string values like:
#     "streetLine":{"value":"5500 Darlington Rd"}
# which in the on-the-wire HTML is the escaped form:
#     streetLine\":{\"value\":\"5500 Darlington Rd\"
# We extract the streetLine value with a single regex pass — no full HTML
# or JSON parse — to keep the parser fast and resilient to surrounding
# state shape changes.
_STREETLINE_RE = re.compile(
    r'streetLine\\":\s*\{\\"value\\":\s*\\"([^\\]+)\\"'
)

# Defensive: also match the un-escaped form (in case Redfin ever serves
# raw JSON or a future MCP-rendered variant).
_STREETLINE_PLAIN_RE = re.compile(
    r'"streetLine"\s*:\s*\{\s*"value"\s*:\s*"([^"]+)"'
)

# Bot-wall / CAPTCHA detection heuristics. Signals must be specific enough
# not to false-positive on incidental occurrences (e.g. "blocked" appears
# in adblock-detection JS on real Redfin pages — too broad on its own).
# We require either an explicit interstitial phrase OR a CAPTCHA + no
# listings parsed (handled at the call site).
_BLOCK_SIGNALS = (
    "are you a robot",
    "verify you are not a robot",
    "please verify you are not a robot",
    "access to this page has been denied",
    "unusual traffic from your computer",
    "automated requests",
)


def _looks_blocked(text: str) -> bool:
    lowered = text.lower()
    return any(sig in lowered for sig in _BLOCK_SIGNALS)


def parse_listings(raw: str | bytes | dict | Any) -> list[str]:
    """Parse a Redfin per-zip page → list of normalized street addresses.

    Accepts bytes (auto-decoded), strings, or dict (already-parsed JSON
    variant — not used by Redfin today but kept for adapter flexibility).
    Returns ``[]`` on empty input or apparent bot-wall / CAPTCHA.
    """
    if raw is None:
        return []

    # bytes → str
    if isinstance(raw, bytes):
        try:
            text = raw.decode("utf-8", errors="replace")
        except Exception:
            return []
    elif isinstance(raw, dict):
        # Adapter-flexibility: if a future caller hands us pre-parsed JSON,
        # walk it for streetLine.value occurrences.
        return _parse_dict(raw)
    else:
        text = str(raw)

    if not text.strip():
        return []

    if _looks_blocked(text):
        logger.warning("redfin: parse_listings sees a bot-wall / CAPTCHA page")
        return []

    # Escaped form first (the real Redfin shape).
    matches = _STREETLINE_RE.findall(text)
    if not matches:
        # Fall back to plain form.
        matches = _STREETLINE_PLAIN_RE.findall(text)

    # Normalize + dedupe preserving order.
    seen: set[str] = set()
    out: list[str] = []
    for raw_addr in matches:
        norm = normalize(raw_addr)
        if norm and norm not in seen:
            seen.add(norm)
            out.append(norm)
    return out


def _parse_dict(payload: dict) -> list[str]:
    """Walk a pre-parsed dict for streetLine.value entries.

    Not used by Redfin today; defensive for future adapter shapes.
    """
    found: list[str] = []

    def _walk(node: Any) -> None:
        if isinstance(node, dict):
            sl = node.get("streetLine")
            if isinstance(sl, dict) and isinstance(sl.get("value"), str):
                found.append(sl["value"])
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for v in node:
                _walk(v)

    _walk(payload)
    seen: set[str] = set()
    out: list[str] = []
    for a in found:
        n = normalize(a)
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def fetch_listings(zip_code: str, *, throttle_seconds: float = 2.0) -> list[str]:
    """Fetch a single zip's active listings from Redfin.

    Returns a list of normalized street addresses (caller can pass directly
    to ``subtract_listed``).

    Sleeps ``throttle_seconds`` BEFORE the request so the caller can loop
    over many zips without an explicit external delay.

    On any HTTP error (4xx, 5xx) or rate-limit / block (403, 429): returns
    ``[]`` and logs a warning. Does NOT raise — the orchestrator treats
    empty as "subtraction unavailable, all parcels remain candidates."
    """
    if not zip_code or not zip_code.strip():
        return []
    zc = zip_code.strip()

    # Polite throttle BEFORE the request.
    if throttle_seconds > 0:
        time.sleep(throttle_seconds)

    url = f"https://www.redfin.com/zipcode/{zc}"
    try:
        with httpx.Client(
            headers=HEADERS, timeout=20.0, follow_redirects=True
        ) as client:
            r = client.get(url)
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        logger.warning("redfin: fetch_listings(%s) failed at HTTP layer: %s", zc, e)
        return []
    except Exception as e:
        # Defensive: never propagate to the caller, no matter how exotic.
        logger.warning("redfin: fetch_listings(%s) unexpected error: %s", zc, e)
        return []

    if r.status_code in (403, 429):
        logger.warning("redfin: fetch_listings(%s) rate-limited / blocked (%d)", zc, r.status_code)
        return []
    if r.status_code >= 400:
        logger.warning("redfin: fetch_listings(%s) HTTP %d", zc, r.status_code)
        return []

    return parse_listings(r.text)
