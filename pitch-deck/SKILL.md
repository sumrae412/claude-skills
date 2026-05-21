---
name: pitch-deck
description: Use when the user wants to create a pitch deck — investor, sales, or product-launch presentation. Triggers on "build a pitch deck", "investor slides", "sales presentation", "create a deck", or as a follow-on to startup-analysis.
---

# Pitch Deck

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad
exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the reference needed for the current step.
- Keep slide drafts compact; do not re-explain the framework on every iteration.
- If deck type and audience are obvious, generate slides without re-loading
  references.

## Overview

Generate slide-by-slide pitch decks (headline, body, visual, speaker notes)
for investors, sales, or product launches. Optional PDF render via Marp.

Companion to `startup-analysis` — validate the idea first, then pitch it.

## When to Use

- "build a pitch deck" / "investor slides" / "sales presentation"
- post-`startup-analysis` follow-on (verdict → deck)
- product launch deck (internal or external)
- partnership / fundraising / sales-enablement deck

Skip if the user wants narrative copy only (use `sc-marketing-scripts`) or a
one-pager (no slide structure needed).

## Inputs (gather once before drafting)

1. **Purpose** — investor raise, sales pitch, product launch, partnership?
2. **Audience** — VC / angel / enterprise buyer / press / internal team?
3. **Duration** — 5 / 10 / 20 minutes? (controls slide count)
4. **The ask** — what should they do after?
5. **Source content** — startup brief, product spec, traction data, team bios

If audience and purpose conflict ("investor deck for a sales meeting"), ask
once which dominates.

## Workflow

### Step 1 — Choose structure

Pick one. Detail in `references/structures.md`:

- **Investor (10–12 slides):** title, problem, solution, market, product,
  business model, traction, GTM, competition, team, financials, ask
- **Sales (8–10 slides):** title, their problem, cost of inaction, solution,
  how it works, proof, pricing, next steps
- **Launch (8–12 slides):** market timing, problem, product, benefits,
  competitive position, GTM, success metrics, availability

Tune for stage / context. See `references/audiences.md` for seed vs Series A,
VC vs angel, C-suite vs technical buyer.

### Step 2 — Write each slide

For every slide produce four fields:

- **Headline** — *one takeaway sentence*, not a label. Headlines tell the
  story even if every body is hidden.
- **Body** — 3–5 bullets max. Under 30 words total.
- **Visual** — chart / diagram / image suggestion. One per slide.
- **Speaker notes** — what to say out loud. 2–4 sentences.

### Step 3 — Quality check

Run the checklist below. Fix anything failing before showing the user.

## Output Format

Use this exact structure so downstream rendering works:

```markdown
# Pitch Deck: [Title]

## Slide 1 — [Title slide]
**Headline:** [Company name + one-line description]
**Body:**
- (optional tagline / category / one-line differentiator)
**Visual:** Logo, tagline
**Speaker notes:** [2–4 sentences]

## Slide 2 — [Problem]
**Headline:** [Problem stated as insight, not label]
**Body:**
- Point 1
- Point 2
- Point 3
**Visual:** [Suggestion]
**Speaker notes:** [What to say]

[continue for all slides]
```

## The Headline Rule

The single highest-leverage technique: **every headline is a takeaway, not a
label.**

| Label (weak) | Takeaway (strong) |
|---|---|
| "Market Size" | "A $47B market growing 23% annually" |
| "Problem" | "Small landlords lose $2,400/yr to missed tenant follow-ups" |
| "Traction" | "From 0 to 1,200 paying users in 6 months" |
| "Team" | "Three operators who shipped this exact product at scale before" |

If a reader skimmed only the headlines in order, the deck should still tell
the story. If it doesn't, the headlines are labels.

## Quality Checklist

Before delivering:

- [ ] Every headline is a takeaway, not a label
- [ ] One main idea per slide
- [ ] Body text under 30 words per slide
- [ ] Visual suggested for every slide
- [ ] Speaker notes for every slide
- [ ] Final slide has a clear, specific ask
- [ ] Logical flow — story arc, not a feature dump
- [ ] No information overload (move detail to appendix)
- [ ] Audience-tuned register (see `references/audiences.md`)

Common pitfalls and fixes: `references/pitfalls.md`.

## Render to PDF

The output format above is Marp-compatible. Add Marp frontmatter and use
`---` between slides instead of `## Slide N` headings, then:

```bash
npx @marp-team/marp-cli@latest deck.md --pdf
```

Full render guide (Marp frontmatter, themes, Beamer alternative, HTML +
Chrome headless): `references/render-pdf.md`.

## Reference Map

- `references/structures.md` — full slide-by-slide flows for each deck type
- `references/audiences.md` — investor / sales / launch tuning
- `references/pitfalls.md` — common failure modes + fixes
- `references/render-pdf.md` — PDF rendering options and Marp frontmatter

## Guardrails

- no headline that's just a category label
- no slide with more than one main idea
- no fabricated numbers — every metric traceable to user-provided source
- no "disrupting" / "AI-powered" / "platform" filler — concrete claims only
- if the user can't supply traction, name the gap honestly; don't invent it
