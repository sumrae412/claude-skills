#!/usr/bin/env python3
"""Filter nvidia/Nemotron-Personas-USA by app segments and stratified-sample a fat-middle pool.

Usage:
    python filter_nemotron.py \
        --segments "small_landlord_us,renter_us_urban" \
        --count 15 \
        --out <run-dir>/nemotron-raw.json

Writes a JSON list of persona records matching the persona-pool schema
(minus `axis_positions`, which Phase 2 Step 2 fills via LLM).
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any, Callable

try:
    from datasets import load_dataset
except ImportError:
    sys.exit("install `datasets`: pip install datasets")


SegmentRule = Callable[[dict[str, Any]], bool]


def _occupation_in(p: dict[str, Any], values: set[str]) -> bool:
    return (p.get("occupation") or "").lower() in values


def _persona_text_contains(p: dict[str, Any], needle: str) -> bool:
    return needle.lower() in (p.get("persona_text") or "").lower()


SEGMENT_RULES: dict[str, SegmentRule] = {
    "small_landlord_us": lambda p: (
        _occupation_in(p, {"landlord", "property manager", "real estate investor"})
        or _persona_text_contains(p, "rental propert")
    ),
    "renter_us_urban": lambda p: (
        _persona_text_contains(p, "rent")
        and (p.get("location_type") or "").lower() == "urban"
    ),
    "freelance_creative": lambda p: (
        _occupation_in(p, {"designer", "writer", "artist", "freelancer"})
        and (p.get("employment_type") or "").lower() == "self-employed"
    ),
    "retiree_fixed_income": lambda p: (
        (p.get("age") or 0) >= 65
        and (p.get("household_income_bracket") or "") in {"<25k", "25-50k"}
    ),
}


def age_bucket(age: int | None) -> str:
    if age is None:
        return "unknown"
    if age < 30:
        return "18-29"
    if age < 45:
        return "30-44"
    if age < 60:
        return "45-59"
    if age < 75:
        return "60-74"
    return "75+"


def stratify_key(p: dict[str, Any]) -> tuple[str, str, str]:
    return (
        age_bucket(p.get("age")),
        (p.get("location_type") or "unknown").lower(),
        (p.get("education") or "unknown").lower(),
    )


def filter_by_segments(ds, segments: list[str]) -> list[dict[str, Any]]:
    unknown = [s for s in segments if s not in SEGMENT_RULES]
    if unknown:
        sys.exit(f"no rules for segments: {unknown}. Extend SEGMENT_RULES in filter_nemotron.py.")
    rules = [SEGMENT_RULES[s] for s in segments]
    return [p for p in ds if any(rule(p) for rule in rules)]


def stratified_sample(personas: list[dict[str, Any]], count: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    buckets: dict[tuple, list[dict]] = {}
    for p in personas:
        buckets.setdefault(stratify_key(p), []).append(p)
    if not buckets:
        return []
    per_bucket = max(1, count // len(buckets))
    sampled: list[dict] = []
    for bucket in buckets.values():
        rng.shuffle(bucket)
        sampled.extend(bucket[:per_bucket])
    rng.shuffle(sampled)
    return sampled[:count]


def normalize_record(p: dict[str, Any], idx: int) -> dict[str, Any]:
    text = p.get("persona_text") or ""
    descriptor = text.split(".")[0][:100] if text else ""
    return {
        "id": f"p{idx:02d}",
        "source": "nemotron",
        "axis_positions": {},
        "descriptor": descriptor,
        "backstory": text,
        "demographics": {
            "age": p.get("age"),
            "location": p.get("location"),
            "occupation": p.get("occupation"),
            "education": p.get("education"),
            "household_income_bracket": p.get("household_income_bracket"),
            "marital_status": p.get("marital_status"),
        },
        "goals_in_app": "",
        "frustrations": [],
        "communication_style": "",
        "_nemotron_id": p.get("id"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--segments", required=True, help="comma-separated segment tags")
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    segments = [s.strip() for s in args.segments.split(",") if s.strip()]
    if not segments:
        sys.exit("--segments must list at least one tag")

    ds = load_dataset("nvidia/Nemotron-Personas-USA", split="train")
    matched = filter_by_segments(ds, segments)
    if not matched:
        sys.exit(f"no personas matched segments: {segments}")
    print(f"matched {len(matched)} personas across {len(segments)} segments", file=sys.stderr)

    sampled = stratified_sample(matched, args.count, args.seed)
    records = [normalize_record(p, i + 1) for i, p in enumerate(sampled)]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, indent=2))
    print(f"wrote {len(records)} personas to {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
