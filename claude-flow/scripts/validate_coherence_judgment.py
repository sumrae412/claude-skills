#!/usr/bin/env python3
"""One-time model-in-the-loop validation for the Phase 5 mid-plan coherence check.

PURPOSE
-------
This is a throwaway validation script — NOT wired into CI, NOT a standing eval
harness, NOT a nightly. Run it by hand, once, with an API key in env, to close
§Risks#4 of docs/decisions/2026-06-26-goap-resume-replanning-spike.md.

§Risks#4 (paraphrased): "No test coverage for mid-plan pivots. We can't verify
the coherence check helps without evals."

This script proves the Phase 5 coherence-check PROMPT works for its two critical
behaviors:
  - POSITIVE (surface): model faces a plan-invalidating discovery and emits "surface"
  - NEGATIVE (continue): model faces a clean plan state and emits "continue"

USAGE
-----
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 claude-flow/scripts/validate_coherence_judgment.py

    # Optional overrides:
    python3 claude-flow/scripts/validate_coherence_judgment.py \\
        --samples 10 \\
        --model claude-sonnet-4-6 \\
        --output /tmp/coherence_validation_results.json

MODEL PINNING
-------------
The model is pinned to a published snapshot string to prevent alias-rotation
from silently shifting pass-rate semantics between runs. The default is Sonnet
(the model that actually executes Phase 5) for fidelity. Haiku is acceptable
if cost is a concern — pass --model claude-haiku-4-5-20251022.

Default model updated 2026-06-29: claude-sonnet-4-5-20251022 → claude-sonnet-4-6
(prior pin 404'd on live API; sonnet-4-6 is the current valid snapshot).

ANTI-PATTERN GUARD
------------------
Never adjust fixtures to make the model look good. If surface-recall is low,
that is a genuine finding about the coherence-check PROMPT — see the notes
block at the bottom of each run for remediation guidance.

FIXTURES
--------
4 fixtures: 2 positive (expect "surface"), 2 negative (expect "continue").

Positive fixtures embed a discovery that invalidates a remaining step.
Negative fixtures are clean — no discovery changed anything.

Each fixture is injected into the EXACT Phase 5 coherence-check prompt
(copied verbatim from phase-5-implementation.md § "Mid-Plan Coherence Check").
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Model pin — change only when a newer snapshot is published and you want to
# document that this validation ran against it.
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# The EXACT coherence-check prompt from Phase 5, lines 163-179 of
# phase-5-implementation.md (as of PR #182 / commit 79c1f44).
# Injected verbatim so this script tests the real prompt, not a paraphrase.
# ---------------------------------------------------------------------------

COHERENCE_CHECK_PROMPT_TEMPLATE = """\
PLAN COHERENCE CHECK — pause before step {next_step} of {total_steps}.

Answer three questions based only on what has been built and discovered so far:

1. COMPLETED: Which steps are done with passing tests?
   (List step numbers only.)

2. INVALIDATED: Has anything discovered or built since the plan was written
   changed the preconditions or approach for any REMAINING step?
   (If yes, name the step and what changed. If no, say "none".)

3. VERDICT:
   - "continue" — remaining steps are still valid as written; proceed.
   - "surface" — a discovery invalidates at least one remaining step;
     describe it and stop for user input before proceeding.

---

CURRENT STATE:
{plan_and_state}
"""

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@dataclass
class Fixture:
    id: str
    description: str
    expected_verdict: str  # "surface" | "continue"
    plan_and_state: str
    next_step: int
    total_steps: int


FIXTURES: list[Fixture] = [
    # ------------------------------------------------------------------
    # POSITIVE fixtures — a plan-invalidating discovery exists.
    # The model should emit "surface".
    # ------------------------------------------------------------------
    Fixture(
        id="pos-1-schema-mismatch",
        description="Step 3 (add payment endpoint) depends on a payments table "
                    "that does not exist — discovered during step 2 migration",
        expected_verdict="surface",
        next_step=3,
        total_steps=5,
        plan_and_state=textwrap.dedent("""\
            PLAN (approved before implementation):
            Step 1: Add User model + migration  [DONE — tests pass]
            Step 2: Add Tenancy model + migration  [DONE — tests pass]
            Step 3: Add POST /payments endpoint (writes to payments table)
            Step 4: Add GET /payments/:id endpoint
            Step 5: Wire Stripe webhook handler

            WHAT HAPPENED DURING IMPLEMENTATION:
            - Step 1 complete. User model, users table, 3 tests pass.
            - Step 2 complete. Tenancy model, tenancies table, 5 tests pass.
            - DISCOVERY during step 2: the Phase 2 schema exploration missed a
              constraint. The DB is multi-tenant and the payments table does NOT
              exist — it lives in a separate billing microservice accessed only
              via a REST client, not via ORM. Writing POST /payments directly to
              a local payments table (step 3) is architecturally wrong. The
              approved plan assumes local ORM access that does not exist.
        """),
    ),
    Fixture(
        id="pos-2-auth-constraint",
        description="Step 4 (admin-only bulk delete) requires a permission bit "
                    "that does not exist — discovered when writing step 3 auth middleware",
        expected_verdict="surface",
        next_step=4,
        total_steps=6,
        plan_and_state=textwrap.dedent("""\
            PLAN (approved before implementation):
            Step 1: Add role enum to User model  [DONE — tests pass]
            Step 2: Add require_login middleware  [DONE — tests pass]
            Step 3: Add require_admin middleware  [DONE — tests pass]
            Step 4: Add DELETE /admin/bulk-delete endpoint (requires admin + owner_id match)
            Step 5: Add audit log entry on bulk delete
            Step 6: Add rate-limit decorator to bulk delete

            WHAT HAPPENED DURING IMPLEMENTATION:
            - Steps 1-3 complete and tests pass.
            - DISCOVERY while implementing require_admin (step 3): the role enum
              only has ROLES = ('viewer', 'editor'). There is no 'admin' or 'owner'
              role. The codebase uses a separate ACL table (acl_grants) to gate
              destructive operations, not a role column. The approved plan's step 4
              assumes a role-based admin check that does not match the actual
              permission model. Steps 4-6 need redesign to use acl_grants.
        """),
    ),

    # ------------------------------------------------------------------
    # NEGATIVE fixtures — clean state, no discoveries invalidate anything.
    # The model should emit "continue".
    # ------------------------------------------------------------------
    Fixture(
        id="neg-1-clean-progress",
        description="3 of 5 steps done with passing tests, no discoveries, "
                    "remaining steps still valid as written",
        expected_verdict="continue",
        next_step=4,
        total_steps=5,
        plan_and_state=textwrap.dedent("""\
            PLAN (approved before implementation):
            Step 1: Add Property model + migration  [DONE — tests pass]
            Step 2: Add Unit model + migration  [DONE — tests pass]
            Step 3: Add POST /properties endpoint  [DONE — tests pass]
            Step 4: Add GET /properties/:id endpoint
            Step 5: Add PATCH /properties/:id endpoint

            WHAT HAPPENED DURING IMPLEMENTATION:
            - Step 1: Property model added, migration applied. 4 tests pass.
            - Step 2: Unit model added with FK to Property. Migration applied. 6 tests pass.
            - Step 3: POST /properties endpoint added. Validates required fields,
              returns 201 with created resource. 5 tests pass including edge cases
              for missing fields and duplicate slug.
            - No new schema constraints discovered. The DB schema matches
              Phase 2 exploration exactly. Steps 4 and 5 still align with the
              approved architecture — same model, same ORM patterns, same
              validation approach established in step 3.
        """),
    ),
    Fixture(
        id="neg-2-minor-fix-not-invalidating",
        description="A type-error fix in step 2 looked like a bigger issue "
                    "but turned out local — remaining steps are still valid",
        expected_verdict="continue",
        next_step=3,
        total_steps=4,
        plan_and_state=textwrap.dedent("""\
            PLAN (approved before implementation):
            Step 1: Add Lease model + migration  [DONE — tests pass]
            Step 2: Add LeaseService.create() method  [DONE — tests pass]
            Step 3: Add POST /leases endpoint calling LeaseService.create()
            Step 4: Add email notification on lease creation

            WHAT HAPPENED DURING IMPLEMENTATION:
            - Step 1: Lease model, leases table. 3 tests pass.
            - Step 2: LeaseService.create() implemented. During implementation,
              a mypy error surfaced: start_date was typed as str but the ORM
              field is datetime. Fixed with a one-line dateutil.parser.parse()
              call. This was a local type-error fix — it did not change the
              method signature, the return type, or any downstream contract.
              8 tests pass including the type-corrected paths.
            - The type fix does NOT invalidate step 3 or step 4. The endpoint
              in step 3 will pass an ISO string from the request body, which
              the now-corrected service handles correctly. The email notification
              in step 4 depends only on the Lease object returned by create(),
              which is unchanged.
        """),
    ),
]


# ---------------------------------------------------------------------------
# Parser (reuse the deterministic parser from coherence_check.py)
# ---------------------------------------------------------------------------

def _import_coherence_check_module():
    """Import coherence_check.py from the same scripts directory."""
    scripts_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(scripts_dir))
    import coherence_check  # noqa: PLC0415
    return coherence_check


# ---------------------------------------------------------------------------
# Model call
# ---------------------------------------------------------------------------

def call_model(client, model: str, prompt: str) -> str:
    """Call the Anthropic API and return the assistant text."""
    response = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# ---------------------------------------------------------------------------
# Run validation
# ---------------------------------------------------------------------------

@dataclass
class FixtureResult:
    fixture_id: str
    expected: str
    samples: list[str] = field(default_factory=list)   # raw verdicts
    pass_count: int = 0
    pass_rate: float = 0.0
    passed: bool = False


def run_validation(
    client,
    model: str,
    n_samples: int,
    coherence_check,
) -> list[FixtureResult]:
    results = []

    for fixture in FIXTURES:
        print(f"\n[{fixture.id}] expected={fixture.expected_verdict}", flush=True)
        prompt = COHERENCE_CHECK_PROMPT_TEMPLATE.format(
            next_step=fixture.next_step,
            total_steps=fixture.total_steps,
            plan_and_state=fixture.plan_and_state,
        )

        fr = FixtureResult(fixture_id=fixture.id, expected=fixture.expected_verdict)

        for i in range(n_samples):
            raw = call_model(client, model, prompt)
            parsed = coherence_check.parse_verdict(raw)
            verdict = parsed["verdict"]
            fr.samples.append(verdict)
            hit = (verdict == fixture.expected_verdict)
            if hit:
                fr.pass_count += 1
            print(
                f"  sample {i+1}/{n_samples}: {verdict} {'OK' if hit else 'MISS'}"
                f"{' | invalidated: ' + parsed['invalidated'][:80] if parsed.get('invalidated') else ''}",
                flush=True,
            )
            # Polite rate limit
            if i < n_samples - 1:
                time.sleep(0.5)

        fr.pass_rate = fr.pass_count / n_samples
        # Pass threshold: >=2/3 of samples correct (67%) for N=3; scales for higher N
        threshold = 2 / 3
        fr.passed = fr.pass_rate >= threshold
        print(f"  -> pass_rate={fr.pass_rate:.2f} ({'PASS' if fr.passed else 'FAIL'})", flush=True)
        results.append(fr)

    return results


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def build_report(
    results: list[FixtureResult],
    model: str,
    n_samples: int,
) -> dict[str, Any]:
    positive = [r for r in results if r.expected == "surface"]
    negative = [r for r in results if r.expected == "continue"]

    def direction_stats(group: list[FixtureResult]) -> dict[str, Any]:
        if not group:
            return {"fixture_count": 0, "avg_pass_rate": None, "all_passed": False}
        avg = sum(r.pass_rate for r in group) / len(group)
        return {
            "fixture_count": len(group),
            "avg_pass_rate": round(avg, 3),
            "all_passed": all(r.passed for r in group),
        }

    overall_pass_rate = sum(r.pass_rate for r in results) / len(results)
    overall_passed = all(r.passed for r in results)

    per_fixture = [
        {
            "fixture_id": r.fixture_id,
            "expected": r.expected,
            "samples": r.samples,
            "pass_rate": round(r.pass_rate, 3),
            "passed": r.passed,
        }
        for r in results
    ]

    verdict_str: str
    caveat: str | None = None

    surface_stats = direction_stats(positive)
    continue_stats = direction_stats(negative)

    if overall_passed:
        if surface_stats["avg_pass_rate"] == 1.0 and continue_stats["avg_pass_rate"] == 1.0:
            verdict_str = "resolved"
        else:
            verdict_str = "resolved-with-caveat"
            caveat = (
                f"surface-recall={surface_stats['avg_pass_rate']:.2f}, "
                f"continue-precision={continue_stats['avg_pass_rate']:.2f} — "
                "one or both directions below 100% but above pass threshold (0.67)."
            )
    else:
        # Which direction failed?
        surface_ok = surface_stats["all_passed"]
        continue_ok = continue_stats["all_passed"]
        if not surface_ok:
            verdict_str = "detection-weakness-found"
            caveat = (
                f"surface-recall={surface_stats['avg_pass_rate']:.2f} — "
                "model fails to emit 'surface' on plan-invalidating discoveries. "
                "The coherence-check PROMPT likely needs stronger language "
                "distinguishing plan-invalidating changes from local fixes. "
                "Do NOT adjust fixtures. Tune the prompt text in "
                "phase-5-implementation.md § 'Mid-Plan Coherence Check'."
            )
        else:
            verdict_str = "detection-weakness-found"
            caveat = (
                f"continue-precision={continue_stats['avg_pass_rate']:.2f} — "
                "model emits 'surface' on clean state (false positives). "
                "Coherence-check prompt may be too aggressive; consider "
                "sharpening the 'local fixes stay local' scope guard language."
            )

    return {
        "meta": {
            "model": model,
            "n_samples_per_fixture": n_samples,
            "fixture_count": len(results),
            "date": __import__("datetime").date.today().isoformat(),
        },
        "summary": {
            "overall_pass_rate": round(overall_pass_rate, 3),
            "overall_passed": overall_passed,
            "positive_direction": surface_stats,
            "negative_direction": continue_stats,
            "verdict": verdict_str,
            "caveat": caveat,
        },
        "per_fixture": per_fixture,
    }


def print_summary(report: dict[str, Any]) -> None:
    s = report["summary"]
    m = report["meta"]
    print("\n" + "=" * 60)
    print("COHERENCE JUDGMENT VALIDATION — SUMMARY")
    print("=" * 60)
    print(f"Model:           {m['model']}")
    print(f"Date:            {m['date']}")
    print(f"Fixtures:        {m['fixture_count']} ({m['n_samples_per_fixture']} samples each)")
    print(f"Overall pass:    {s['overall_pass_rate']:.0%} ({'PASS' if s['overall_passed'] else 'FAIL'})")
    print(f"  surface-recall:    {s['positive_direction']['avg_pass_rate']:.0%}")
    print(f"  continue-prec:     {s['negative_direction']['avg_pass_rate']:.0%}")
    print(f"Verdict:         {s['verdict']}")
    if s["caveat"]:
        print(f"Caveat:          {s['caveat']}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=10,
        help="Number of model samples per fixture (default: 10)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Pinned snapshot string (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON results to this path (optional)",
    )
    args = parser.parse_args(argv)

    # ------------------------------------------------------------------
    # Gate: check for API key FIRST. Do NOT fabricate results.
    # ------------------------------------------------------------------
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print(
            "ERROR: ANTHROPIC_API_KEY is not set.\n"
            "\n"
            "This script requires a live API key. Set it with:\n"
            "    export ANTHROPIC_API_KEY=sk-ant-...\n"
            "\n"
            "The validation script is built and ready — it just cannot run\n"
            "without the key. Results have NOT been fabricated.\n",
            file=sys.stderr,
        )
        return 2  # distinct exit code for 'blocked on key'

    # ------------------------------------------------------------------
    # Import SDK
    # ------------------------------------------------------------------
    try:
        import anthropic  # noqa: PLC0415
    except ImportError:
        print(
            "ERROR: anthropic SDK not installed.\n"
            "    pip install anthropic\n",
            file=sys.stderr,
        )
        return 1

    client = anthropic.Anthropic(api_key=api_key)

    # ------------------------------------------------------------------
    # Import deterministic parser
    # ------------------------------------------------------------------
    try:
        coherence_check = _import_coherence_check_module()
    except ImportError as exc:
        print(f"ERROR: could not import coherence_check.py: {exc}", file=sys.stderr)
        return 1

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------
    print(f"Running coherence judgment validation")
    print(f"  model:   {args.model}")
    print(f"  samples: {args.samples} per fixture")
    print(f"  fixtures: {len(FIXTURES)}")

    results = run_validation(
        client=client,
        model=args.model,
        n_samples=args.samples,
        coherence_check=coherence_check,
    )

    report = build_report(results, model=args.model, n_samples=args.samples)
    print_summary(report)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2))
        print(f"\nResults written to: {args.output}")

    # Exit 0 = passed, 1 = failed/weakness-found, 2 = blocked
    return 0 if report["summary"]["overall_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
