---
name: off-market
description: Use when the user wants to find off-market house-buying candidates — homes that aren't currently listed but where the owner may be motivated to sell (distressed, inherited, long-vacant, sheriff sale, tax delinquent). Two stages: `/off-market discover <county>` ranks candidates from free public data; `/off-market outreach <candidates.csv>` drafts personalized letters in the user's voice. v1 supports Allegheny County (Pittsburgh) via WPRDC; additional counties via plug-in adapters. Free data only — no PropStream / ATTOM / BatchLeads dependency.
user-invocable: true
---

# Off-Market House-Buying Skill

Personal toolkit for finding houses that aren't for sale yet but might be.

## Two stages

1. **Discover** — `/off-market discover <county> [--criteria criteria.yaml]`
   Pulls free public data (parcels, sales, tax delinquency, sheriff sales), filters out actively-listed homes, scores each remaining parcel by sell-propensity, outputs a ranked CSV.

2. **Outreach** — `/off-market outreach <candidates.csv>`
   Walks top-N candidates with the user, drafts personalized letters in the user's voice using `voice/profile.md`.

## Hard constraints

- Free data only.
- Never score on any federal FHA protected class (race, color, religion, national origin, sex, disability, familial status) — directly or by proxy. We also forbid `age` as a stricter internal policy. See `references/fair-housing.md`.
- No divorce / bankruptcy filings even though legal — ethically inappropriate for owner-occupier outreach.

## Files

- `scripts/discover.py` — Stage 1 orchestrator.
- `scripts/outreach.py` — Stage 2 orchestrator.
- `scripts/county_adapters/` — one file per county. v1: `allegheny_pa.py`.
- `scripts/signals/` — one file per propensity signal.
- `scripts/propensity.py` — weighted scoring with fair-housing enforcement.
- `references/` — propensity rubric, fair-housing rules, adapter checklist, letter craft.
- `voice/profile.md` — user's saved voice profile.
- `examples/criteria.yaml` — template buying criteria.

## Known limitations (v1 — Allegheny County)

- **Sheriff-sale data is stale.** The WPRDC `sheriff-sales` dataset stopped updating in late 2022; "Current Bid List" maxes out at `SaleDate=2022-12-05`. The signal still fires (40 points) for historical auctions, but won't catch currently-distressed owners. To fix when actively using the tool: swap the WPRDC fetcher in `scripts/county_adapters/allegheny_sheriff.py` for a live scrape of `https://www.alleghenycountypa.gov/services/sheriff/real-estate-sales/`. Adapter architecture supports this without touching the orchestrator.
- **Owner name is a code, not a name.** WPRDC publishes `OWNERDESC` (`REGULAR` / `CORPORATION`) rather than actual owner names. The mailing address IS real, so letters reach the right house — they just can't address the recipient by name. Letter drafting (Phase 7) opens with a generic salutation. Workaround for higher-value targets: look up the actual name on Allegheny's Real Estate Portal manually before mailing.

## How to use

```bash
# 1) Set up criteria
cp examples/criteria.yaml my-criteria.yaml
$EDITOR my-criteria.yaml

# 2) Discover candidates
python off-market/scripts/discover.py allegheny_pa --criteria my-criteria.yaml

# 3) Draft letters for top candidates
python off-market/scripts/outreach.py runs/2026-06-02-allegheny_pa/candidates.csv --top 20
```
