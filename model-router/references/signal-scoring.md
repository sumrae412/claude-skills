# Signal Scoring — Detailed Algorithm

This file holds the full weighted-signal table for Step 2 of the model-router decision algorithm. Loaded on-demand when a routing decision is ambiguous and needs explicit scoring; the compact tier-to-model lookup in `SKILL.md` covers ~80% of cases without needing this detail.

---

## When to load this file

- A task's complexity is genuinely ambiguous between two tiers
- Signals conflict (e.g., "single file" pushes trivial, but "new feature" pushes complex)
- You need to explain a routing decision in detail (audit trail, user pushback, debugging)

For obvious cases ("rename a variable" → trivial, "design auth system" → architectural), skip this file and route directly from the `SKILL.md` lookup.

---

## Weighted signal table

Sum hits within a tier; assign to the lowest tier whose threshold is met. Signals are matched against the user's request text and the inferred task context (files mentioned, scope, change type).

| Tier | Signal | Weight |
|---|---|---|
| trivial | typo, spelling fix | +3 |
| trivial | rename variable | +3 |
| trivial | fix lint error | +3 |
| trivial | update comment | +2 |
| trivial | format code | +2 |
| trivial | single file mention | +1 |
| simple | fix bug | +2 |
| simple | add validation | +2 |
| simple | refactor function | +2 |
| simple | write test for | +2 |
| simple | update config | +1 |
| complex | new feature | +2 |
| complex | multiple files | +2 |
| complex | API endpoint | +2 |
| complex | database migration | +2 |
| complex | integration | +1 |
| architectural | system design | +3 |
| architectural | architecture | +3 |
| architectural | security audit | +3 |
| architectural | major refactor | +2 |
| architectural | performance optimization | +2 |
| architectural | breaking change | +2 |

**Thresholds:** trivial ≥ 3 · simple ≥ 2 · complex ≥ 2 · architectural ≥ 2

---

## Tier → model mapping

| Tier | Model | Relative input cost |
|---|---|---|
| trivial | Haiku 4.5 | 1× |
| simple | Sonnet 5 | 3× |
| complex | Sonnet 5 | 3× |
| architectural | Opus 4.8 | 5× Haiku / ~1.7× Sonnet |

---

## First-match precedence within tier

Evaluate trivial → simple → complex → architectural. If a task scores into trivial AND complex (e.g., "fix typo in auth.py, part of a multi-file feature" — scores +3 trivial AND +2 complex), the trivial threshold fires first and wins.

This biases toward cheaper models when signals are mixed — escalation after the fact is cheaper than over-spend. If the user pushes back ("actually this is more complex than that"), apply the manual override and re-route.

---

## Worked ambiguous cases

**Case A: "Fix the bug in the auth module — it's just a one-line change"**

- Signals: `fix bug` (+2 simple), `single file mention` (+1 trivial)
- Trivial sum = 1 (below threshold of 3) — does not fire
- Simple sum = 2 (meets threshold) — fires
- **Result:** simple → Sonnet 5
- Note: the "one-line change" framing tempts trivial, but `fix bug` is the dominant signal. Bugs require reasoning even when the diff is small.

**Case B: "Add a new feature to handle Stripe webhooks across the payment service and the audit log"**

- Signals: `new feature` (+2 complex), `multiple files` (+2 complex), `integration` (+1 complex)
- Complex sum = 5 (well above threshold of 2) — fires
- Architectural sum = 0 — does not fire
- **Result:** complex → Sonnet 5
- Note: integrations *can* be architectural if they introduce a new auth or data model, but "handle Stripe webhooks" is pattern-execution, not system design. Apply Step 4 modifier "+1 complexity (down-shift)" if the codebase has well-established webhook patterns.

**Case C: "Audit the auth flow for security issues and refactor anything risky"**

- Signals: `security audit` (+3 architectural), `major refactor` (+2 architectural)
- Architectural sum = 5 (above threshold) — fires
- **Result:** architectural → Opus 4.8
- Override check: "security audit" matches Step 3 override "Security or vulnerability task" → forces Opus regardless of score. Same answer, but if scoring had landed on simple/complex, the override would still escalate.

---

## When the score feels wrong

If the algorithm produces a tier that feels off, three diagnostic questions:

1. **Did Step 0 fire?** If context > 60K, `longContext` mode wins regardless of complexity. Re-check Step 0 first.
2. **Is there a mode signal you missed?** `think` mode (Plan Mode active, "think carefully") or `subagent-fleet` mode preempts default-mode scoring entirely.
3. **Should Step 3 fire?** Override rules (security, production, irreversible) trump complexity score. Re-read the user's request for override triggers.

If none of the three apply and the score still feels wrong, that's a calibration signal — note the case in `docs/decisions/2026-05-17-model-router-progressive-disclosure.md` so the weights can be revisited.
