"""Tests for the Redfin listings fetcher.

The fixture (`listings_15217_redfin.html`) is a ~43KB snippet of a real
Redfin per-zip page response — enough JS-embedded state to exercise the
parser without bloating the repo. It includes 15 listings from 15217
(Squirrel Hill, Pittsburgh).
"""

import os
import pathlib

import pytest

from scripts.listings.redfin import parse_listings


FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "listings_15217_redfin.html"


def test_parse_returns_list_of_strings():
    raw = FIXTURE.read_text()
    listings = parse_listings(raw)
    assert isinstance(listings, list)
    assert len(listings) >= 10, f"expected ≥10 listings, got {len(listings)}"
    assert all(isinstance(a, str) for a in listings)


def test_parse_addresses_are_normalized():
    # Normalized per scripts.listings.address_norm.normalize:
    # lowercase, abbreviations expanded.
    raw = FIXTURE.read_text()
    listings = parse_listings(raw)
    for addr in listings:
        assert addr == addr.lower(), f"unnormalized casing: {addr!r}"
        # No street-type abbreviations should remain (e.g. " st", " ave").
        tokens = addr.split(" ")
        for abbrev in ("st", "ave", "rd", "dr", "blvd", "ln", "ct", "pl", "pkwy", "ter", "cir", "hwy"):
            assert abbrev not in tokens, f"unexpanded abbreviation {abbrev!r} in {addr!r}"


def test_parse_known_addresses_present():
    # A handful of addresses we KNOW are in the fixture (snipped from a real
    # 2026 fetch). If any of these go missing the parser broke.
    raw = FIXTURE.read_text()
    listings = parse_listings(raw)
    listing_set = set(listings)
    # 5500 Darlington Rd → 5500 darlington road
    assert "5500 darlington road" in listing_set
    # 1156 S Negley Ave → 1156 south negley avenue
    assert "1156 south negley avenue" in listing_set
    # 6328 Douglas St → 6328 douglas street
    assert "6328 douglas street" in listing_set


def test_parse_handles_empty_input():
    assert parse_listings("") == []
    assert parse_listings("<html></html>") == []


def test_parse_handles_blocked_response():
    # If a fetch hits a CAPTCHA / "are you a robot" page, parse should
    # return [] not crash.
    captcha = "<html><body>Please verify you are not a robot</body></html>"
    assert parse_listings(captcha) == []


def test_parse_handles_bytes_input():
    raw = FIXTURE.read_bytes()
    listings = parse_listings(raw)
    assert isinstance(listings, list)
    assert len(listings) > 0


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_TESTS") != "1", reason="live listings fetch (set RUN_LIVE_TESTS=1)"
)
def test_live_fetch_15217():
    from scripts.listings.redfin import fetch_listings

    result = fetch_listings("15217")
    # Empty list is acceptable if the source is hostile/blocked — the
    # contract is "don't raise", and subtraction-unavailable degrades
    # gracefully upstream.
    assert isinstance(result, list)
