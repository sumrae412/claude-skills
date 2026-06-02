"""User-supplied filtering criteria for off-market parcel discovery.

`Criteria` is a pydantic v2 model loaded from `criteria.yaml`. Protected-class
keys (per `references/fair-housing.md`) are rejected at load time BEFORE
pydantic sees the dict, so an attacker can't smuggle a forbidden field in by
relying on pydantic's "ignore extras" behavior.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

# Forbidden keys per references/fair-housing.md. Federal FHA (7 classes) plus
# `age` as a stricter internal policy.
FORBIDDEN_FIELDS: frozenset[str] = frozenset({
    "race",
    "color",
    "religion",
    "national_origin",
    "sex",
    "disability",
    "familial_status",
    "age",
})


class Criteria(BaseModel):
    """Off-market filtering criteria. All fields optional."""

    model_config = ConfigDict(extra="forbid")

    beds_min: int | None = None
    baths_min: float | None = None
    lot_sqft_min: float | None = None
    lot_sqft_max: float | None = None
    sqft_min: float | None = None
    sqft_max: float | None = None
    year_built_min: int | None = None
    year_built_max: int | None = None
    price_min: float | None = None
    price_max: float | None = None
    zips: list[str] = []
    neighborhoods: list[str] = []


def load_criteria(path: str | Path) -> Criteria:
    """Load and validate a criteria YAML file.

    Raises:
        ValueError: if any top-level key matches a protected class.
    """
    text = Path(path).read_text()
    raw = yaml.safe_load(text) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"criteria.yaml root must be a mapping, got {type(raw).__name__}")

    for key in raw:
        if key in FORBIDDEN_FIELDS:
            raise ValueError(f"criteria.yaml contains protected-class key: {key}")

    return Criteria(**raw)
