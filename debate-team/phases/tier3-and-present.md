### Step 4.5: Devil's Advocate Challenge (Tier 3 Only)

<SKIP-CONDITION>
Skip for Tier 1 and Tier 2 reviews — the cost of an extra agent pass isn't justified for simple reviews.
</SKIP-CONDITION>

For Tier 3 (full debate), challenge the synthesis before presenting to the user. This catches false positives that survived synthesis — style preferences masquerading as bugs, fixes that introduce worse problems, or groupthink where multiple critics echo the same flawed reasoning.

Dispatch a **haiku** agent:

```
Use Task tool:
  subagent_type: general-purpose
  model: haiku
  prompt: |
    You are a devil's advocate reviewer. Your job is to challenge these ADOPT decisions:

    [list of ADOPT findings with reasoning from Step 4]

    For each ADOPT, argue why it might be WRONG:
    - Is this a false positive disguised as a real issue?
    - Does the "fix" introduce worse problems than the original?
    - Is this a style preference masquerading as a bug?
    - Did multiple critics flag this for the same flawed reason (echo, not independent signal)?

    Be adversarial. Only flag findings where you have >70% confidence the ADOPT is wrong.
    Output format: one line per challenged finding with your counter-argument.
    If all ADOPTs are solid, say "No challenges — findings are sound."
```

**Triage devil's advocate output:**
- Challenge is convincing → downgrade ADOPT to DEFER (let user decide)
- Challenge is weak → keep ADOPT (finding survived adversarial review)
- **Max 2 downgrades per round** — prevents wholesale reversal of the synthesis

**Cost:** ~$0.01 per haiku pass. Negligible relative to the Tier 3 cost of ~$0.15-0.35.

### Step 5: Present to User

Show the user:
1. **The final artifact** (with all ADOPT fixes applied)
2. **The Changelog** (adopt/reject/defer with reasoning)
3. **Any DEFER items** that need user decision
4. **Devil's advocate challenges** (if any ADOPTs were downgraded, show the counter-argument)

### Step 6: Auto-Fix Loop (PR Review Only)

If reviewing a PR and CRITICAL findings were adopted:

1. Assign fixes to Generator (Sonnet teammate)
2. Generator commits fixes
3. Re-run critics on updated diff
4. **Max 2 cycles** — if unresolved after 2, escalate to user

