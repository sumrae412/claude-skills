#!/usr/bin/env python3
"""Analyze claude-flow run event logs for tool/subagent reliability."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ERROR_EVENT_TYPES = {"tool_error", "subagent_error"}
UNKNOWN_ERROR_CLASS = "unknown-tool-error"


def load_event_log(path: Path) -> list[dict[str, Any]]:
    """Load one JSONL event log."""
    events = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"event log is not valid JSONL at {path}:{line_number}"
            ) from exc
        if not isinstance(event, dict):
            raise ValueError(
                f"event log line must be a JSON object at {path}:{line_number}"
            )
        events.append(event)
    return events


def discover_event_logs(runs_dir: Path) -> list[Path]:
    """Return run event logs under a runs directory in deterministic order."""
    if not runs_dir.exists():
        return []
    return sorted(runs_dir.glob("*.events.jsonl"))


def counter_rows(counter: Counter[str]) -> list[dict[str, int | str]]:
    """Return stable rows sorted by count descending, then key ascending."""
    return [
        {"key": key, "count": count}
        for key, count in sorted(
            counter.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]


def repeated_rows(counter: Counter[str]) -> list[dict[str, int | str]]:
    """Return counters with at least two occurrences."""
    repeated = Counter(
        {key: count for key, count in counter.items() if count >= 2}
    )
    return counter_rows(repeated)


def _payload_value(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if value is None or value == "":
        return "unknown"
    return str(value)


def _run_error_counts(events: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for event in events:
        if event.get("type") not in ERROR_EVENT_TYPES:
            continue
        payload = event.get("payload") or {}
        if not isinstance(payload, dict):
            payload = {}
        counts[_payload_value(payload, "error_class")] += 1
    return counts


def recent_spikes(
    per_run_counts: list[Counter[str]],
) -> list[dict[str, int | str]]:
    """Return error classes that exceeded prior maxima in the latest run."""
    if len(per_run_counts) < 2:
        return []

    latest = per_run_counts[-1]
    previous = per_run_counts[:-1]
    spikes = []
    for error_class, latest_count in latest.items():
        previous_max = max(
            (run.get(error_class, 0) for run in previous),
            default=0,
        )
        if latest_count >= 2 and latest_count > previous_max:
            spikes.append(
                {
                    "dimension": "error_class",
                    "key": error_class,
                    "latest_count": latest_count,
                    "previous_max": previous_max,
                }
            )
    return sorted(
        spikes,
        key=lambda row: (-int(row["latest_count"]), str(row["key"])),
    )


def analyze_event_logs(paths: list[Path]) -> dict[str, Any]:
    """Aggregate reliability data from run event logs."""
    by_error_class: Counter[str] = Counter()
    by_phase: Counter[str] = Counter()
    by_tool: Counter[str] = Counter()
    by_subagent: Counter[str] = Counter()
    per_run_counts: list[Counter[str]] = []
    events_scanned = 0
    error_events = 0

    for path in sorted(paths):
        events = load_event_log(path)
        events_scanned += len(events)
        per_run_counts.append(_run_error_counts(events))
        for event in events:
            if event.get("type") not in ERROR_EVENT_TYPES:
                continue
            payload = event.get("payload") or {}
            if not isinstance(payload, dict):
                payload = {}
            error_events += 1
            error_class = _payload_value(payload, "error_class")
            by_error_class[error_class] += 1
            by_phase[_payload_value(payload, "phase")] += 1
            if event.get("type") == "tool_error":
                by_tool[_payload_value(payload, "tool_name")] += 1
            else:
                by_subagent[_payload_value(payload, "subagent_role")] += 1

    return {
        "runs_scanned": len(paths),
        "events_scanned": events_scanned,
        "error_events": error_events,
        "unknown_error_count": by_error_class.get(UNKNOWN_ERROR_CLASS, 0),
        "by_error_class": counter_rows(by_error_class),
        "by_phase": counter_rows(by_phase),
        "by_tool": counter_rows(by_tool),
        "by_subagent": counter_rows(by_subagent),
        "repeated_failures": {
            "tools": repeated_rows(by_tool),
            "subagents": repeated_rows(by_subagent),
        },
        "recent_spikes": recent_spikes(per_run_counts),
    }


def render_text(report: dict[str, Any]) -> str:
    """Render a compact human-readable report."""
    lines = [
        "Run reliability report",
        f"Runs scanned: {report['runs_scanned']}",
        f"Events scanned: {report['events_scanned']}",
        f"Error events: {report['error_events']}",
        f"Unknown errors: {report['unknown_error_count']}",
        "",
        "By error class:",
    ]
    lines.extend(
        f"- {row['key']}: {row['count']}" for row in report["by_error_class"]
    )
    lines.append("")
    lines.append("Repeated tool failures:")
    repeated_tools = report["repeated_failures"]["tools"]
    lines.extend(f"- {row['key']}: {row['count']}" for row in repeated_tools)
    if not repeated_tools:
        lines.append("- none")
    lines.append("")
    lines.append("Recent spikes:")
    lines.extend(
        "- {key}: latest {latest_count}, previous max {previous_max}".format(
            **row
        )
        for row in report["recent_spikes"]
    )
    if not report["recent_spikes"]:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs-dir",
        type=Path,
        default=Path(".claude/runs"),
        help="Directory containing *.events.jsonl run logs.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main() -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()
    try:
        paths = discover_event_logs(args.runs_dir)
        report = analyze_event_logs(paths)
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
