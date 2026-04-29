#!/usr/bin/env python3
"""Export a claude-flow run manifest as deterministic JSONL timeline events."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


TIMESTAMPLESS_SORT_KEY = "9999-12-31T23:59:59+00:00"


def load_manifest(path: Path) -> dict[str, Any]:
    """Load and validate a run manifest JSON file."""
    if not path.exists():
        raise FileNotFoundError(f"manifest not found: {path}")
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"manifest is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError("manifest root must be a JSON object")
    return payload


def _event(
    event_type: str,
    timestamp: str | None,
    payload: dict[str, Any],
    manifest_order: int,
) -> dict[str, Any]:
    """Build an internal event with a manifest-order marker."""
    return {
        "type": event_type,
        "timestamp": timestamp,
        "payload": payload,
        "_manifest_order": manifest_order,
    }


def _metadata_event(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return the first event describing the run configuration."""
    payload = {
        "workflow_version": manifest.get("workflow_version"),
        "session_id": manifest.get("session_id"),
        "workflow_path": manifest.get("workflow_path"),
        "task_summary": manifest.get("task_summary"),
        "review_base_sha": manifest.get("review_base_sha"),
        "capability_matrix": manifest.get("capability_matrix", {}),
    }
    return _event(
        "metadata",
        manifest.get("last_updated_at"),
        payload,
        manifest_order=-1,
    )


def _approval_events(
    manifest: dict[str, Any],
    kind: str,
    start_order: int,
) -> list[dict[str, Any]]:
    """Return approval timeline events for one approval kind."""
    key = f"{kind}_approvals"
    events = []
    for index, approval in enumerate(manifest.get(key, [])):
        payload = {"kind": kind, **approval}
        events.append(
            _event(
                "approval",
                approval.get("recorded_at"),
                payload,
                manifest_order=start_order + index,
            )
        )
    return events


def _list_events(
    manifest: dict[str, Any],
    manifest_key: str,
    event_type: str,
    start_order: int,
) -> list[dict[str, Any]]:
    """Return timeline events from a manifest list field."""
    events = []
    for index, item in enumerate(manifest.get(manifest_key, [])):
        if not isinstance(item, dict):
            item = {"value": item}
        events.append(
            _event(
                event_type,
                item.get("recorded_at"),
                dict(item),
                manifest_order=start_order + index,
            )
        )
    return events


def manifest_to_events(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert a manifest object into ordered JSON-serializable events."""
    metadata = _metadata_event(manifest)
    ordered_events = []
    ordered_events.extend(_approval_events(manifest, "requirements", 0))
    ordered_events.extend(_approval_events(manifest, "plan", 10_000))
    ordered_events.extend(
        _list_events(manifest, "verification_runs", "verification_run", 20_000)
    )
    ordered_events.extend(
        _list_events(manifest, "review_runs", "review_run", 30_000)
    )
    ordered_events.extend(
        _list_events(manifest, "commands_run", "command", 40_000)
    )

    ordered_events.sort(
        key=lambda event: (
            event["timestamp"] is None,
            event["timestamp"] or TIMESTAMPLESS_SORT_KEY,
            event["_manifest_order"],
        )
    )
    events = [metadata, *ordered_events]
    for sequence, event in enumerate(events):
        event["sequence"] = sequence
        event.pop("_manifest_order", None)
    return events


def write_jsonl(
    events: list[dict[str, Any]],
    output: Path | None = None,
) -> None:
    """Write timeline events to a file or stdout."""
    lines = [json.dumps(event, sort_keys=True) for event in events]
    text = "\n".join(lines)
    if text:
        text += "\n"
    if output is None:
        sys.stdout.write(text)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()
    try:
        manifest = load_manifest(args.manifest)
        events = manifest_to_events(manifest)
        write_jsonl(events, args.output)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
