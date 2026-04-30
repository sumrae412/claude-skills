#!/usr/bin/env python3
"""Analyze the skill-selection A/B JSONL log and print per-variant metrics.

Reads .claude/experiments/skill_selection_ab.jsonl (or --log path), groups
trials by variant, and computes the 5 metrics from the experiment plan:

  1. skill_loaded_rate    — fraction of dispatches that loaded any skill
  2. correct_skill_rate   — fraction where loaded skill matches gold
  3. need_aware_rate      — load-rate on tasks the base model fails skill-free
  4. over_load_rate       — load-rate on tasks where gold is `none` AND
                            baseline-skill-free-pass is true
  5. end_task_pass_rate   — fraction passing quick_ci.sh + reviewer spot-check

Then prints a side-by-side comparison and applies the decision tree from
docs/plans/2026-04-29-skill-selection-vs-progressive-disclosure.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOG = REPO_ROOT / ".claude" / "experiments" / "skill_selection_ab.jsonl"


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"no log at {path} — run replay_skill_selection.py first")
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def safe_rate(num: int, denom: int) -> float:
    return (num / denom) if denom else 0.0


def compute_metrics(records: list[dict]) -> dict[str, float | int]:
    n = len(records)
    if n == 0:
        return {"n": 0}
    loaded = sum(1 for r in records if r["skill_loaded"])
    correct = sum(1 for r in records if r["correct_skill"])
    skill_free_fail = [r for r in records if not r["baseline_skill_free_pass"]]
    need_aware_loads = sum(1 for r in skill_free_fail if r["skill_loaded"])
    over_load_eligible = [
        r for r in records
        if r["baseline_skill_free_pass"] and r["gold_skill"] == "none"
    ]
    over_loads = sum(1 for r in over_load_eligible if r["skill_loaded"])
    end_pass = sum(1 for r in records if r["end_task_pass"])
    return {
        "n": n,
        "skill_loaded_rate": safe_rate(loaded, n),
        "correct_skill_rate": safe_rate(correct, n),
        "need_aware_rate": safe_rate(need_aware_loads, len(skill_free_fail)),
        "need_aware_denom": len(skill_free_fail),
        "over_load_rate": safe_rate(over_loads, len(over_load_eligible)),
        "over_load_denom": len(over_load_eligible),
        "end_task_pass_rate": safe_rate(end_pass, n),
    }


def fmt_pct(v: float) -> str:
    return f"{v * 100:5.1f}%"


def print_comparison(by_variant: dict[str, dict]) -> None:
    a = by_variant.get("a", {"n": 0})
    b = by_variant.get("b", {"n": 0})
    print(f"\n{'metric':<22} {'variant A':>12} {'variant B':>12} {'Δ (B−A)':>12}")
    print("-" * 62)
    for key, label in [
        ("skill_loaded_rate", "skill loaded"),
        ("correct_skill_rate", "correct skill"),
        ("need_aware_rate", "need-aware load"),
        ("over_load_rate", "over-load (lower=better)"),
        ("end_task_pass_rate", "end-task pass"),
    ]:
        va = a.get(key, 0.0)
        vb = b.get(key, 0.0)
        delta = vb - va
        print(f"{label:<22} {fmt_pct(va):>12} {fmt_pct(vb):>12} "
              f"{('+' if delta >= 0 else '') + fmt_pct(delta):>12}")
    print(f"\nn (a) = {a.get('n', 0)} | n (b) = {b.get('n', 0)}")
    print(f"need-aware denom (a/b) = {a.get('need_aware_denom', 0)}/"
          f"{b.get('need_aware_denom', 0)}")
    print(f"over-load denom  (a/b) = {a.get('over_load_denom', 0)}/"
          f"{b.get('over_load_denom', 0)}")


def apply_decision_tree(by_variant: dict[str, dict]) -> str:
    """Return a one-line ship/no-ship recommendation per the plan."""
    a, b = by_variant.get("a"), by_variant.get("b")
    if not a or not b or a["n"] == 0 or b["n"] == 0:
        return "INCOMPLETE — need both variants populated to decide."
    correct_delta_pp = (b["correct_skill_rate"] - a["correct_skill_rate"]) * 100
    pass_delta_pp = (b["end_task_pass_rate"] - a["end_task_pass_rate"]) * 100

    if b["end_task_pass_rate"] == 0 and a["end_task_pass_rate"] == 0:
        # Replay didn't measure end-task pass; fall back to correct-skill only.
        if correct_delta_pp >= 15:
            return ("PARTIAL: correct-skill +%.1fpp meets the ≥15pp threshold, "
                    "but end-task pass not measured. Run a manual scoring pass "
                    "before shipping." % correct_delta_pp)
        return ("PARTIAL: correct-skill Δ=%.1fpp, below the ≥15pp threshold. "
                "Investigate whether the test set is biased before re-running."
                % correct_delta_pp)

    if correct_delta_pp >= 15 and pass_delta_pp >= 5:
        return f"SHIP B: correct +{correct_delta_pp:.1f}pp, pass +{pass_delta_pp:.1f}pp."
    if correct_delta_pp >= 15 and pass_delta_pp >= -2:
        return (f"SHIP B (cautious): correct +{correct_delta_pp:.1f}pp, "
                f"pass Δ={pass_delta_pp:+.1f}pp — investigate Phase 5 "
                "incorporation as next bottleneck.")
    if abs(correct_delta_pp) < 5:
        return (f"NO-OP: correct Δ={correct_delta_pp:+.1f}pp is within noise. "
                "Phase 1 routing already does the work; consider testing on "
                "Phase 2 (research) instead.")
    if pass_delta_pp < -2:
        return (f"REGRESSION: pass Δ={pass_delta_pp:+.1f}pp. Re-read paper "
                "§5.2 for retrieval-noise robustness explanation.")
    return f"AMBIGUOUS: correct Δ={correct_delta_pp:+.1f}pp, pass Δ={pass_delta_pp:+.1f}pp."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--by-row", action="store_true",
                        help="Print per-dispatch breakdown in addition to summary.")
    args = parser.parse_args(argv)

    records = load_records(args.log)
    by_variant: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_variant[r["variant"]].append(r)

    metrics = {v: compute_metrics(rs) for v, rs in by_variant.items()}
    print(f"loaded {len(records)} trials from {args.log}")
    print_comparison(metrics)
    print(f"\nrecommendation: {apply_decision_tree(metrics)}")

    if args.by_row:
        print("\nper-dispatch:")
        by_dispatch: dict[str, dict[str, dict]] = defaultdict(dict)
        for r in records:
            by_dispatch[r["dispatch_id"]][r["variant"]] = r
        for did in sorted(by_dispatch):
            a = by_dispatch[did].get("a", {})
            b = by_dispatch[did].get("b", {})
            print(f"  {did}: A→{a.get('loaded_skill','?'):<28} "
                  f"B→{b.get('loaded_skill','?'):<28} gold={a.get('gold_skill') or b.get('gold_skill','?')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
