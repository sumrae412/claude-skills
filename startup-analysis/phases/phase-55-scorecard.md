# Phase 5.5: Idea Stress-Test Scorecard

## Goal

Synthesise Phases 1-5 into a structured scored report — a shareable,
visual output with pillar-level breakdowns, green/red flags, and
prioritised next actions. Inspired by KnowInsideIQ's Idea Intelligence
report format.

This is NOT the final verdict — Phase 7 holds that. This phase produces
decision support that Phase 7 consumes alongside the debate-team output.

## Six Pillars

Score each pillar 0-100. Use the full range — don't cluster scores in
70-85. Each gets a verdict: **Pass** (≥70), **Warn** (50-69), or **Fail**
(<50) with a one-sentence rationale.

### 1. Demand Reality — Is the demand real and measurable?

- Derive from: Phase 1 (TAM, problem urgency, WTP signals, acquisition
  channels) + Phase 2 (core frustrations, JTBD evidence, pain frequency)
- High score: painful recurring problem, clear WTP from real conversations,
  multiple viable channels, repeat purchase dynamic
- Low score: no evidence people will pay, vague pain, no repeat dynamic,
  TAM too small or untestable
- Kill condition: WTP signals weaker than "I'd consider paying" from fewer
  than 3 independent sources
- **Score problem intensity and willingness-to-pay separately.** They
  diverge routinely — high stated fear with low WTP is a real and common
  result, and averaging them into one "demand" number hides it. Fear is
  not a budget line. When they diverge, that is a channel and
  business-model finding (someone else is expected to pay), not
  automatically a Fail.
- **WTP counts only as a number, segmented by behaviour.** "Would you pay"
  yes/no does not clear this pillar — a majority "yes" routinely sits on
  top of a median price most of the market rejects. Cross-tab against what
  the buyer already purchases, never against age or income. See
  [`../references/primary-research-playbook.md`](../references/primary-research-playbook.md).
- Treat stated WTP as a **ceiling**, not an estimate. Never score this
  pillar off a figure modelled at the stated conversion rate.

### 2. Status Quo — What do people do today, how painful is their solution?

- Derive from: Phase 1 (saturation, dominant players, buyer sophistication,
  pricing ceiling) + Phase 2 (current alternatives, switching triggers,
  workarounds)
- High score: existing solutions expensive, fragmented, or hated; active
  workarounds with public complaints; frequent switching triggers
- Low score: the "competition" is doing nothing (hard to displace);
  alternatives are free and good enough; low switching urgency
- Kill condition: users describe their current solution as "fine" — no
  active frustration to tap

### 3. Desperate Specificity — How specific and urgent is the problem for a well-defined persona?

- Derive from: Phase 2 (ICP: awareness level, psychographics, core
  frustrations, resonant messaging) + Phase 4 (wedge: audience specificity,
  one-liner precision)
- High score: single well-defined persona with urgent recurring pain; JTBD
  names a specific situation and outcome; resists "everyone needs this"
- Low score: persona is "SMBs" or "anyone who..." — too broad; pain is
  mild or infrequent; product is a nice-to-have
- Kill condition: ICP description applies to 3+ unrelated customer types
  with equal relevance

### 4. Narrowest Wedge — What's the smallest entry point that delivers value?

- Derive from: Phase 4 (unclaimed positioning axes, recommended wedge) +
  Phase 3 (value prop: one thing done well) + Phase 5 (GTM optimisation
  priority)
- High score: single-feature wedge solves one urgent problem; competitor
  can't easily copy; wedge opens a larger market
- Low score: requires the full product to deliver value; "platform play" as
  starting point; wedge matches every competitor's
- Kill condition: smallest shipable version requires >3 months build or
  >$50K investment to test

### 5. Observation & Surprise — Did the insight come from real-world observation? Is there a non-obvious angle?

- Derive from: Meta-analysis across Phases 1-5 — is the insight
  first-principles or derivative? Check for: real customer language,
  non-obvious connections, evidence of original thinking
- High score: founder quotes verbatim customer language; the insight
  contradicts conventional wisdom; the solution isn't "AI for X" or
  "Uber for Y"
- Low score: idea applies a generic template ("AI-powered platform for...");
  the "insight" is common knowledge; no evidence of primary observation
- Kill condition: one-line pitch uses a known startup cliché as its core
  mechanic ("X as a Service," "AI-powered Y," "marketplace for Z")

### 6. Future-Fit — Is the timing right? Still relevant in 2-3 years?

- Derive from: Phase 1 (category maturity, growth rate, market timing) +
  Phase 5 (GTM structural alignment, strategic blind spots)
- High score: early-growth category, tailwind from regulation/culture/tech
  shift, product improves with data or network effects, hard to dislodge
- Low score: mature/declining category, late timing, no defensibility,
  depends on a fragile trend
- Kill condition: category declining AND no adjacent pivot exists within
  same capability stack

## Overall Score

Calculate as a weighted average (or reasoned judgment — don't let math
override clear qualitative evidence):

| Range | Verdict |
|---|---|
| ≥75 | **GO** — strong across most pillars |
| 55-74 | **CONDITIONAL GO** — address Warn pillars before proceeding |
| <55 | **NO-GO** — fatal weakness in one or more pillars |

Display as a compact visual block (adjust bar widths to approximate the
score, 20 █ characters = 100):

```
┌────────────────────────────────────────────────────────────────┐
│  IDEA STRESS-TEST SCORECARD                                    │
│  Score: 78/100 · GO                                            │
├────────────────────────────────────────────────────────────────┤
│  Demand Reality       ████████████████████░░░  85/100  Pass    │
│  Status Quo           ███████████████████░░░░  80/100  Pass    │
│  Desperate Specificity ████████████████████░░░  81/100  Pass    │
│  Narrowest Wedge      ██████████████████░░░░░  78/100  Pass    │
│  Observation & Surprise ██████████████░░░░░░░  66/100  Warn    │
│  Future-Fit           ████████████████████░░░  82/100  Pass    │
└────────────────────────────────────────────────────────────────┘
```

## Green Lights & Red Flags

**Green Lights** (3-5) — concrete findings in the idea's favour. Each is a
specific finding, not generic praise. Start each with a bold signal word.

**Red Flags** (2-4) — material risks that could kill it. Flag whether each
is solvable or structural.

```
 Green lights
- Painful, recurring problem (every quote)
- Clear willingness-to-pay signals from interviews
- Low-cost MVP via existing data partners
- Distribution through target communities already mapped

 Red flags
- Data acquisition is the moat — and the bottleneck
- Competitor could ship this in 30 days if motivated
- Single-buyer persona limits TAM ceiling
```

## Top Recommendations

Exactly 3, each with Impact and Ease ratings:

| # | Recommendation | Impact | Ease |
|---|---|---|---|
| 1 | Concise action | High/Medium/Low | High/Medium/Low |
| 2 | Second action | High/Medium/Low | High/Medium/Low |
| 3 | Third action | High/Medium/Low | High/Medium/Low |

Falsifiable and actionable. "Run 20 paid pre-orders before building" beats
"validate demand." One-line note per recommendation if the action isn't
self-explanatory.

## 11-Criteria Weighted Radar (optional addendum)

Include when deeper granularity would help a close verdict:

| Criterion | Wt | /10 | Evidence pointer |
|---|---|---|---|
| Problem urgency | 12 | | |
| Problem-solution fit | 10 | | |
| Target persona clarity | 8 | | |
| Market size | 10 | | |
| Market timing | 8 | | |
| Competition gap | 10 | | |
| Willingness to pay | 10 | | |
| MVP viability | 8 | | |
| Distribution access | 8 | | |
| Moat / defensibility | 8 | | |
| Evidence strength | 8 | | |
| **Total** | **100** | | |

## Keyword-backed validation signal (optional bonus)

Include when search is a viable acquisition channel:

| Signal | Read |
|---|---|
| **Search demand** | Low / Medium / High |
| **Organic opportunity** | Weak / Moderate / Strong |
| **Primary keyword** | Suggested term |
| **Signal source** | Estimate / Known market / N/A |

## Output

- Six-pillar scorecard with overall score and verdict
- Green Lights & Red Flags
- Top Recommendations with Impact/Ease
- 11-criteria radar (optional)
- Keyword validation signal (optional)
- Strategist's note: what worked, what didn't, what's missing
