# Strategy Anchor — `STRATEGY.md` as durable product grounding

<!-- Loaded: Phase 0 Step 1.5 (only if repo-root STRATEGY.md exists) | also consulted Phase 2 Step 0, Phase 3, Phase 4 -->

A short, durable repo-root doc (peer of `README.md`) that captures what the
product is, who it serves, how it succeeds, and where effort is invested.
When present, claude-flow phases read it as grounding so each run doesn't
re-litigate "are we building the right thing?"

Adapted from EveryInc/compound-engineering's `ce-strategy` (the upstream
anchor in their ideate→brainstorm→plan→work loop). See SOURCE at bottom.

## Scope — WHERE this applies

**Downstream product repos with evolving direction** (e.g. courierflow_beta),
NOT claude-flow's own infrastructure repo. claude-flow has a stable mission;
a strategy anchor earns its keep when product direction shifts across
sessions. Treat `STRATEGY.md` as **opt-in per project**: consume it if it
exists, never require or auto-create it.

## What it is (and isn't)

- **Anchor, not plan** — what the product is and *why*. Features belong in
  requirements (Phase 3); schedules belong in the issue tracker.
- **Short is a feature** — a 20-page strategy nobody opens anchors nothing.
  Constrain to a scannable page.
- **Rumelt kernel** (from *Good Strategy Bad Strategy*): diagnosis →
  guiding policy → coherent action. Sections are plain English; the rigor
  lives in the answers, not the headings.

Typical sections: target problem, approach, persona, key metrics, active
tracks; optional milestones / non-goals.

## How claude-flow phases consume it

- **Phase 0 Step 1.5** — load it (if it exists) alongside project identity;
  carry it as durable grounding through later phases.
- **Phase 2 Step 0** — include in the prior-knowledge check; weight
  exploration toward the active tracks / stated approach.
- **Phase 3 (requirements)** — anchor scope decisions to active tracks;
  flag requests that pull away from them.
- **Phase 4 (architecture)** — the design doc flags decisions that diverge
  from the stated approach as explicit trade-offs, not silent drift.

This composes directly with the user's framing-verification guardrails
(Guardrail 5): a stated persona + target problem in `STRATEGY.md` is the
canonical disambiguator for actor-class nouns ("customer" vs "tenant").

## If you author/refresh one (optional `/strategy`-style interview)

The value of `ce-strategy` is **pushback discipline**, not the template:

- Per section, ask the question then push past named anti-patterns —
  slogan-not-strategy ("we delight users"), goal-dressed-as-strategy
  ("grow ARR 30%"), feature-list-as-policy ("we're building X, Y, Z").
- Two rounds of pushback max; if still weak, capture what's given and flag
  the section for next time.
- **Update in place across runs** — don't rewrite confirmed sections; bump
  a `last_updated` frontmatter field, revisit only weak sections.

## When NOT to use

- claude-flow's own repo (stable-mission infra — see Scope).
- Greenfield throwaway / single-session tasks — no direction to anchor.
- Projects where `CLAUDE.md` + `session-handoff` already carry enough
  product context; don't add a third grounding surface that drifts.

---

SOURCE: anchor concept, Rumelt structure, and pushback discipline adapted
from EveryInc/compound-engineering-plugin `ce-strategy`
(https://github.com/EveryInc/compound-engineering-plugin,
`docs/skills/ce-strategy.md`). Triaged via `/articles` → `useful-for` on
2026-06-01.
