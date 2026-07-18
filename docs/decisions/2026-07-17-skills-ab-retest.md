# A/B retest of four model-weakness-compensator skills — 3 retire, 1 keep

**Status:** Decided 2026-07-17 (Summer, Option A). Follows the same-day skills audit ([#232](https://github.com/sumrae412/claude-skills/pull/232), [#233](https://github.com/sumrae412/claude-skills/pull/233)).

## Method

Per Anthropic's skills-audit guidance ("retest skills that compensate for a general weakness of a current model"): for each skill, two subagents ran the **identical task prompt** on the same model (Claude Fable 5) — one instructed to read and follow the skill (including bundled scripts/tools), one barred from reading anything under `~/.claude/skills`. Fixtures had planted ground truth where possible. N=1 per arm; verdicts are directional.

| Skill | Task | Verdict | Deciding evidence |
|---|---|---|---|
| `dependency-auditor` | Audit a fixture package.json seeded with ~9 known CVEs + 1 commercial-license dep | **Retire** | WITH arm: `upgrade_planner.py` crashed (`KeyError: 'by_risk'`), `license_checker.py` returned all-"Unknown/critical" noise, offline CVE DB caught 2/9; findings were model-knowledge with stale fix versions. WITHOUT arm: live OSV.dev batch verification, all planted issues + license flag, current fix versions, honest transitive-deps caveat. |
| `fetch-api-docs` | Stripe customer + trial subscription + webhook module with provenance tagging | **Retire** | WITH arm (chub): pinned API version `2025-02-24` from a curated doc dated 2025-10-28; used `invoice.customer` from memory. WITHOUT arm: fetched docs.stripe.com live, pinned current `2026-06-24.dahlia`, caught the `invoice.subscription` field migration. The skill routed to *staler* data than native doc-fetching. |
| `image-generation` | Text-to-image hero prompt (cozy bookshop at dusk) | **Retire** | Outputs near-identical: both arms produced complementary amber/dusk palette, upper-third negative space for headline copy, concrete focal anchors, equivalent negative prompts. Subject-Context-Style structure is native model behavior now. |
| `vercel-react-best-practices` | Perf-review a fixture component with 9 planted defects | **Keep** | WITH arm: 13 findings = all of WITHOUT's 12 + effect-dependency granularity (`user?.accountId`), `useDeferredValue` for input latency, and an unused-computation catch, with correct SPA/Next rule scoping. Modest, real lift. |

## Notable secondary finding

Skill-following **displaced** better native workflows: the with-skill arms skipped live OSV/Stripe verification *because* the skill prescribed its own (broken or stale) tooling. A compensator skill that under-performs the model's native behavior is net-negative, not neutral.

## Limitations / revisit conditions

- N=1 per arm, single model (Fable 5). A cheaper fleet model (Haiku) might extract more value from image-generation's prompt structure — revisit if Haiku-dispatched image-prompt quality becomes a problem.
- fetch-api-docs' failure is partly the chub cache's staleness; if Context Hub adds reliable freshness guarantees, a thin "prefer chub when fresher than training data" note could return as a CLAUDE.md line (not a skill).
- dependency-auditor's scripts were broken outright; repair was considered and declined — the without-arm's OSV.dev live-query workflow needs no local tooling.

## Follow-up

- `vercel-react-best-practices`: keep; trim generic sections per the 2026-07-17 deep-dive (cluster C) at leisure.
- Raw agent outputs: session transcripts, 2026-07-17 henry session (summarized verbatim in this record's table).
