# Matching Rubric + Reframing Strategies

For every resume bullet (and every role headline/summary line), assign a confidence band vs. the JD profile from Phase 1, then apply a reframing strategy if helpful. The rubric also surfaces missing JD requirements (`GAP`) that no existing bullet covers — see below.

## Confidence Bands

The first four bands label existing bullets. `GAP` is a separate category for JD requirements the resume doesn't cover at all.

| Band | Applies to | Criteria | Typical action |
|------|------------|----------|----------------|
| **DIRECT** | a bullet | Bullet already matches a must-have keyword or a weighted focus area in the JD's own language | Keep. Promote to top of its section. |
| **TRANSFERABLE** | a bullet | Same underlying skill, different domain / stack / scale | Reframe using JD vocabulary. Bridge the domain explicitly. |
| **ADJACENT** | a bullet | Related skill, not a direct match | Reframe cautiously. Keep only if it supports a weighted focus area. |
| **WEAK** | a bullet | Bullet doesn't support the JD profile; burns line real-estate | Cut, or shorten and demote. |
| **GAP** | a JD requirement | JD requires X, resume has no bullet covering X | Route to Phase 3 discovery. Never invent. |

**Scoring calibration:**

- `DIRECT` = 80–100%. `TRANSFERABLE` = 50–79%. `ADJACENT` = 25–49%. `WEAK` = 1–24%. `GAP` = no bullet exists (scored against the JD requirement, not a bullet).
- Ranges are contiguous — every score lands in exactly one band.
- **Round all percentages to the nearest 5%.** The bands aren't calibrated to two-sig-fig precision; reporting `TRANSFERABLE 74%` implies false accuracy. Use `70%`, `75%`, `80%` instead.
- Always show the rounded percent alongside the band. The number (even rounded) forces both the skill and the user to defend the judgment.

## Four Reframing Strategies

Every proposed reframe must name which strategy it uses. Users can veto strategies that feel dishonest.

### 1. Keyword Alignment

Swap the user's term for the JD's term when they refer to the same thing. No new claims — only vocabulary.

- *Before:* "Led a sprint team of engineers to ship new customer onboarding flows."
- *After:* "Led engineering team on self-serve onboarding redesign."

(Adding a metric like "23% activation lift" would be Scale Emphasis, not Keyword Alignment — and only permitted if the user can substantiate the number. See strategy 4.)

**Use when:** the skill and outcome are identical; only the vocabulary differs.
**Don't use when:** the JD term has materially different meaning in this industry.

### 2. Emphasis Shift

Same bullet, different prominence. Move up, move down, combine, split, or lead with a different clause.

- *Before:* "Managed launch calendar, worked with marketing and eng, owned the launch post-mortem."
- *After:* "Owned launch post-mortem process, surfacing 4 cross-team coordination gaps that cut subsequent launch cycles by 2 weeks."

**Use when:** the bullet has a relevant clause buried.
**Don't use when:** the lead clause would misrepresent the role's actual focus.

### 3. Abstraction Level

Zoom in (specific tool) or zoom out (underlying capability) to match the JD.

- *Before:* "Built Looker dashboards for exec weekly reviews."
- *After (zoom out):* "Built executive-facing analytics systems, translating ambiguous business questions into self-serve dashboards used in weekly operating reviews."
- *After (zoom in, if JD names Looker):* keep Looker explicit.

**Use when:** the JD operates at a different altitude than the resume.
**Don't use when:** abstraction flattens important detail the JD will test.

### 4. Scale Emphasis

Add numbers (team size, revenue, users, %, time, volume) to contextualize at the JD's seniority.

- *Before:* "Led product team through re-platforming."
- *After:* "Led 8-person product team through 14-month re-platforming affecting 2.3M users, delivered on time and $180K under budget."

**Use when:** the `QUANTIFY` action code applies, or the user has numbers and left them out.
**Don't use when:** user can't substantiate. Round, omit, or ask — never fabricate.

## Matching Output Format

For the Phase 2 checkpoint, present blocks per role:

```
ROLE: Senior Product Manager, Acme (2022–present)

  [DIRECT 90%]         "Shipped 3 products from 0 to 1 through customer discovery and prototype testing" (resume-body text — ATS-safe, no Unicode)
                       ← matches JD focus 'product discovery' (weight 0.4, LEAD_WITH)
                       → keep; promote to top of role

  [TRANSFERABLE 75%]   "Partnered with growth team on PLG expansion"
                       ← JD focus 'B2B SaaS growth' (weight 0.3, EMPHASIZE)
                       → reframe (Keyword Alignment): swap "partnered with" for "led PLG workstream"
                       Before: Partnered with growth team on PLG expansion.
                       After:  Led PLG workstream, partnering with growth to design self-serve activation flows.
                       Verify with user: scope of "led"?

  [WEAK 20%]           "Ran weekly team lunches"
                       → cut; no JD signal support
```

## When to Bail on a Reframe

If the reframe requires asserting something the user hasn't already demonstrated, STOP. Surface it as a Phase 3 discovery question instead.

**The rule:** a reframe is reshuffling existing truth; a discovery question is asking for truth not yet on the page. If the reframed sentence contains a claim you cannot trace to a bullet in the current resume, you're over the line.

## Bullet-level Sanity Checks

Before shipping a reframe to the checkpoint:

- Every number in the reframe appears in the original bullet OR is marked "needs user confirmation".
- Every capability claimed in the reframe is substantiated by the same or an earlier bullet.
- The reframe's verb matches the seniority register from `references/positioning.md` level-calibration table.
- No reframe adds a first-person claim ("my team", "I architected") stronger than the original.

## CAR Shape (Challenge → Action → Result)

Strong bullets answer "so what?" — they name the context, the action, and the measurable outcome. Aim for **at least 60% of bullets** to land a quantified result (percent, dollars, volume, time, ranking). The rest can carry qualitative outcomes ("adopted org-wide", "established standard"), but a bullet that's pure activity with no result is a cut candidate.

When reframing, check each bullet for all three slots. If a slot is missing, either (a) ask the user a discovery question to fill it, or (b) cut the bullet.

## Action Verbs by Contribution Type

Match the verb to the actual contribution. Mixing registers ("helped drive strategy") is a seniority tell.

| Category | Verbs |
|----------|-------|
| Leadership | Led, directed, managed, oversaw, mentored, championed, established |
| Creation | Developed, designed, built, launched, created, implemented, introduced, architected |
| Improvement | Increased, improved, streamlined, optimized, reduced, enhanced, modernized |
| Analysis | Analyzed, evaluated, assessed, identified, researched, investigated |
| Communication | Presented, negotiated, facilitated, coordinated, advised, authored |
| Technical | Engineered, automated, configured, deployed, integrated, migrated, shipped |

**Banned openers** (describe proximity, not contribution):

- "Responsible for"
- "Helped with" / "Assisted in"
- "Involved in" / "Participated in"
- "Worked on"
- "Tasked with"

If an existing bullet starts with one of these, the reframe must replace the opener with a verb that names what the user actually did.
