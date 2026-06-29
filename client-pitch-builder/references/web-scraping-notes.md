# Web Scraping Notes for Client Pitch Research

Load this in Phase 2 only. Token-efficient scraping protocol — do not dump raw HTML into context.

---

## The Gate

Before any fetch, ask: is the goal extraction from a large or JS-rendered page?

- **Prospect company website** — likely large, extraction goal. Use the pattern below.
- **LinkedIn export** — provided as text by the user; no fetching needed.
- **Your own company website** — same as above; use the pattern.

---

## Token-Efficient Fetch Pattern

### Step 1 — Fetch the page

Use `WebFetch` for static sites. If it returns an HTTP 500 or obviously truncated/empty content, the page is JS-rendered.

### Step 2 — JS-rendered fallback

If `WebFetch` fails, use Playwright MCP:

```
mcp__playwright__browser_navigate -> URL
mcp__playwright__browser_evaluate -> "document.body.innerHTML.slice(0, 8000)"
```

Fetch in chunks if needed. Stop when you have enough for extraction — typically 8-12KB of HTML captures the homepage value prop, nav, and about section.

### Step 3 — Extract, don't dump

Parse the fetched content for the specific fields needed (see SKILL.md Phase 2A/2B tables). Write extracted facts to `research.md`. Never paste raw HTML into the conversation or the research file.

---

## Signals to Extract Per Page Type

### Company homepage
- Tagline / hero headline (positioning)
- "Who we serve" or ICP language
- Service names and descriptions (nav + service sections)
- Social proof: client logos, testimonials, case study teasers
- Team/about section

### LinkedIn company page
- Company size, industry
- "About us" description
- Recent posts (reveals current priorities and messaging)

### Prospect's personal LinkedIn (from PDF export or pasted text)
- Current title and company
- Role description / summary
- Career arc (seniority trajectory)
- Skills section (what they self-identify as expert in)
- Any published posts or articles (reveals priorities and pain points)
- Education (useful for tone calibration)

### Job postings (bonus signal if visible)
- Active job posts reveal gaps — a "Head of Operations" listing suggests ops is under-resourced
- The requirements language often mirrors the decision-maker's own pain language

---

## Pain Point Extraction Heuristics

Look for these patterns in the prospect's copy and the company's site:

- "We help X achieve Y without Z" — Z is the pain
- "Our customers struggle with..." — direct statement
- "Stop wasting time on..." — pain framing
- Job post bullet: "partner with cross-functional teams to..." — coordination is a pain
- Testimonial: "before [company], we used to..." — pre-state is the pain

Map each extracted pain directly to a service in your company's offering (Phase 2C solution mapping).

---

## Rate-Limit Caution

Do not fetch more than 3-4 pages per research session. The homepage + About + one case study page is usually sufficient. If a site requires login (LinkedIn authenticated pages), rely on the user-provided export.
