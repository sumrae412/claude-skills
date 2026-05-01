---
name: web-scraping-efficient
description: Token-efficient Python web scraping. Use whenever the user wants to scrape, crawl, extract, or pull data from a website, HTML page, or online table — even when they don't say "token-efficient." Triggers on "scrape this site," "get the data from this page," "crawl X," "extract the listings/products/articles," "pull prices from," or pasting a URL with an extraction goal. The skill's whole point is to keep raw HTML out of Claude's context: fetch and parse in Python, return only the structured fields the user asked for.
---

# Token-efficient web scraping

## The core idea

Raw HTML is huge — a single product page can be 100k+ tokens of nav, scripts, tracking, and CSS. If that lands in your context, the session is wrecked before you've even extracted anything.

**The whole game is: do the fetch and the parse in a Python subprocess, and only return the structured rows back.** Claude sees `[{"title": "...", "price": 19.99}, ...]`, never `<html>...</html>`.

Everything else in this skill is a corollary of that rule.

## Decision order (cheapest first)

Before writing a scraper, check whether you can avoid scraping at all. In order:

1. **Is there a JSON API?** Open the page in a browser, watch the Network tab (XHR/Fetch). Most modern sites hydrate from JSON endpoints — those are 10–100× cheaper to parse than HTML and usually stable. If you find one, hit it directly with `httpx` and skip HTML entirely.
2. **Is there a sitemap, RSS, or data dump?** Check `/sitemap.xml`, `/rss`, `/feed`, or the site's data/exports page. Often gives you every URL or every record without crawling.
3. **Is the content static HTML?** Use `httpx` + `selectolax` (fast C-based CSS selector parser). This is the default path.
4. **Does the content require JavaScript execution?** Use Playwright headless, but **extract via `page.evaluate(...)` running JS in the browser** so only the JSON result crosses the boundary. Don't return `page.content()` to Python and parse there — same trap as returning HTML to Claude.

When in doubt, try (3) first. View-source the page; if the data is in the HTML, you don't need a browser.

## Reconnaissance — do this before writing the scraper

Most scraping projects waste time because the engineer skipped recon and went straight to selectors. One curl + a few greps will usually tell you which tier you need.

### Phase 0: the curl quality gate

One HTTP request. No browser.

```bash
curl -sL -A "Mozilla/5.0 (compatible; research-bot/1.0)" -D headers.txt \
     "https://target.com/page" -o page.html
wc -c page.html headers.txt
```

Then:
- `grep -i "^server:\|x-powered-by:\|cf-ray:\|set-cookie:" headers.txt` — framework + protection markers.
- `grep -c "<term>" page.html` for each field the user wants.
- Eyeball framework signatures (next section).

**Quality gate:** if every target field is present in `page.html` AND there are no protection signals (403/503, `cf-ray`, Cloudflare challenge HTML, CAPTCHA strings), you're done with recon. Write a `selectolax` parser and ship. **Do not launch a browser.** That decision alone saves enormous time and tokens.

Otherwise, continue to API discovery.

### Framework signatures — instant Tier 0 shortcuts

Grep `page.html` for these. Each one points you at structured data that's already on the page or one fetch away:

| Marker | What it means | Where the data is |
|---|---|---|
| `__NEXT_DATA__` | Next.js | `<script id="__NEXT_DATA__">{...}</script>` — entire page state as JSON. Parse it directly. |
| `window.__NUXT__` | Nuxt | Inline JS object with full state |
| `application/ld+json` | schema.org | One or more JSON-LD blocks — often has product/article fields you want |
| `/_next/data/...` | Next.js page-data API | Hit that URL directly for clean JSON of any other page |
| `/wp-json/wp/v2/` | WordPress REST API | `?per_page=100` lists posts/pages/media; no scraping needed |
| `/api/`, `/v1/`, `/v2/`, `/rest/`, `/graphql` | Backend API path | Inspect with the network-discovery recipe below |
| `data-reactroot`, `id="__next"`, empty `<div id="app">` | SPA — raw HTML is empty | Use the network-discovery recipe; do **not** scrape rendered DOM |
| `Shopify.theme`, `cdn.shopify.com` | Shopify | `?view=json` on collection/product URLs returns JSON |

A single match here can collapse a half-day scraper into a 20-line script.

### Sitemap discovery

Before crawling, check:

```bash
curl -s https://target.com/robots.txt | grep -i "^sitemap:"
```

Then fetch each sitemap URL listed. Be aware:
- `sitemap_index.xml` is a sitemap-of-sitemaps — recurse one level.
- `*.xml.gz` is gzipped — `curl ... | gunzip | ...`.
- Sites often expose specialized sitemaps: `products-sitemap.xml`, `posts-sitemap.xml`, `news-sitemap.xml`. Each is a flat URL list — way faster than BFS crawling.

If a sitemap exists, you almost never need to crawl page-by-page.

### Network-panel API discovery (for SPAs)

When the raw HTML is empty (SPA) and there's no obvious `__NEXT_DATA__` blob, the data is in XHR/fetch calls. Capture them once with Playwright, then ditch the browser:

```python
from playwright.sync_api import sync_playwright
import json

calls = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.on("response", lambda r: calls.append({
        "url": r.url, "status": r.status,
        "ctype": r.headers.get("content-type", ""),
    }))
    page.goto("https://target.com/page", wait_until="networkidle")
    # Optionally click around to surface lazy-loaded endpoints:
    # page.click("button.load-more"); page.wait_for_load_state("networkidle")
    browser.close()

json_calls = [c for c in calls if "json" in c["ctype"]]
for c in json_calls: print(c["status"], c["url"])
```

Filter the resulting list for `/api/`, `/graphql`, or any path that returns JSON. Hit those URLs directly with `httpx` from then on — the browser was a one-time tool to find the endpoints.

### Blocking and protection signals — watch for these

Flag any of these and adjust strategy (back off, rotate UA, switch to authenticated session, or stop):

| Signal | Means |
|---|---|
| `403 Forbidden`, `503 Service Unavailable` | Blocked or under protection |
| `429 Too Many Requests` | Rate-limited — honor `Retry-After` if present |
| `cf-ray` response header, `__cf_bm` cookie, "Checking your browser" HTML | Cloudflare challenge |
| `<title>Access Denied</title>`, "unusual traffic", "please verify" | Bot detection |
| CAPTCHA elements (`g-recaptcha`, `hcaptcha`, Turnstile iframe) | Stop — don't try to solve |
| Empty body or content that differs from a real-browser fetch | Server is serving you a stub |

For a casual scrape, polite delays + a real User-Agent solve most things. For Cloudflare/CAPTCHA, escalate to Playwright with `storage_state` from a manual login — don't try to defeat the protection.

## The scraper script pattern

Write a standalone Python script. Run it with `python scraper.py <args>`. It writes structured output (JSON or CSV) to a file. Claude reads the file (or just a head of it).

**Skeleton — adapt, don't ceremonially follow:**

```python
import httpx, json, sys, time
from selectolax.parser import HTMLParser

UA = "Mozilla/5.0 (compatible; research-bot/1.0)"

def fetch(url: str) -> str:
    r = httpx.get(url, headers={"User-Agent": UA}, timeout=20, follow_redirects=True)
    r.raise_for_status()
    return r.text

def parse(html: str) -> list[dict]:
    tree = HTMLParser(html)
    rows = []
    for card in tree.css("div.product-card"):  # adjust selector
        title = card.css_first("h2")
        price = card.css_first(".price")
        rows.append({
            "title": title.text(strip=True) if title else None,
            "price": price.text(strip=True) if price else None,
            "url":   card.css_first("a").attributes.get("href") if card.css_first("a") else None,
        })
    return rows

def main(urls: list[str], out: str):
    all_rows = []
    for u in urls:
        try:
            all_rows.extend(parse(fetch(u)))
        except Exception as e:
            print(f"FAIL {u}: {e}", file=sys.stderr)
        time.sleep(1)  # be polite
    with open(out, "w") as f:
        json.dump(all_rows, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(all_rows)} rows to {out}")

if __name__ == "__main__":
    main(sys.argv[1:-1], sys.argv[-1])
```

**Higher-level alternative:** if you'd rather not assemble `httpx` + `selectolax` + Playwright yourself, [`crawl4ai`](https://github.com/unclecode/crawl4ai) bundles fetch + headless rendering + Markdown conversion + schema-based extraction behind one library and CLI (`crwl <url> -o markdown`). Heavier dep, but a one-call shortcut for "render this JS-heavy page and give me clean Markdown." Same token-efficiency rules apply: have it write to disk, then read a head.

**LLM-per-page tools — use sparingly.** Frameworks like [ScrapeGraphAI](https://github.com/ScrapeGraphAI/Scrapegraph-ai) take the opposite stance: they send page content to an LLM for *every* extraction, with graph-of-nodes pipelines (`SmartScraperGraph`, `SearchGraph`, `OmniScraperGraph`). They're convenient for one-off scrapes of irregular sites where writing selectors isn't worth the time. The cost: you pay per-page LLM tokens forever. **Prefer the generate-once-selectors pattern above for anything you'll run more than a few times.** ScrapeGraphAI's own `code_generator_graph` is exactly this idea — use it (or the 30-line equivalent) rather than `SmartScraperGraph` for repeat work.

**Library choices and why:**
- `httpx` over `requests`: HTTP/2, async-ready, same API.
- `selectolax` over `BeautifulSoup`: 5–30× faster, lower memory, supports CSS selectors. Use BeautifulSoup only if you need its forgiving parser for very broken HTML.
- `trafilatura` for article body extraction (news, blog posts) — strips chrome, returns clean text. One call: `trafilatura.extract(html)`.
- `playwright` for JS-rendered sites. Prefer `page.evaluate()` to do the extraction in-browser.

If the deps aren't installed, install them in a venv: `python -m venv .venv && .venv/bin/pip install httpx selectolax`. Don't install globally.

## Pre-prep tiers — how much to clean before Claude sees anything

Pre-prep in Python is the whole point. The question is *how much* to do, because over-stripping can destroy the structure the user (or Claude) actually needs. Pick the lowest tier that gets the job done.

**Tier 0 — Deterministic extraction (preferred).** You know the fields. Use CSS selectors / `pandas.read_html` / a JSON API and emit `{title, price, date, ...}` rows. Claude never sees text at all, just structured data. Cheapest, most accurate, most stable. ~95% of scrapes should land here. **Walk every block type when the source uses a block model (Notion, Roam, etc.)** — callouts, toggles, embeds, and quotes hide links and content the headline blocks miss. Heading-only walks routinely under-extract.

**Tier 1 — Targeted slice + light clean.** You need a chunk of prose (an article body, a product description) but the page is mostly chrome. Use `trafilatura.extract(html)` for articles, or CSS-select the content container, then normalize whitespace. Output a small text field per record. Claude sees clean prose, not HTML.

**Tier 2 — Cleaned HTML for LLM extraction.** The structure is too irregular for selectors (e.g., wildly varying templates across a long-tail of sites). Strip `<script>`/`<style>`/`<nav>`/`<footer>`, drop noisy attributes (`class`, `style`, `data-*`, tracking IDs), keep semantic tags (`article`, `h1`–`h6`, `table`, `tr`, `td`, `ul`, `li`, `a[href]`). Pass the cleaned slice — not the full page — to Claude with a tight extraction schema. Use only when Tier 0/1 won't work; expect 5–20× the token cost of Tier 0.

**Tier 3 — Markdown conversion.** Same situation as Tier 2 but you want maximum readability/density. Convert cleaned HTML to Markdown (`html2text`, `markdownify`) before sending. Markdown is ~30–50% denser than equivalent HTML for the same semantic content, and Claude reads it well. Good for "summarize this page" or "answer questions about this doc" tasks.

### Pre-prep moves that always pay off

- **Strip chrome:** `<script>`, `<style>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, ad/cookie banners.
- **Normalize whitespace:** collapse runs of spaces and blank lines. Saves 10–30% with zero info loss.
- **Drop noisy attributes:** `class`, `style`, `data-*`, `aria-*` (unless you specifically need them), tracking IDs. Keep `href`, `src`, `id`, `itemprop`.
- **Deduplicate boilerplate across pages:** when crawling, hash repeated blocks (nav, sidebars) and drop them from all but the first occurrence.
- **Project early:** the moment you know which fields the user wants, project to them. Don't carry a 50k-token "cleaned page" forward when a 30-token row is the actual answer.

### Pre-prep moves that can hurt accuracy

- **Flattening tables to text** — destroys row/column relationships. Keep `<table>` structure or convert to CSV/Markdown tables, not prose.
- **Stripping headings** — `h1`–`h6` are cheap and disambiguate sections. Keep them.
- **Killing list markers** — `<ul>`/`<ol>` carry "these items are peers" meaning that's hard to recover.
- **Over-aggressive regex cleanup** that mangles content (e.g., a regex meant to strip nav links eating real body links).
- **Brittle deep selectors** like `div.container > div.row > div.col-md-8 > article > p` — break on the next site redesign. Prefer semantic selectors (`article`, `[itemprop="price"]`, `main`).

### Generate-once selectors (Tier 0 bootstrap)

When you don't yet know the right selectors for a new site, the cheap pattern is **generate the schema once with an LLM, then use it deterministically forever after**. One LLM call replaces every future LLM call:

1. Fetch one sample page.
2. Send a *small slice* of cleaned HTML (Tier 2 cleaning, just the repeating container) plus the field list to Claude with a tight schema-output prompt: `"Return JSON: {baseSelector, fields: [{name, css, attr?}]}"`.
3. Persist the resulting schema to disk (`schema.json`).
4. Every subsequent fetch uses `selectolax` + that schema — no LLM, no surprises, fully reproducible.

This is the right way to use an LLM in a scraper: as a *one-time selector generator*, not a per-page extractor. If the site changes layout, regenerate the schema (still one call) and keep going. Tools like `crawl4ai` ship this as `--generate-schema`; you can also do it in 30 lines with the Anthropic SDK.

### Decision rule

Ask: *"Can I name the fields I want?"*
- **Yes** → Tier 0. Selectors and structured output. Done.
- **No, but I want clean readable text** → Tier 1 (`trafilatura` or container-select).
- **No, and the structure varies wildly** → Tier 2 or 3 with a small cleaned slice and a tight schema.

Does pre-prep decrease accuracy? Only if you over-strip. Done well, it *increases* accuracy because Claude isn't distracted by 90% irrelevant chrome — the signal-to-noise ratio is much higher.

## Keeping HTML out of context — the rules

These all flow from the core idea. Violate them and the skill has failed.

1. **Never `cat`, `Read`, `head`, or otherwise pipe HTML into Claude's context.** If you need to see structure to write selectors, save HTML to `/tmp/page.html` and inspect it with `grep`/`wc -l`/targeted `sed -n '120,140p'` line ranges — never the whole file.
2. **To find selectors, write a tiny probe script** that prints, say, the first 3 matches of a guessed selector with their `outerHTML` truncated to 200 chars. Iterate on the script, not by reading the page.
3. **Output structured data, not HTML.** JSON for nested, CSV for flat tabular. Write to disk; don't print everything.
4. **When the user wants to see results, show a head:** `head -20 out.json` or `wc -l out.csv && head -5 out.csv`. The full file lives on disk.
5. **For multi-page crawls, log progress to stderr** (`page 47/200, 2341 rows`), not row dumps to stdout.
6. **If a page is huge and you only need one section,** slice the HTML before parsing: find the container div with a string search, parse only that subtree. Saves memory, not tokens — but on very large pages it speeds parsing too.

## Politeness and robustness

Not the focus of this skill, but worth getting right because failed scrapes waste tokens too:

- **Respect `robots.txt`.** Check it before crawling; the user is responsible for the legal/ToS call but you should surface obvious blocks.
- **Rate limit.** `time.sleep(1)` between requests is a sane default; back off on 429/503.
- **Set a real User-Agent** with a contact, not a fake browser string. Sites are nicer to honest bots.
- **Cache fetched HTML to disk** during development (`/tmp/scrape-cache/<hash>.html`) so iterating on selectors doesn't re-hit the server. Delete the cache when shipping.
- **Retry transient failures** (5xx, timeouts) with exponential backoff, max 3 attempts. Log permanent failures and continue — one bad URL shouldn't kill a 10k-page crawl.
- **Validate as you go.** If the parser returns 0 rows from a page that should have many, the selector broke — fail loudly rather than silently producing an empty CSV.

## When the user wants something specific

A few common shapes:

- **"Get all the products / listings / articles from this page"** → static HTML path. One script, CSS selectors, JSON output.
- **"Crawl the whole site"** → start from `sitemap.xml` if it exists. Otherwise, BFS from the homepage with a visited-set and a same-domain filter. Cap depth and total pages, and ask the user if the cap is right.
- **"Extract the article text from these URLs"** → `trafilatura.extract`. One row per URL: `{url, title, text, date}`.
- **"Scrape this table"** → try `pandas.read_html(url)` first; it's a one-liner if the table is well-formed `<table>` markup.
- **"This site needs login / is JS-heavy / has Cloudflare"** → Playwright. Persist the storage state file after manual login so the user only logs in once.

## Recipes for specific sources

These are the patterns that come up over and over. Each one trades a bit of generality for a *much* cheaper, more reliable extraction. Reach for these before writing a generic scraper.

### Notion public pages

Notion pages render client-side from JSON, so you do **not** need a browser. The page exposes an internal API that returns the entire block tree:

- Endpoint: `POST https://www.notion.so/api/v3/loadPageChunk` with body `{"pageId": "<uuid-with-dashes>", "limit": 100, "cursor": {"stack": []}, "chunkNumber": 0, "verticalColumns": false}`.
- The page ID is the 32-hex string at the end of the URL; insert dashes to get the UUID form (`8-4-4-4-12`).
- The response has `recordMap.block.<id>.value` entries. Each block has a `type` (`header`, `sub_header`, `text`, `bulleted_list`, `callout`, `toggle`, `bookmark`, `quote`, etc.) and `properties.title`, which is a rich-text array: `[["plain text"], ["linked text", [["a", "https://..."]]]]`.
- **Walk every block type, not just headings and paragraphs.** Callouts, toggles, bookmarks, and quotes routinely contain links and important text that a heading-only walk misses.
- For long pages, paginate with `cursor.stack` from the previous response until `cursor.stack` is empty.

### LinkedIn job postings

LinkedIn aggressively blocks scrapers and requires login for most data, so the cheap, durable path is the **public guest job-view endpoint**:

- URL pattern: `https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/<jobId>` where `<jobId>` is the numeric ID from a job URL (`/jobs/view/<jobId>`).
- Returns server-rendered HTML — no JS, no login.
- Selectors with `selectolax`:
  - **Title:** `h2.top-card-layout__title` or `h1` (fallback)
  - **Company:** `a.topcard__org-name-link` or `.topcard__flavor` (first `<a>`)
  - **Location:** `.topcard__flavor.topcard__flavor--bullet`
  - **Posted date:** `time.posted-time-ago__text` or `time[datetime]`
  - **Description HTML:** `div.show-more-less-html__markup` — pass to `trafilatura.extract` or `html2text` to get clean prose; this is the only field you'd ever need to clean rather than select.
  - **Seniority / employment type / function / industry:** `ul.description__job-criteria-list li` (each `<li>` has a `<h3>` label and `<span>` value).
- For search results pages, hit `https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=...&location=...&start=<N>` (pagination by 25). Returns a list of job cards with IDs you can then dereference.
- Be polite: 2–3 second delay between requests, set a real User-Agent. Don't try to log in or use authenticated endpoints — LinkedIn's ToS is explicit and enforcement is real.

**Output shape per job:** `{job_id, title, company, location, posted_date, description, seniority, employment_type, function, industries, url}`.

### YouTube video transcripts

The transcript is already a structured caption track — don't scrape the page, fetch the captions directly:

- Easiest path: `youtube-transcript-api` (`pip install youtube-transcript-api`).
  ```python
  from youtube_transcript_api import YouTubeTranscriptApi
  segments = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US"])
  # segments: [{"text": "...", "start": 0.0, "duration": 3.2}, ...]
  ```
  - `video_id` is the 11-char string after `v=` in the URL (or after `youtu.be/`).
  - Falls back gracefully across language codes; raises if no transcript exists.
  - Returns auto-generated transcripts when no manual one is available — flag `is_generated` on the returned `Transcript` object via `list_transcripts(video_id)` if that distinction matters.
- For metadata (title, channel, description, duration, publish date) you have two options:
  - **Cheap:** parse the `oEmbed` endpoint `https://www.youtube.com/oembed?url=<video_url>&format=json` for title and channel.
  - **Full:** the YouTube Data API v3 `videos.list?part=snippet,contentDetails,statistics&id=<id>` if the user has an API key. Don't scrape the watch page — it's huge and JS-rendered.
- Output format choice:
  - **Plain text:** join segment texts with spaces, optionally insert paragraph breaks at long pauses (`segment.start - prev.end > 2.0`). Smallest output, best for summarization.
  - **Timestamped:** keep `[hh:mm:ss] text` lines for each segment or every Nth segment. Useful when the user wants to cite or jump to specific moments.
  - **Chapter-aligned:** if the description contains chapter markers (`0:00 Intro\n2:34 ...`), parse them and group transcript segments into chapters.

**Output shape per video:** `{video_id, title, channel, published_at, duration_seconds, transcript: [{start, text}], full_text}`.

### Adding new recipes

When you find another source that comes up repeatedly (Reddit, GitHub issues, Substack, Hacker News, etc.), add a recipe here with: the cheapest endpoint, the exact selectors or JSON path, the output shape, and any politeness/auth gotchas. The recipe library is what makes this skill faster the more it gets used.

## Anti-patterns to avoid

- Using an LLM to parse HTML when CSS selectors would do. Selectors are deterministic, free, and 1000× faster.
- Reading the full HTML into the conversation "just to look at the structure." Use a probe script.
- Scraping with `curl` + Claude parsing the response. That's the worst of both worlds.
- Returning everything as one giant printed dict. Write to a file; show a head.
- Reinventing pagination logic when the site exposes a `?page=N` JSON API two clicks away in DevTools.

## Heavy-crawl patterns

When the job is more than a few hundred URLs, three patterns earn their keep. Skip them for one-off scrapes — they're overhead you don't need.

### 1. Scroll-to-completion (infinite scroll)

Many SPAs lazy-load content. Scroll until the page height stabilizes for several iterations:

```python
last_h, stable = 0, 0
while stable < 3:
    h = page.evaluate("document.body.scrollHeight")
    if h == last_h:
        stable += 1
    else:
        stable = 0
        last_h = h
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1500)
```

Three consecutive no-change reads is the standard "done" signal. Cap total iterations (e.g. 50) so a broken page doesn't loop forever.

### 2. Detail-page follow

Many list pages only render summaries; the real content lives on per-item detail pages. Two-phase scrape:

1. Walk the list and collect `(id, summary, detail_url)` tuples — cheap, one fetch per list page.
2. For each tuple, fetch the detail URL, parse, merge into the row. Polite delay (2–5s) between detail fetches.

Write intermediate results to disk after every N detail fetches so a crash doesn't lose progress.

### 3. Resume + concurrency for long crawls

For crawls that take more than a few minutes, build in:

- **Checkpointing.** After each successful fetch, append the URL to `done.txt` (one URL per line) and the row to `out.jsonl`. On startup, read `done.txt` into a set and skip URLs already there. A `Ctrl+C` mid-crawl loses at most one in-flight fetch.
- **Bounded concurrency with a per-domain cap.** A global `asyncio.Semaphore(N)` controls total in-flight requests; a `defaultdict(lambda: asyncio.Semaphore(M))` keyed by host caps per-domain. Typical defaults: global 5–10, per-domain 1–2. Without per-domain caps, even 5 workers can hammer a single host.
- **Exponential backoff on retryable errors.** 5xx and timeouts: retry up to 3× with `2 ** attempt` seconds plus jitter. 4xx (except 429): don't retry, log and skip.

Keep these in the same script that does the scraping; don't pull in a framework for a few hundred URLs.

### Save the script next to the data

When you finish a non-trivial scrape, save the final scraper script in the same directory as its output:

```
scrapes/acme-products-2026-05-01/
  scrape_acme_products.py    # the actual scraper used
  products.jsonl              # the data
  README.md                   # 3 lines: source URL, run date, row count
```

Future-you (or the user) re-runs the same scrape with one command, and the selectors you reverse-engineered aren't lost in chat history. Cheap habit, high payoff.

## Output expectations

When you finish a scrape, report to the user:
- The output file path and format.
- Row count.
- A 3–5 row sample (head of the file).
- Any URLs that failed and why.

That's it — the data lives on disk, not in chat.
