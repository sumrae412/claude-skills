#!/usr/bin/env python3
"""Parse and evaluate mid-plan coherence check output from Phase 5.

The mid-plan coherence check is a prompt-level gate injected every N steps
in Phase 5 (default: every 3 steps for plans <8 steps, every 5 for plans
>=8 steps). The agent answers three structured questions and returns one of
two verdicts:

  - "continue" — remaining plan steps are still valid; proceed.
  - "surface" — a discovery invalidates at least one remaining step; stop and
    surface to the user before proceeding.

This module provides:

  parse_verdict(text) -> dict
    Extract the verdict keyword and classified output from agent-produced text.
    Returns {"verdict": "continue"|"surface"|"unknown", "summary": str,
             "invalidated": str|None}.

  validate_spec(phase5_text) -> list[str]
    Assert the structural invariants of the coherence check spec inside the
    phase-5-implementation.md doc. Returns a list of violation strings (empty
    = spec is intact).

  record_coherence_check(manifest_path, step_index, total_steps, result)
    Append a coherence check event to the run manifest event log.

Used by:
  - test_coherence_check.py (unit tests for both verdict directions)
  - run_manifest.py record-event (for manifest logging)

Phase 5 spec reference:
  claude-flow/phases/phase-5-implementation.md § "Mid-Plan Coherence Check"
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Spec invariants (strings that MUST appear in phase-5-implementation.md)
# ---------------------------------------------------------------------------

REQUIRED_SPEC_PHRASES = [
    # Verdict keywords documented
    '"continue"',
    '"surface"',
    # Both routing branches documented
    "proceed immediately to the next plan step",
    "DO NOT proceed to the next step",
    # Trigger condition documented
    "step index mod N == 0",
    # Scope guard documented
    "bounded to three questions",
    # Skipped-when condition documented
    "plan has ≤2 remaining steps",
]


# ---------------------------------------------------------------------------
# Verdict parsing
# ---------------------------------------------------------------------------

# Regex patterns for each verdict keyword. Accept variations in whitespace,
# casing, quoting, and surrounding punctuation so the parser is robust to
# minor formatting differences in agent output.
_CONTINUE_PATTERN = re.compile(
    r'\b(?:VERDICT|verdict)[^\n]*["\']?continue["\']?',
    re.IGNORECASE,
)
_SURFACE_PATTERN = re.compile(
    r'\b(?:VERDICT|verdict)[^\n]*["\']?surface["\']?',
    re.IGNORECASE,
)

# Fallback: bare keyword on its own line (agent may omit the label)
_BARE_CONTINUE = re.compile(r"^\s*[\"']?continue[\"']?\s*$", re.IGNORECASE | re.MULTILINE)
_BARE_SURFACE = re.compile(r"^\s*[\"']?surface[\"']?\s*$", re.IGNORECASE | re.MULTILINE)


def _extract_invalidated(text: str) -> str | None:
    """Return the INVALIDATED answer from agent output, or None if not found."""
    # Look for the INVALIDATED section (question 2 in the coherence check).
    # Supported label formats:
    #   "2. INVALIDATED: <answer>"   (numbered + keyword)
    #   "INVALIDATED: <answer>"      (keyword only)
    # Capture only the answer body after the label, not the label itself.
    # The `[^\S\n]*` after the colon eats horizontal whitespace (not newlines)
    # so inline answers start correctly on the same line as the label.
    match = re.search(
        r"(?:2\.\s*)?INVALIDATED:[^\S\n]*(.*?)(?=\n\s*(?:3\.|VERDICT:?)|\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()
    return None


def parse_verdict(text: str) -> dict[str, Any]:
    """Parse coherence check output from an agent response.

    Parameters
    ----------
    text:
        The raw agent output containing the coherence check answers.

    Returns
    -------
    dict with keys:
      - "verdict": "continue" | "surface" | "unknown"
      - "summary": the full input text (for logging)
      - "invalidated": the INVALIDATED answer section, or None
    """
    has_continue = bool(
        _CONTINUE_PATTERN.search(text) or _BARE_CONTINUE.search(text)
    )
    has_surface = bool(
        _SURFACE_PATTERN.search(text) or _BARE_SURFACE.search(text)
    )

    if has_surface and not has_continue:
        verdict = "surface"
    elif has_continue and not has_surface:
        verdict = "continue"
    elif has_surface and has_continue:
        # Both present — surface wins (conservative: stop and ask rather than
        # silently proceeding when the output is ambiguous)
        verdict = "surface"
    else:
        verdict = "unknown"

    return {
        "verdict": verdict,
        "summary": text,
        "invalidated": _extract_invalidated(text),
    }


# ---------------------------------------------------------------------------
# Spec validation
# ---------------------------------------------------------------------------


def validate_spec(phase5_text: str) -> list[str]:
    """Assert coherence check spec invariants in phase-5-implementation.md.

    Parameters
    ----------
    phase5_text:
        Full text of phase-5-implementation.md.

    Returns
    -------
    List of violation strings. Empty list means the spec is intact.
    """
    violations: list[str] = []
    for phrase in REQUIRED_SPEC_PHRASES:
        if phrase not in phase5_text:
            violations.append(
                f"phase-5-implementation.md: required coherence check phrase missing: {phrase!r}"
            )
    return violations


# ---------------------------------------------------------------------------
# Manifest logging
# ---------------------------------------------------------------------------


def record_coherence_check(
    manifest_path: Path,
    step_index: int,
    total_steps: int,
    result: dict[str, Any],
) -> dict[str, Any]:
    """Append a coherence-check event to the run manifest event log.

    Parameters
    ----------
    manifest_path:
        Path to the current session's run manifest JSON.
    step_index:
        1-based index of the completed step that triggered the check.
    total_steps:
        Total number of plan steps.
    result:
        Output of parse_verdict() for this check.

    Returns
    -------
    The recorded event dict.
    """
    # Import here to avoid circular import if this module is used standalone
    from run_manifest import record_event  # noqa: PLC0415

    payload = {
        "step_index": step_index,
        "total_steps": total_steps,
        "verdict": result["verdict"],
        "invalidated": result.get("invalidated"),
    }

    event_type = (
        "coherence_check_surface"
        if result["verdict"] == "surface"
        else "coherence_check_continue"
    )

    return record_event(
        manifest_path=manifest_path,
        event_type=event_type,
        category="phase-5",
        source="coherence_check",
        payload=payload,
    )


# ---------------------------------------------------------------------------
# CLI (for ad-hoc use)
# ---------------------------------------------------------------------------


def _build_parser():
    import argparse  # noqa: PLC0415

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_cmd = subparsers.add_parser(
        "parse",
        help="Parse a coherence check response from stdin or a file.",
    )
    parse_cmd.add_argument(
        "input",
        nargs="?",
        default="-",
        help="File containing agent response, or - for stdin.",
    )
    parse_cmd.add_argument("--json", action="store_true", help="Output JSON.")

    validate_cmd = subparsers.add_parser(
        "validate-spec",
        help="Validate spec invariants in phase-5-implementation.md.",
    )
    validate_cmd.add_argument(
        "--phase5-file",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "phases"
        / "phase-5-implementation.md",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    import json  # noqa: PLC0415

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "parse":
        if args.input == "-":
            text = sys.stdin.read()
        else:
            text = Path(args.input).read_text()
        result = parse_verdict(text)
        if args.json:
            import json as _json  # noqa: PLC0415

            print(_json.dumps(result, indent=2))
        else:
            print(f"verdict: {result['verdict']}")
            if result["invalidated"]:
                print(f"invalidated: {result['invalidated']}")
        return 0 if result["verdict"] != "unknown" else 1

    if args.command == "validate-spec":
        text = args.phase5_file.read_text()
        violations = validate_spec(text)
        for v in violations:
            print(v, file=sys.stderr)
        return 1 if violations else 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
