#!/usr/bin/env python3
"""Two-stage tail persona generator (Paglieri et al. 2026).

Stage 1: Sobol quasi-random axis positions, farthest-first-filtered away from
the Nemotron cloud.

Stage 2: expand each position into a full persona via one LLM call (wired to
the project's configured persona_player).

Usage:
    python generate_tail.py \
        --config <run-dir>/app-config.yaml \
        --count 10 \
        --nemotron-coverage <run-dir>/nemotron-raw.json \
        --out <run-dir>/tail-raw.json \
        --seed 12345

Run with --dry-run to skip Stage 2 LLM calls and emit axis positions only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.exit("install `pyyaml`: pip install pyyaml")

try:
    from scipy.stats import qmc
except ImportError:
    sys.exit("install `scipy`: pip install scipy")


EXPANSION_PROMPT = """\
You are generating a synthetic user persona for testing {app_name}.

The persona sits at these positions on the diversity axes:
{axis_lines}

The app is for these segments: {segments}.

Write a persona that:
- naturally sits at those axis positions,
- is plausibly a member of one of the target segments,
- has a real reason to use this app.

Return strict JSON with fields:
{{
  "descriptor": "one line",
  "backstory": "~150 words, first or third person",
  "demographics": {{"age": int, "location": "City, ST", "occupation": "..."}},
  "goals_in_app": "why this persona is using the app",
  "frustrations": ["...", "..."],
  "communication_style": "for linguistic fidelity scoring"
}}

Do NOT caricature the axis positions — make them believable and specific.
"""


def sobol_positions(n_axes: int, count: int, seed: int) -> list[list[float]]:
    engine = qmc.Sobol(d=n_axes, scramble=True, seed=seed)
    return engine.random(n=count).tolist()


def nearest_distance(point: list[float], cloud: list[list[float]]) -> float:
    if not cloud:
        return math.inf
    return min(
        math.sqrt(sum((a - b) ** 2 for a, b in zip(point, q)))
        for q in cloud
    )


def farthest_first(candidates: list[list[float]], cloud: list[list[float]], count: int) -> list[list[float]]:
    """Iterative farthest-first: each pick augments the cloud before scoring the next."""
    selected: list[list[float]] = []
    remaining = list(candidates)
    augmented = list(cloud)
    for _ in range(min(count, len(remaining))):
        best_idx = max(
            range(len(remaining)),
            key=lambda i: nearest_distance(remaining[i], augmented),
        )
        chosen = remaining.pop(best_idx)
        selected.append(chosen)
        augmented.append(chosen)
    return selected


def expand_persona(axes: list[dict], position: list[float], app_name: str, segments: list[str]) -> dict[str, Any]:
    """Stage 2 — LLM call to expand an axis position into a full persona.

    Wire this to the project's configured persona_player (e.g. via the Anthropic
    SDK). Unit tests should mock this function directly.
    """
    axis_lines = "\n".join(
        f"- {a['name']}: {p:.2f} (0={a['low']}, 1={a['high']})"
        for a, p in zip(axes, position)
    )
    prompt = EXPANSION_PROMPT.format(
        app_name=app_name,
        axis_lines=axis_lines,
        segments=", ".join(segments),
    )
    del prompt  # referenced to show the shape; real impl sends it to the LLM
    raise NotImplementedError(
        "wire to persona_player per model_config; return dict with descriptor, "
        "backstory, demographics, goals_in_app, frustrations, communication_style"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--nemotron-coverage", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--dry-run", action="store_true", help="skip Stage 2 LLM calls; emit positions only")
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text())
    for key in ("diversity_axes", "app", "segments"):
        if key not in cfg:
            sys.exit(f"error: config missing required key: {key}")
    if "name" not in cfg["app"]:
        sys.exit("error: config missing required key: app.name")
    axes = cfg["diversity_axes"]
    app_name = cfg["app"]["name"]
    segments = cfg["segments"]

    nem = json.loads(Path(args.nemotron_coverage).read_text())
    nem_positions = [
        [r["axis_positions"].get(a["name"], 0.5) for a in axes]
        for r in nem
        if r.get("axis_positions")
    ]

    candidates = sobol_positions(len(axes), args.count * 5, args.seed)
    chosen = farthest_first(candidates, nem_positions, args.count)

    out_records: list[dict[str, Any]] = []
    for i, pos in enumerate(chosen, start=len(nem) + 1):
        record: dict[str, Any] = {
            "id": f"p{i:02d}",
            "source": "tail",
            "axis_positions": {a["name"]: p for a, p in zip(axes, pos)},
        }
        if args.dry_run:
            record.update({
                "descriptor": "(dry-run placeholder)",
                "backstory": "",
                "demographics": {},
                "goals_in_app": "",
                "frustrations": [],
                "communication_style": "",
            })
        else:
            record.update(expand_persona(axes, pos, app_name, segments))
        out_records.append(record)

    prompt_hash = hashlib.sha256(EXPANSION_PROMPT.encode()).hexdigest()
    payload = {
        "personas": out_records,
        "generator_metadata": {
            "tail_generator_seed": args.seed,
            "tail_generator_prompt_hash": prompt_hash,
            "segments": segments,
        },
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))
    print(f"wrote {len(out_records)} tail personas to {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
