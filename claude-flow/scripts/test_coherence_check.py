"""Tests for the mid-plan coherence check (Phase 5, claude-flow).

Coverage:
  - POSITIVE (surface verdict): a discovery that invalidates a remaining step
    triggers "surface", not "continue". This is the regression-detection
    direction — if the check stops returning "surface" when it should, these
    tests fail.
  - NEGATIVE (continue verdict): when nothing invalidates the remaining steps,
    the check returns "continue". These tests fail if the parser misclassifies
    clean output as an escalation.

Invariants protected (what these tests guard):
  P1. A discovery that changes a remaining step's preconditions routes to
      "surface", not "continue" — the check cannot silently proceed past a
      plan-invalidating discovery.
  P2. A clean check (no invalidating discovery) routes to "continue", not
      "surface" — the check does not introduce spurious round-trips to the
      user on noise.
  P3. The spec in phase-5-implementation.md contains all required structural
      phrases — a future edit that removes the scope guard, verdict keywords,
      or routing branches will be caught here before it ships.
  P4. Coherence check events are recorded in the run manifest with the correct
      event type and step metadata.

Why both directions matter: a test that only checks "surface fires" or only
checks "continue fires" is a snapshot — it cannot detect a regressed parser
that always returns one verdict regardless of input. Both must be covered.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from coherence_check import parse_verdict, record_coherence_check, validate_spec
from run_manifest import init_manifest, load_manifest


# ---------------------------------------------------------------------------
# Fixtures — synthetic agent responses
# ---------------------------------------------------------------------------

# Invariant P1: discovery invalidates a remaining step → verdict must be "surface"
SURFACE_FIXTURE = """\
PLAN COHERENCE CHECK — pause before step 4 of 6.

1. COMPLETED: Steps 1, 2, 3 are done with passing tests.

2. INVALIDATED: Step 4 (add tenancy migration) assumed the `tenancies` table
   did not yet exist. During Step 3 we discovered the table was created by a
   seed migration in 2026-05-01. The precondition for Step 4 is violated: the
   migration would fail with "table already exists". The remaining approach for
   Step 4 needs to change.

3. VERDICT: "surface" — Step 4's precondition was invalidated by a discovery
   in Step 3. Stopping for user input before proceeding.
"""

# Invariant P2: no invalidating discovery → verdict must be "continue"
CONTINUE_FIXTURE = """\
PLAN COHERENCE CHECK — pause before step 4 of 6.

1. COMPLETED: Steps 1, 2, 3 are done with passing tests.

2. INVALIDATED: none. No discoveries in Steps 1-3 changed the preconditions
   or approach for any remaining step. All remaining steps are still valid
   as written.

3. VERDICT: "continue" — remaining steps are still valid; proceeding to Step 4.
"""

# Edge case: bare verdict keyword without the VERDICT label (agent formatting
# variation) — should still parse correctly
BARE_CONTINUE_FIXTURE = """\
Steps 1-3 complete. Nothing changed. All remaining steps still valid.

continue
"""

BARE_SURFACE_FIXTURE = """\
Step 5 assumed Redis was available, but Step 3 revealed the staging env has
no Redis instance. Step 5 cannot proceed without a major rethink.

surface
"""

# Ambiguous fixture: both verdict keywords on the VERDICT line — "surface" should win
# (conservative). This tests the tie-breaking rule when an agent hedges on a
# single line: "initially seemed like 'continue' but actually 'surface'".
AMBIGUOUS_FIXTURE = """\
3. VERDICT: "surface" — though the check initially suggested "continue", the
   discovery in Step 3 does invalidate Step 4's precondition.
"""

# Unknown fixture: no verdict keyword at all
UNKNOWN_FIXTURE = """\
The plan steps are proceeding normally. Everything looks fine. No issues.
No verdict keyword present.
"""


# ---------------------------------------------------------------------------
# P1 — surface verdict (positive direction)
# ---------------------------------------------------------------------------


def test_surface_verdict_on_invalidating_discovery():
    """Invariant P1: a plan-invalidating discovery routes to 'surface'."""
    result = parse_verdict(SURFACE_FIXTURE)

    assert result["verdict"] == "surface", (
        f"Expected 'surface' but got {result['verdict']!r}. "
        "Regression: the coherence check no longer surfaces plan-invalidating "
        "discoveries to the user."
    )


def test_surface_verdict_captures_invalidated_section():
    """Invariant P1 detail: the INVALIDATED answer is extracted for logging."""
    result = parse_verdict(SURFACE_FIXTURE)

    assert result["invalidated"] is not None
    assert "Step 4" in result["invalidated"]


def test_bare_surface_keyword_is_detected():
    """Invariant P1: a bare 'surface' line without the VERDICT label parses correctly."""
    result = parse_verdict(BARE_SURFACE_FIXTURE)

    assert result["verdict"] == "surface"


def test_ambiguous_output_resolves_surface_conservatively():
    """Invariant P1: when both keywords appear, 'surface' wins (conservative escalation)."""
    result = parse_verdict(AMBIGUOUS_FIXTURE)

    assert result["verdict"] == "surface", (
        "When both 'continue' and 'surface' appear, 'surface' must win to "
        "prevent silent pass-through of ambiguous output."
    )


# ---------------------------------------------------------------------------
# P2 — continue verdict (negative direction)
# ---------------------------------------------------------------------------


def test_continue_verdict_on_clean_check():
    """Invariant P2: a clean check with no invalidation routes to 'continue'."""
    result = parse_verdict(CONTINUE_FIXTURE)

    assert result["verdict"] == "continue", (
        f"Expected 'continue' but got {result['verdict']!r}. "
        "Regression: the coherence check is over-triggering 'surface' on "
        "clean output, causing spurious user interruptions."
    )


def test_continue_verdict_invalidated_section_is_none_or_none_text():
    """Invariant P2 detail: 'none' answer in INVALIDATED section doesn't escalate."""
    result = parse_verdict(CONTINUE_FIXTURE)

    assert result["verdict"] == "continue"
    # Parser may return None or the "none." text — both are acceptable for continue
    if result["invalidated"] is not None:
        assert result["invalidated"].lower().startswith("none")


def test_bare_continue_keyword_is_detected():
    """Invariant P2: a bare 'continue' line without the VERDICT label parses correctly."""
    result = parse_verdict(BARE_CONTINUE_FIXTURE)

    assert result["verdict"] == "continue"


def test_unknown_verdict_on_missing_keyword():
    """Invariant: output with no verdict keyword returns 'unknown', not a false positive."""
    result = parse_verdict(UNKNOWN_FIXTURE)

    assert result["verdict"] == "unknown", (
        "Output with no verdict keyword must not silently pass as 'continue'. "
        "The caller should treat 'unknown' as an incomplete check."
    )


# ---------------------------------------------------------------------------
# P3 — spec integrity
# ---------------------------------------------------------------------------


def test_phase5_spec_contains_all_required_coherence_check_phrases():
    """Invariant P3: phase-5-implementation.md has not lost any required phrases.

    A future edit that removes the scope guard, verdict keywords, routing
    branches, or trigger condition will be caught here before it ships.
    """
    phase5_path = (
        Path(__file__).resolve().parents[1]
        / "phases"
        / "phase-5-implementation.md"
    )
    assert phase5_path.exists(), f"Phase 5 doc not found at {phase5_path}"

    violations = validate_spec(phase5_path.read_text())

    assert violations == [], (
        "Coherence check spec integrity check failed. "
        "Required phrases missing from phase-5-implementation.md:\n"
        + "\n".join(f"  - {v}" for v in violations)
    )


# ---------------------------------------------------------------------------
# P4 — manifest recording
# ---------------------------------------------------------------------------


def test_surface_event_recorded_in_manifest(tmp_path: Path):
    """Invariant P4: a 'surface' result writes a coherence_check_surface event."""
    manifest_path = tmp_path / "runs" / "session.json"
    init_manifest(manifest_path=manifest_path)

    result = parse_verdict(SURFACE_FIXTURE)
    record_coherence_check(
        manifest_path=manifest_path,
        step_index=3,
        total_steps=6,
        result=result,
    )

    event_log_path = manifest_path.with_name("session.events.jsonl")
    assert event_log_path.exists()
    events = [json.loads(line) for line in event_log_path.read_text().splitlines()]
    assert len(events) == 1
    ev = events[0]
    assert ev["type"] == "coherence_check_surface"
    assert ev["payload"]["verdict"] == "surface"
    assert ev["payload"]["step_index"] == 3
    assert ev["payload"]["total_steps"] == 6


def test_continue_event_recorded_in_manifest(tmp_path: Path):
    """Invariant P4: a 'continue' result writes a coherence_check_continue event."""
    manifest_path = tmp_path / "runs" / "session.json"
    init_manifest(manifest_path=manifest_path)

    result = parse_verdict(CONTINUE_FIXTURE)
    record_coherence_check(
        manifest_path=manifest_path,
        step_index=3,
        total_steps=6,
        result=result,
    )

    event_log_path = manifest_path.with_name("session.events.jsonl")
    events = [json.loads(line) for line in event_log_path.read_text().splitlines()]
    assert len(events) == 1
    ev = events[0]
    assert ev["type"] == "coherence_check_continue"
    assert ev["payload"]["verdict"] == "continue"
    assert ev["payload"]["step_index"] == 3


def test_surface_and_continue_events_are_distinct_types(tmp_path: Path):
    """Invariant P4: surface and continue are logged as different event types.

    If both were logged as the same type, the manifest event log could not be
    used to distinguish escalations from clean checks in post-hoc analysis.
    """
    manifest_path = tmp_path / "runs" / "session.json"
    init_manifest(manifest_path=manifest_path)

    record_coherence_check(
        manifest_path=manifest_path,
        step_index=3,
        total_steps=6,
        result=parse_verdict(SURFACE_FIXTURE),
    )
    record_coherence_check(
        manifest_path=manifest_path,
        step_index=6,
        total_steps=6,
        result=parse_verdict(CONTINUE_FIXTURE),
    )

    event_log_path = manifest_path.with_name("session.events.jsonl")
    events = [json.loads(line) for line in event_log_path.read_text().splitlines()]
    assert len(events) == 2
    types = {ev["type"] for ev in events}
    assert "coherence_check_surface" in types
    assert "coherence_check_continue" in types
    assert len(types) == 2, "Surface and continue must be logged as distinct event types."
