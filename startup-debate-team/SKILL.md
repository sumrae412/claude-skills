---
name: startup-debate-team
description: Five-role validation engine — Researcher, Strategist, Copywriter, Builder, Marketer — invoked by `startup-analysis` Phase 6 to produce evidence for the Go/No-Go verdict. Each role challenges the prior one and ends with Pass/Hold; structural Holds force a No-Go. Can also run standalone for "run the startup team on this idea" / "five-person AI team" requests, but the canonical entry point is `startup-analysis`.
---

# Startup Debate Team

## Token Economy

Load only the role file you are currently running. Do not pre-load all five.

## When to Use

**Primary entry point: `startup-analysis` Phase 6.** That phase invokes
this skill so the five Pass/Hold calls feed the Go/No-Go scorecard.
Prefer the integrated path — a debate-team run divorced from CLEARFRAME
market / ICP / wedge analysis is operating on weaker context.

Standalone use is acceptable when:

- The user has already validated the idea elsewhere and only wants the
  research → offer → copy → site → funnel chain.
- The user explicitly asks for the "five-person AI team" without a
  full validation pass.

Skip for:

- Genesis / Kawasaki workshop — use `startup-planner`.
- Prompt rewriting — use `structured-prompt-builder`.

## How It Differs From `debate-team`

`debate-team` is a generic tri-model critique pipeline (Generator + Critics + Lead). This skill is a **sequential five-role chain** specific to startup ideas. Each role's output is the next role's input. Roles do not run in parallel.

## Inputs (gather once)

- one-line idea
- target customer
- desired conversion (download, signup, payment)
- optional: design reference (URL or image), tone preferences, budget ceiling

If any of the first three are missing, ask one consolidated question before starting.

## Run Order

1. `roles/01-researcher.md` — validate the pain with real-source evidence.
2. `roles/02-strategist.md` — turn the validated pain into 5 ranked lead magnets; pick one.
3. `roles/03-copywriter.md` — write headline, sub-headline, 3-5 bullets, CTA.
4. `roles/04-builder.md` — produce a one-page site spec wired to the copy.
5. `roles/05-marketer.md` — build the 30/60/90 funnel and weekly cadence.

## Hand-off Rule

Each role MUST start with a one-paragraph **Challenge** of the prior role's output before producing its own. If the prior step is weak (no real-source evidence, vague ICP, generic lead magnet), the current role pushes back and asks for a redo rather than rubber-stamping. This is what makes it a debate team, not a relay race.

## Halting Rules (structural No-Go signals)

When invoked from `startup-analysis` Phase 6, the following Holds force a
No-Go in Phase 7 regardless of scorecard total:

- **Researcher Hold** — fewer than 2 of 5 pains have verbatim customer
  language. The pain is not real.
- **Strategist Hold after two attempts** — cannot design an offer the
  customer would pay $50-$100 for. The wedge has no commercial pull.
- **Marketer Hold on math** — visitor → MRR math cannot reach target at
  any defensible ARPU or conversion rate.

When run standalone, halting rules still trip; surface them as a
recommendation to halt building until the founder fixes the upstream
gap.

## Output Discipline

- Every claim that depends on real-world data must cite a source type (Reddit thread, Amazon review, FB group, G2 review) and quote 1-2 phrases of customer language verbatim.
- No invented stats. Mark estimates as estimates.
- No motivational filler. Direct, specific, founder-grade.
- Each role ends with a one-line **Pass / Hold** call: pass to next role, or hold and request a fix.

## Companion Skills

- **Canonical caller: `startup-analysis` Phase 6** — prefer this entry
  point so the validation packet feeds the Go/No-Go verdict.
- Post-step (after a Go verdict): `frontend-design` or
  `web-artifacts-builder` to actually build the Builder spec.
- Post-step: `writing-workshop` to polish the Copywriter output for a
  specific channel.
