#!/usr/bin/env python3
"""PersonaGym-adapted fidelity scorer + pool coverage metrics.

Two subcommands:

    python score_fidelity.py coverage \
        --pool <run-dir>/persona-pool.json \
        --axes <run-dir>/app-config.yaml

    python score_fidelity.py score \
        --transcripts <run-dir>/eval-transcripts.json \
        --pool <run-dir>/persona-pool.json \
        --evaluators "claude-sonnet-4-6,claude-opus-4-7" \
        --out <run-dir>/fidelity-report.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.exit("install `pyyaml`: pip install pyyaml")


# ---------------- Coverage ----------------

def monte_carlo_support_coverage(
    positions: list[list[float]],
    n_axes: int,
    k_radius: float,
    n_samples: int = 10000,
    seed: int = 42,
) -> float:
    """Fraction of the unit hypercube within k_radius of any persona position."""
    rng = random.Random(seed)
    hits = 0
    for _ in range(n_samples):
        pt = [rng.random() for _ in range(n_axes)]
        for p in positions:
            if math.sqrt(sum((a - b) ** 2 for a, b in zip(pt, p))) <= k_radius:
                hits += 1
                break
    return hits / n_samples


def pairwise_distances(positions: list[list[float]]) -> tuple[float, float]:
    if len(positions) < 2:
        return 0.0, 0.0
    dists = [
        math.sqrt(sum((a - b) ** 2 for a, b in zip(p, q)))
        for p, q in itertools.combinations(positions, 2)
    ]
    return min(dists), sum(dists) / len(dists)


def calibrate_k_radius(n_personas: int, n_axes: int) -> float:
    """Heuristic: 1.5× the expected nearest-neighbor distance under uniform N."""
    if n_personas <= 0:
        return 0.0
    return (1 / n_personas) ** (1 / n_axes) * 1.5


def _personas_from_pool(pool: Any) -> list[dict]:
    if isinstance(pool, list):
        return pool
    if isinstance(pool, dict):
        return pool.get("personas", [])
    return []


def cmd_coverage(args: argparse.Namespace) -> int:
    pool = json.loads(Path(args.pool).read_text())
    cfg = yaml.safe_load(Path(args.axes).read_text())
    axes = [a["name"] for a in cfg["diversity_axes"]]
    personas = _personas_from_pool(pool)
    positions = [
        [p.get("axis_positions", {}).get(a, 0.5) for a in axes]
        for p in personas
    ]

    k = calibrate_k_radius(len(positions), len(axes))
    support = monte_carlo_support_coverage(positions, len(axes), k)
    min_d, avg_d = pairwise_distances(positions)

    result = {
        "method": "monte_carlo_k_radius",
        "estimated_support_coverage": round(support, 3),
        "k_radius": round(k, 3),
        "min_pairwise_distance": round(min_d, 3),
        "average_pairwise_distance": round(avg_d, 3),
    }
    print(json.dumps(result, indent=2))
    return 0


# ---------------- Fidelity scoring ----------------

TASKS = [
    "action_justification",
    "expected_action",
    "linguistic_habits",
    "persona_consistency",
    "toxicity_control",
]

REFUSAL_PATTERNS = [
    r"i can(?:not|'t) role-?play",
    r"as an ai,?\s",
    r"i don't feel comfortable",
    r"i'?m not able to pretend",
    r"i cannot pretend to be",
]


def score_one(transcript: dict, persona: dict, task: str, evaluator: str) -> int:
    """Real impl: dispatch to evaluator LLM with the task rubric.

    See references/personagym-rubrics.md for the rubric anchors. Unit tests
    should mock this function.
    """
    raise NotImplementedError(
        "wire to fidelity_evaluators per model_config; return int in [1, 5]"
    )


def detect_refusal(transcript: dict) -> bool:
    compiled = [re.compile(p, re.IGNORECASE) for p in REFUSAL_PATTERNS]
    for step in transcript.get("steps", []):
        text = step.get("persona_utterance") or ""
        if any(r.search(text) for r in compiled):
            return True
    return False


def _gate(task_scores: dict[str, float], refused: bool) -> bool:
    if refused or not task_scores:
        return False
    mean = sum(task_scores.values()) / len(task_scores)
    return mean >= 3.5 and min(task_scores.values()) >= 2.0


def cmd_score(args: argparse.Namespace) -> int:
    transcripts_doc = json.loads(Path(args.transcripts).read_text())
    pool_doc = json.loads(Path(args.pool).read_text())
    personas = {p["id"]: p for p in _personas_from_pool(pool_doc)}
    evaluators = [e.strip() for e in args.evaluators.split(",") if e.strip()]
    if len(evaluators) < 2:
        print("warning: fewer than 2 evaluators — self-eval bias risk", file=sys.stderr)

    raw_transcripts = (
        transcripts_doc.get("transcripts")
        if isinstance(transcripts_doc, dict)
        else transcripts_doc
    )

    scored: list[dict] = []
    refusal_counts: dict[str, list[int]] = {}
    by_task_totals: dict[str, list[float]] = {t: [] for t in TASKS}

    for t in raw_transcripts:
        persona = personas.get(t["persona_id"])
        if not persona:
            continue
        refused = detect_refusal(t)
        refusal_counts.setdefault(t["persona_id"], []).append(int(refused))

        task_scores: dict[str, float] = {}
        if args.dry_run:
            task_scores = {task: 0.0 for task in TASKS}
        else:
            for task in TASKS:
                raw = [score_one(t, persona, task, e) for e in evaluators]
                task_scores[task] = sum(raw) / len(raw)

        mean = sum(task_scores.values()) / len(task_scores)
        passed = _gate(task_scores, refused)

        scored.append({
            "cell_id": t.get("cell_id"),
            "persona_id": t["persona_id"],
            "scores": task_scores,
            "mean_score": round(mean, 2),
            "evaluator_ensemble": evaluators,
            "passed_gate": passed,
            "refusal_detected": refused,
        })
        for task, s in task_scores.items():
            by_task_totals[task].append(s)

    pass_rate = (
        sum(1 for s in scored if s["passed_gate"]) / len(scored)
        if scored
        else 0.0
    )
    by_task_mean = {
        t: round(sum(v) / len(v), 2) if v else 0.0
        for t, v in by_task_totals.items()
    }
    refusal_rate = {
        pid: round(sum(v) / len(v), 2)
        for pid, v in refusal_counts.items()
    }

    report = {
        "run_id": transcripts_doc.get("run_id") if isinstance(transcripts_doc, dict) else None,
        "scored_transcripts": scored,
        "aggregate": {
            "pass_rate": round(pass_rate, 2),
            "by_task_mean": by_task_mean,
            "refusal_rate_per_persona": refusal_rate,
        },
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"wrote fidelity report to {out}", file=sys.stderr)
    return 0


# ---------------- Dispatch ----------------

def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    cov = sub.add_parser("coverage")
    cov.add_argument("--pool", required=True)
    cov.add_argument("--axes", required=True)
    cov.set_defaults(func=cmd_coverage)

    sc = sub.add_parser("score")
    sc.add_argument("--transcripts", required=True)
    sc.add_argument("--pool", required=True)
    sc.add_argument("--evaluators", required=True)
    sc.add_argument("--out", required=True)
    sc.add_argument("--dry-run", action="store_true")
    sc.set_defaults(func=cmd_score)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
