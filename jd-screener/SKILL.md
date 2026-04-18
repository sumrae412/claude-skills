---
name: jd-screener
description: Triages a batch of job postings against the candidate's canonical profile and produces a ranked, scored list with go/no-go recommendations. Hands off confirmed winners to `resume-tailor` one at a time. Does NOT auto-draft resumes or cover letters and does NOT submit applications — drafting and applying stay human-gated.
---

# JD Screener — Fit Triage for Job Search

Screens a batch of job postings and produces a ranked, scored list with go/no-go recommendations. Hands off confirmed winners to `resume-tailor` one JD at a time.

## Mission

Shortlisting is the highest-leverage step in a job search — the difference between 2 targeted applications and 20 scattershot ones shows up in callback rate. This skill absorbs the scoring work so the candidate focuses drafting energy on roles they actually want. **Truth-preserving, non-autopilot:** the skill scores fit and flags gaps; it does not apply, send, or draft under the candidate's name.

## Before Starting

Ask the user for:

1. **JD list** — URLs, pasted snippets, or a mix. LinkedIn job URLs preferred; any text-readable posting works.
2. **Profile source** — point to memory files (`user_<name>_profile.md` and related) if they exist, OR ask the user to paste a current resume. The skill will NOT proceed without a confirmed candidate profile.
3. **Preferences / deal-breakers** — comp floor, remote/hybrid/onsite, domain preferences, level range (IC / manager / director / VP / exec), locations, visa constraints, deal-breakers. Captured once, at session start, into a `search_preferences` block.

If the list is empty or the profile is missing, ask once. Don't score with half the inputs.

---

## Phase 1 — Profile & Preferences

Produce a single `candidate_profile` block that downstream phases reference. Load `references/fit-rubric.md` §Profile Schema.

Output to user (checkpoint):

- Role history summary (titles, dates, scale/team-size numbers)
- Signature projects / differentiators
- Keyword coverage (from profile, not yet from JDs)
- Search preferences / deal-breakers as declared

Ask: *"Is this profile current and accurate? Anything to add or correct before I score JDs against it?"* Wait for confirmation before Phase 2.

---

## Phase 2 — Bulk JD Ingestion

### Step 1: Dedupe the URL list

Before any fetching, normalize and dedupe. See `references/ingestion-patterns.md` §URL Normalization for rules by board. Summary:

- **LinkedIn:** compare on numeric job ID from `/jobs/view/<id>/`; strip query params + trailing slashes.
- **Greenhouse / Lever / Ashby:** strip query params; compare on canonical path.
- **Workday:** extract `R-######` requisition number.
- **Pasted text (no URL):** dedupe by `(company, title)` tuple; flag near-duplicates for user resolution.

Report the dedupe result out loud: *"N URLs submitted, D duplicates removed, M unique to fetch."* Do NOT silently drop dupes — show which URLs were marked duplicates of which canonical entry.

### Step 2: Fetch

For each unique JD, fetch and extract a structured posting. See `references/ingestion-patterns.md` for the fallback ladder (WebFetch → URL variants → manual paste). LinkedIn job pages often auth-gate; plan on partial fetch failures.

For each JD, store:

- `title`, `company`, `location`, `seniority`, `comp_band`, `must_haves`, `nice_to_haves`, `red_flags`, `raw_text`, `source_url` *(always retained — downstream outputs must cite it so the user knows where to apply)*

Present a batch summary (M unique, N fetched cleanly, K failed with reason) and resolve the failed ones (ask user to paste, skip, or retry) before scoring.

---

## Phase 3 — Fit Scoring

For each JD, compute a fit score across 6 dimensions (criteria in `references/fit-rubric.md` §Scoring):

1. **Title/level fit** (0–100)
2. **YOE fit** — required vs candidate tenure
3. **Domain fit** — industry/vertical match
4. **Must-have coverage** — % of JD must-haves with DIRECT or TRANSFERABLE evidence in profile
5. **Nice-to-have coverage**
6. **Deal-breaker check** — binary pass/fail against `search_preferences`

Combine into a weighted composite score. Default weights in the rubric; tunable per session. Band into:

- **STRONG_FIT** (80–100): worth drafting
- **STRETCH** (60–79): worth drafting if the role is a genuine want
- **WEAK_FIT** (40–59): skip unless user has specific reason
- **NO_GO** (any deal-breaker tripped OR composite <40): do not pursue

---

## Phase 4 — Triage Review

Present a ranked table with one row per JD. Format in `references/output-templates.md` §Ranked Table. Per row:

- Composite score + band
- **Source URL** (every row — so the user knows where to apply even without drilling down)
- One-line "why fit" (strongest 2 signals)
- One-line "main gap" (largest shortfall)
- Go/no-go recommendation

Walk through STRETCH and borderline STRONG_FIT items with the user for confirmation — these are where the user's judgment matters more than the rubric's arithmetic.

User selects which to pursue. Defaults: pursue all STRONG_FIT, opt-in STRETCH, skip WEAK_FIT/NO_GO unless overridden.

---

## Phase 5 — Handoff to resume-tailor

For each JD the user confirms, write one directory under `~/Documents/resumes/<Company>/` containing:

- `jd.md` — fetched posting + extracted structure (**`source_url` in the header is mandatory** — the user needs to know where to submit)
- `fit-analysis.md` — Phase 3 score breakdown + Phase 4 reasoning (include `source_url` at the top)

Then prompt the user:

> *"To draft resume + cover letter for <Company>, invoke `/resume-tailor` and point it at `~/Documents/resumes/<Company>/jd.md`. Each invocation runs the full phased flow with review at each checkpoint — no batch auto-drafting."*

Do NOT invoke `resume-tailor` programmatically. Do NOT batch-draft. The handoff is a file + a nudge.

---

## Principles

1. **Triage, not applying.** This skill scores fit. Drafting goes through `resume-tailor` one JD at a time with full checkpoints. Sending applications is the user's hand only.
2. **Profile-first.** No scoring without a confirmed candidate profile. Stale profiles produce stale triage.
3. **Honest scoring.** Bands are calibrated; do not inflate STRETCH into STRONG_FIT to justify 15 applications.
4. **Deal-breakers are deal-breakers.** A hard preference fail is NO_GO regardless of skill match.
5. **One score per JD, one handoff per JD.** Batches are for efficient fetching, not shortcut drafting.
6. **Fetch failures surface, not silently skip.** If a JD can't be fetched, tell the user and resolve (paste or skip) — don't quietly drop it from the ranked list.
7. **Dedupe before work, report dedupe out loud.** Duplicate URLs in a user-supplied list get normalized away at the top of Phase 2 with visible accounting — never silent. Applies to every subsequent session, not just the first time the user notices a dupe.
8. **Source URL is always retained.** Every ranked-table row and every handoff artifact cites the original URL. The user needs to know where to apply; the skill does not make that information harder to find.

---

## Professional Help Boundary

This skill helps triage job postings. It does **not** replace professional help for:

- **Career direction, field changes, longer-term strategy** → licensed career coach.
- **Salary negotiation strategy** → licensed career coach or negotiation specialist.
- **Sustained job-search distress, burnout, or anxiety spirals** → therapist or EAP. If the session surfaces "I'll apply to anything, I just need something" desperation or compulsive applying, pause and say so directly.
- **Legal questions** (visa sponsorship, non-competes, discrimination claims, termination disputes) → employment attorney.

When the conversation drifts into any of those, name the limit and suggest the appropriate professional before continuing with triage.
