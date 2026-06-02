# Adding a County Adapter

A county adapter is the unit of geographic expansion for this skill. Each adapter encapsulates one county's free public-data quirks behind a uniform contract, so the rest of the pipeline (`discover.py`, `propensity.py`, `outreach.py`) doesn't have to know whether you're in Pittsburgh or Cleveland.

## The contract

Every county adapter lives at `scripts/county_adapters/<name>.py` and must export a class with this shape:

```python
class CountyAdapter:
    def load(self, criteria: Criteria) -> list[Parcel]:
        """
        Fetch and assemble parcels for this county, enriched with all
        available signals, with hard filters from `criteria` applied.

        Returns a list of `Parcel` objects with as many of the following
        fields populated as the county's data sources support:
          - parcel_id, address, owner_name, owner_mailing  (required)
          - last_sale_date, last_sale_price, assessed_value
          - lot_sqft, beds, baths, year_built
          - tax_owed_usd            (None if no delinquency data)
          - sheriff_sale_date       (None if not scheduled)
        """
```

The adapter is responsible for:

1. Fetching parcel data from the county assessor (or equivalent).
2. Fetching sales history (the propensity scorer needs `years_owned` and `equity_pct`).
3. Fetching tax-delinquency data (annual list is fine — most counties publish one).
4. Fetching sheriff-sale / foreclosure-auction data (county sheriff's office, usually).
5. Applying hard filters from `criteria.yaml` (beds, sqft, lot, year built, price band, zips).
6. Returning a clean `list[Parcel]` for the rest of the pipeline to score.

## What a "good" adapter pulls

A complete adapter pulls four data feeds:

| Feed | Source pattern | Cache TTL |
|---|---|---|
| Parcels | County assessor CSV / API | 30 days |
| Sales | County recorder or assessor sale history | 30 days |
| Tax delinquency | County treasurer annual list | 7 days |
| Sheriff sales | County sheriff's office, weekly auction list | 7 days |

Optional / Tier 1+ feeds an adapter can add later:

- Code violations (city housing department).
- Vacant-property registry (some cities maintain one).
- Probate filings (Orphans' Court or equivalent — augments the name-pattern signal with hard cases).
- Pre-foreclosure notices / Lis Pendens (county recorder).

A minimally viable adapter ships with just parcels + sales. The other two unlock the highest-weight signals (sheriff sale, tax delinquency); without them the rubric still works but recall drops sharply.

## Canonical worked example: Allegheny PA (WPRDC)

The reference implementation lives at `scripts/county_adapters/allegheny_pa.py`. It targets Allegheny County, Pennsylvania (Pittsburgh) and uses the Western Pennsylvania Regional Data Center as its primary feed.

**Data sources used:**

| Feed | URL pattern | Notes |
|---|---|---|
| Parcels | `data.wprdc.org/dataset/property-assessments` | CSV download; ~600k rows countywide. |
| Sales | `data.wprdc.org/dataset/real-estate-sales` | Joinable to parcels on `PARID`. |
| Tax delinquency | Annual delinquent-tax list (county treasurer, posted as CSV via WPRDC most years) | Posted ~April each year for prior year. |
| Sheriff sales | `alleghenycountypa.gov/services/sheriff/real-estate-sales/` | HTML scrape; auction list updates weekly. |

**Adapter responsibilities:**

1. Fetch parcels CSV (via `httpx`, cached 30 days).
2. Fetch sales CSV (cached 30 days), build `parcel_id → last_sale_date / last_sale_price` map.
3. Fetch delinquency list (cached 7 days), build `parcel_id → tax_owed_usd` map.
4. Fetch + parse sheriff-sale HTML (cached 7 days), build `parcel_id → sheriff_sale_date` map.
5. Join all four into `Parcel` objects.
6. Apply `criteria` hard filters (zips, beds, sqft, lot, year built, price band) early to keep the working set small.
7. Return `list[Parcel]`.

**Gotchas specific to Allegheny:**

- WPRDC parcel IDs (`PARID`) are zero-padded — keep them as strings, not ints.
- The assessor's mailing-address column splits city/state/zip across multiple fields; normalize before comparing to the property address for the absentee signal.
- Sheriff-sales HTML structure changes occasionally; the scraper is fixture-tested and live-test-gated on `RUN_LIVE_TESTS=1`.

## How to add a new county

1. Copy `allegheny_pa.py` as the starting skeleton.
2. Replace each fetcher (`fetch_parcels`, `fetch_sales`, `fetch_delinquency`, `parse_sheriff_sales`) with the local equivalents. If a feed doesn't exist in your county yet, the adapter should still work — just leave the corresponding field as `None` on each Parcel.
3. Save fixture rows from each new data source under `tests/fixtures/<county>_<source>.{csv,html}`.
4. Write fixture-driven tests for each fetcher.
5. Wire the new class into `discover.py`'s adapter registry (a dict mapping county name → adapter class).
6. Add a sample `examples/<county>-<city>.yaml` criteria file.

The propensity scorer, listings subtraction, and letter drafting all just work — they only see `Parcel` objects, not county-specific data.
