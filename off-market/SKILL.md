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
- Never score on any HUD protected class (race, color, religion, national origin, sex, disability, familial status, age) — directly or by proxy. See `references/fair-housing.md`.
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

## How to use

```bash
# 1) Set up criteria
cp examples/criteria.yaml my-criteria.yaml
$EDITOR my-criteria.yaml

# 2) Discover candidates
python -m off-market.scripts.discover allegheny_pa --criteria my-criteria.yaml

# 3) Draft letters for top candidates
python -m off-market.scripts.outreach runs/2026-06-02-allegheny_pa/candidates.csv --top 20
```
