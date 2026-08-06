# Spend Alerts — Ready-to-Paste Ruleset

Borrowed from Ameya Kanitkar, "The CTO's Playbook for Managing AI Coding Spend" ([Larridin, 2026-05-13](https://larridin.com/blog/the-ctos-playbook-for-managing-ai-coding-spend)). Tuned for solo and small-team usage; calibrate thresholds to your own baseline before deploying.

## Why these five (not three, not ten)

The article's central claim: AI coding spend is reaching 2–4% of headcount budgets (8–10% for AI-first teams), and unsupervised agents can burn thousands of dollars in hours. Five alerts cover the four failure modes that actually produce surprise bills — spike, drift, creep, ceiling — plus one early-warning signal on the monthly burn-down. Fewer than five misses one of the modes; more than five gets ignored.

## The five alerts

| Alert | Trigger | Failure mode it catches |
|---|---|---|
| **Spike** | Daily spend > 3× the 7-day rolling average | Runaway loop, prompt-injection cost amplification, accidental Opus routing |
| **Burst** | Single session > $N (set per project) | One job goes wide — fan-out without a budget cap |
| **Mix drift** | Sudden 80%+ shift to frontier-tier models | Router fell through to default, or a new feature bypassed routing |
| **Token-per-PR creep** | Tokens-per-merged-PR trending up week-over-week with no quality lift | Prompt bloat, cache misses, context leak — silent regression |
| **Burn-down** | Monthly spend crosses 60% of quarterly budget by week 6 | Pace problem — you'll blow the ceiling unless you cut now |

Sample thresholds for one-person setups (calibrate to your baseline): **Spike** at 3× rolling avg or $20/day, whichever is lower; **Burst** at $10/session for personal projects, $50 for production agents; **Burn-down** at 60% of the quarter by week 6.

## Why quarterly, not annual

Model prices and quality tiers shift every 4–8 weeks. An annual budget set in January is fiction by April. Re-baseline each quarter against (a) current pricing for the models you actually call, (b) last quarter's actual token-mix, (c) any new feature that changed the call pattern. Treat the quarter ceiling as a hard stop and the alerts as the tripwires before you hit it.

## AI gateway / proxy comparison

When direct-to-provider keys become unmanageable (per-key limits don't scale; spend visibility is per-provider-dashboard; routing rules live in app code), move to a proxy layer.

| Tool | Best for | Tradeoff |
|---|---|---|
| **[LiteLLM](https://github.com/BerriAI/litellm)** | OSS, self-host, broad provider coverage (100+) | You operate the proxy; latency adds a hop |
| **[OpenRouter](https://openrouter.ai)** | Hosted, dead-simple multi-provider; per-request budget caps | Vendor lock on routing logic; less observability than purpose-built |
| **[Portkey](https://portkey.ai)** | Production-grade gateway + observability + guardrails | Pricier; aimed at teams, not solo |
| **[Helicone](https://helicone.ai)** | Logging + cost analytics first, gateway second | Less routing power than LiteLLM/Portkey |

Decision shortcut: solo + want control → LiteLLM. Solo + want simple → OpenRouter. Team + need governance → Portkey. Anyone who just needs visibility before deciding → start with Helicone, swap later.

## How to apply

1. Pick the 2–3 alerts that match your actual failure modes (spike + burst is the floor; add token-per-PR if you ship to a repo).
2. Wire to whatever notification channel you actually read (Slack DM, Telegram, email). If it goes to a channel you mute, the alert isn't doing work.
3. Re-tune thresholds monthly until they stop firing on noise. False positives erode the signal faster than missing alerts erodes the budget.
4. At quarter-end, audit which alerts actually fired and whether each catch was real. Drop alerts that never fire; tighten ones that fire too late.

## Composes with

- This skill's "Cost-discipline triad" — alerts catch what gets through the meter/cap/path-filter layers.
- `/evals` skill's combined-meter pattern (`cost_usd_total` checked before each next call) — alerts are the safety net when the meter itself silently misbehaves.
- `/token-economy` — tactical per-tool-call discipline; this is the strategic backstop.

## Source

Ameya Kanitkar, "The CTO's Playbook for Managing AI Coding Spend," Larridin, 2026-05-13.
