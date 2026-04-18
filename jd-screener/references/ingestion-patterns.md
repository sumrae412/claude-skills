# Ingestion Patterns — Fetching JDs Reliably

LinkedIn is the common case and the hardest case. Most other job boards (Greenhouse, Lever, Ashby, company careers pages) are cleanly fetchable via `WebFetch`.

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

## Failure Modes to Surface (Not Silently Skip)

- LinkedIn auth wall — surface and ask for paste.
- 404 / expired posting — surface and confirm user wants to remove from list.
- Company name is "confidential" / "stealth" — surface; user may still want to pursue.
- Comp not listed — not a failure; note `comp_band: unknown` and let Phase 3 deal-breaker check warn.
- Seniority unclear from title (e.g., "AI Lead" could be IC or director) — surface and ask user; don't guess.

## What NOT to Do

- Do not invent details for a JD that failed to fetch. Missing data is missing data.
- Do not re-fetch a URL that's been marked failed — go straight to paste fallback on retry.
- Do not log in to LinkedIn or other sites programmatically. The skill operates on publicly-fetchable content only.
- Do not send the fetched content to any external service beyond the local session.
