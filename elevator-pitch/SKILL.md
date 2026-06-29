---
name: elevator-pitch
description: Use when the user wants a spoken elevator pitch — a 10/30/60/90-second verbal pitch for an investor, a networking intro, a cold outreach opener, or a meeting opener. Triggers on "write me an elevator pitch", "30-second pitch", "how do I pitch this in an elevator", "pitch this to a VC", "intro for a networking event", or "verbal pitch" (distinct from a slide deck — use pitch-deck for slides).
---

# Elevator Pitch

## Communication Principles

Before drafting any pitch line, load [`../shared/communication-principles.md`](../shared/communication-principles.md). A pitch is the highest-density sameness risk in this repo — investors hear the same "We're the Uber for X / leveraging AI to disrupt Y" cadence dozens of times a day and tune it out. Before shipping, run the **§9 sameness-detector** pass on every version: name concrete instances across the eight axes, apply the cut/combine/sharpen/surprise/specify/restructure moves, and run the generic-swap test (swap the company name for a competitor — if the line still lands, it's too generic and must be rewritten). The villain statistic and the hero's one differentiator must both survive the swap.

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad
exploration, repeated web fetches, or heavy reference loading.

- Load only the reference for the version the user asked for. A 30-second
  ask does not need `references/investor-types.md`.
- Do not re-explain the framework on every iteration — quote the line back,
  fix the one weak part.
- If the villain, hero, and ask are already clear from context, draft without
  re-running research.

## Overview

Build spoken elevator pitches using the **Villain-Hero** narrative: name a
problem the listener already hates (the villain), present the founder as the one
with the weapon to kill it (the hero), then prove it and ask. Investors fund
heroes slaying villains, not feature lists.

Companion skills: validate the idea first with `startup-analysis`, turn the
winning pitch into slides with `pitch-deck`.

## When to Use

- A founder needs a spoken pitch: investor, angel, accelerator, strategic.
- A networking intro, conference opener, or "what do you do?" answer.
- A cold-email / LinkedIn opener compressed from the 30-second version.
- A meeting opener that sets up a deeper deck walkthrough.

**When NOT to use:**
- Slide deck or written investor memo → `pitch-deck`.
- "Is this idea even worth building?" → `startup-analysis`.
- Course / marketing video scripts → `sc-marketing-scripts`.
- A résumé summary or career-change pitch → `resume-tailor` (career framing),
  though the Villain-Hero shape below adapts to a personal pitch too.

## Workflow

1. **Gather the six inputs.** Use `AskUserQuestion` to collect, in one pass:
   villain (the painful problem + who suffers), weapon (the solution), superpower
   (the unfair advantage), proof (traction / evidence), audience (which investor
   type), and the ask (amount + milestone). Ask only for the gaps context
   doesn't already fill.
2. **Research the real numbers.** Run `WebSearch` for the market size, recent
   funding rounds in the space, competitor positioning language, and a shocking
   stat to anchor the villain. Specific real numbers beat "it's a huge market."
3. **Write the villain.** Name its victims, quantify its damage, and find its
   weakness (the insight that lets this founder win). A weak villain = a weak
   pitch.
4. **Position the hero.** State the weapon, the origin story (why this founder),
   the proof, and the quest (the world after the villain dies). Confident, never
   arrogant.
5. **Produce the version(s) asked for.** Default to the length the user named.
   For an investor pitch, pick the matching script from
   `references/investor-types.md`. For length variants and context adaptations,
   use `references/length-variations.md`.
6. **Sharpen.** Load `references/hooks-and-delivery.md` for opening hooks,
   delivery coaching, and the iteration tests. Run the §9 sameness pass, then
   read every version aloud and time it before shipping.

## The Villain-Hero Framework

Three acts, every length:

- **Act 1 — The Villain.** Introduce the problem as a villain the listener
  already recognizes. Make them feel the pain.
- **Act 2 — The Hero.** The founder and team are the hero with the unique
  weapon. Show why they are the ones to slay it.
- **Act 3 — The Victory + Ask.** Paint the world after the villain is dead,
  prove it is already working, then make one clear ask.

Never open with the company name. Never feature-dump. Always close with a
specific ask.

A pitch worked when the listener says **"tell me more."** The goal is the next
conversation, not closing in the elevator.

## Pick the frame

Villain-Hero is the default and fits investor pitches (founder as hero). For
other audiences, swap the frame. Use one frame per pitch; do not blend.

- **Golden Circle (Sinek)** — open with Why, then How, then What. Reach for it
  when the mission is the differentiator.
- **StoryBrand (SB7)** — make the *listener* the hero and the founder the guide
  with a plan. Better than founder-as-hero for sales and consumer pitches.
- **Sparkline (Duarte)** — oscillate between "what is" and "what could be" to
  build tension. Good for vision-led pitches.

## Quick Reference

| Want | Go to |
|---|---|
| 10s one-liner, 30s, 60s, 90s scripts | `references/length-variations.md` |
| Conference / cold-email / meeting-opener / follow-up versions | `references/length-variations.md` |
| Personalize for a known contact, or a career / personal pitch | `references/length-variations.md` |
| Technical-investor pitch (IP, moat, performance) | `references/investor-types.md` |
| Market / growth-investor pitch (TAM, unit economics) | `references/investor-types.md` |
| Customer-obsessed-investor pitch (persona, NPS, retention) | `references/investor-types.md` |
| Opening hooks, closing lines, delivery coaching, A/B tests | `references/hooks-and-delivery.md` |

## Common Mistakes

- **Opening with the company name.** Forgettable. Open with the villain.
- **Feature-dumping.** They do not care about features before they hate the
  villain.
- **Vague market sizing.** "Huge market" reads as no research. Cite a real
  number from step 2.
- **No clear ask.** Every version names what the listener should do next.
- **Hedging.** "We're still early, but..." kills momentum. State what is true.
- **Generic framing.** If the line survives the generic-swap test, it is not a
  pitch yet — rewrite it (see §9).

## See also

- `pitch-deck` — turn the winning pitch into investor / sales slides.
- `startup-analysis` — validate the idea before pitching it.
- `sc-marketing-scripts` — script discipline for spoken / teleprompter delivery.
- `resume-tailor` — Villain-Hero adapts to a career-change personal pitch.
