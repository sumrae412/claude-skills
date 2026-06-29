---
name: accelerator-application
description: >
  Use when a founder wants to apply to startup accelerators, incubators, or fellowship programs.
  Triggers on: YC application, Techstars, accelerator, apply to programs, incubator application,
  fellowship program. Outputs a ranked program shortlist, core narrative, per-program application
  draft, video script, and interview prep.
user-invocable: true
---

# Accelerator Application

## When to Use

- Founder wants to apply to Y Combinator, Techstars, or other accelerator programs.
- Founder wants to identify which accelerators are the best fit for their stage and sector.
- Founder wants help drafting application essays and preparing for interviews.
- Founder wants to batch-apply to multiple programs efficiently.

## Context Required

- Company stage, product, and traction metrics.
- Founder backgrounds and why this team is uniquely positioned.
- What the founder wants from an accelerator (funding, network, credibility, customers, mentorship).
- Industry/vertical (some accelerators are sector-specific).
- Geography and willingness to relocate.
- Previous applications or rejections (to improve this round).

## Workflow

1. **Match accelerators to the startup** - filter the directory below by stage fit, sector focus,
   geography, and program terms. Recommend a shortlist of 5-10 programs ranked by fit.
2. **Research each program's preferences** - review recent cohort companies, partner bios, and
   published advice on what they look for. Note patterns (YC values technical founders and fast
   growth; Techstars values coachability and market size).
3. **Draft the core narrative** - write foundational answers most applications share:
   - What does your company do? (one sentence, no jargon)
   - What problem are you solving and for whom?
   - Why now? What's changed that makes this possible?
   - Why is this team the right team?
   - What traction do you have?
   - What's your unfair advantage or unique insight?
4. **Customize per application** - adapt the core narrative to each program's specific questions,
   word limits, and culture. YC applications are famously terse. Techstars wants coachability.
5. **Prepare the video** (if required) - draft a script for the 1-2 minute application video.
   Structure: problem, solution, traction, team, ask. Keep it authentic, not polished.
6. **Prepare for interviews** - draft answers to common accelerator interview questions (see below).
   Practice the 30-second pitch.

## Output Format

```markdown
## Accelerator Application Plan

### Recommended Programs (ranked by fit)
1. **[Program]** - [why it's a fit] | Deadline: [date] | Apply: [link]

### Core Narrative
- **One-liner:** [what you do in one sentence]
- **Problem:** [2-3 sentences]
- **Solution:** [2-3 sentences]
- **Why now:** [1-2 sentences]
- **Traction:** [key metrics]
- **Team:** [why you're the right people]
- **Unique insight:** [what you know that others don't]

### [Program Name] Application Draft
**Q: [Question from application]**
A: [Draft answer within word limit]

### Interview Prep
**30-second pitch:** [draft]
**Common questions:**
- "What do you understand that others don't?" - [answer]
- "How do you acquire users/customers?" - [answer]
- "What's the biggest risk?" - [answer]
- "Why hasn't this been done before?" - [answer]
```

## Program Directory

### Tier 1 - Generalist, Top-Tier

| Program | Investment | Equity | Duration | Best For |
|---------|-----------|--------|----------|----------|
| Y Combinator | $500K ($125K for 7% + $375K uncapped MFN SAFE) | 7% | 3 months | Technical founders, fast-growing startups at any stage |
| Techstars | $120K | 6% | 3 months | Coachable founders, strong mentor network needs |
| 500 Global | $150K | 5% | 4 months | International founders, diverse backgrounds |
| Antler | $250K | 8-10% | 6 months | Pre-team/pre-idea founders looking for co-founders |
| Launch Accelerator | $100K | 6% | 3 months | Consumer and SaaS, media exposure via TWIST network |
| Entrepreneur First | $80-125K | ~10% | 6 months | Pre-team, build with a co-founder from the cohort |
| South Park Commons | Fellowship | No equity | Ongoing | Experienced operators exploring what to build next |
| Pioneer | $20K | 1% | Remote | Very early stage, global, remote-first |
| HF0 | Fellowship | No equity | Ongoing | Deeply technical founders, hacker community, ex-FAANG |

### Tier 2 - Sector-Specific

| Program | Focus | Investment |
|---------|-------|-----------|
| a16z Speedrun | Consumer tech | $750K |
| Alchemist Accelerator | Enterprise sales | $36K |
| Dreamit Ventures | HealthTech, UrbanTech | $50-100K |
| Indie Bio | Biotech/life sciences | $250K |
| HAX | Hardware/deep tech | $250K |
| Techstars AI | AI-native startups | $120K |
| Google for Startups Accelerator | AI, Cloud | $0, no equity |
| Microsoft for Startups | Cloud/AI | Credits, no equity |

### Tier 3 - Non-Profit, University, Government

| Program | Focus |
|---------|-------|
| MassChallenge | Social impact, any sector ($0, no equity) |
| StartX (Stanford) | Stanford-affiliated |
| Creative Destruction Lab | Science-based ventures |
| NSF I-Corps | Deep tech commercialization |
| SBIR/STTR | Government R&D grants |
| Berkeley SkyDeck | UC Berkeley-affiliated |

*Terms, investment amounts, and equity percentages change frequently. Verify current terms on each
program's website before applying.*

## Frameworks

### What Top Accelerators Look For

- **YC:** founders who build fast. Technical co-founders. Clear thinking, not polish. "Make something
  people want." They read applications in under 2 minutes - be concise.
- **Techstars:** coachability and self-awareness. Market size. The "why you" answer. They call
  references on founders.
- **500 Global:** diverse founders, international-friendly. Traction and hustle over pedigree.

### Application Writing Principles

- Lead with what you've built and what's working, not the market opportunity.
- Use specific numbers ("1,200 users, 40% WoW growth"), not vague claims ("rapidly growing").
- Show velocity - what you've accomplished in the last 4 weeks matters more than a 5-year vision.
- Be honest about what's not working - self-awareness signals founder quality.
- Write at a 6th-grade reading level. No jargon, no buzzwords, no "leveraging AI to disrupt".

### Common Mistakes

- Applying to every accelerator instead of targeting the best 5-7 fits.
- Writing what you think they want to hear instead of what's true.
- Burying the traction (put numbers in the first sentence).
- Over-explaining the market instead of showing what you've done.
- Sending a polished video instead of an authentic one (YC explicitly says don't).
- Not researching which partners at the program are relevant to your space.

## See also

- `yc-pitch-deck` — accelerator interviews often involve a short investor pitch.
- `fundraising-email` — follow-up communication with program partners.
- `investor-research` — accelerator partners are also investors; apply the same tiering logic.
- `startup-analysis` — validate the idea before applying.
