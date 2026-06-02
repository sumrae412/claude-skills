from datetime import date
from scripts.models import Parcel
from scripts.signals.tenure_equity import score


def _p(sale_date, sale_price, assessed):
    return Parcel(
        parcel_id="x", address="x", owner_name="x", owner_mailing="x",
        last_sale_date=sale_date, last_sale_price=sale_price, assessed_value=assessed,
    )


def test_tenure_equity_match_long_tenure_high_equity():
    r = score(_p(date(2001, 1, 1), 80_000.0, 250_000.0), as_of=date(2026, 6, 1))
    assert r.matched is True
    assert r.weight == 10
    assert r.reason == "long_tenure_high_equity:25"


def test_tenure_equity_no_match_short_tenure():
    r = score(_p(date(2021, 1, 1), 100_000.0, 350_000.0), as_of=date(2026, 6, 1))
    assert r.matched is False


def test_tenure_equity_no_match_long_tenure_low_equity():
    r = score(_p(date(2001, 1, 1), 200_000.0, 250_000.0), as_of=date(2026, 6, 1))
    # equity_pct = (250k - 200k) / 250k = 20% < 60%
    assert r.matched is False


def test_tenure_equity_no_match_missing_data():
    r = score(Parcel(parcel_id="x", address="x", owner_name="x", owner_mailing="x"), as_of=date(2026, 6, 1))
    assert r.matched is False


def test_tenure_equity_no_match_negative_equity():
    r = score(_p(date(2001, 1, 1), 300_000.0, 250_000.0), as_of=date(2026, 6, 1))
    assert r.matched is False
