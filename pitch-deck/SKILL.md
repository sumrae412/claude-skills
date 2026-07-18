---
name: pitch-deck
description: Use when the user wants to create a pitch deck — investor, sales, or product-launch presentation. Triggers on "build a pitch deck", "investor slides", "sales presentation", "create a deck", or as a follow-on to startup-analysis.
---

# Pitch Deck

## Communication Principles

Before drafting any slide prose (headlines, body, speaker notes), load [`../shared/communication-principles.md`](../shared/communication-principles.md). Decks are the highest-risk surface for sameness — investors and sales audiences see hundreds, and generic ("We're the X for Y," "leveraging AI to disrupt Z") gets pattern-matched and dismissed. Before shipping, run the **§9 sameness-detector** pass on every slide: name concrete instances across the eight axes, apply the cut/combine/sharpen/surprise/specify/restructure moves, and verify the generic-swap test (swap the company name for a competitor — if the slide still works, it's too generic). Headlines especially must survive the swap test.

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
6. **Delivery mode** — live pitch (you present) or send-ahead (read with no
   presenter)? Sets the per-slide word budget (Step 2).

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

For every slide produce these fields:

- **Headline** — *one takeaway sentence*, not a label. Headlines tell the
  story even if every body is hidden.
- **Body** — 3–5 bullets max. Word budget depends on delivery mode: live-pitch
  decks stay under ~40 words/slide (the visual carries it); send-ahead decks
  can run ~60-80 words so they read without a presenter.
- **Visual** — chart / diagram / image suggestion. One per slide.
- **Speaker notes** — what to say out loud. 2–4 sentences.
- **Investor question** — *(investor decks)* the question in the investor's
  head at this point that the slide must answer ("Is this problem real and
  expensive?", "Why now?", "Why this team?"). A slide that answers no real
  question gets cut. For sales decks, substitute the buyer's question.

**Entry conditions for optional/specialty slides.** Every slide beyond the core arc must earn its place with real input, not template momentum. Before including one, check its entry condition — if the input doesn't exist, cut the slide rather than filling it with generic content:

| Slide | Entry condition |
|---|---|
| Traction | At least one sourced, dated figure (revenue, users, retention — not "growing fast") |
| Demo / product tour | A live product or real screenshots exist (never mock UI as if shipped) |
| Team | Named people with claims the fact inventory supports |
| Testimonial / logo wall | Real quotes/customers with permission to name |
| Competition matrix | You can name actual competitors — a matrix with invented axes and no rivals is filler |

(Pattern adapted from [Bolt Slides](https://github.com/stackblitz/bolt-slides)' agent skill, which gates each specialty layout on an explicit entry condition — e.g. a chat layout only for genuinely conversational products, a big-number slide only with one sourced figure.)

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
**Investor question:** [the implicit question this slide answers — investor decks]

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
- [ ] Body within the delivery-mode word budget (live ~40 / send-ahead ~60-80)
- [ ] Every slide answers a real investor (or buyer) question; none answers nothing
- [ ] Visual suggested for every slide
- [ ] Speaker notes for every slide
- [ ] Final slide has a clear, specific ask
- [ ] Logical flow — story arc, not a feature dump
- [ ] No information overload (move detail to appendix)
- [ ] Audience-tuned register (see `references/audiences.md`)
- [ ] Every optional/specialty slide met its entry condition (Step 2 table) — no filler sections
- [ ] Send-ahead decks: a partner could follow it alone at 11pm on their iPad, no presenter

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

## See also

- `startup-analysis` — validate the idea before building the deck.
- `startup-positioning` — sharpen positioning before the deck narrative.
