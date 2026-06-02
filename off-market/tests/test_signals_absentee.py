from datetime import date
from scripts.models import Parcel
from scripts.signals.absentee import score


def _p(addr, mailing):
    return Parcel(parcel_id="x", address=addr, owner_name="Doe", owner_mailing=mailing)


def test_absentee_same_city_same_state_no_match():
    r = score(_p("123 Elm St, Pittsburgh, PA 15217", "123 Elm St, Pittsburgh, PA 15217"))
    assert r.matched is False
    assert r.weight == 0


def test_absentee_in_state_different_city_matches():
    r = score(_p("123 Elm St, Pittsburgh, PA 15217", "456 Oak Ave, Philadelphia, PA 19103"))
    assert r.matched is True
    assert r.weight == 10
    assert r.reason == "absentee:PA"


def test_absentee_out_of_state_matches():
    r = score(_p("123 Elm St, Pittsburgh, PA 15217", "999 Beach Rd, Miami, FL 33101"))
    assert r.matched is True
    assert r.weight == 10
    assert r.reason == "absentee:FL"


def test_absentee_conservative_when_addresses_unparseable():
    r = score(_p("weird address", "other weird address"))
    assert r.matched is False


def test_absentee_signal_fires_on_wprdc_comma_before_zip():
    """Real WPRDC shape: ``"... PITTSBURGH, PA, 15222"`` (note: comma)."""
    r = score(
        _p(
            "239 FORT PITT BLVD, PITTSBURGH, PA, 15222",
            "501 S OCEAN BLVD, DELRAY BEACH, FL, 33483",
        )
    )
    assert r.matched is True
    assert r.weight == 10
    assert r.reason == "absentee:FL"


def test_absentee_signal_fires_on_wprdc_mailing_no_comma_between_city_and_state():
    """Real WPRDC mailing shape: ``"... SAINT LOUIS MO, 63141"``.

    Mailing addresses in the WPRDC CHANGENOTICEADDRESS columns frequently
    concatenate city + state with whitespace only (no comma) AND put a
    comma before the zip — distinct from the property-address shape which
    uses commas in both gaps. Verified on 2026-06-02 live run: 21 of the
    first 500 parcels in zip 15217 had this shape; the signal was matching
    only 1 of them before this regex widening.
    """
    r = score(
        _p(
            "5308 BEELER ST, PITTSBURGH, PA, 15217",
            "22 S TEALBROOK DR, SAINT LOUIS MO, 63141",
        )
    )
    assert r.matched is True
    assert r.reason == "absentee:MO"
