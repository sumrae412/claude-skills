---
name: investor-research
description: >
  Use when a founder wants to identify, evaluate, or prioritize potential investors for a fundraising
  round. Triggers on: who should I pitch, find me investors, build an investor list, VC targeting,
  angel targeting, qualify my investor list. Outputs a tiered investor table with warm-path suggestions
  and conflict flags.
user-invocable: true
---

# Investor Research

## When to Use

- Founder is preparing to fundraise and needs a target investor list.
- Founder has a list of investors and wants to qualify or prioritize them.
- Founder asks which VCs or angels are a good fit for their stage, sector, or geography.
- Founder wants to understand a specific fund's thesis, portfolio, or decision-making process.

## Context Required

From the user: stage, sector/category, location, current round target (amount), business model,
existing investor relationships or warm connections, geographic preferences, VC-only or angel-only
or both, investors already in conversation, and any firms to explicitly avoid (portfolio conflicts).

## Workflow

1. **Define investor criteria** - based on context, establish filtering parameters: stage match,
   sector focus, typical check size range, geographic relevance, and portfolio conflict exclusions.
2. **Build the raw list** - research investors matching the criteria. For each investor capture:
   firm name, partner name, fund stage focus, sector focus, typical check size, recent fund
   size/vintage, portfolio companies, geographic preference, and source URL.
3. **Check for conflicts** - flag any firm with a portfolio company directly competing with the
   founder's startup. These go on a "conflicts" list, not the target list.
4. **Score and tier** - assign each investor to Tier 1 (strong fit), Tier 2 (good fit), or Tier 3
   (acceptable backfill) using the scoring framework below.
5. **Identify warm paths** - for each Tier 1 investor, suggest how the founder might get a warm
   intro: mutual connections, portfolio founder intros, accelerator networks, or conference overlap.
6. **Deliver the target list** - output a structured, sortable markdown table with tiers and
   recommended outreach order.

## Output Format

```
## Tier 1 - High Priority

| Firm | Partner | Stage Focus | Sector Fit | Check Size | Recent Fund | Conflict? | Warm Path | Notes |
|------|---------|-------------|------------|------------|-------------|-----------|-----------|-------|
```

Followed by a "Conflicts" section listing excluded firms and why.
Followed by a "Research Gaps" section listing anything that could not be verified.

## Frameworks

### Investor Qualification - The 7-Point Filter

1. **Stage fit** - does the firm invest at the founder's current stage? Binary: pass or fail.
2. **Sector focus** - does the firm have a stated thesis or track record in the founder's sector?
   Look at their last 10 investments, not just website copy.
3. **Check size match** - does the firm's typical check size align with what the founder needs?
   A $2B fund rarely writes $500K checks; a $50M fund rarely leads $20M rounds.
4. **Portfolio conflicts** - does the firm already have a company in the same space? The most common
   reason pitches are dead-on-arrival. Check every portfolio company, including quiet ones.
5. **Fund vintage** - is the firm actively deploying from a recent fund? A fund raised 4+ years ago
   is likely in harvest mode. Prefer firms that closed a fund within the last 18 months.
6. **Geographic relevance** - some firms only invest locally or require board seat proximity.
7. **Partner-level interest** - is there a specific partner whose background or public writing aligns
   with the startup? Pitching the right partner matters as much as the right firm.

### Tiering Framework

- **Tier 1:** matches 6-7 criteria. Firm invested in adjacent companies, partner speaks publicly
  about the space, warm intro path exists. Pursue first.
- **Tier 2:** matches 4-5 criteria. Good fit on stage and sector but may lack a warm path or have
  a slightly mismatched check size. Pursue in the second wave.
- **Tier 3:** matches 3 criteria. Acceptable as backfill. Don't spend significant time here until
  Tier 1 and 2 are exhausted.

### Sourcing Investor Information

- **Crunchbase / PitchBook:** fund size, recent investments, portfolio companies.
- **Firm website:** stated thesis, partner bios, blog posts revealing focus areas.
- **Twitter/X and Substack:** many partners publish current interests publicly. Recent posts beat old About pages.
- **SEC Form D filings:** fund size when not publicly disclosed.
- **Portfolio founder back-channels:** the single best diligence on an investor.

### Common Mistakes to Avoid

- **Spraying 200 cold emails** - 30 well-targeted, well-introduced conversations beat 200 cold ones.
- **Ignoring portfolio conflicts** - founders waste weeks pitching firms that will never invest.
- **Pitching the wrong partner** - the wrong partner will pass or deflect internally.
- **Targeting only brand-name firms** - Tier 2 and emerging funds are often faster, more founder-friendly.
- **Not tracking your pipeline** - use a simple spreadsheet: investor name, status, and next action.

### Angel Investor Considerations

- Angels decide faster (days, not weeks) but write smaller checks ($25K-$250K typically).
- Look for angels with operational experience in your sector.
- Angel syndicates (AngelList, etc.) can aggregate small checks into a meaningful allocation.
- Be cautious about taking angel money from potential acquirers or competitors.

## See also

- `fundraising-email` — write targeted outreach once the investor list is built.
- `yc-pitch-deck` — tailor the deck narrative based on what specific investors care about.
- `fundraising` — broader fundraising strategy and process.
- `elevator-pitch` — verbal pitch to deploy at meetings surfaced by investor research.
- `pitch-deck` — tailor the deck narrative to what specific investors care about.
