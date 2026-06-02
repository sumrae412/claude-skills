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
