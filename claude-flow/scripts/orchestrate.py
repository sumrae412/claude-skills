#!/usr/bin/env python3
"""Compose helper scripts with manifest recording in a single call.

Each subcommand fuses an existing helper-script invocation with the
corresponding ``run_manifest`` record so phase docs stay terse and a live
claude-flow run can populate the manifest without manual JSON plumbing.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import resolve_review_base
import run_manifest
import scrub_review_payload

SCRIPTS_DIR = Path(__file__).resolve().parent


def discover_manifest_path(
    project_root: Path,
    explicit: Path | None,
) -> Path:
    """Return the manifest path, resolved from CLI arg or workflow state."""
    if explicit is not None:
        return explicit
    state_path = project_root / ".claude" / "workflow-state.json"
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text())
        except (OSError, json.JSONDecodeError):
            state = {}
        manifest_path = state.get("run_manifest_path")
        if isinstance(manifest_path, str) and manifest_path:
            return Path(manifest_path)
    raise SystemExit(
        "No --manifest provided and no run_manifest_path found in "
        ".claude/workflow-state.json. Initialize the manifest with "
        "`run_manifest.py init` first or pass --manifest explicitly."
    )


def discover_state_path(
    project_root: Path,
    explicit: Path | None,
) -> Path | None:
    """Return the workflow-state path when one is available."""
    if explicit is not None:
        return explicit
    candidate = project_root / ".claude" / "workflow-state.json"
    return candidate if candidate.exists() else None


def status_from_summary(summary: dict[str, Any]) -> str:
    """Map a verify_plan summary block to a manifest status."""
    counts = summary.get("summary", {})
    if counts.get("missing", 0) or counts.get("errors", 0):
        return "fail"
    if counts.get("warnings", 0):
        return "warning"
    return "ok"


def run_verify_plan(
    plan_file: str,
    project_root: Path,
    plan_text: str | None = None,
) -> tuple[dict[str, Any], int]:
    """Run verify_plan.py as a subprocess and return parsed JSON + exit code."""
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "verify_plan.py"),
        plan_file,
        "--project-root",
        str(project_root),
        "--json",
    ]
    completed = subprocess.run(
        cmd,
        input=plan_text if plan_file == "-" else None,
        capture_output=True,
        text=True,
    )
    stdout = completed.stdout.strip()
    if not stdout:
        raise SystemExit(
            f"verify_plan.py emitted no JSON (stderr: {completed.stderr.strip()})"
        )
    summary = json.loads(stdout)
    return summary, completed.returncode


def cmd_verify_plan(args: argparse.Namespace) -> int:
    """Verify a plan file and append the result to the manifest."""
    project_root = args.project_root.resolve()
    manifest_path = discover_manifest_path(project_root, args.manifest)

    plan_text = None
    if args.plan_file == "-":
        plan_text = sys.stdin.read()
    summary, exit_code = run_verify_plan(args.plan_file, project_root, plan_text)

    status = status_from_summary(summary)
    plan_label = args.plan_file if args.plan_file != "-" else "<stdin>"
    run_manifest.record_verification(
        manifest_path=manifest_path,
        phase=args.phase,
        status=status,
        summary=summary,
        plan_file=plan_label,
    )

    if args.json:
        json.dump(
            {
                "manifest": str(manifest_path),
                "status": status,
                "exit_code": exit_code,
                "summary": summary.get("summary", {}),
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        counts = summary.get("summary", {})
        print(
            f"verify-plan: status={status} ok={counts.get('ok', 0)} "
            f"missing={counts.get('missing', 0)} warnings={counts.get('warnings', 0)}"
        )
    return exit_code


def cmd_resolve_review_base(args: argparse.Namespace) -> int:
    """Resolve the review base and persist it to the manifest."""
    project_root = args.project_root.resolve()
    manifest_path = discover_manifest_path(project_root, args.manifest)
    state_path = discover_state_path(project_root, args.state_file)

    result = resolve_review_base.resolve_review_base(project_root)
    run_manifest.set_review_base(
        manifest_path=manifest_path,
        review_base_sha=result["review_base_sha"],
        source=result.get("source"),
        base_ref=result.get("base_ref"),
        state_path=state_path,
    )

    if args.json:
        json.dump(
            {"manifest": str(manifest_path), **result},
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        print(
            f"review-base: {result['review_base_sha']} "
            f"(source={result.get('source')}, ref={result.get('base_ref')})"
        )
    return 0


def cmd_scrub_diff(args: argparse.Namespace) -> int:
    """Scrub a diff payload and emit scrubbed text plus redactions JSON."""
    if args.input_file is not None:
        text = Path(args.input_file).read_text()
    else:
        text = sys.stdin.read()
    if not text:
        print("No review payload provided", file=sys.stderr)
        return 2

    scrubbed, redactions = scrub_review_payload.scrub_text(text)
    redaction_count = sum(int(item["count"]) for item in redactions)
    redaction_summary = {
        "redaction_count": redaction_count,
        "redactions": redactions,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(scrubbed)

    redactions_path = (
        Path(args.redactions_output)
        if args.redactions_output is not None
        else out_path.with_suffix(out_path.suffix + ".redactions.json")
    )
    redactions_path.parent.mkdir(parents=True, exist_ok=True)
    redactions_path.write_text(json.dumps(redaction_summary, indent=2) + "\n")

    if args.json:
        json.dump(
            {
                "scrubbed_path": str(out_path),
                "redactions_path": str(redactions_path),
                "redaction_count": redaction_count,
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        print(
            f"scrub-diff: redactions={redaction_count} "
            f"output={out_path} redactions_file={redactions_path}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the orchestrate CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser(
        "verify-plan",
        help="Run verify_plan.py and append the result to the manifest.",
    )
    verify.add_argument("plan_file", help="Plan markdown path or '-' for stdin")
    verify.add_argument("--manifest", type=Path)
    verify.add_argument("--project-root", type=Path, default=Path.cwd())
    verify.add_argument("--phase", default="phase-4c")
    verify.add_argument("--json", action="store_true")
    verify.set_defaults(func=cmd_verify_plan)

    review_base = subparsers.add_parser(
        "resolve-review-base",
        help="Resolve the diff base and persist it to the manifest.",
    )
    review_base.add_argument("--manifest", type=Path)
    review_base.add_argument("--project-root", type=Path, default=Path.cwd())
    review_base.add_argument("--state-file", type=Path)
    review_base.add_argument("--json", action="store_true")
    review_base.set_defaults(func=cmd_resolve_review_base)

    scrub = subparsers.add_parser(
        "scrub-diff",
        help="Scrub a diff payload and emit scrubbed text plus redactions JSON.",
    )
    scrub.add_argument(
        "input_file",
        nargs="?",
        help="Optional diff file path. Defaults to stdin.",
    )
    scrub.add_argument(
        "--output",
        required=True,
        help="Path for the scrubbed diff text.",
    )
    scrub.add_argument(
        "--redactions-output",
        help="Path for the redactions JSON. Defaults to <output>.redactions.json.",
    )
    scrub.add_argument("--json", action="store_true")
    scrub.set_defaults(func=cmd_scrub_diff)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
