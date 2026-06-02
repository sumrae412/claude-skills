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


def test_tenure_equity_leap_year_boundary_not_overcounted():
    # 19 years + 360 days = NOT 20 years — must NOT match.
    # Day-based math (7300 // 365 = 20) was wrong.
    # Calendar-year math: today.year - sale.year = 20, but month/day check subtracts 1.
    sale = date(2006, 6, 6)
    today = date(2026, 6, 1)  # 5 days before the 20-year anniversary
    p = Parcel(
        parcel_id="x", address="x", owner_name="x", owner_mailing="x",
        last_sale_date=sale, last_sale_price=80_000.0, assessed_value=250_000.0,
    )
    r = score(p, as_of=today)
    assert r.matched is False, f"expected no match — true tenure is 19y, got {r}"


def test_tenure_equity_exactly_20_years_to_the_day_matches():
    # The 20-year anniversary itself — should match.
    sale = date(2006, 6, 1)
    today = date(2026, 6, 1)
    p = Parcel(
        parcel_id="x", address="x", owner_name="x", owner_mailing="x",
        last_sale_date=sale, last_sale_price=80_000.0, assessed_value=250_000.0,
    )
    r = score(p, as_of=today)
    assert r.matched is True
    assert r.reason == "long_tenure_high_equity:20"
