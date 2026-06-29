---
name: yc-pitch-deck
description: >
  Use when a founder wants to build or review a YC-style investor pitch deck and produce a
  .pptx file. Triggers on: pitch deck, investor slides, demo day presentation, fundraising deck,
  seed deck, Series A deck, what to put on slides, how to present to investors. Covers slide
  content (Geoff Ralston framework), visual design (Kevin Hale rules), and PptxGenJS code
  production. Outputs a .pptx to a dedicated output dir outside any tracked repo.
user-invocable: true
---

# YC Pitch Deck Skill

A YC-distilled skill for building pitch decks that are clear, compelling, and investor-ready.
Covers three layers: Kevin Hale's design framework, Geoff Ralston's content/story framework, and a
production design system for generating the actual .pptx file with PptxGenJS.

**Workspace discipline:** write all .pptx output to a dedicated directory (e.g. `~/Desktop/pitch-output/`)
outside any git-tracked repo. Never write generated files into the skills directory.

## Two Modes

**CREATE mode** - User has a startup and wants to build a deck from scratch.
Run the Founder Interview, then produce a full deck as a .pptx file using the Design System.

**REVIEW mode** - User shares existing slides (text, description, or uploaded deck).
Audit each slide against the content guide and design rules. Flag issues, suggest fixes.

When in doubt about which mode, ask: "Do you want to build a new deck or improve an existing one?"

---

## Step 1 - Founder Interview (CREATE mode only)

Before writing a single slide, extract the vertebrae. Ask all of these in one message:

1. **What does your startup do?** (One plain sentence - no jargon)
2. **Who is the customer?** (Specific - not "enterprises", but "ops managers at mid-market logistics companies")
3. **What problem are you solving?** (What's painful, broken, or missing today?)
4. **Why now / why hasn't this been done before?**
5. **What's your traction?** (Revenue, users, growth rate, notable customers)
6. **What's the market size?** (Push for bottoms-up numbers)
7. **What's the team's unfair advantage?** (Relevant credentials, domain expertise, prior exits)
8. **What's the ask / what stage are you?** (Pre-seed, seed, Series A)
9. **Do you have a brand colour?** (If yes, use it as the accent. If no, default to Klein Blue #002FA7)
10. **Do you have a logo file?** (PNG or SVG - placed top-right on every slide)

Once you have answers, identify the **3-4 vertebrae** - the most memorable, compelling facts that will
make investors afraid to miss this deal. These drive every slide.

---

## Step 2 - Build or Review the Deck

Load the reference files:
- Slide-by-slide **content guidance** - read `references/content.md`
- **Design rules and PptxGenJS code system** - read `references/design.md`

**CREATE mode:** produce a complete `.pptx` file using PptxGenJS, following the Design System in
`references/design.md` exactly. Build the file - do not describe what the deck looks like.

**REVIEW mode:** go slide by slide. For each one call out:
- What's working
- Content or design violations
- Specific fix

---

## The Golden Rule

Always apply both layers together. A beautifully designed slide with weak content fails. Strong
content in a cluttered slide also fails. Every decision serves one goal: **make the investor
immediately understand why this is a deal they can't miss.**

---

## Quick Reference - The 3 Design Principles

| Principle | What it means | Test |
|-----------|--------------|------|
| **Legible** | Helvetica Bold, large, high contrast on white. | Can someone read it from the back row? |
| **Simple** | One idea per slide. Billboard, not essay. Max ~7 words in the headline. | Remove everything that doesn't serve the one idea. |
| **Obvious** | Conclusion written explicitly. Understood in 3 seconds. | Show to a stranger - do they immediately say the right thing? |

## Quick Reference - The 7 Slides

1. Cover
2. Problem
3. Product
4. Market
5. Traction
6. Team
7. Ask / Conclusion

See `references/content.md` for what to write on each.
See `references/design.md` for the visual system and PptxGenJS code patterns.

---

See also: `pitch-deck/SKILL.md` (generic deck skill); `client-pitch-builder/SKILL.md` (B2B sales deck)
