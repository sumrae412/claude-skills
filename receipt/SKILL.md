---
name: receipt
description: Use when the user says "/receipt", "work receipt", "AI receipt", "give me a receipt", or asks to evaluate, score, or estimate the value of the AI-assisted work just completed. Produces a 6-line conservative honesty audit (finished output / human baseline / AI-assisted time / review required / risk / final value estimate) of the current session's actual shipped work — not drafts, ideas, or unused output.
user-invocable: true
---

# Receipt

Audit the work just completed in this session and produce a conservative receipt the user can use to judge whether AI was worth it.

## When to invoke

- User types `/receipt` or asks "give me a receipt" / "was that worth it?" / "score this session"
- After a deliverable lands (PR merged, file shipped, task completed) and the user wants honest accounting

## How to produce the receipt

Review the actual completed work in this session. Then write the 6-section receipt below. **Be conservative.** Do not count drafts, abandoned approaches, ideas explored, or unused output as completed work — only what was shipped, saved, merged, or accepted.

### Format

```
RECEIPT — <one-line session summary>

1. Finished output
   <What was actually completed and now exists. Cite file paths, PR URLs, or concrete artifacts. If nothing shipped, say so.>

2. Human baseline
   <Conservative estimate of how long this would take the user manually, assuming their normal skill level. Range, not point estimate. Name the slowest sub-task.>

3. AI-assisted time
   <Wall-clock time this session took. If unknown, say "unmeasured — N tool calls, ~M turns." Don't inflate.>

4. Review required
   <What the user still had to check, rewrite, redirect, or fix. Count corrections, AskUserQuestion turns, and rework. If you don't know what they fixed after handoff, say "unknown post-handoff edits.">

5. Risk
   <What could be wrong, incomplete, or misleading in the shipped output. Name specific failure modes — stale assumptions, unverified claims, edge cases not tested, third-party names not grounded. "Low risk" requires evidence, not vibes.>

6. Final value estimate
   <One of: "Not worth using AI" / "Small assist" / "Solid time saver" / "Major time saver" / "Couldn't have done this manually." Justify in one sentence tied to sections 2–5, not section 1.>
```

## Conservative-counting rules

- **Drafts ≠ shipped.** A design doc that was discarded is zero output, not "we explored architecture."
- **Ideas ≠ work.** Brainstorming that didn't produce a saved artifact is zero output.
- **Unused output ≠ value.** Code written but reverted, files written but deleted, PRs closed without merge — zero.
- **Review time counts against AI.** If the user spent 20 min checking a 5-min generation, the AI-assisted time is 25 min, not 5.
- **Risk floor is "medium" by default.** Drop to "low" only if you verified the load-bearing claims (greps ran, tests passed, file content confirmed). Otherwise the receipt overclaims confidence.
- **"Couldn't have done this manually" is rare.** Reserve for cases requiring scale (100+ files), specialized knowledge the user lacks, or speed-to-market windows. Default to "Major time saver" instead.

## Anti-patterns

- Padding section 1 with intermediate steps ("explored 3 options, picked one") — only the picked-one counts.
- Estimating human baseline at the high end to make AI look better — estimate at the user's actual skill level.
- Burying risk in soft language ("possibly", "might want to double-check") — name the specific thing that could break.
- Skipping section 4 because "the user didn't ask for changes" — they may not have reviewed yet. Note that explicitly.
