# Live LLM pricing sources

Model pricing changes frequently. The Claude-family cost ratios in `SKILL.md` ("Opus ≈ 5× Sonnet ≈ 3× Haiku" and the per-tier cost columns) are stable shape-of-relationship anchors, but absolute prices and cross-vendor comparisons need a live source.

---

## Comparison sites

**LLM Price Check** — https://llmpricecheck.com/
Side-by-side API pricing for OpenAI, Anthropic, Google, Meta, Mistral, Cohere, AWS, Fireworks, Deepinfra, Perplexity, Groq, Cloudflare, Replicate, and others. Sortable by quality, context window, input/output per million tokens, knowledge cutoff. Saved from Mem 2026-05-20.

Use when:
- Considering routing some workload to a non-Claude model and need a quality-vs-cost snapshot
- Re-verifying Claude pricing ratios in `SKILL.md` after Anthropic publishes a new model
- Comparing context-window cost across vendors

## Notable non-Claude data points

**Cursor Composer 2.5** (Moonshot Kimi K2.5 base + heavy synthetic-RL post-training) — $0.50 input / $2.50 output per million tokens. ~10% of Opus 4.7 / GPT-5.5 prices at comparable SWE-Bench Multilingual (79.8%). Saved from Mem 2026-05-20.

Source: https://cursor.com/blog/composer-2-5

The data point matters because it demonstrates that open-source bases with aggressive RL post-training can rival closed coding models at a fraction of the cost — relevant when evaluating whether to route mechanical / high-volume coding work outside the Claude family.

## Re-check cadence

Pricing tables in this file or in `SKILL.md` should be re-verified against the live sources above when:
- A model in the Claude family ships (Opus / Sonnet / Haiku version bump)
- A vendor publishes a price-cut announcement
- This file is more than 90 days stale (check `git log -1 --format=%ci references/live-pricing-sources.md`)
