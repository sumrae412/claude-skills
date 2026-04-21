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

