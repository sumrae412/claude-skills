from datetime import date

from scripts.models import Parcel


def test_parcel_minimal_construction():
    p = Parcel(
        parcel_id="0001-A-001",
        address="123 Elm St, Pittsburgh, PA 15217",
        owner_name="Doe, John",
        owner_mailing="123 Elm St, Pittsburgh, PA 15217",
    )
    assert p.parcel_id == "0001-A-001"
    assert p.is_absentee() is False


def test_parcel_absentee_when_state_differs():
    p = Parcel(
        parcel_id="x",
        address="123 Elm St, Pittsburgh, PA 15217",
        owner_name="Doe, John",
        owner_mailing="999 Beach Rd, Miami, FL 33101",
    )
    assert p.is_absentee() is True


def test_parcel_absentee_handles_unparseable_addresses_conservatively():
    p = Parcel(
        parcel_id="x",
        address="some weird address",
        owner_name="Doe, John",
        owner_mailing="other weird address",
    )
    assert p.is_absentee() is False


def test_parcel_accepts_optional_fields():
    p = Parcel(
        parcel_id="x",
        address="123 Elm St, Pittsburgh, PA 15217",
        owner_name="Doe, John",
        owner_mailing="123 Elm St, Pittsburgh, PA 15217",
        last_sale_date=date(2001, 5, 15),
        last_sale_price=82000.0,
        assessed_value=250000.0,
        lot_sqft=4500.0,
        beds=3,
        baths=1.5,
        year_built=1925,
    )
    assert p.year_built == 1925
