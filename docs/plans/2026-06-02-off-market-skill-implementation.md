# Off-Market Skill — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use @superpowers:executing-plans to implement this plan task-by-task. Each task is TDD: write failing test → run to confirm fail → minimal impl → run to confirm pass → commit. Use @superpowers:test-driven-development for the signal modules and propensity scorer (pure logic, perfect for TDD). Use @web-scraping-efficient when implementing the Allegheny adapter and Zillow/Redfin listings fetcher (keep raw HTML out of context). Use @superpowers:verification-before-completion before any "task complete" claim.

**Goal:** Ship a personal Claude Code skill that surfaces motivated-seller candidates in Allegheny County (Pittsburgh) using only free public data, scores them by sell-propensity, and drafts personalized outreach letters in Summer's voice.

**Architecture:** Two-stage skill (`/off-market discover` → `/off-market outreach`) with pluggable county adapters. Pure-Python signal modules (TDD), one county adapter (Allegheny via WPRDC), one listings-subtraction layer (Zillow/Redfin), one propensity scorer with fair-housing enforcement.

**Tech Stack:** Python 3.11+, `httpx` for fetches, `pydantic` for schemas, `pytest` for tests, `pyyaml` for criteria files, `pandas` for parcel-CSV joins, `rapidfuzz` for address normalization. No paid APIs.

**Design doc:** [`docs/plans/2026-06-02-off-market-skill-design.md`](2026-06-02-off-market-skill-design.md)

---

## References

- Design doc (above) — load it before starting any task.
- WPRDC catalog: `https://data.wprdc.org/dataset` — find dataset IDs for parcels / sales / tax delinquency.
- Allegheny Sheriff Sales: `https://www.alleghenycountypa.gov/services/sheriff/real-estate-sales/`
- HUD protected classes: `https://www.hud.gov/program_offices/fair_housing_equal_opp/fair_housing_act_overview`
- Personal CLAUDE.md gotchas relevant here: Plugin cache symlink resolution (skill lives at canonical `/Users/summerrae/claude_code/claude-skills/`), parallel-session-races (re-check branch before each commit), `user-invocable: true` frontmatter for slash-command registration.

---

## Phase 0 — Skill scaffolding

### Task 1: Create skill directory + SKILL.md router

**Files:**
- Create: `off-market/SKILL.md`
- Create: `off-market/scripts/__init__.py`
- Create: `off-market/scripts/county_adapters/__init__.py`
- Create: `off-market/scripts/listings/__init__.py`
- Create: `off-market/scripts/signals/__init__.py`
- Create: `off-market/tests/__init__.py`
- Create: `off-market/voice/.gitkeep`
- Create: `off-market/examples/.gitkeep`

**Step 1:** Create the directories with `mkdir -p`.

**Step 2:** Write `SKILL.md` (router only, no implementation detail):

```markdown
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
```

**Step 3:** Commit.

```bash
cd /Users/summerrae/claude_code/claude-skills
git add off-market/
git commit -m "feat(off-market): scaffold skill directory + router"
```

---

### Task 2: Reference docs

**Files:**
- Create: `off-market/references/propensity-rubric.md`
- Create: `off-market/references/fair-housing.md`
- Create: `off-market/references/letter-craft.md`
- Create: `off-market/references/adding-county-adapter.md`

**Step 1:** Write `propensity-rubric.md` — copy the rubric table from the design doc, plus weight rationale per row.

**Step 2:** Write `fair-housing.md`:

```markdown
# Fair Housing Rules

## Forbidden classes (HUD)

Race, color, religion, national origin, sex, disability, familial status, age.

## Enforcement in this skill

- `propensity.py` imports `FORBIDDEN_FIELDS = frozenset({"race", "ethnicity", "religion", "sex", "family_status", "disability", "age", "national_origin"})`.
- A unit test asserts no scoring expression references any forbidden field.
- The skill refuses CLI flags or `criteria.yaml` keys whose name matches a protected class.
- Neighborhood targeting is allowed by polygon / zip / boundary — NEVER by demographic descriptor.

## Why divorce / bankruptcy are excluded

Legal to use (public records), but coming from a family wanting to live there, this kind of outreach is creepy. Investor playbook ≠ owner-occupier playbook. If you ever flip this skill into an investor tool, revisit.
```

**Step 3:** Write `letter-craft.md` — tone guide: warm, specific to the property, no investor jargon, mentions a real reason to love that house/street.

**Step 4:** Write `adding-county-adapter.md` — adapter contract (function signature + expected return shape), Allegheny worked example as the canonical reference.

**Step 5:** Commit.

```bash
git add off-market/references/
git commit -m "docs(off-market): reference docs (rubric, fair-housing, letter-craft, adapter-howto)"
```

---

## Phase 1 — Foundations

### Task 3: Parcel dataclass

**Files:**
- Create: `off-market/scripts/models.py`
- Create: `off-market/tests/test_models.py`

**Step 1:** Write the failing test:

```python
# tests/test_models.py
from off_market.scripts.models import Parcel

def test_parcel_minimal_construction():
    p = Parcel(parcel_id="0001-A-001", address="123 Elm St, Pittsburgh, PA 15217",
               owner_name="Doe, John", owner_mailing="123 Elm St, Pittsburgh, PA 15217")
    assert p.parcel_id == "0001-A-001"
    assert p.is_absentee() is False

def test_parcel_absentee_when_mailing_state_differs():
    p = Parcel(parcel_id="x", address="123 Elm St, Pittsburgh, PA 15217",
               owner_name="Doe, John", owner_mailing="999 Beach Rd, Miami, FL 33101")
    assert p.is_absentee() is True
```

**Step 2:** Run: `pytest off-market/tests/test_models.py -v` — expect import error.

**Step 3:** Implement `Parcel` dataclass with `parcel_id`, `address`, `owner_name`, `owner_mailing`, optional `last_sale_date`, `last_sale_price`, `assessed_value`, `lot_sqft`, `beds`, `baths`, `year_built`, plus `is_absentee()` helper (compare state token in property vs mailing address using simple regex).

**Step 4:** Run tests — expect PASS.

**Step 5:** Commit:

```bash
git add off-market/scripts/models.py off-market/tests/test_models.py
git commit -m "feat(off-market): Parcel model with absentee helper"
```

---

### Task 4: `criteria.yaml` schema + validator

**Files:**
- Create: `off-market/scripts/criteria.py`
- Create: `off-market/tests/test_criteria.py`
- Create: `off-market/examples/criteria.yaml`

**Step 1:** Write failing test:

```python
def test_criteria_loads_valid_yaml(tmp_path):
    yml = tmp_path / "c.yaml"
    yml.write_text("""
beds_min: 3
lot_sqft_min: 5000
price_max: 350000
zips: ["15217", "15232"]
""")
    c = load_criteria(yml)
    assert c.beds_min == 3
    assert c.zips == ["15217", "15232"]

def test_criteria_rejects_protected_class_key(tmp_path):
    yml = tmp_path / "c.yaml"
    yml.write_text("race: white\n")
    with pytest.raises(ValueError, match="protected class"):
        load_criteria(yml)
```

**Step 2:** Run test — fail.

**Step 3:** Implement `Criteria` (pydantic model: `beds_min`, `baths_min`, `lot_sqft_min`, `lot_sqft_max`, `sqft_min`, `sqft_max`, `year_built_min`, `year_built_max`, `price_min`, `price_max`, `zips: list[str]`, `neighborhoods: list[str]`). Add a pre-load check that rejects any key in `FORBIDDEN_FIELDS`.

**Step 4:** Write `examples/criteria.yaml` template with comments.

**Step 5:** Run tests — pass. Commit.

---

### Task 5: Disk cache primitive

**Files:**
- Create: `off-market/scripts/cache.py`
- Create: `off-market/tests/test_cache.py`

**Step 1:** Failing test:

```python
def test_cache_returns_stale_when_no_network(tmp_path, monkeypatch):
    cache = Cache(root=tmp_path)
    cache.write("allegheny", "parcels", {"rows": 5})
    # force the fetcher to raise
    result = cache.get_or_fetch("allegheny", "parcels", lambda: 1/0, ttl_days=30)
    assert result == {"rows": 5}
```

**Step 2:** Implement `Cache` with `read`, `write`, `get_or_fetch(county, source, fetcher, ttl_days)` that returns cached value if within TTL, calls fetcher otherwise, falls back to stale cache if fetcher raises (and logs the fallback). Storage: `<root>/<county>/<source>.json` with timestamp.

**Step 3:** Test passes. Commit.

---

## Phase 2 — Signal modules (TDD pure logic)

Each signal is a pure function: `signal(parcel: Parcel, extra: dict) -> SignalResult` where `SignalResult(matched: bool, weight: float, reason: str)`.

### Task 6: `signals/absentee.py`

**Files:**
- Create: `off-market/scripts/signals/__init__.py` (already exists; add `SignalResult` dataclass)
- Create: `off-market/scripts/signals/absentee.py`
- Create: `off-market/tests/test_signals_absentee.py`

**Step 1:** Failing test — three rows: in-state non-absentee, in-state absentee (different city), out-of-state absentee. Expect weights 0 / 10 / 10 with reason codes `absentee:PA` / `absentee:FL`.

**Step 2:** Implement `score_absentee(parcel)` → `SignalResult` per design rubric.

**Step 3:** Test pass. Commit.

---

### Task 7: `signals/tenure_equity.py`

**Files:**
- Create: `off-market/scripts/signals/tenure_equity.py`
- Create: `off-market/tests/test_signals_tenure_equity.py`

**Step 1:** Failing test — three rows: bought 5 yrs ago (no match), bought 25 yrs ago at $80k now worth $250k (matches: 25 yrs, equity ~68%), bought 25 yrs ago at $200k now worth $250k (no match — equity below 60%).

**Step 2:** Implement `score_tenure_equity(parcel)` → weight 10 only if `years_owned >= 20 AND equity_pct >= 60`. Reason: `long_tenure_high_equity:<years>`.

**Step 3:** Test pass. Commit.

---

### Task 8: `signals/delinquency.py`

**Step 1:** Failing test — three rows: not delinquent (no match), delinquent $1,500 (weight ~5.75), delinquent $80,000 (cap at 25).

**Step 2:** Implement formula `5 + 0.5 * (owed_usd / 1000)` capped at 25.

**Step 3:** Test pass. Commit.

---

### Task 9: `signals/sheriff_sale.py`

**Step 1:** Failing test — not scheduled / scheduled in 14 days / scheduled in 60 days. All "scheduled" cases score 40.

**Step 2:** Implement: if `sheriff_sale_date` is present and in the future → weight 40, reason `sheriff_sale:<YYYY-MM-DD>`.

**Step 3:** Test pass. Commit.

---

### Task 10: `signals/probate_name.py`

**Step 1:** Failing test — `"Doe, John"` (no match), `"Estate of John Doe"` (match), `"Doe, John (Heirs of)"` (match), `"Smith, Jane, Deceased"` (match), `"Estate Realty LLC"` (NO MATCH — corporate name, not probate).

**Step 2:** Implement regex `r"\b(estate of|heirs of|deceased)\b"` case-insensitive, with a corporate-suffix exclusion list (`LLC`, `Inc`, `Realty`, `Holdings`).

**Step 3:** Test pass. Commit.

---

## Phase 3 — Propensity scorer

### Task 11: `propensity.py` core

**Files:**
- Create: `off-market/scripts/propensity.py`
- Create: `off-market/tests/test_propensity.py`

**Step 1:** Failing test — fixture parcel that hits absentee + tenure + sheriff sale → score 60 with all three reason codes.

**Step 2:** Implement `score(parcel, signals) -> PropensityScore(total: int, reasons: list[str], tier: str)`. Sum all weights, cap at 100; tier from cutoffs (`<15 dropped` / `15–39 worth a letter` / `40–69 high priority` / `≥70 act this week`).

**Step 3:** Pass. Commit.

---

### Task 12: Fair-housing guardrail test

**Files:**
- Modify: `off-market/tests/test_propensity.py`

**Step 1:** Add this test (designed to fail loudly if anyone later adds a forbidden field):

```python
import ast, pathlib
def test_no_forbidden_field_in_propensity_source():
    src = pathlib.Path("off-market/scripts/propensity.py").read_text()
    forbidden = {"race", "ethnicity", "religion", "sex", "family_status",
                 "disability", "age", "national_origin"}
    tree = ast.parse(src)
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    names |= {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    bad = names & forbidden
    assert not bad, f"propensity.py references forbidden fields: {bad}"
```

**Step 2:** Run — must already pass (no forbidden field used yet). Commit.

---

### Task 13: Score cutoffs + tier labels

Already covered in Task 11. If not, isolate the cutoff function `tier_for(score) -> str` with its own test (4 boundary cases) and commit.

---

## Phase 4 — Allegheny adapter

**Sub-skill brief:** Use @web-scraping-efficient for any HTML scraping in this phase. Run the actual fetch in a Python subprocess and return only structured fields — never paste raw HTML into the conversation. Cache aggressively.

### Task 14: WPRDC parcels fetcher

**Files:**
- Create: `off-market/scripts/county_adapters/allegheny_pa.py`
- Create: `off-market/tests/test_allegheny_pa.py`
- Create: `off-market/tests/fixtures/wprdc_parcels_sample.csv`

**Step 1:** Hand-pick 10 sample rows from the WPRDC parcels dataset; save as fixture CSV with the real column names. Document the source URL + dataset ID at the top of the adapter file.

**Step 2:** Failing test — given fixture CSV, `fetch_parcels(fixture_path)` returns 10 `Parcel` objects with correct mapping.

**Step 3:** Implement `fetch_parcels(source: str | Path) -> list[Parcel]`. If `source` is a URL, use `httpx.get` with `User-Agent: off-market-skill/0.1 (personal use)`. If a Path, read directly. Normalize column names → Parcel fields.

**Step 4:** Pass. Commit.

---

### Task 15: WPRDC sales fetcher

Same shape as Task 14. Fixture CSV with 10 sales rows. Function: `fetch_sales(source) -> dict[parcel_id, list[Sale]]`. Used to populate `last_sale_date` and `last_sale_price` on Parcels.

Commit.

---

### Task 16: Tax delinquency fetcher

Same shape. Annual delinquency CSV. Function `fetch_delinquency(source) -> dict[parcel_id, float]` (parcel_id → amount owed). Commit.

---

### Task 17: Allegheny sheriff sales scraper

**Files:**
- Modify: `off-market/scripts/county_adapters/allegheny_pa.py`
- Create: `off-market/tests/fixtures/allegheny_sheriff_sales.html`

**Step 1:** Snapshot the Allegheny sheriff-sales page HTML into the fixture file.

**Step 2:** Failing test — given fixture HTML, `parse_sheriff_sales(html) -> dict[parcel_id, date]` returns the expected mapping.

**Step 3:** Implement parser (BeautifulSoup). Live fetch is gated by `RUN_LIVE_TESTS=1`.

**Step 4:** Pass. Commit.

---

### Task 18: Allegheny adapter orchestrator

Compose Tasks 14–17 into `class AlleghenyPAAdapter` with one method `load(criteria) -> list[Parcel]` that returns parcels with all fields populated (parcels enriched with sales, delinquency amounts, sheriff-sale dates). Filters parcels failing `criteria` early.

Test: fixture-driven, end-to-end on the 10-row sample. Commit.

---

## Phase 5 — Listings subtraction

### Task 19: Zillow active-listings fetcher

**Sub-skill brief:** Use @web-scraping-efficient. Respect robots.txt and rate-limit (≥2s between requests). Real User-Agent. Cache 7 days.

**Files:**
- Create: `off-market/scripts/listings/zillow_redfin.py`
- Create: `off-market/tests/fixtures/zillow_search_15217.html`

Fixture-driven parser test → implement → live test gated on env var → commit.

---

### Task 20: Address normalization for join

**Files:**
- Create: `off-market/scripts/listings/address_norm.py`
- Create: `off-market/tests/test_address_norm.py`

Address strings from assessor ("123 ELM ST, PITTSBURGH PA 15217") and Zillow ("123 Elm Street, Pittsburgh, PA 15217") differ in punctuation/casing/abbreviation. Implement `normalize(addr) -> str` that lowercases, expands `ST→STREET`, etc.; use `rapidfuzz` to ensure 95%+ match on canonical forms. Five test cases. Commit.

---

### Task 21: Active-listing subtraction

`subtract_listed(parcels, listings) -> list[Parcel]` returns parcels NOT in the active-listings set (joined on normalized address). Two test cases. Commit.

---

## Phase 6 — Stage 1 orchestrator

### Task 22: `discover.py` wired end-to-end

**Files:**
- Create: `off-market/scripts/discover.py`
- Create: `off-market/tests/test_discover_e2e.py`

Wires: adapter.load → subtract_listed → score per parcel → sort by score desc.

Test: fixture-only end-to-end run produces a deterministic ranked list. Commit.

---

### Task 23: Output writers

**Files:**
- Modify: `off-market/scripts/discover.py`
- Create: `off-market/tests/test_outputs.py`

Three output files per run:
- `candidates.csv` — every scored parcel + reasons.
- `candidates.md` — top 20 in readable form with Street View URL `https://maps.google.com/?cbll=<lat>,<lng>&layer=c`.
- `health.md` — per-source fetch status.

Snapshot test for the markdown formatting. Commit.

---

### Task 24: CLI surface + cache flag

**Files:**
- Modify: `off-market/scripts/discover.py`

Add `argparse`: `discover.py <county> [--criteria PATH] [--no-cache] [--output-dir DIR]`. Default output: `runs/<YYYY-MM-DD>-<county>/`.

Test: invoke with `--help`, assert flags present. Commit.

---

### Task 25: Live integration smoke test (gated)

**Files:**
- Create: `off-market/tests/test_live_allegheny.py`

Gated on `RUN_LIVE_TESTS=1`. Fetches the real WPRDC parcels dataset, asserts non-empty + expected columns. Skipped by default in CI. Commit.

---

## Phase 7 — Voice profile + outreach

### Task 26: `voice_capture.py`

**Files:**
- Create: `off-market/scripts/voice_capture.py`
- Create: `off-market/tests/test_voice.py`

Input: 3+ sample paragraphs in a `samples/` directory. Output: `voice/profile.md` with extracted rules (avg sentence length, preferred openings, banned phrases, signature closers). Implemented as a prompt template, not heavy NLP; the agent that runs this task fills the template by reading the samples.

Test: golden-fixture sample → profile contains all expected rule sections.

Commit.

---

### Task 27: Voice profile schema

The `voice/profile.md` file format. Markdown with H2 sections: `## Tone` / `## Sentence cadence` / `## Vocabulary I use` / `## Vocabulary I avoid` / `## Signature openers` / `## Signature closers` / `## Forbidden phrases`. Commit a `voice/profile-template.md`.

---

### Task 28: `outreach.py` draft loop

**Files:**
- Create: `off-market/scripts/outreach.py`
- Create: `off-market/tests/test_outreach.py`

Pseudo-flow:

1. Load `candidates.csv` and `voice/profile.md`.
2. For each of top-N (default 20): build a per-candidate context (address, owner-name hint, signal reasons, optional user note), invoke the letter-drafting prompt.
3. Write `letters/<sanitized-address>.md` to the run folder.

Test: snapshot test on a fixture candidate → drafted letter contains the property-specific reason and matches voice rules.

Commit.

---

### Task 29: Letter snapshot stability

A pinned snapshot for one canonical candidate ensures future prompt edits surface as visible diffs. Commit.

---

## Phase 8 — Skill integration

### Task 30: Finalize `SKILL.md`

Verify `user-invocable: true`. Add real CLI usage examples (real paths). Commit.

---

### Task 31: Examples

**Files:**
- Modify: `off-market/examples/criteria.yaml`
- Create: `off-market/examples/allegheny-pittsburgh.yaml`

Two sample criteria files: blank template, one filled in for an East End Pittsburgh search (real zips: 15217 / 15232 / 15206 / 15208). Commit.

---

### Task 32: Skill discovery verification

Run `Skill` tool on `off-market` from a fresh-feeling conversation seed and confirm it loads. If `user-invocable: true` is missing → fix. Commit any fix.

---

## Phase 9 — Ship

### Task 33: Lint + final pass

- `ruff check off-market/` and `ruff format off-market/`.
- Re-run full test suite: `pytest off-market/ -v`.
- Re-run live smoke: `RUN_LIVE_TESTS=1 pytest off-market/tests/test_live_allegheny.py -v`.
- If patterns from this build belong in MEMORY (e.g. a WPRDC quirk worth remembering), add memory entries.
- Commit any fixes.

### Task 34: Open PR

**Files:** none (PR-only).

```bash
cd /Users/summerrae/claude_code/claude-skills
env -u GH_TOKEN gh pr create --base main --head feat/off-market-skill-design \
  --title "feat(off-market): personal-use motivated-seller discovery skill (Lean v1, Allegheny)" \
  --body "$(cat <<'EOF'
## What

Adds the `off-market` skill — a personal toolkit for surfacing motivated-seller candidates in Allegheny County (Pittsburgh) from free public data, with letter-drafting in the user's voice.

## Design and plan

- Design: \`docs/plans/2026-06-02-off-market-skill-design.md\`
- Plan: \`docs/plans/2026-06-02-off-market-skill-implementation.md\`

## Scope (Lean v1)

- Signals: absentee, long-tenure + high-equity, tax-delinquent, sheriff-sale scheduled, "Estate of" name pattern.
- Subtracts actively-listed homes (Zillow/Redfin scrape).
- One county adapter: Allegheny PA (via WPRDC). Architecture is plug-in for additional counties.
- Fair-housing enforcement baked into propensity scorer (forbidden-field assertion test).
- Free data only. No PropStream / ATTOM / BatchLeads.

## Test plan

- [ ] \`pytest off-market/ -v\` green
- [ ] \`RUN_LIVE_TESTS=1 pytest off-market/tests/test_live_allegheny.py -v\` green
- [ ] Manual: \`python -m off-market.scripts.discover allegheny_pa --criteria off-market/examples/allegheny-pittsburgh.yaml\` produces a non-empty \`candidates.csv\` and \`health.md\` shows ≥4 sources ✓.
- [ ] Manual: \`python -m off-market.scripts.outreach <candidates.csv> --top 3\` produces 3 letter drafts matching \`voice/profile.md\`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Commit any post-PR fixes from review.

---

## Done criteria

- All 34 tasks committed.
- `pytest off-market/` green.
- Live smoke against WPRDC green.
- One end-to-end manual run produces a `candidates.csv` with ≥10 rows scoring ≥40 in Allegheny East End zips.
- One end-to-end manual run produces 3 letter drafts that pass `references/letter-craft.md` review.
- PR open and ready for self-merge (no CodeRabbit / reviewers wired on claude-skills).
