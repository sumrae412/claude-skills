from scripts.models import Parcel
from scripts.signals.delinquency import score


def _p(owed):
    return Parcel(
        parcel_id="x", address="x", owner_name="x", owner_mailing="x",
        tax_owed_usd=owed,
    )


def test_delinquency_no_match_when_zero_or_none():
    assert score(_p(None)).matched is False
    assert score(_p(0.0)).matched is False


def test_delinquency_small_amount():
    # $1500 → 5 + 0.5 * 1.5 = 5.75
    r = score(_p(1500.0))
    assert r.matched is True
    assert r.weight == 5.75
    assert r.reason == "tax_delinquent:$1500"


def test_delinquency_capped_at_25():
    # $80,000 → 5 + 0.5 * 80 = 45 → cap 25
    r = score(_p(80_000.0))
    assert r.matched is True
    assert r.weight == 25
    assert r.reason == "tax_delinquent:$80000"


def test_delinquency_just_above_cap_boundary():
    # $40k → 5 + 20 = 25 exactly (the cap)
    r = score(_p(40_000.0))
    assert r.weight == 25
