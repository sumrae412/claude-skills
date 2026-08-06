# Off-Market Skill — Design

**Date:** 2026-06-02
**Status:** Approved (Summer, 2026-06-02)
**Author:** Brainstorming session with Claude (this conversation)
**Implementation plan:** _to be authored next via `superpowers:writing-plans`_

## Problem

Buying a house on the open market is increasingly a bidding-war scrum, while the homes a buyer actually wants often never list. The Notion brief [Off-Market House Buying Agent](https://loud-particle-7d0.notion.site/Off-Market-House-Buying-Agent-3728d2b9402b805fb2afc78fe3749c06) frames the productized version. This design is the **personal-use slice** of that idea: a Claude Code skill that helps Summer find motivated-seller candidates in her search area (Pittsburgh / Allegheny County initially, expanding to NY / OH / WV) using only free public data.

## Scope decisions (locked during brainstorming)

| Question | Answer |
|---|---|
| Use case | Toolkit for future use — re-runnable, not a one-shot |
| Data appetite | Free only |
| Form factor | Claude Code skill in `~/claude_code/claude-skills/off-market/` |
| Search shape | **Discovery** of motivated-seller candidates (distressed / inherited / long-vacant) |
| Geography | Allegheny County (Pittsburgh) for v1; PA / NY / WV / OH via plug-in adapters later |
| v1 signal set | Lean (5 signals — see Propensity Rubric below) |

## Non-goals

- No paid data integrations (PropStream / ATTOM / BatchLeads) in v1. Architect plug-in points so they can be added without a refactor, but ship $0 to run.
- No web UI / map UX. CLI / skill invocation only.
- No mailing automation (no Lob integration). Skill produces letter drafts as markdown; physical mailing is a manual export.
- No deal-side support (comps, negotiation scripts, solicitor referral) in v1. That's a Phase 2 conversation if she ever bites.
- No targeting on any HUD-protected class, directly or by proxy.

## Architecture

```
~/claude_code/claude-skills/off-market/
├── SKILL.md                      # Router; explains discover + outreach stages
├── scripts/
│   ├── discover.py               # Stage 1 orchestrator
│   ├── outreach.py               # Stage 2 orchestrator
│   ├── county_adapters/
│   │   ├── allegheny_pa.py       # v1 adapter — WPRDC datasets
│   │   ├── _generic.py           # Assessor-only fallback
│   │   └── README.md             # Checklist + Allegheny worked example
│   ├── listings/
│   │   └── zillow_redfin.py      # Active-listings scrape (subtract)
│   ├── signals/
│   │   ├── absentee.py
│   │   ├── tenure_equity.py
│   │   ├── delinquency.py
│   │   ├── sheriff_sale.py
│   │   └── probate_name.py       # "Estate of / Heirs of" pattern
│   ├── propensity.py             # Weighted scoring (rubric below)
│   └── voice_capture.py
├── references/
│   ├── propensity-rubric.md
│   ├── fair-housing.md           # HUD protected classes; enforcement
│   ├── adding-county-adapter.md
│   └── letter-craft.md
├── voice/                        # Voice samples + saved profile
└── examples/
    ├── criteria.yaml             # Template buying criteria
    └── allegheny-pittsburgh.yaml # Filled-in example
```

### Stage 1 — `/off-market discover <county> [--criteria criteria.yaml]`

1. Load county adapter; fetch parcels + sales + tax delinquency + sheriff sales.
2. Fetch active listings via Zillow / Redfin scrape → subtract from candidate set.
3. Compute per-parcel signals: `absentee`, `years_owned`, `equity_estimate`, `tax_delinquent`, `sheriff_sale_scheduled`, `probate_name_pattern`.
4. Apply hard filters from `criteria.yaml` (beds, lot, year built, price band, neighborhood).
5. Score propensity (see rubric).
6. Output `runs/<date>-<county>/`:
   - `candidates.csv` — full ranked table.
   - `candidates.md` — top 20, human-readable, with Street View URLs and per-row reason codes.
   - `health.md` — per-source fetch health (so a stale-cache run is obvious).

### Stage 2 — `/off-market outreach <candidates.csv>`

1. Walk top-N candidates with Summer; she flags manual signals (visible disrepair / overgrown from Street View).
2. Use voice profile + per-candidate context to draft a letter per address.
3. Output `runs/<date>-<county>/letters/<address>.md`, print-ready.

### Why two stages

- **Independent** — re-run drafting against the same `candidates.csv` with different voice / season / opener.
- **Failure-isolated** — a flaky scraper doesn't block a drafting session.
- **Cost-shaped** — Stage 1 is slow (network-bound); Stage 2 is fast (LLM-bound).

## Propensity rubric (Lean v1)

Each candidate scored 0–100. Weights and reason codes surfaced per row.

| Signal | Weight | Reason code |
|---|---|---|
| Sheriff sale scheduled (auction date set) | 40 | `sheriff_sale:<YYYY-MM-DD>` |
| Tax-delinquent | 5 base + 0.5 per $1k owed (cap 25) | `tax_delinquent:$<amount>` |
| Owner name matches `Estate of` / `Heirs of` / `, Deceased` | 20 | `probate_name_pattern` |
| Absentee owner (mailing state ≠ property state) | 10 | `absentee:<owner_state>` |
| Long tenure (≥20 yrs) AND equity ≥ 60% of est. value | 10 | `long_tenure_high_equity:<years>` |

**Cutoffs:**
- `<15` → drop
- `15–39` → "worth a letter"
- `40–69` → "high priority"
- `≥70` → "act this week"

**Hard filters (applied before scoring):**

- Currently listed (Zillow/Redfin) → excluded.
- Fails `criteria.yaml` → excluded.
- LLC owner with >5 properties → flagged `professional_investor` but kept (may be tired landlord).

## Fair-housing enforcement

`references/fair-housing.md` codifies HUD protected classes: race, color, religion, national origin, sex, disability, familial status, age.

- `propensity.py` imports `FORBIDDEN_FIELDS = frozenset({"race", "ethnicity", "religion", "sex", "family_status", "disability", "age", "national_origin"})`.
- A unit test grep-asserts no scoring expression references any of these fields, directly or via a known proxy column.
- The skill refuses CLI flags or `criteria.yaml` keys that name a protected class.
- Neighborhood targeting is allowed by polygon / zip / boundary — never by demographic descriptor.
- Divorce filings and bankruptcy filings are deliberately **excluded** from v1 signals on ethical grounds (legal but creepy for an owner-occupier outreach).

## Data flow

```
criteria.yaml ─┐
               ├──► discover.py ──► allegheny_pa adapter
county name   ─┘         │              ├── parcels (WPRDC CSV)
                         │              ├── sales (WPRDC)
                         │              ├── tax delinquency (annual list)
                         │              └── sheriff sales (web scrape)
                         │
                         ├──► listings/zillow_redfin → active list (subtract)
                         │
                         └──► propensity.py ──► runs/2026-06-02-allegheny/
                                                  ├── candidates.csv
                                                  ├── candidates.md
                                                  ├── health.md
                                                  └── street-view-links.md

candidates.csv ──► outreach.py ──► voice profile ──► letters/<address>.md
```

**Caching:**

- Parcel data: 30 days.
- Listings: 7 days.
- Delinquency / sheriff sales: 7 days.
- Storage: `~/.cache/off-market/<county>/`.
- Force refresh: `--no-cache`.

## Error handling

- Each scraper wrapped in try/except; missing fields → `unknown`, never crash a run.
- Per-source health surfaced in `health.md`:
  ```
  ✓ parcels (124,331 rows, fetched 2026-06-02 09:14)
  ✓ sales (last 90 days, 2,047 rows)
  ✓ delinquency (annual 2026 list, 8,213 rows)
  ✗ sheriff sales (timeout — using cache from 2026-05-28)
  ✓ listings (Zillow active, 1,432 rows)
  ```
- Reason codes alongside each score so stale-data scores are auditable.
- Network failures never kill a run — partial data + clear health report.

## Testing

- **Unit:** `propensity.py` deterministic (fixture row → fixed score); fair-housing forbidden-field assertion; criteria.yaml schema validation.
- **Integration:** one live fetch against WPRDC parcels endpoint asserting non-empty + expected columns; gated on `RUN_LIVE_TESTS=1` so CI without internet is clean.
- **Snapshot:** letter-drafting prompt → output stability check, so future prompt edits surface as diffs.
- **No paid services in any test path.**

## Signals deferred (Tier 1+ candidates for v1.1)

- Pre-foreclosure / Notice of Default / Lis Pendens (county recorder scrape).
- Code violations (Pittsburgh PLI via WPRDC).
- Vacant property registry (Pittsburgh maintains one).
- Tired-landlord join (multi-property + repeat violations + eviction filings as plaintiff via UJS Portal).
- Allegheny estate filings (Orphans' Court) + Pittsburgh Legal Journal probate notices.

## Signals explicitly off the roadmap

- Divorce filings, bankruptcy filings — legal but ethically inappropriate for an owner-occupier outreach.
- USPS per-address vacancy — only census-tract aggregates are free.
- Anything keyed to a HUD protected class, directly or via proxy.

## Open questions for the implementation plan

1. WPRDC dataset IDs and column names — pin during implementation; cache snapshots in `references/wprdc-schema.md`.
2. Zillow / Redfin scraping fragility — pick a respectful rate limit (≥2s/request, real User-Agent) and define a circuit breaker.
3. Voice profile schema — start with 3 sample paragraphs Summer wrote, extract tone/cadence rules, save to `voice/profile.md`.
4. Street View URL format — confirm static URL pattern + whether an API key is strictly necessary for `https://maps.google.com/?cbll=<lat>,<lng>&layer=c`.
5. `criteria.yaml` schema — beds, baths, sqft range, lot range, year-built range, price-band (use Zestimate or assessor value?), neighborhood polygon vs zip list, must-haves, deal-breakers.
