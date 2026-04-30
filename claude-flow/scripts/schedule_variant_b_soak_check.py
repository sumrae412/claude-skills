#!/usr/bin/env python3
"""Register a 1-week soak-check task for the variant B rollout.

Fires 7 days from `--fire-at` (or 7 days from now). The scheduled task runs
analyze_skill_selection.py against the live JSONL log and writes a follow-up
note alongside the original decision record. If the scheduled-tasks MCP isn't
available at fire time, the fallback markdown reminder at
docs/decisions/REMINDERS.md catches the next session that loads it.

Usage:
    schedule_variant_b_soak_check.py                    # 7 days from now
    schedule_variant_b_soak_check.py --dry-run          # print, don't register
    schedule_variant_b_soak_check.py --fire-at 2026-05-06T15:00:00Z

The MCP scheduling call is wrapped — if no MCP server is connected, the
script writes the fallback reminder and exits 0 (not an error). The reminder
is the durable record; the MCP task is the convenience layer.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DECISION_RECORD = REPO_ROOT / "docs" / "decisions" / "2026-04-29-ship-forced-selection-phase5.md"
REMINDERS_FILE = REPO_ROOT / "docs" / "decisions" / "REMINDERS.md"
# Use a path relative to repo root so the reminder survives worktree deletion
# (e.g., after the PR merges and the local worktree is cleaned up).
ANALYZER_REL = "claude-flow/scripts/analyze_skill_selection.py"


def soak_check_command(log_path: str, output_note: str) -> str:
    """Build the shell command the scheduled task will execute.

    All paths are relative to the canonical claude-skills repo root so the
    command survives worktree deletion. The fire-time session must cd into
    the canonical repo before invoking.
    """
    return (
        f"cd ~/claude_code/claude-skills && "
        f"python3 {ANALYZER_REL} --log {log_path} --by-row > {output_note} 2>&1 && "
        f"printf '\\n\\n--- Soak check complete: %s ---\\n' "
        f"\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\" >> {output_note}"
    )


def write_fallback_reminder(fire_at: datetime, command: str) -> None:
    """Write a durable markdown reminder so the soak isn't lost if the MCP fails."""
    REMINDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = (
        f"\n## Variant B soak check — fire at {fire_at.isoformat()}\n\n"
        f"**Source:** [decision record](2026-04-29-ship-forced-selection-phase5.md)\n\n"
        f"On or after the fire date, run:\n\n```bash\n{command}\n```\n\n"
        f"Then update the decision record's follow-ups section with the result.\n"
    )
    if REMINDERS_FILE.exists():
        existing = REMINDERS_FILE.read_text()
        # Idempotent — don't duplicate if already present.
        if entry.strip() in existing:
            print(f"reminder already present in {REMINDERS_FILE}")
            return
        REMINDERS_FILE.write_text(existing + entry)
    else:
        REMINDERS_FILE.write_text(
            "# Decision-record reminders\n\n"
            "Scheduled-task fallback reminders. Any session that loads this file "
            "should check whether listed dates are due and run the listed command "
            "if so.\n" + entry
        )
    print(f"reminder written to {REMINDERS_FILE}")


def try_register_mcp_task(fire_at: datetime, command: str, dry_run: bool) -> bool:
    """Attempt to register a task via the scheduled-tasks MCP. Returns True on success."""
    # The scheduled-tasks MCP exposes a `create_scheduled_task` tool. We can't call
    # it directly from a script; the registration must happen via Claude. So this
    # function emits a JSON payload that the orchestrator (or human) can paste
    # into a Claude session to register. In dry-run mode, just print.
    payload = {
        "name": f"variant-b-soak-{fire_at.date().isoformat()}",
        "fire_at": fire_at.isoformat(),
        "command": command,
        "description": (
            "Re-analyze variant B Phase 5 trial logs 7 days post-rollout. "
            "Source: docs/decisions/2026-04-29-ship-forced-selection-phase5.md."
        ),
    }
    print(json.dumps(payload, indent=2))
    if dry_run:
        return False
    # No direct script→MCP call. The orchestrator handles registration; this
    # script's role is to emit the canonical payload + write the fallback.
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fire-at",
        help="ISO-8601 datetime (e.g. 2026-05-06T15:00:00Z). Default: 7 days from now.",
    )
    parser.add_argument(
        "--log",
        default=".claude/experiments/skill_selection_ab.jsonl",
        help="Path to the live JSONL log (relative to project root at fire time).",
    )
    parser.add_argument(
        "--output-note",
        default="docs/decisions/2026-05-06-variant-b-soak-results.md",
        help="Where the soak-check output will be written.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.fire_at:
        fire_at = datetime.fromisoformat(args.fire_at.replace("Z", "+00:00"))
    else:
        fire_at = datetime.now(timezone.utc) + timedelta(days=7)

    command = soak_check_command(args.log, args.output_note)

    print(f"Fire at: {fire_at.isoformat()}")
    print(f"Command: {command}\n")
    print("MCP payload:")
    try_register_mcp_task(fire_at, command, args.dry_run)

    # Always write the fallback reminder — the MCP is the convenience layer,
    # the reminder is the durable record.
    write_fallback_reminder(fire_at, command)
    return 0


if __name__ == "__main__":
    sys.exit(main())
