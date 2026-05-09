## Cost Budget

| Tier | Critics | Cost per round | With Claude batch | Token cap |
|------|---------|---------------|-------------------|-----------|
| 1 (Scope Check) | DeepSeek only | ~$0.03 | ~$0.03 (no batch) | 15,000 |
| 2 (Dual Critic) | DeepSeek + GPT-4o (Architecture OR Completeness) | ~$0.08 | ~$0.13 (+Claude batch) | 15,000 per critic |
| 3 (Full Debate) | DeepSeek + GPT-4o (role-routed) + Haiku (conditional) + Sonnet Generator + Opus Lead | ~$0.15-0.35 | ~$0.22-0.40 (+Claude batch) | 15,000 per external critic |

Claude batch adds ~$0.05 per round (2 Sonnet reviews at 50% batch discount).
Net cost increase per round is modest; provides a third independent model perspective.

- Max per feature (3 full debate rounds): ~$1.20
- Tier 1 drops GPT-4o entirely — acceptable for 1-2 file changes
- GPT-4o cost is the same regardless of role (Architecture vs Completeness) — the routing only changes the prompt, not the model or token cap

## Operational fallbacks

**GPT-4o TPM rate-limit (HTTP 429) on large plan artifacts:** Plans/specs ≥1,000 lines submitted as `--plan-file` can exceed OpenAI's per-minute token quota even on paid org tiers, blowing both attempts of a Tier 3 dispatch. **Fallback:** drop to Tier 2 with DeepSeek + Sonnet-as-judge (the Sonnet teammate doing the synthesis fills the architecture-and-completeness role GPT-4o would have provided) instead of waiting out the rate-limit window. This is a clean substitute, not a degraded one — a single external critic + Sonnet judgment beats a stalled review. Hit 2026-05-08 reviewing a 1,373-line greenfield build doc; both GPT-4o attempts 429'd 60 seconds apart.

