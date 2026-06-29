---
name: client-pitch-builder
description: "Analyse a prospect's LinkedIn profile and company website, compare against your own services, and build a custom B2B client pitch deck (8-10 slides) delivered as a real .pptx file ready to send. Use when the user says 'build a pitch for this prospect', 'I want to pitch this client', 'sales presentation for this company', 'client deck for [name]', 'prospect pitch', 'tailor a proposal for', or 'I have a sales meeting with'. Distinct from pitch-deck (investor/generic decks) and elevator-pitch (spoken verbal pitches)."
user-invocable: true
---

# Client Pitch Builder

A B2B sales pitch orchestrator. Given a prospect and your own service offering, it researches both sides and produces a tailored 8-10 slide deck as a `.pptx` file ready to send.

## Communication Principles

Before drafting any slide prose, load [`../shared/communication-principles.md`](../shared/communication-principles.md). Run the **§9 sameness-detector** pass on every headline and value-proposition bullet before finalising: name concrete instances across the eight axes, verify the generic-swap test (replace the prospect name or industry - if the line still works, it's too generic and must be rewritten).

## See Also

- [`../sales-enablement/SKILL.md`](../sales-enablement/SKILL.md) - deck frameworks, objection libraries, proposal templates; use for broader sales collateral beyond this pitch
- [`../product-marketing/SKILL.md`](../product-marketing/SKILL.md) - ICP and positioning context file; run first if you haven't captured your own company's positioning yet
- [`../copywriting/SKILL.md`](../copywriting/SKILL.md) - conversion copywriting depth for slide headlines and CTAs
- [`../pitch-deck/SKILL.md`](../pitch-deck/SKILL.md) - investor or generic pitch deck flow (different audience, different structure)
- [`../startup-planner/SKILL.md`](../startup-planner/SKILL.md) - validate the business model before pitching; run this first if the offering is still being shaped

## Output Workspace

Write the `.pptx` and all working files to `~/Documents/<ProspectName>-pitch/`. Never write inside a tracked git repo.

```
~/Documents/AcmeCorp-pitch/
  pitch.pptx          # deliverable
  research.md         # scratch notes (prospect + your-company profiles)
  script.js           # PptxGenJS generation script
```

---

## Phase 1 - Inputs (Forced Gate)

**Block until all three are provided.** Do not proceed with partial inputs.

Ask for exactly:

1. **Prospect LinkedIn** - paste the PDF export or raw text from their profile page. Minimum: name, title, company, current role description.
2. **Prospect company URL** - their company website (e.g. `https://acmecorp.com`).
3. **Your company URL** - your own website (e.g. `https://myagency.com`).

If any input is missing, reply:

> "I need all three inputs before I can build the deck: (1) the prospect's LinkedIn export, (2) their company URL, and (3) your company URL. Drop them in and I'll get started."

Optional: ask for a brand hex colour to replace the default Klein Blue (`#002FA7`) in the deck.

---

## Phase 2 - Research and Analysis

Use token-efficient fetching (see [`references/web-scraping-notes.md`](references/web-scraping-notes.md)). Do not dump raw HTML into context.

### 2A - Prospect Profile

From the LinkedIn text and company website, extract:

| Field | What to capture |
|---|---|
| **Role** | Title, seniority, tenure, reporting level |
| **Industry** | Sector and sub-sector |
| **Company stage** | Headcount signal, funding stage if visible, revenue signals |
| **Goals** | What a person in this role is measured on (infer from role if not stated) |
| **Pain points** | Operational friction, gaps, pressures - look for language in their About section, company blog, and job postings |
| **Where they need support** | The intersection of their goals and visible gaps |

Write findings to `~/Documents/<ProspectName>-pitch/research.md` under `## Prospect`.

### 2B - Your Company Profile

From your website, extract:

| Field | What to capture |
|---|---|
| **Services** | What you offer, concisely |
| **Positioning** | Who you serve and how you frame your value |
| **Differentiators** | What you do that alternatives don't |
| **Proof points** | Client names, outcomes, metrics if visible |

Write findings to `~/Documents/<ProspectName>-pitch/research.md` under `## Your Company`.

### 2C - Solution Mapping

For each prospect pain point, identify the specific service or capability that addresses it. This mapping drives slide 3 (Solutions). Write it as a table:

```
| Pain Point | Your Solution | Proof/Evidence |
|---|---|---|
| [specific pain] | [specific service] | [outcome or example] |
```

---

## Phase 3 - Deck Build

Build the deck as a PptxGenJS Node.js script. See [`references/pptxgenjs-engine.md`](references/pptxgenjs-engine.md) for the full design system, code patterns, and the shadow-object mutation gotcha.

**The slide flow - 8 slides minimum, 10 maximum:**

### Slide 1 - Intro / About Us (tailored to their industry)
- Headline: your company name, bold, large
- Subtext: one-sentence positioning statement rewritten for this prospect's industry (not your generic tagline)
- Right column: 2-3 stat cards with your strongest proof points relevant to this sector
- Section label: `ABOUT US`

### Slide 2 - Prospect's Challenges (personalised)
- Headline: names the prospect's specific challenge in 5-7 words (not a generic "The Problem")
- Headline must use assertion style: a claim or stat, not a question or label
- Right column: 3-4 numbered cards, one per named pain point - drawn directly from Phase 2 research
- Section label: `YOUR CHALLENGES`

### Slide 3 - Our Solutions (mapped 1-for-1 to their pain points)
- Headline: the transformation, not the feature list
- Right column: 2x2 grid of step/solution cards - each card directly corresponds to a pain point from Slide 2 (use the same numbering)
- Section label: `HOW WE HELP`

### Slide 4 - How We Work (process)
- Headline: the engagement model in one line
- Right column: 3-4 numbered process step cards
- Section label: `HOW WE WORK`

### Slide 5 - Case Study / Example (aligned to their role or industry)
- Headline: the result, not the project name ("3x pipeline in 90 days" not "Acme Project")
- Body: who the client was (role/industry, not necessarily name), the challenge, the intervention, the outcome with numbers
- If no real case study exists, frame as a representative example or a methodology walkthrough
- Section label: `RESULTS`

### Slide 6 - Recommended Package / Service
- Headline: the specific package name or engagement type you recommend for this prospect
- Right column: what's included, timeline, expected outcome
- Include a "Why this, for you" one-liner that references their specific situation
- Section label: `RECOMMENDED`

### Slide 7 - Pricing (optional - include if user provides pricing)
- If pricing provided: stat card with the investment number, surrounded by outcome cards
- If not provided: skip this slide or replace with a "What you get" deliverables breakdown
- Section label: `INVESTMENT`

### Slide 8 - Next Steps (CTA)
- Headline: the action, not "Next Steps" as a label (e.g. "Book 30 minutes. Let's scope it.")
- 3-4 numbered cards for the concrete next steps: book call, receive proposal, kick off by [date]
- Include contact details: name, email, calendly or booking link
- Section label: `NEXT STEPS`

**Optional slides (add if content is strong):**
- Slide 9: Team / Who You'll Work With
- Slide 10: Testimonials / Social proof

---

## Phase 4 - Generate the .pptx

Write `~/Documents/<ProspectName>-pitch/script.js` using the PptxGenJS patterns in [`references/pptxgenjs-engine.md`](references/pptxgenjs-engine.md).

Then run:

```bash
cd ~/Documents/<ProspectName>-pitch/
node script.js
```

This writes `pitch.pptx` to the same directory.

**On completion, confirm:**
- File exists: `ls -lh ~/Documents/<ProspectName>-pitch/pitch.pptx`
- Report the file size (must be > 10KB - a corrupt .pptx from bad hex or shadow mutation is often < 5KB)

**Common failure modes** (see the gotcha list in `references/pptxgenjs-engine.md`):
- Hex colours with `#` prefix corrupt the file silently
- Shadow option objects mutated in-place produce blank slides
- Missing `pptxgenjs` package - install with `npm install pptxgenjs` in the workspace dir

---

## QA Before Delivering

Run the §9 sameness-detector pass (from `../shared/communication-principles.md`) on:
- Every slide headline
- The "Why this, for you" line on Slide 6
- The CTA headline on Slide 8

Each must pass the generic-swap test: replace the prospect name or industry - if the line still works for any company, rewrite it until it doesn't.

Confirm file is non-corrupt and > 10KB before handing to the user.

**Deliver:** `~/Documents/<ProspectName>-pitch/pitch.pptx` - share the absolute path.
