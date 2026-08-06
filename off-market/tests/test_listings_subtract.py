"""Tests for the active-listing subtraction step.

`subtract_listed` is the single integration point between the listings
fetcher (`scripts.listings.redfin.fetch_listings`) and the candidate-parcel
pipeline. It removes parcels whose address matches an actively-listed
home so the off-market workflow doesn't surface homes the owner has
already put on the market.
"""

from scripts.listings.address_norm import normalize
from scripts.listings.subtract import subtract_listed
from scripts.models import Parcel


def _p(addr: str) -> Parcel:
    return Parcel(parcel_id=addr, address=addr, owner_name="x", owner_mailing="x")


def test_subtract_removes_listed_parcels():
    parcels = [
        _p("123 Elm St, Pittsburgh, PA 15217"),
        _p("456 Oak Ave, Pittsburgh, PA 15217"),
    ]
    listings = {normalize("123 Elm St")}
    result = subtract_listed(parcels, listings)
    assert len(result) == 1
    assert result[0].address.startswith("456")


def test_subtract_keeps_all_when_no_listings():
    parcels = [_p("123 Elm St, Pittsburgh, PA 15217")]
    assert len(subtract_listed(parcels, set())) == 1


def test_subtract_handles_abbreviation_mismatch():
    # Parcel has "St", listing was scraped as "Street" — should still match
    # because both sides normalize to the same join key.
    parcels = [_p("123 Elm St, Pittsburgh, PA 15217")]
    listings = {normalize("123 Elm Street")}
    result = subtract_listed(parcels, listings)
    assert len(result) == 0


def test_subtract_empty_parcels():
    assert subtract_listed([], {"any"}) == []


def test_subtract_preserves_input_order():
    parcels = [
        _p("100 Elm St"),
        _p("200 Oak Ave"),
        _p("300 Maple Blvd"),
        _p("400 Pine Dr"),
    ]
    listings = {normalize("200 Oak Ave"), normalize("400 Pine Dr")}
    result = subtract_listed(parcels, listings)
    assert [p.address for p in result] == ["100 Elm St", "300 Maple Blvd"]


def test_subtract_handles_directional_mismatch():
    # Parcel has "N Main", listing scraped as "North Main".
    parcels = [_p("789 N Main Blvd")]
    listings = {normalize("789 North Main Boulevard")}
    assert subtract_listed(parcels, listings) == []
