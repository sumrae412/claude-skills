from scripts.models import Parcel
from scripts.signals.probate_name import score


def _p(name):
    return Parcel(
        parcel_id="x", address="x", owner_name=name, owner_mailing="x",
    )


def test_probate_estate_of_matches():
    r = score(_p("Estate of John Doe"))
    assert r.matched is True
    assert r.weight == 20
    assert r.reason == "probate_name_pattern"


def test_probate_heirs_of_matches():
    r = score(_p("Doe, John (Heirs of)"))
    assert r.matched is True


def test_probate_deceased_suffix_matches():
    r = score(_p("Smith, Jane, Deceased"))
    assert r.matched is True


def test_probate_case_insensitive():
    r = score(_p("ESTATE OF Mary Jones"))
    assert r.matched is True


def test_probate_plain_name_no_match():
    r = score(_p("Doe, John"))
    assert r.matched is False


def test_probate_corporate_estate_llc_no_match():
    r = score(_p("Estate Realty LLC"))
    assert r.matched is False


def test_probate_corporate_family_trust_no_match():
    r = score(_p("John Doe Family Trust"))
    assert r.matched is False


def test_probate_corporate_inc_no_match():
    r = score(_p("Heirs of Smith Inc"))
    assert r.matched is False
