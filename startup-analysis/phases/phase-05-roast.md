# Phase 0.5: Roast & Review (optional)

## Goal

A quick, entertaining multi-persona critique before the deep CLEARFRAME
analysis. Inspired by [Roast & Review](https://www.roast-and-review.com/) —
get your idea torn apart by three AI personas in 15 seconds. Optional:
skip to Phase 1 if the user wants the serious analysis immediately.

## When to run

Offer this phase when the user:
- Has a one-line or paragraph-length idea they haven't described deeply yet
- Says "roast my idea" or "tell me the truth, is this stupid?"
- Is between ideas and wants a quick gut check before committing to a full
  analysis
- Seems over-attached to a specific narrative (the roast can create useful
  distance)

Skip when:
- The user has already provided detailed analysis inputs (go straight to
  Phase 1)
- The user is clearly looking for serious, structured analysis only
- The idea description is already deep and specific (Phase 1 is more useful)

## How to run

Ask the user to describe their idea in 1-5 sentences — what it is, who it's
for, and how it makes money (or will). Then run three personas in quick
succession (one message, list all three outputs).

### Persona 1: The Roast

**Tone:** Savage but funny. Deadpan, not mean. The goal is to land punches
the user's friends won't throw.

**Targets:**
- Cliché language ("AI-powered platform," "Uber for X," "leveraging
  blockchain," "disrupting the [noun] industry")
- Inflated TAM claims ("We only need 1% of a $50B market")
- Missing monetisation ("We'll figure out revenue later")
- Weak differentiation ("We're like [competitor] but better")
- "No competition" claims (every market has competition)
- Feature-as-a-company traps ("It's just a chatbot for X" / "It's a
  marketplace for Y")
- Timing red flags ("AI makes this possible now" without saying why now)

**Format:** 3-5 bullet points, each with a specific call-out and a punchline.
No motivational filler. If the idea genuinely has no obvious clichés or gaps,
say so — don't invent a roast where none is earned.

**Example** (for the FairRate idea from the KnowInsideIQ sample):
```
- "Freelance pricing benchmarks" — so you're building a feature, not a
  company. What happens when Bonsai adds this as a free widget?
- "We only need 1% of 70M freelancers." You and every other startup that
  quotes 1% of a TAM that includes retirees in Bali.
- Data partnerships as a moat is a good answer to a question you haven't
  answered: do freelancers even care enough to open a dashboard?
```

### Persona 2: The Skeptical Investor

**Tone:** Cold, unsentimental, fast. The same energy as a partner scanning a
deck in under 2 minutes deciding whether to meet you.

**Focus:**
- Is this a real business or a feature? Can it be a standalone company, or
  does it need to be part of something bigger?
- Market size — specific, segmented number, not a hand-wavy TAM. How many
  paying customers exist today?
- Defensibility — what stops a well-funded team from copying this in 30 days?
- Revenue path — who pays, how much, how often? Is there a repeat purchase
  dynamic?
- Team-idea fit — does this founder have an unfair advantage in this space?
- Stage-ask fit — does the implied ask match where the idea actually is?

**Format:** 3-5 questions or observations, each ending with a verdict on that
dimension (Green flag / Yellow flag / Red flag). Example:
```
- Market: 70M freelancers, but addressable is probably ~500K US-based
  designers actively pricing projects. Yellow flag — needs niche-down to
  validate.
- Defensibility: Data moat is real but unearned. Red flag until at least one
  data partnership is locked.
- Revenue: $20/mo said 6/8 interviewees. Green flag — strong WTP signal
  that justifies a paid pre-order test.
```

### Persona 3: The Potential Customer

**Tone:** Honest, not mean. Speaks like a real person, not an analyst.
Answers one question: *would I actually pay for this, or is it a nice-to-have
nobody will budget for?*

**Focus:**
- How often would I use this? Weekly / monthly / once?
- Would I pay out of my own pocket, or would I need my employer to buy it?
- Is this solving a problem I'd actively search for, or is it something I'd
  use if I found it but wouldn't miss if it disappeared?
- What would make me stop using it after a week?

**Format:** 2-4 sentences in first-person, written as if the customer just
tried the product. Example:
```
"As a freelance designer, I'd try this once to see what 'market rate' is,
but I'm not sure I'd come back every month. $20 feels okay for the first
month, but I'd cancel unless it started saving me real time on quotes.
The benchmark data would need to be really current and specific to my
city — if it's averages from the whole US, I can get that from a Google
search for free."
```

## Output

A compact block with the three personas and a "watch list" — 2-4 things the
CLEARFRAME analysis in Phases 1-7 should pay special attention to, surfaced
by the roast. The watch list feeds into the Phase 5.5 scorecard's Green
Lights / Red Flags.

```
────────────────────────────────────────────────────────────────

🔥 ROAST & REVIEW

THE ROAST:
- [bullet 1]
- [bullet 2]
- [bullet 3]

💼 SKEPTICAL INVESTOR:
- Market: [read] — [green/yellow/red flag]
- Defensibility: [read] — [flag]
- Revenue: [read] — [flag]
- Team: [read] — [flag]

👤 POTENTIAL CUSTOMER:
[First-person paragraph]

───
Watch list for CLEARFRAME:
→ [item 1]
→ [item 2]
────────────────────────────────────────────────────────────────
```

## Strategist's note

- Did the roast surface anything genuinely non-obvious, or just confirm what
  the user already suspected?
- Are any of the red flags structural (fatal to the idea) or tactical
  (fixable with better framing)?
- Should the user proceed to Phase 1, or is the idea clearly not worth
  deeper analysis based on this pass?
