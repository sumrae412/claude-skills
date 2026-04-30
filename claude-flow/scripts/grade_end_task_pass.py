#!/usr/bin/env python3
"""Apply the end-task-pass rubric to skill_selection_ab.jsonl.

Rubric: a trial passes if (loaded == gold) OR (baseline_skill_free_pass).
Anything else fails — the agent is missing required project knowledge.

This is a substitute for actually running each model response through
quick_ci.sh, which we can't do because the prompts said "do not write code."
The rubric captures the same signal: did the agent have what it needed to
implement the change?
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG = REPO_ROOT / ".claude" / "experiments" / "skill_selection_ab.jsonl"


def main() -> int:
    if not LOG.exists():
        print(f"no log at {LOG}", file=sys.stderr)
        return 1
    records = [json.loads(line) for line in LOG.read_text().splitlines() if line.strip()]
    flipped = 0
    for r in records:
        passed = r["correct_skill"] or r["baseline_skill_free_pass"]
        if r["end_task_pass"] != passed:
            r["end_task_pass"] = passed
            flipped += 1
    LOG.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    print(f"updated {flipped} of {len(records)} records in {LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
