# Ingestion Patterns — Fetching JDs Reliably

LinkedIn is the common case and the hardest case. Most other job boards (Greenhouse, Lever, Ashby, company careers pages) are cleanly fetchable via `WebFetch`.

## URL Normalization (dedup prerequisite)

Before any fetching, normalize URLs so duplicates collapse to one canonical form.

### LinkedIn

- Canonical form: `https://www.linkedin.com/jobs/view/<numeric-id>/`
- Extract `<numeric-id>` with a regex on the path (e.g., `/jobs/view/(\d+)`).
- Compare URLs on numeric ID alone — strip query params (`?eBP=...`, `&trackingId=...`, etc.), trailing slash variations, host case.
- A URL without a trailing slash (`/jobs/view/4403401820`) is the same as one with (`/jobs/view/4403401820/`).

### Greenhouse

- Canonical form: `https://boards.greenhouse.io/<company>/jobs/<numeric-id>`
- Strip query params (often `?gh_src=...` or `?source=...`).

### Lever

- Canonical form: `https://jobs.lever.co/<company>/<uuid>`
- Strip query params.

### Ashby

- Canonical form: `https://jobs.ashbyhq.com/<company>/<uuid>`
- Strip query params.

### Workday

- Canonical form varies by tenant; stable ID is the `R-######` req number embedded in the URL path.
- Extract the `R-\d+` pattern; compare on that.

### Other boards / company sites

- Strip query params (tracking codes, UTM, session IDs).
- Preserve path.
- If the posting has both a public-site URL and an ATS URL, the ATS URL is canonical (more fetchable).

### Pasted text (no URL)

- Dedupe by `(company_normalized, title_normalized)` where normalization is lowercase + whitespace-collapsed.
- Two pastes that dedupe to the same `(company, title)` — flag for user to resolve (one may be a revised/re-posted version).

### Reporting

Dedup must always be reported to the user, even when no duplicates were found:
- `N URLs submitted, D duplicates removed, M unique.`
- List the canonical URLs so the user can verify.
- Name which duplicates collapsed onto which canonical entry.

Never silently drop duplicates. A dedupe that removes entries without the user seeing which ones creates a trust gap.

## Fetch Order (per JD URL)

1. **WebFetch** — default first try. Prompt asking for structured extraction (title, company, location, seniority, must-haves, nice-to-haves, comp, culture).
2. **If WebFetch returns an auth wall, error, or obviously-truncated content** → try URL variants (LinkedIn specifically: strip query params, try `/jobs/view/<id>/` bare form).
3. **If variants fail** → ask the user to paste the JD text. Proceed with their paste as `raw_text`.
4. **Optional: Playwright fallback** — only if the user has Playwright set up and explicitly asks. Not default.

## Known LinkedIn Patterns

- Public JD pages sometimes render for unauthenticated fetches; sometimes not. No deterministic rule.
- Tracking query params (`?eBP=…&trackingId=…`) can be stripped — core URL is `https://www.linkedin.com/jobs/view/<numeric-id>/`.
- When LinkedIn returns a login wall, the WebFetch response often looks fine on the surface but the body is login-prompt HTML. Look for phrases like "Sign in to see" in the extracted content; treat as a fetch failure.
- Some LinkedIn alerts include alternate URLs to the company's own ATS (Greenhouse/Lever) — prefer those when available; they fetch cleanly.

## Known Greenhouse / Lever / Ashby Patterns

- Greenhouse URLs (`boards.greenhouse.io/<company>/jobs/<id>`): fetch cleanly.
- Lever URLs (`jobs.lever.co/<company>/<uuid>`): fetch cleanly.
- Ashby URLs (`jobs.ashbyhq.com/<company>/<uuid>`): usually fetch cleanly.
- Workday URLs (`<company>.wd1.myworkdayjobs.com/…`): JavaScript-heavy; often need paste fallback.

## Structured Extraction Prompt (for WebFetch)

Use this prompt shape for consistency:

> *"Extract the full job posting: company name, job title, location, seniority level, posted date / applicant count, full job description, listed responsibilities, required qualifications (bulleted if possible), preferred/nice-to-have qualifications, technologies/tools mentioned, compensation (if listed), and any culture/team signals. Return verbatim where possible. If the page shows a login wall instead of the posting, say so."*

## Batch Ingestion Flow

For a list of N URLs:

1. Fetch each (serially or in parallel — parallel is faster but rate-limits can bite; serial is safer for >5 URLs).
2. For each result, classify:
   - **Success** → extract structured JD
   - **Auth wall** → mark for paste-fallback
   - **404 / expired** → mark for user confirmation (JD may have been closed)
   - **JS-rendered failure** → mark for paste-fallback
3. Present a summary: "Fetched N, M need paste, K were expired/404."
4. Resolve the paste-needed ones by asking the user to paste each, one at a time.

## Structured JD Schema (output of ingestion)

```yaml
jd:
  source_url: "https://www.linkedin.com/jobs/view/…"
  fetched_at: "2026-04-18T12:00:00Z"
  fetch_method: webfetch | paste | variant_url
  title: "Vice President of Data and AI"
  company: "Enzo Tech Group (client: healthcare advocacy platform)"
  location: "United States (Remote / Pittsburgh)"
  seniority: exec
  posted_at: "2 days ago"
  applicant_count: "200+"
  comp_band: "$325K–$450K base + equity"
  required:
    - "12–15+ years in data, analytics, or AI leadership"
    - "…"
  preferred: []
  tech_mentioned:
    - "cloud-native microservices"
    - "…"
  culture_signals:
    - "post-modernization activation"
    - "cross-functional partnership"
  red_flags:
    - "200+ applicants already"
  raw_text: "… full posting text …"
```

## Salary Recon (when `comp_band` is empty)

Most LinkedIn postings omit compensation. When the user needs a comp estimate before the Phase 3 deal-breaker pre-check, run a parallel-batch recon in a single Agent call — do not serialize.

**Query shape (3 parallel calls):**

1. `WebSearch` — `<company> <title> salary Glassdoor` (Glassdoor is the broadest ground truth for named-company comp bands)
2. `WebSearch` — `<company> <title> salary Ladders` (Ladders surfaces $100K+ postings and often has tighter role-specific bands)
3. `WebFetch` — the company careers page or About/Comp page (signals internal comp philosophy, pay-transparency laws may force disclosure)

Collate results into a single `comp_estimate` block:

```yaml
comp_estimate:
  source: glassdoor | ladders | careers_page | triangulated
  base_range: "$120K–$150K"
  confidence: high | medium | low
  notes: "Glassdoor Director ceiling $139K; Ladders estimated $120-150K for exact title; no careers-page disclosure."
```

**Caveats:**

- **Small orgs:** Glassdoor may have <5 data points; mark `confidence: low` and surface the sample-size caveat.
- **Non-profits / global-health / gov:** Bands often skew 20–40% below commercial tech. Do not benchmark CHAI-type roles against FAANG-adjacent medians — anchor to the sector.
- **VP+ / exec roles:** Public-scrape data thins out above Director. If both sources return "insufficient data," report that and suggest the user ask the recruiter during screen.
- **Geographic skew:** US median unless JD specifies region. Flag if role is region-locked (e.g., Bay Area, NYC, remote-US) since median assumptions diverge.

**Failure fallback:** If all three queries return nothing usable, emit `comp_estimate: unavailable` and recommend the user ask the recruiter during the initial screen. Never invent a band.

See memory `salary_recon_parallel_search_pattern.md` for the pattern's origin.

## Failure Modes to Surface (Not Silently Skip)

- LinkedIn auth wall — surface and ask for paste.
- 404 / expired posting — surface and confirm user wants to remove from list.
- Company name is "confidential" / "stealth" — surface; user may still want to pursue.
- Comp not listed — not a failure; note `comp_band: unknown` and let Phase 3 deal-breaker check warn. Optionally run §Salary Recon above.
- Seniority unclear from title (e.g., "AI Lead" could be IC or director) — surface and ask user; don't guess.

## What NOT to Do

- Do not invent details for a JD that failed to fetch. Missing data is missing data.
- Do not re-fetch a URL that's been marked failed — go straight to paste fallback on retry.
- Do not log in to LinkedIn or other sites programmatically. The skill operates on publicly-fetchable content only.
- Do not send the fetched content to any external service beyond the local session.
