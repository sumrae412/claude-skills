#!/usr/bin/env python3
"""Log a single skill-selection A/B trial for the Phase 5 experiment.

Plan: docs/plans/2026-04-29-skill-selection-vs-progressive-disclosure.md.

Each invocation appends one JSONL line to the experiment log so the analyzer
can compute the 5 metrics (loaded-rate, correct-skill, need-aware, over-load,
end-task-pass) from the variant A vs variant B runs.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LOG = Path(".claude") / "experiments" / "skill_selection_ab.jsonl"

VALID_VARIANTS = {"a", "b", "b150", "c1", "c3"}
VALID_GOLD = {"courierflow-ui", "courierflow-api", "courierflow-data",
              "courierflow-integrations", "courierflow-security", "none"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dispatch-id", required=True,
                        help="Stable identifier for the historical Phase 5 dispatch.")
    parser.add_argument("--variant", required=True, choices=sorted(VALID_VARIANTS))
    parser.add_argument("--loaded-skill", default="none",
                        help="The skill the subagent actually loaded (or 'none').")
    parser.add_argument("--gold-skill", required=True,
                        help="Human-labeled gold skill for this dispatch.")
    parser.add_argument("--baseline-skill-free-pass", type=lambda v: v.lower() == "true",
                        required=True,
                        help="Did the base model pass this task with NO skill? true/false.")
    parser.add_argument("--end-task-pass", type=lambda v: v.lower() == "true",
                        required=True,
                        help="Did this run pass quick_ci.sh + reviewer spot-check? true/false.")
    parser.add_argument("--tokens-in", type=int, default=0)
    parser.add_argument("--tokens-out", type=int, default=0)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    args = parser.parse_args()

    if args.gold_skill not in VALID_GOLD:
        print(f"error: --gold-skill must be one of {sorted(VALID_GOLD)}", file=sys.stderr)
        return 2

    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "dispatch_id": args.dispatch_id,
        "variant": args.variant,
        "loaded_skill": args.loaded_skill,
        "gold_skill": args.gold_skill,
        "baseline_skill_free_pass": args.baseline_skill_free_pass,
        "end_task_pass": args.end_task_pass,
        "skill_loaded": args.loaded_skill != "none",
        "correct_skill": args.loaded_skill == args.gold_skill,
        "need_aware_load": (
            args.loaded_skill != "none" and not args.baseline_skill_free_pass
        ),
        "over_load": (
            args.loaded_skill != "none" and args.baseline_skill_free_pass
            and args.gold_skill == "none"
        ),
        "tokens_in": args.tokens_in,
        "tokens_out": args.tokens_out,
    }

    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("a") as f:
        f.write(json.dumps(record) + "\n")

    print(f"logged: {args.dispatch_id} variant={args.variant} "
          f"loaded={args.loaded_skill} gold={args.gold_skill} "
          f"correct={record['correct_skill']} pass={args.end_task_pass}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
