# The Debate Technique

A structured framework for surfacing the strongest arguments for and against a product idea using real user evidence. Based on Marily Nika's approach of creating opposing AI agents that debate using forum/review data.

## Why This Works

Traditional user research produces agreeable summaries. The debate technique forces confrontation — a PRO agent must convince a skeptical CON agent using real evidence, surfacing the exact features needed to overcome objections.

## Setup

### Agent PRO (Enthusiastic Early Adopter)
- Believes in the product's potential
- Argues from user enthusiasm, unmet needs, market trends
- Must cite real user opinions found via search
- Goal: prove the product should exist

### Agent CON (Skeptical Pragmatist)
- Questions everything about the product
- Argues from user complaints, existing alternatives, adoption barriers
- Must cite real user concerns found via search
- Goal: find the fatal flaw that kills the idea

## Research Phase

Before the debate, gather evidence:

1. **Search targets** (use WebSearch):
   - `[concept] site:reddit.com` — raw user opinions
   - `[concept] opinions forum` — broader forum discussions
   - `[concept] complaints reviews` — what doesn't work about existing solutions
   - `[concept] vs [alternative]` — how users compare options
   - `[concept] "I wish"` OR `[concept] "I hate"` — emotional signals

2. **Evidence types to collect**:
   - Direct user quotes expressing need or frustration
   - Adoption barriers mentioned by real users
   - Feature requests from forum threads
   - Complaints about existing solutions
   - Privacy/trust/cost concerns

## Debate Format

Run **10+ rounds**. Each round:

```
ROUND [N]:

PRO: [Argument citing real user evidence]
     Evidence: "[user quote or data point]"

CON: [Rebuttal citing real user concerns]
     Evidence: "[user quote or data point]"

PRO COUNTER: [Response to rebuttal]

VERDICT: [CON concedes / CON holds firm / Draw]
```

### Round Topics (suggested order)

1. **Core need** — Does this problem actually exist?
2. **Existing alternatives** — Why not just use [competitor]?
3. **Willingness to pay** — Would users actually pay for this?
4. **Privacy/trust** — What about data concerns?
5. **Adoption friction** — Is the switching cost too high?
6. **Technical feasibility** — Can this actually work reliably?
7. **Target audience size** — Is the market big enough?
8. **Differentiation** — What makes this better, not just different?
9. **Long-term viability** — Will this matter in 3 years?
10. **Deal-breaker features** — What single missing feature kills it?

Add more rounds if important topics remain unresolved.

## Synthesis

After the debate, extract:

### Minimum Feature Set
Features that made CON concede. These are the non-negotiable requirements for product-market fit:
- List each feature
- Note which debate round proved it necessary
- Note the specific concern it addresses

### Unresolved Concerns
Arguments where CON never conceded. These are risks to track:
- List each concern
- Note why PRO couldn't overcome it
- Flag as risk for the PRD

### Key User Evidence
The strongest quotes and data points from both sides — these become ammunition for the PRD and pitch.

## Common Patterns

**Privacy always comes up.** If the product touches personal data, CON will raise privacy. PRO must have a concrete answer (local processing, encryption, data minimization) — "we take privacy seriously" never works.

**"Just use X" is the hardest argument.** When a strong existing alternative exists, PRO must articulate a specific wedge — one thing the product does 10x better, not 2x better.

**Cost sensitivity varies by audience.** B2B buyers accept higher prices for clear ROI. Consumer products face intense price pressure. The debate should calibrate to the target market.
