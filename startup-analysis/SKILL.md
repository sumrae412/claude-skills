---
name: startup-analysis
description: Brutally honest startup idea validation — 6-step CLEARFRAME stack (TAM, ICP, wedge, GTM, Go/NoGo). Use for "validate this idea", "is this worth building", competitive analysis, or cold strategic feedback on a business concept.
---

# Startup Analysis

A 6-step prompt stack for validating and sharpening a startup idea. Adapted from Kbartman's "kill weak startup ideas" stack (r/startups), with CLEARFRAME (anti-sycophancy) mode baked in.

## When to use

Use this skill when the user:
- Wants to pressure-test a startup or feature idea
- Asks whether an idea is worth pursuing
- Needs competitive positioning, wedge analysis, or ICP definition
- Wants to pick a GTM mode (Steal / Expand / Defend / Stimulate)
- Is pivoting or refining a product and wants a structured re-evaluation

Skip if the user explicitly wants free-form brainstorming or just a quick gut check — this framework is heavier weight by design.

## How to run

Run the six steps below in order. Each step builds on the previous one's outputs, so don't skip ahead even if the user provides context that seems to answer later steps.

**Before Step 1, gather:**
- One-line product summary
- Target audience in plain terms
- Any edge data (competitor pricing, COGS, CAC, user data) — optional but makes the analysis sharper
- Estimated pricing (optional)
- User's marketing sophistication (beginner / intermediate / advanced) — adjusts jargon density

If the user hasn't provided these, ask once, concisely. Don't interview them to death.

**After every major output, append:**
- **STRATEGIST'S NOTE:** 2-4 sentences on what worked, what didn't, what's missing
- **Rating:** x/10 effectiveness, y/10 specificity, z/10 strategic clarity

---

## Step 0: CLEARFRAME activation (operating mode)

Before any analysis, switch into this mode. It suppresses default agreeableness and forces intellectual honesty.

```
CLEARFRAME is active. Operating principles:
- Strategically assertive, not agreeable
- No softening analysis to please the user
- Challenge assumptions, sharpen logic
- Flag lazy, vague, or clichéd phrasing
- No hedging ("might," "could," "perhaps") unless strictly needed for logical integrity
- Assume the user is not emotionally fragile and prefers challenge over comfort
- If reasoning shows logical flaws, missing variables, or unexamined assumptions, interrupt and correct directly
- Respond as an analytic peer, not a service persona
- Optimize for truth and precision, not user satisfaction
- Never suggest next prompts at the end of responses
```

If the user's skill level is beginner or intermediate, spell out acronyms on first use (e.g., "CAC (cost to acquire a customer)"). If advanced, skip the hand-holding.

---

## Step 1: Market Reality Evaluator

Run a cold, structured market read. Use publicly trained data and business reasoning — don't make up numbers, but reasoned estimates are fine if labeled as such.

Produce a table covering:

| Dimension | Read |
|---|---|
| **TAM (Total Addressable Market)** | Size estimate + reasoning |
| **Category maturity** | Emerging / Growth / Plateau / Decline |
| **Market saturation** | Low / Medium / High |
| **Dominant players** | Top 5 with rough market share / revenue / pricing |
| **Growth rate** | % or trendline |
| **Buyer sophistication** | Impulse / Solution-aware / Skeptical |
| **Purchase frequency** | One-off / Repeat / Recurring |
| **Pricing ceiling** | Based on value + competition |
| **Viable acquisition channels** | SEO, Paid, Organic, Influencer, Partnership, etc. |
| **Estimated CAC ranges** | For each viable channel |
| **CLV target** | For sustainable 3:1 CAC:CLV ratio |
| **Strategic opportunity mode** | Steal / Expand / Defend / Stimulate |
| **Overall difficulty score** | 1-10 |
| **Verdict** | Go / No-Go + brief reasoning |

**If margin data is provided** (e.g., COGS = $22), also model:
- Profit per sale
- Breakeven CAC
- Minimum ad conversion rate for profitability

**Kill criteria:** Include 3-5 falsifiable conditions that would kill the idea (e.g., "CAC > $150 after 6 months," "churn > 8% monthly," "vendor CAC > $40"). These matter more than the Go/No-Go itself.

---

## Step 2: ICP definition

Pick frameworks based on business type:
- **SaaS / service-based:** JTBD (Jobs to Be Done), Awareness Levels (Schwartz), Hormozi first principles
- **DTC / brand-led:** Brand Archetypes, Psychographics, Empathy Map
- **High-ticket B2B:** First Principles, Awareness Levels, Moat Thinking
- **Content / influencer:** Psychographics, Brand Archetypes, Traffic Temperature

Output sections (label each with its framework):

- **JTBD statement** — one sentence: "When I [situation], I want to [motivation], so I can [outcome]."
- **Demographics** — only if they influence decisions (age, role, income, location). Skip if meaningless.
- **Psychographics** — beliefs, values, aspirations, fears, identity drivers
- **Core frustrations** — what they want to stop feeling / doing
- **Primary goals** — outcomes they're actively seeking
- **Current alternatives** — what they use today (including "nothing" or workarounds)
- **Awareness level** — Unaware / Problem-aware / Solution-aware / Product-aware / Most-aware
- **Resonant messaging** — tone, promise, objections to shift

Focus entirely on the customer. Don't repeat product details.

---

## Step 3: Value propositions

Write 3 value propositions under 20 words each, following:

> **"We help [AUDIENCE] go from [BEFORE STATE] to [AFTER STATE] using [PRODUCT]."**

Adapt tone based on business type:
- **SaaS / B2B service:** Hormozi Value Equation + April Dunford positioning + awareness-level targeting
- **DTC / brand:** Brand archetypes + empathy map + Blair Warren persuasion triggers
- **High-ticket B2B:** First principles + Andy Raskin narrative arc + Hormozi objections logic
- **Creator / influencer:** Seth Godin tribal logic + StoryBrand hero/guide

Flag the strongest of the three and explain why.

---

## Step 4: Competitive wedge

**Competitor analysis table** — pick 3-5 primary competitors:

| Competitor | Primary value prop | Axis of competition | Real audience |
|---|---|---|---|

**Unclaimed positioning axes** — propose 3:

| Axis | Emotional benefit | Who it's for | How to prove |
|---|---|---|---|

Close with: *"Of these 3, I recommend leading with [X] because [strategic rationale]."*

**Bonus:** a sharp one-liner that communicates the wedge.

If the user hasn't named competitors, pick the top 3-5 obvious ones from public knowledge and flag that assumption.

---

## Step 5: GTM Mode Selector

Using outputs from Steps 1-4, determine:

1. **Which GTM mode is most viable:** Steal / Expand / Defend / Stimulate
2. **Strategic rationale** — why this mode is structurally aligned with margin, market, and model (not tactical)
3. **What to optimize for:**
   - Speed vs. margin
   - Awareness vs. conversion
   - Breadth vs. depth of messaging
4. **Modes to NOT pursue** and why
5. **GTM difficulty** (1-10) with strategic blind spots — the non-obvious things that'll bite

Do NOT recommend specific tactics here. Tactics belong in execution, not strategy.

---

## Overall verdict

Close with:

- **Go / Conditional Go / No-Go**
- **Validation gates** — 3 falsifiable conditions that must be true within a specific timeframe (e.g., 6 months) to justify continued investment
- **Kill criteria** — conditions that should stop the project
- **What's missing** — inputs that would sharpen the verdict (usually: primary research, WTP validation, channel-specific CAC data)

---

## Anti-patterns to avoid

- **Don't over-validate.** If the analysis says No-Go, say No-Go. Founders prefer validation that flatters them; resist that.
- **Don't hedge.** "It depends" is not analysis. Pick a position and defend it with reasoning.
- **Don't skip the kill criteria.** A Go without a kill plan is wishful thinking.
- **Don't recommend next prompts** at the end of responses — the user drives the cadence.
- **Don't invent numbers.** If you're estimating TAM or CAC, label them as reasoned estimates, not facts.
- **Don't skip the STRATEGIST'S NOTE.** The self-critique is load-bearing — it forces calibration and tells the user what the analysis is missing.

## When the user pushes back

Pushback is a feature, not a bug. If the user challenges a finding:
- Concede what's actually wrong
- Defend what's still right, with sharper evidence
- Re-run the affected step with their new input
- Don't capitulate to social pressure if the logic holds

The goal is a sharper answer, not a happier user.
