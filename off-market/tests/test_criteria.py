import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pytest

from scripts.criteria import Criteria, load_criteria, FORBIDDEN_FIELDS


def test_criteria_loads_valid_yaml(tmp_path):
    yml = tmp_path / "c.yaml"
    yml.write_text("""
beds_min: 3
lot_sqft_min: 5000
price_max: 350000
zips:
  - "15217"
  - "15232"
""")
    c = load_criteria(yml)
    assert c.beds_min == 3
    assert c.lot_sqft_min == 5000.0
    assert c.zips == ["15217", "15232"]


def test_criteria_rejects_protected_class_key(tmp_path):
    yml = tmp_path / "c.yaml"
    yml.write_text("race: white\nbeds_min: 3\n")
    with pytest.raises(ValueError, match="protected-class"):
        load_criteria(yml)


def test_forbidden_fields_constant_matches_fair_housing_doc():
    assert FORBIDDEN_FIELDS == frozenset({
        "race", "color", "religion", "national_origin",
        "sex", "disability", "familial_status", "age",
    })


def test_criteria_empty_yaml_yields_defaults(tmp_path):
    yml = tmp_path / "c.yaml"
    yml.write_text("{}\n")
    c = load_criteria(yml)
    assert c.beds_min is None
    assert c.zips == []
