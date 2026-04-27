#!/usr/bin/env python3
"""Record replayable claude-flow run metadata."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CAPABILITY_MATRIX = {
    "test_command": None,
    "lint_command": None,
    "typecheck_command": None,
    "static_analysis_command": None,
    "analysis_roots": [],
    "dev_server_command": None,
    "ci_present": False,
    "diff_base_strategy": None,
}


def now_iso() -> str:
    """Return an ISO-8601 timestamp in UTC."""
    return datetime.now(timezone.utc).isoformat()


def default_manifest() -> dict[str, Any]:
    """Return the baseline manifest shape."""
    return {
        "workflow_version": "2",
        "session_id": None,
        "workflow_path": None,
        "task_summary": None,
        "review_base_sha": None,
        "review_base": None,
        "capability_matrix": dict(DEFAULT_CAPABILITY_MATRIX),
        "requirements_approvals": [],
        "plan_approvals": [],
        "verification_runs": [],
        "review_runs": [],
        "commands_run": [],
    }


def ensure_parent(path: Path) -> None:
    """Create the path parent directory if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json_file(path: Path, fallback: Any) -> Any:
    """Read JSON from path, returning fallback when the file is absent."""
    if not path.exists():
        return fallback
    return json.loads(path.read_text())


def write_json_file(path: Path, payload: Any) -> None:
    """Write pretty JSON to path."""
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def load_manifest(path: Path) -> dict[str, Any]:
    """Load an existing manifest or create a default one in memory."""
    payload = read_json_file(path, None)
    if payload is None:
        payload = default_manifest()
    return payload


def normalize_capability_matrix(
    capability_matrix: dict[str, Any] | None,
) -> dict[str, Any]:
    """Merge supplied capability fields into the default shape."""
    merged = dict(DEFAULT_CAPABILITY_MATRIX)
    if capability_matrix:
        merged.update(capability_matrix)
    return merged


def load_state_file(path: Path | None) -> dict[str, Any] | None:
    """Load workflow state when a state path is provided."""
    if path is None:
        return None
    return read_json_file(path, {})


def write_state_file(path: Path | None, payload: dict[str, Any] | None) -> None:
    """Persist workflow state when present."""
    if path is None or payload is None:
        return
    write_json_file(path, payload)


def sync_state_manifest_path(
    state: dict[str, Any] | None,
    manifest_path: Path,
    task_summary: str | None = None,
    workflow_path: str | None = None,
    capability_matrix: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Update the workflow state with manifest metadata."""
    if state is None:
        return None
    state["run_manifest_path"] = str(manifest_path)
    if task_summary is not None:
        state["task_summary"] = task_summary
    if workflow_path is not None:
        current_phase = state.setdefault("current_phase", {})
        current_phase["path"] = workflow_path
    if capability_matrix is not None:
        state["capability_matrix"] = normalize_capability_matrix(capability_matrix)
    return state


def sync_state_approval(
    state: dict[str, Any] | None,
    kind: str,
    sha256: str,
) -> dict[str, Any] | None:
    """Mirror approval hashes into workflow state."""
    if state is None:
        return None
    approvals = state.setdefault("approvals", {})
    approvals[f"{kind}_sha256"] = sha256
    return state


def sync_state_review_base(
    state: dict[str, Any] | None,
    review_base_sha: str,
) -> dict[str, Any] | None:
    """Mirror review base into workflow state."""
    if state is None:
        return None
    state["review_base_sha"] = review_base_sha
    return state


def hash_text(text: str) -> str:
    """Return a stable SHA256 hex digest for text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_text_source(
    content: str | None = None,
    content_file: Path | None = None,
) -> tuple[str, str]:
    """Read text from an inline value or a file and return text plus label."""
    if content is not None:
        return content, "inline"
    if content_file is not None:
        return content_file.read_text(), str(content_file)
    raise ValueError("either content or content_file is required")


def init_manifest(
    manifest_path: Path,
    workflow_path: str | None = None,
    task_summary: str | None = None,
    capability_matrix: dict[str, Any] | None = None,
    session_id: str | None = None,
    state_path: Path | None = None,
) -> dict[str, Any]:
    """Create or update the manifest and optionally sync workflow state."""
    manifest = load_manifest(manifest_path)
    if workflow_path is not None:
        manifest["workflow_path"] = workflow_path
    if task_summary is not None:
        manifest["task_summary"] = task_summary
    if session_id is not None:
        manifest["session_id"] = session_id
    manifest["capability_matrix"] = normalize_capability_matrix(
        capability_matrix or manifest.get("capability_matrix")
    )
    manifest["last_updated_at"] = now_iso()
    write_json_file(manifest_path, manifest)

    state = load_state_file(state_path)
    state = sync_state_manifest_path(
        state,
        manifest_path,
        task_summary=task_summary,
        workflow_path=workflow_path,
        capability_matrix=capability_matrix,
    )
    write_state_file(state_path, state)
    return manifest


def record_approval(
    manifest_path: Path,
    kind: str,
    content: str | None = None,
    content_file: Path | None = None,
    note: str | None = None,
    state_path: Path | None = None,
) -> dict[str, Any]:
    """Append a requirements or plan approval record."""
    manifest = load_manifest(manifest_path)
    state = load_state_file(state_path)
    text, source = read_text_source(content=content, content_file=content_file)
    sha256 = hash_text(text)
    entry = {
        "sha256": sha256,
        "recorded_at": now_iso(),
        "source": source,
        "size_bytes": len(text.encode("utf-8")),
    }
    if note:
        entry["note"] = note

    key = f"{kind}_approvals"
    manifest.setdefault(key, []).append(entry)
    manifest["last_updated_at"] = now_iso()
    write_json_file(manifest_path, manifest)

    state = sync_state_approval(state, kind, sha256)
    write_state_file(state_path, state)
    return entry


def set_review_base(
    manifest_path: Path,
    review_base_sha: str,
    source: str | None = None,
    base_ref: str | None = None,
    state_path: Path | None = None,
) -> dict[str, Any]:
    """Persist the chosen review base and optionally sync workflow state."""
    manifest = load_manifest(manifest_path)
    state = load_state_file(state_path)
    entry = {
        "review_base_sha": review_base_sha,
        "recorded_at": now_iso(),
        "source": source,
        "base_ref": base_ref,
    }
    manifest["review_base_sha"] = review_base_sha
    manifest["review_base"] = entry
    manifest["last_updated_at"] = now_iso()
    write_json_file(manifest_path, manifest)

    state = sync_state_review_base(state, review_base_sha)
    write_state_file(state_path, state)
    return entry


def record_verification(
    manifest_path: Path,
    phase: str,
    status: str,
    summary: dict[str, Any] | None = None,
    summary_file: Path | None = None,
    plan_file: str | None = None,
) -> dict[str, Any]:
    """Append a plan-verification or similar verification record."""
    manifest = load_manifest(manifest_path)
    if summary is None and summary_file is not None:
        summary = json.loads(summary_file.read_text())
    entry = {
        "phase": phase,
        "status": status,
        "recorded_at": now_iso(),
        "summary": summary or {},
        "plan_file": plan_file,
    }
    manifest.setdefault("verification_runs", []).append(entry)
    manifest["last_updated_at"] = now_iso()
    write_json_file(manifest_path, manifest)
    return entry


def record_review(
    manifest_path: Path,
    summary: dict[str, Any] | None = None,
    summary_file: Path | None = None,
    redactions: dict[str, Any] | None = None,
    redactions_file: Path | None = None,
    reviewers_run: list[str] | None = None,
) -> dict[str, Any]:
    """Append a Phase 6 review record."""
    manifest = load_manifest(manifest_path)
    if summary is None and summary_file is not None:
        summary = json.loads(summary_file.read_text())
    if redactions is None and redactions_file is not None:
        redactions = json.loads(redactions_file.read_text())

    summary = summary or {}
    redactions = redactions or {}
    entry = {
        "recorded_at": now_iso(),
        "review_base_sha": manifest.get("review_base_sha"),
        "review_budget": summary.get("review_budget"),
        "budget_reasons": summary.get("budget_reasons", []),
        "by_tier": summary.get("by_tier", {}),
        "budget_skipped": summary.get("budget_skipped", []),
        "conditional_skipped": summary.get("conditional_skipped", []),
        "registry_sources": summary.get("registry_sources", []),
        "reviewers_run": reviewers_run or [],
        "redaction_count": redactions.get("redaction_count", 0),
        "redactions": redactions.get("redactions", []),
    }
    manifest.setdefault("review_runs", []).append(entry)
    manifest["last_updated_at"] = now_iso()
    write_json_file(manifest_path, manifest)
    return entry


def record_command(
    manifest_path: Path,
    command: str,
    exit_code: int,
    category: str | None = None,
    cwd: str | None = None,
) -> dict[str, Any]:
    """Append a command execution record."""
    manifest = load_manifest(manifest_path)
    entry = {
        "command": command,
        "exit_code": exit_code,
        "recorded_at": now_iso(),
    }
    if category is not None:
        entry["category"] = category
    if cwd is not None:
        entry["cwd"] = cwd
    manifest.setdefault("commands_run", []).append(entry)
    manifest["last_updated_at"] = now_iso()
    write_json_file(manifest_path, manifest)
    return entry


def print_result(payload: dict[str, Any], as_json: bool) -> None:
    """Render a result payload."""
    if as_json:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return
    print(payload)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--manifest", type=Path, required=True)
    init_parser.add_argument("--workflow-path")
    init_parser.add_argument("--task-summary")
    init_parser.add_argument("--session-id")
    init_parser.add_argument("--capability-matrix-file", type=Path)
    init_parser.add_argument("--state-file", type=Path)
    init_parser.add_argument("--json", action="store_true")

    approval_parser = subparsers.add_parser("record-approval")
    approval_parser.add_argument("--manifest", type=Path, required=True)
    approval_parser.add_argument(
        "--kind", choices=["requirements", "plan"], required=True
    )
    approval_parser.add_argument("--content")
    approval_parser.add_argument("--content-file", type=Path)
    approval_parser.add_argument("--note")
    approval_parser.add_argument("--state-file", type=Path)
    approval_parser.add_argument("--json", action="store_true")

    review_base_parser = subparsers.add_parser("set-review-base")
    review_base_parser.add_argument("--manifest", type=Path, required=True)
    review_base_parser.add_argument("--review-base-sha", required=True)
    review_base_parser.add_argument("--source")
    review_base_parser.add_argument("--base-ref")
    review_base_parser.add_argument("--state-file", type=Path)
    review_base_parser.add_argument("--json", action="store_true")

    verification_parser = subparsers.add_parser("record-verification")
    verification_parser.add_argument("--manifest", type=Path, required=True)
    verification_parser.add_argument("--phase", required=True)
    verification_parser.add_argument(
        "--status", choices=["ok", "warning", "fail"], required=True
    )
    verification_parser.add_argument("--summary-file", type=Path)
    verification_parser.add_argument("--plan-file")
    verification_parser.add_argument("--json", action="store_true")

    review_parser = subparsers.add_parser("record-review")
    review_parser.add_argument("--manifest", type=Path, required=True)
    review_parser.add_argument("--summary-file", type=Path)
    review_parser.add_argument("--redactions-file", type=Path)
    review_parser.add_argument("--reviewers-run", nargs="*")
    review_parser.add_argument("--json", action="store_true")

    command_parser = subparsers.add_parser("record-command")
    command_parser.add_argument("--manifest", type=Path, required=True)
    command_parser.add_argument("--command-text", required=True)
    command_parser.add_argument("--exit-code", type=int, required=True)
    command_parser.add_argument("--category")
    command_parser.add_argument("--cwd")
    command_parser.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        matrix = None
        if args.capability_matrix_file is not None:
            matrix = json.loads(args.capability_matrix_file.read_text())
        payload = init_manifest(
            manifest_path=args.manifest,
            workflow_path=args.workflow_path,
            task_summary=args.task_summary,
            capability_matrix=matrix,
            session_id=args.session_id,
            state_path=args.state_file,
        )
        print_result(payload, args.json)
        return 0

    if args.command == "record-approval":
        payload = record_approval(
            manifest_path=args.manifest,
            kind=args.kind,
            content=args.content,
            content_file=args.content_file,
            note=args.note,
            state_path=args.state_file,
        )
        print_result(payload, args.json)
        return 0

    if args.command == "set-review-base":
        payload = set_review_base(
            manifest_path=args.manifest,
            review_base_sha=args.review_base_sha,
            source=args.source,
            base_ref=args.base_ref,
            state_path=args.state_file,
        )
        print_result(payload, args.json)
        return 0

    if args.command == "record-verification":
        payload = record_verification(
            manifest_path=args.manifest,
            phase=args.phase,
            status=args.status,
            summary_file=args.summary_file,
            plan_file=args.plan_file,
        )
        print_result(payload, args.json)
        return 0

    if args.command == "record-review":
        payload = record_review(
            manifest_path=args.manifest,
            summary_file=args.summary_file,
            redactions_file=args.redactions_file,
            reviewers_run=args.reviewers_run,
        )
        print_result(payload, args.json)
        return 0

    if args.command == "record-command":
        payload = record_command(
            manifest_path=args.manifest,
            command=args.command_text,
            exit_code=args.exit_code,
            category=args.category,
            cwd=args.cwd,
        )
        print_result(payload, args.json)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
