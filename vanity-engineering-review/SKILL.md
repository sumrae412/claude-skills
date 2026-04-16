---
name: vanity-engineering-review
description: >
  Reviews codebases, architectures, PRs, and plans for vanity engineering — code built for
  ego rather than user value. Produces a structured assessment with V0-V3 severity scores,
  a Requirement-to-Complexity Ratio, and kill criteria. Triggers: "is this over-engineered",
  "complexity audit", "vanity check", "is this necessary", "simplify this", "tech debt review",
  or when you detect unnecessary abstraction, premature optimization, or resume-driven choices.
  Also usable as a Phase 6 reviewer in claude-flow.
---

# Vanity Engineering Review

Identifies code and architecture built to impress rather than to ship. Vanity engineering
increases complexity without proportional capability gain.

**The only legitimate purpose of engineering is to solve a problem someone actually has.**

This skill does not oppose quality or rigor. It opposes engineering that exists to satisfy
the builder rather than the user.

## When to Apply

- Codebase audits (full repo or specific modules)
- Pull request reviews
- Architecture proposals or RFCs
- Technology selection decisions
- Refactoring plans
- "Should we rebuild this?" discussions

---

## Review Process

### Phase 1: Establish the Requirement Anchor

Before examining code, establish what the system needs to do:

1. **Who uses this?** (End users, internal team, API consumers, nobody yet)
2. **What must it do?** (Core jobs-to-be-done — max 5)
3. **What scale does it actually operate at?** (Actual, not projected)
4. **What are the real constraints?** (Regulatory, latency SLAs, integrations)
5. **What is the team size?** (Solo dev? 3-person startup? 50-person org?)

If these cannot be answered, that is itself a vanity signal.

### Phase 2: Detection Scan

Scan against the patterns in `references/detection-patterns.md`. Score each finding:

| Severity | Meaning | Action |
|----------|---------|--------|
| **V0** | Cosmetic — unnecessary but harmless, no maintenance burden | Note and move on |
| **V1** | Drag — ongoing cognitive/maintenance cost without user value | Flag for simplification |
| **V2** | Structural — shapes architecture around vanity | Flag for redesign |
| **V3** | Compounding — forces other code to be more complex | Flag as urgent |

### Phase 3: Produce the Assessment

```
## Vanity Engineering Assessment

### Summary
[What this codebase does vs what it is engineered to do.
The gap is the vanity surface area.]

### Requirement-to-Complexity Ratio (RCR)
[Scale 1-10. 1 = minimal viable. 10 = PhD thesis disguised as CRUD.
Most production systems should score 2-4.]

### Top Findings (max 7)
For each:
- What: The specific pattern
- Where: File/module/component
- Severity: V0-V3
- Why vanity: How it fails "does a user need this?"
- Should be: The simpler alternative
- Kill cost: Effort to simplify (hours/days)

### Vanity Debt Estimate
[Person-hours of maintenance per month attributable to vanity
patterns rather than actual requirements.]

### The Hard Question
[One direct question the team needs to answer honestly.
Example: "If you deleted the plugin system and hardcoded the
three integrations you actually use, what would you lose?"]
```

### Phase 4: Kill Criteria

For every reviewed system, generate kill criteria using `references/kill-criteria-template.md`.
This prevents vanity from recurring.

---

## Anti-Vanity Quick Checks

Use these as a fast screen before a full review:

| Question | Red flag answer |
|----------|----------------|
| How many files for how many features? | >10 files per feature |
| Single-implementation interfaces? | Any abstract class with one child |
| Config longer than code it configures? | Yes |
| Can a junior maintain this? | "It takes a while to understand" |
| Why this technology? | "We wanted to try it" |
| What would you lose by simplifying? | Long pause |

---

## Scope

This skill reviews — it does not refactor. Output is a diagnostic report.
If the user wants to act on findings, hand off to implementation skills.

## Next Steps

- Use `/engineering:tech-debt` for prioritized remediation planning
- Use `/engineering:architecture` for ADR documentation of simplification decisions
