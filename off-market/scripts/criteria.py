"""User-supplied filtering criteria for off-market parcel discovery.

`Criteria` is a pydantic v2 model loaded from `criteria.yaml`. Protected-class
keys (per `references/fair-housing.md`) are rejected at load time BEFORE
pydantic sees the dict, so an attacker can't smuggle a forbidden field in by
relying on pydantic's "ignore extras" behavior.

The protected-class check is case-insensitive and recurses into nested dicts
and lists — a forbidden key anywhere in the YAML tree raises.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

import yaml
from pydantic import BaseModel, ConfigDict, Field

# Forbidden keys per references/fair-housing.md. Federal FHA (7 classes) plus
# `age` as a stricter internal policy. All entries lowercase; comparisons are
# case-insensitive.
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
    zips: list[str] = Field(default_factory=list)
    neighborhoods: list[str] = Field(default_factory=list)


def _walk_keys(obj: Any) -> Iterator[Any]:
    """Yield every dict key found anywhere in a nested dict/list structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _walk_keys(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_keys(item)


def load_criteria(path: str | Path) -> Criteria:
    """Load and validate a criteria YAML file.

    Raises:
        ValueError: if any key (at any nesting level) matches a protected
            class, case-insensitively.
    """
    text = Path(path).read_text()
    raw = yaml.safe_load(text) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"criteria.yaml root must be a mapping, got {type(raw).__name__}")

    for key in _walk_keys(raw):
        if isinstance(key, str) and key.lower() in FORBIDDEN_FIELDS:
            raise ValueError(f"criteria.yaml contains protected-class key: {key}")

    return Criteria(**raw)
