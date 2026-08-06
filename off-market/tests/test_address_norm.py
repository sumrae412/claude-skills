"""Tests for the shared street-address normalizer.

The normalizer is the JOIN KEY for matching parcel addresses to listings,
sheriff sales, and any other free-form address source. Both sides of any
join must run through this function so abbreviation drift doesn't cause
false misses (e.g. "St" vs "Street", "N" vs "North").
"""

from scripts.listings.address_norm import normalize


def test_normalize_basic_lowercases():
    assert normalize("123 Elm St") == "123 elm street"


def test_normalize_strips_city_state_zip():
    assert normalize("123 Elm St, Pittsburgh, PA 15217") == "123 elm street"


def test_normalize_strips_wprdc_comma_before_zip():
    """WPRDC publishes addresses like ``"... PITTSBURGH, PA, 15222"``.

    The trailing-city-tail strip must accept both ``"PA 15222"`` and the
    comma-before-zip form, or the normalizer leaves the city/state/zip
    bolted onto the join key and every WPRDC↔listings join misses.
    """
    assert (
        normalize("239 Fort Pitt Blvd, Pittsburgh, PA, 15222")
        == "239 fort pitt boulevard"
    )


def test_normalize_expands_directionals():
    assert normalize("789 N Main Blvd") == "789 north main boulevard"
    # SW is not in the cardinal-4 list — leave alone rather than guess wrong.
    assert normalize("100 SW 42nd St") == "100 sw 42nd street"


def test_normalize_expands_avenue():
    assert normalize("456 Oak Ave.") == "456 oak avenue"


def test_normalize_strips_apt_unit():
    assert normalize("100 Elm St Apt 4B") == "100 elm street"
    assert normalize("100 Elm St #4B") == "100 elm street"
    assert normalize("100 Elm St Unit 4B") == "100 elm street"


def test_normalize_idempotent():
    once = normalize("123 Elm St")
    twice = normalize(once)
    assert once == twice


def test_normalize_empty_string():
    assert normalize("") == ""


def test_normalize_handles_extra_whitespace():
    # Multiple spaces collapse to one.
    assert normalize("123  Elm   St") == "123 elm street"


def test_normalize_punctuation_dropped():
    # Commas / periods / hashes are noise for the join key.
    assert normalize("123  Main   St.,") == "123 main street"


def test_normalize_back_compat_existing_sheriff_examples():
    # The sheriff adapter's existing tests assert these equivalences.
    assert normalize("110 POPLAR STREET ") == normalize("110 Poplar St")
    assert normalize("8525 PERSHING ST") == normalize("8525 pershing street")


def test_normalize_expands_all_directionals():
    assert normalize("1 N Main St") == "1 north main street"
    assert normalize("1 S Main St") == "1 south main street"
    assert normalize("1 E Main St") == "1 east main street"
    assert normalize("1 W Main St") == "1 west main street"


def test_normalize_does_not_expand_trailing_single_letter():
    # A final 'n' isn't a directional — could be part of a name. Leave alone
    # by only expanding when followed by another whitespace-separated token.
    assert normalize("123 Elm St N") == "123 elm street n"


def test_normalize_expands_more_street_types():
    assert normalize("1 Foo Rd") == "1 foo road"
    assert normalize("1 Foo Dr") == "1 foo drive"
    assert normalize("1 Foo Ln") == "1 foo lane"
    assert normalize("1 Foo Ct") == "1 foo court"
    assert normalize("1 Foo Pl") == "1 foo place"
    assert normalize("1 Foo Way") == "1 foo way"
    assert normalize("1 Foo Pkwy") == "1 foo parkway"
    assert normalize("1 Foo Ter") == "1 foo terrace"
    assert normalize("1 Foo Cir") == "1 foo circle"
    assert normalize("1 Foo Hwy") == "1 foo highway"
