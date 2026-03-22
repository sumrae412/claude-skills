---
name: plancraft
description: ARCHIVED — Use /debate-team instead. PlanCraft scope-check absorbed into debate-team Tier 1. Auto-tiering handles all review complexity levels.
---

# PlanCraft (Archived)

This skill has been absorbed into `/debate-team` with complexity-based auto-tiering.

**What replaced it:**
- Tier 1 (scope check, DeepSeek only): ~$0.03 — replaces PlanCraft's standalone review
- Tier 2 (dual critic, DeepSeek + GPT-4o): ~$0.08
- Tier 3 (full debate, tri-model + Sonnet Generator + Opus Lead): ~$0.15-0.35

**Invoke:** `/debate-team` — complexity gate auto-selects the appropriate tier.

**Scope-check filtering:** Preserved. `OUT_OF_SCOPE` rejection runs on every DeepSeek call at all tiers.

**PlanCraft's workflow phases** (brainstorming, plan writing, quality gate, involvement modes, execution handoff, docs cleanup) were already superseded by `code-creation-workflow` Phases 1-5 (Phase 3 now split into 3A Requirements Discovery + 3B Edge Cases & Test Planning).

See: `docs/superpowers/specs/2026-03-21-unified-review-skill-design.md`
