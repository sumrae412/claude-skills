# Competitor Teardown Prompt (Harvard Case Study Method)

A reusable prompt for Phase 4 (Competitive Wedge) when the user wants a structured teardown of a single competitor or analogue company. Output feeds the competitor table and the structural-incumbent-loses-this-fight check.

Source: Tom Bilyeu, 2026-05. Adapted for CLEARFRAME — strip the prompt's hype, keep the four-section spine.

## When to use this prompt

- Phase 4 already named the competitor, but the user wants a deeper teardown before picking the wedge axis.
- The user asks for an "analogue" — a non-direct competitor whose pattern transfers (e.g., "analyze how Linear took share from Jira").
- A pivot is on the table and the user wants to learn from one specific predecessor before committing.

Skip when:
- The competitor was already analyzed in a prior session (read the file, don't re-prompt).
- Phase 4 needs comparison across 3+ competitors (use the competitor table, not the case-study format).

## The prompt

> Analyze **[company name]** using the Harvard Business School case-study method. Use real numbers when you have them. Don't summarize — analyze.
>
> ### Situation
> - What market did this company enter and what made it broken?
> - What did customers actually want that wasn't being delivered?
> - Who were the existing players and why couldn't they solve it?
>
> ### Decisions
> - What were the 3–5 critical decisions the founders made?
> - What did everyone else say was impossible or stupid?
> - What did they bet on that turned out to be right?
>
> ### Execution
> - How did they get from zero to first revenue?
> - What broke as they scaled, and how did they fix it?
> - What did they refuse to do even when pressured?
>
> ### Outcome
> - What pattern made this work that I could apply?
> - What would I do differently if I were running it today?
> - What does this teach me about my own business?
>
> End with: **"The single most transferable lesson from [company] for someone building [my business type] is _____."**

## How to use the output

The closing sentence is the load-bearing line — it's what Phase 4 actually uses. If the output ends with a generic platitude ("focus on the customer"), the teardown wasn't sharp enough. Re-prompt: *"Be specific. Name the constraint or insight, not the value."*

Feed the four sections into:

- **Situation** → Phase 4 competitor-table "current behavior / status quo" row for this competitor.
- **Decisions** → bigwig-fight reframe (what structural choice made the incumbent lose this fight?).
- **Execution** → Phase 5 GTM mode selection (their first-revenue path is one option for yours).
- **Outcome** → the wedge one-liner test (does our axis explain why a similar pattern would work here, or only why theirs worked there?).

## When the analogue is not a competitor

Useful pattern: when the competitor table is sparse but the user wants pressure-testing, swap a structural analogue. Linear → Jira analogue for any "vertical SaaS replacing horizontal incumbent" pitch. Calm → iOS Health analogue for any "vertical wellness app vs platform feature" pitch. The four-section spine still works; replace `[company]` with the analogue.
