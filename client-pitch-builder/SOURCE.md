# Source Credits — client-pitch-builder

## Primary Design System and .pptx Engine

**YC-Pitch-Deck** by sgatwork  
Repo: `https://github.com/sgatwork/YC-Pitch-Deck`  
File used: `design.md`

The PptxGenJS code patterns in `references/pptxgenjs-engine.md` are adapted from this repo's `design.md` — a production code system for generating pitch decks via PptxGenJS. Specifically sourced:
- The palette constants (`C.offwhite`, `C.accent`, etc.)
- The typography system (Helvetica headlines + Courier New labels)
- The slide factory pattern (`newSlide()`)
- The card helper and the shadow-object mutation gotcha
- Numbered card, stat card, and 2x2 grid patterns
- Layout grid coordinates (left/right column, logo position, section label, slide number)
- The "never do" list (no `#` hex prefix, no shadow reuse, no `FFFFFF` slide backgrounds)
- The QA checklist

License: not specified in the repo at time of import. Patterns adapted, not wholesale copied.

---

## Slide Flow Framework

The 7-8 slide prospect-pitch structure (Intro -> Challenges -> Solutions -> Process -> Case Study -> Package -> Next Steps) is a synthesis of:

- **MindStudio / ART3 article** (slide-by-slide prompt template methodology, brand-concept + research-outline input discipline): frameworks, not literal text.
- **Founder-sales framing principle** ("design the deck around how they buy, not how you sell") — widely attributed across B2B sales literature; no single source cited.
- **Assertion-style slide headlines** (a stat or claim, not a label or question) — core principle in Guy Kawasaki's pitch deck canon and McKinsey slide discipline; no single source cited.

---

## Sibling Skills Referenced

- `sales-enablement` — deck frameworks, objection libraries, proposal templates (imported marketing bundle, PR #191)
- `product-marketing` — ICP and positioning context (same bundle)
- `copywriting` — conversion copy depth for headlines and CTAs (same bundle)
- `pitch-deck` — investor/generic deck flow; cross-referenced as the distinct use case
- `elevator-pitch` — spoken pitch variant; cross-referenced via `pitch-deck`'s See also chain

---

## Web-Scraping Protocol

The token-efficient scraping pattern in `references/web-scraping-notes.md` is the internal `web-scraping-efficient` skill convention, applied here to prospect + company research.
