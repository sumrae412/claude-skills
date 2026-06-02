from datetime import date

from scripts.models import Parcel
from scripts.propensity import score, tier_for, PropensityScore


# Tier boundaries
def test_tier_dropped():
    assert tier_for(0) == "dropped"
    assert tier_for(14.99) == "dropped"


def test_tier_worth_a_letter():
    assert tier_for(15) == "worth_a_letter"
    assert tier_for(39.99) == "worth_a_letter"


def test_tier_high_priority():
    assert tier_for(40) == "high_priority"
    assert tier_for(69.99) == "high_priority"


def test_tier_act_this_week():
    assert tier_for(70) == "act_this_week"
    assert tier_for(105) == "act_this_week"


# Composition
def test_score_no_signals_match_returns_zero_and_dropped():
    p = Parcel(
        parcel_id="x",
        address="123 Elm St, Pittsburgh, PA 15217",
        owner_name="Doe, John",
        owner_mailing="123 Elm St, Pittsburgh, PA 15217",
    )
    r = score(p, as_of=date(2026, 6, 1))
    assert r.total == 0
    assert r.reasons == ()
    assert r.tier == "dropped"


def test_score_absentee_only():
    p = Parcel(
        parcel_id="x",
        address="123 Elm St, Pittsburgh, PA 15217",
        owner_name="Doe, John",
        owner_mailing="999 Beach Rd, Miami, FL 33101",
    )
    r = score(p, as_of=date(2026, 6, 1))
    assert r.total == 10
    assert r.reasons == ("absentee:FL",)
    assert r.tier == "dropped"  # 10 < 15


def test_score_absentee_plus_tenure_equity():
    p = Parcel(
        parcel_id="x",
        address="123 Elm St, Pittsburgh, PA 15217",
        owner_name="Doe, John",
        owner_mailing="999 Beach Rd, Miami, FL 33101",
        last_sale_date=date(2001, 1, 1),
        last_sale_price=80_000.0,
        assessed_value=250_000.0,
    )
    r = score(p, as_of=date(2026, 6, 1))
    assert r.total == 20  # 10 + 10
    assert r.tier == "worth_a_letter"
    assert "absentee:FL" in r.reasons
    assert any(reason.startswith("long_tenure_high_equity:") for reason in r.reasons)


def test_score_full_stack_high_score():
    # Sheriff sale (40) + tax delinq $40k (25) + probate name (20) + absentee (10)
    # + long tenure high equity (10) = 105 (open-scale max).
    p = Parcel(
        parcel_id="x",
        address="123 Elm St, Pittsburgh, PA 15217",
        owner_name="Estate of John Doe",
        owner_mailing="999 Beach Rd, Miami, FL 33101",
        last_sale_date=date(2001, 1, 1),
        last_sale_price=80_000.0,
        assessed_value=250_000.0,
        tax_owed_usd=40_000.0,
        sheriff_sale_date=date(2026, 8, 1),
    )
    r = score(p, as_of=date(2026, 6, 1))
    assert r.total == 105
    assert r.tier == "act_this_week"
    assert "sheriff_sale:2026-08-01" in r.reasons
    assert "tax_delinquent:$40000" in r.reasons
    assert "probate_name_pattern" in r.reasons
    assert "absentee:FL" in r.reasons
    assert any(reason.startswith("long_tenure_high_equity:") for reason in r.reasons)


def test_score_reasons_ordered_by_signal_registry():
    # Two-signal example: sheriff_sale (high weight, first in registry) +
    # tenure_equity (last in registry). Reasons should reflect registry order.
    p = Parcel(
        parcel_id="x",
        address="123 Elm St, Pittsburgh, PA 15217",
        owner_name="Doe, John",
        owner_mailing="123 Elm St, Pittsburgh, PA 15217",
        last_sale_date=date(2001, 1, 1),
        last_sale_price=80_000.0,
        assessed_value=250_000.0,
        sheriff_sale_date=date(2026, 8, 1),
    )
    r = score(p, as_of=date(2026, 6, 1))
    # sheriff first, then tenure_equity
    assert r.reasons[0] == "sheriff_sale:2026-08-01"
    assert r.reasons[-1].startswith("long_tenure_high_equity:")
