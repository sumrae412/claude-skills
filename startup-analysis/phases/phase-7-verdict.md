# Phase 7: Verdict

## Goal

Close with a hard recommendation, a 6-axis scorecard, and explicit
validation gates. Consumes:
- Phase 5.5 stress-test scorecard (six-pillar breakdown, green/red flags,
  top recommendations) as structured decision support
- Phase 6 debate-team output as required evidence — do not issue a
  verdict without Phase 6's Pass/Hold calls

## Halting Rules (override the scorecard)

Issue an immediate **No-Go** — regardless of point total — if Phase 6
tripped any halting rule:

- Researcher Hold (no verbatim pain language)
- Strategist Hold after two attempts (no offer the customer would pay
  $50-$100 for)
- Marketer Hold on math (visitor → MRR math cannot reach target)

These are structural failures, not scoring nuances.

## Check the verdict against the pre-registered kill number

Phase 0 recorded the result that would make this a No-Go. Restate it, put
the observed result beside it, and say plainly whether it was crossed.

| Pre-registered kill number | Observed | Crossed? |
|---|---|---|
| e.g. median WTP under $15/mo | $12/mo median | **Yes → No-Go** |

A crossed threshold overrides the point total the same way a Halting Rule
does. Do not renegotiate the number now that the data is in — that is the
failure mode pre-registration exists to prevent.

If Phase 0 recorded no kill number, label the verdict
`confirmatory — not falsified` in the Output and discount it: the analysis
tested nothing it could have failed.

## Name which constraint this verdict actually tested

Phase 0 diagnosed a binding constraint. State it, and state whether the
analysis tested it.

| Binding constraint (Phase 0) | Tested by | Result |
|---|---|---|
| e.g. Epistemic | pre-Phase-1 literature gate | Required evidence base does not exist |

**A Go verdict is only valid for the constraint it tested.** Phases 1-5
are demand-weighted; if the diagnosed constraint was Epistemic,
Feasibility, Regulatory, Distribution, or Unit cost and no gate tested it,
the verdict must read:

> **Conditional Go — demand only. The binding constraint (<class>) was not
> tested.**

Never issue a clean Go on an untested primary constraint. A strong
demand scorecard on an idea gated by whether the underlying science
exists is not evidence of viability — it is evidence that people would
buy the thing if it could be built honestly, which is a different and
much weaker claim.

If Phase 0 recorded no constraint diagnosis, run
[`../references/binding-constraint-diagnosis.md`](../references/binding-constraint-diagnosis.md)
now and label the verdict accordingly rather than issuing it blind.

## Scorecard

Required. Score each 1-5. Every score must cite evidence from earlier
phases, including Phase 6 debate-team output — no vibes.

| Area | Score | Read |
|---|---:|---|
| Pain intensity | x/5 | Phase 1 + Researcher verbatim quotes |
| Buyer clarity | x/5 | Phase 2 + Researcher pain table |
| Urgency | x/5 | Phase 1 / 2 + Researcher frequency signal |
| Differentiation | x/5 | Phase 4 + Strategist's chosen lead magnet defensibility |
| Speed to validate | x/5 | Builder estimated time-to-live + Marketer 30-day plan |
| Founder advantage | x/5 | founder-market fit |

Verdict thresholds (guideline, not rule): total <18 = No-Go, 18-23 =
Conditional Go, 24+ = Go. Override with reasoning when warranted. A
tripped Halting Rule overrides any total.

## Founder-fit cross-check

If [`references/idea-fit-scorecard.md`](../references/idea-fit-scorecard.md)
has been run for this founder/idea pair, pull its three category
sub-scores (Founder fit, Economic fit, Execution fit) in alongside the
6-axis table above. A collapsed sub-score there (e.g. Economic fit
failing the founder's target-revenue check, or Founder fit tanking on
weekly-hours mismatch) is a structural flag even when the market-fit
axes score well — surface it explicitly rather than letting a strong
blended market score paper over it. Not required to issue a verdict —
this skill's Halting Rules above still govern — but note in Output when
it wasn't run.

## Output

- halting-rule check (any trips? → No-Go)
- 6-axis scorecard with evidence column citing Phase 1-6
- Phase 5.5 pillar scores noted alongside the 6-axis table (cross-reference
  agreement or tension between the two scorecards)
- Go / Conditional Go / No-Go
- validation gates
- kill criteria
- what's missing
- strategist's note and rating
