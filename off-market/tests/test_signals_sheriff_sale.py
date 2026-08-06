from datetime import date
from scripts.models import Parcel
from scripts.signals.sheriff_sale import score


def _p(sale_date):
    return Parcel(
        parcel_id="x", address="x", owner_name="x", owner_mailing="x",
        sheriff_sale_date=sale_date,
    )


def test_sheriff_sale_future_match():
    r = score(_p(date(2026, 7, 15)), as_of=date(2026, 6, 1))
    assert r.matched is True
    assert r.weight == 40
    assert r.reason == "sheriff_sale:2026-07-15"


def test_sheriff_sale_today_matches():
    r = score(_p(date(2026, 6, 1)), as_of=date(2026, 6, 1))
    assert r.matched is True


def test_sheriff_sale_past_no_match():
    r = score(_p(date(2025, 1, 1)), as_of=date(2026, 6, 1))
    assert r.matched is False


def test_sheriff_sale_none_no_match():
    r = score(_p(None), as_of=date(2026, 6, 1))
    assert r.matched is False
