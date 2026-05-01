---
name: web-scraping-efficient
description: Token-efficient Python web scraping. Use whenever the user wants to scrape, crawl, extract, or pull data from a website, HTML page, online article, or GitHub repo — even when they don't say "token-efficient." Triggers on "scrape this site," "get the data from this page," "extract the article," "summarize this URL," "what's in this GitHub repo," or pasting a URL with an extraction goal. The skill's whole point is to keep raw HTML out of Claude's context: fetch and parse in a Python subprocess, return only the structured fields the user asked for. **Default behavior:** pick a bundled script, run it, write JSON to disk, show a head. Multi-step exploration is the exception.
---

# Token-efficient web scraping

## The core idea

Raw HTML is huge — a single article page can be 100k+ tokens of nav, scripts, tracking, and CSS. If that lands in your context, the session is wrecked before you've extracted anything.

**The whole game: do the fetch and parse in a Python subprocess; only structured rows enter Claude's context.** Claude sees `[{"title": "...", "text": "..."}]`, never `<html>...</html>`.

## Bundled scripts — use these first

Four helpers cover the common cases. **Default to `dispatch.py`** — it picks the right script from the URL. Use a specific script only when you want to override the dispatch.

| URL shape | Script | Output |
|---|---|---|
| **Don't know / mixed** | `scripts/dispatch.py` | Routes to the right script below by URL pattern |
| News, blog post, Substack, Medium, any article-shaped page | `scripts/article.py` | `{url, title, author, date, text, word_count, lang}` |
| `github.com/owner/repo` | `scripts/github_repo.py` | `{full_name, description, stars, tree, files: {README.md: ...}}` |
| Anything else — generic webpage, table, structured data | `scripts/webpage.py` | `{title, headings, paragraphs, links, jsonld, og}` |

Dispatch rules (see `scripts/dispatch.py`): GitHub URL → `github_repo.py --files`; URL contains `/blog/`, `/post/`, `/p/`, `substack.com`, `medium.com`, or a `/YYYY/MM/` date → `article.py`; otherwise → `webpage.py`. Override the dispatch only if you have a specific reason.

### One-line invocations

```bash
# Default: let dispatch pick
python /path/to/web-scraping-efficient/scripts/dispatch.py "<any-url>" > /tmp/out.json

# Article → clean text
python /path/to/web-scraping-efficient/scripts/article.py "https://example.com/post" > /tmp/article.json
wc -l /tmp/article.json && jq '{title, word_count, date}' /tmp/article.json

# GitHub repo → structure + README + key docs
python /path/to/web-scraping-efficient/scripts/github_repo.py "https://github.com/owner/repo" --files > /tmp/repo.json
jq '{description, stars, file_count, file_keys: (.files | keys)}' /tmp/repo.json

# Generic webpage → semantic dump
python /path/to/web-scraping-efficient/scripts/webpage.py "https://target.com/page" > /tmp/page.json
jq '{title, headings: (.headings | length), paragraphs: (.paragraphs | length), links: (.links | length)}' /tmp/page.json
```

For GitHub repos, **always prefer `gh api` over scraping** — the script does this for you. Never WebFetch a `github.com` URL when `gh api repos/<owner>/<repo>` will return clean JSON.

### Reporting back — strict 4-line contract

After running a script, return **exactly** these four lines and stop. No preamble, no JSON dump, no "here's what I did."

```
path: <abs/path/to/out.json>
rows: <n>  fields: <key1, key2, key3>
sample: <one-line summary of the first row — e.g. "Title by Author, 2024-12-01, 1,247 words">
failures: <n urls failed | none>
```

The user reads the file if they want detail. Pasting JSON inline is the most common way agents leak HTML-equivalent bloat back into context.

### Budget your exploration

Before writing any custom code: **state in one line what you'll try, then write it in one pass.** Don't iterate on selectors interactively in chat — each round costs tokens and rarely improves the answer. Two budgets to respect:

- **One probe script max** before committing to an approach. If the first probe doesn't tell you enough, write a second — don't read the page.
- **Three tool calls max** for a single-page extraction (one fetch, one parse, one report). If you're past three, you're either solving the wrong problem or you should have used `dispatch.py`.

## When the bundled scripts aren't enough

Fall through to custom scraping in this order:

1. **Is there a JSON API?** Open DevTools → Network → Fetch/XHR. Modern sites hydrate from JSON endpoints — 10–100× cheaper to parse than HTML. Hit the endpoint directly with `httpx`.
2. **Is there a sitemap or RSS feed?** Check `/robots.txt`, `/sitemap.xml`, `/feed`. Often gives you every URL or every record without crawling.
3. **Is the content static HTML with known fields?** Use `httpx` + `selectolax` and write a 30-line scraper. Skeleton:

   ```python
   import httpx, json, sys
   from selectolax.parser import HTMLParser
   r = httpx.get(sys.argv[1], headers={"User-Agent": "research-bot/1.0"}, timeout=20)
   tree = HTMLParser(r.text)
   rows = [{"title": c.css_first("h2").text(strip=True),
            "price": c.css_first(".price").text(strip=True)}
           for c in tree.css("div.product-card")]
   json.dump(rows, open(sys.argv[2], "w"))
   print(f"{len(rows)} rows → {sys.argv[2]}")
   ```

4. **Does it require JavaScript execution?** Use Playwright headless. Extract via `page.evaluate(...)` running JS *in the browser* so only JSON crosses the boundary — don't return `page.content()` to Python and parse there.

## Reconnaissance — when you must explore

One `curl`. No browser. **Cache to a stable path so subsequent steps don't refetch.**

```bash
HASH=$(printf '%s' "$URL" | md5)            # stable per-URL key
CACHE=/tmp/scrape-cache/$HASH
mkdir -p "$CACHE"
test -f "$CACHE/page.html" || curl -sL -A "Mozilla/5.0 (compatible; research-bot/1.0)" \
  -D "$CACHE/headers.txt" "$URL" -o "$CACHE/page.html"
wc -c "$CACHE/page.html"
grep -ic "<term>" "$CACHE/page.html"          # one grep per target field
```

Every later step (selector probes, framework signature checks, blocking-signal grep) reads from `$CACHE/`. **Never refetch a URL within a session** — it wastes the server's bandwidth and your tokens, and gives different results if the page changed mid-task.

**Quality gate:** if every target field is in `page.html` AND no protection signals (`grep -i "^server:\|cf-ray:" "$CACHE/headers.txt"`), write a `selectolax` parser. **Do not launch a browser.**

### Framework signatures — instant Tier-0 shortcuts

Grep `page.html` for these:

| Marker | What it means | Where the data is |
|---|---|---|
| `__NEXT_DATA__` | Next.js | `<script id="__NEXT_DATA__">{...}</script>` — entire page state as JSON |
| `application/ld+json` | schema.org | One or more JSON-LD blocks — often has all your fields |
| `/_next/data/...` | Next.js page-data API | Hit that URL directly for clean JSON |
| `/wp-json/wp/v2/` | WordPress REST API | `?per_page=100` lists posts/pages |
| `data-reactroot`, empty `<div id="app">` | SPA — raw HTML is empty | Use the network-discovery recipe; do NOT scrape rendered DOM |
| `Shopify.theme` | Shopify | `?view=json` on collection/product URLs returns JSON |

A single match collapses a half-day scraper into 20 lines.

### Network-panel API discovery (for SPAs)

When raw HTML is empty and there's no `__NEXT_DATA__`, capture XHR/fetch calls once with Playwright then ditch the browser:

```python
from playwright.sync_api import sync_playwright
calls = []
with sync_playwright() as p:
    page = p.chromium.launch().new_page()
    page.on("response", lambda r: calls.append((r.status, r.headers.get("content-type", ""), r.url)))
    page.goto("https://target.com/page", wait_until="networkidle")
for s, ct, url in calls:
    if "json" in ct: print(s, url)
```

Filter for `/api/`, `/graphql`. Hit those URLs with `httpx` from then on.

### Blocking signals

Flag these and adjust strategy (back off, rotate UA, switch to authenticated session, or stop):

| Signal | Means |
|---|---|
| 403, 503 | Blocked or under protection |
| 429 | Rate-limited — honor `Retry-After` |
| `cf-ray` header, "Checking your browser" | Cloudflare challenge |
| CAPTCHA elements (`g-recaptcha`, `hcaptcha`, Turnstile) | Stop — don't try to solve |
| Empty body / content differs from real-browser fetch | Server is serving you a stub |

For casual scrapes, polite delays + a real User-Agent solve most things.

## Generate-once selectors (advanced Tier-0)

When the bundled scripts don't fit and you don't know the right selectors, **use an LLM exactly once** to generate a CSS-selector schema from a sample page:

1. Fetch one sample page.
2. Send a small slice of cleaned HTML (just the repeating container) plus the field list to Claude: `"Return JSON: {baseSelector, fields: [{name, css, attr?}]}"`.
3. Persist `schema.json` to disk.
4. Every subsequent fetch uses `selectolax` + that schema — no LLM, no surprises.

If the site changes layout, regenerate (still one call). This is the correct way to use an LLM in a scraper: as a one-time selector generator, never as a per-page extractor.

## The rules — keeping HTML out of context

1. **Never `cat`/`Read`/`head` HTML into Claude's context.** Save to `/tmp/page.html`, inspect with `grep`/`wc -l`/targeted `sed -n '120,140p'`.
2. **To find selectors, write a tiny probe script** that prints first 3 matches truncated to 200 chars. Iterate on the script, not by reading the page.
3. **Output structured data, not HTML.** JSON for nested, CSV for flat. Write to disk.
4. **Show a head, not the full file:** `head -20 out.json` or `jq '{title, count: (.rows | length)}' out.json`.
5. **For multi-page crawls, log progress to stderr** (`page 47/200, 2341 rows`), not row dumps to stdout.

## Politeness and robustness

- **Respect `robots.txt`.** Surface obvious blocks; the user owns the legal/ToS call.
- **Rate limit.** `time.sleep(1)` between requests; back off on 429/503.
- **Real User-Agent.** `"Mozilla/5.0 (compatible; research-bot/1.0; <contact>)"` beats fake browsers — sites are nicer to honest bots.
- **Cache fetched HTML to disk** during dev (`/tmp/scrape-cache/<hash>.html`) so iterating on selectors doesn't re-hit the server.
- **Retry transient failures** (5xx, timeouts) with exponential backoff, max 3 attempts.
- **Validate as you go.** If the parser returns 0 rows from a page that should have many, fail loudly.

## Library choices

- `httpx` over `requests`: HTTP/2, async, same API.
- `selectolax` over `BeautifulSoup`: 5–30× faster, supports CSS selectors. Use BS4 only for very broken HTML.
- `trafilatura` for article body extraction (the bundled `article.py` uses it).
- `playwright` for JS-rendered sites. Prefer `page.evaluate()` for in-browser extraction.
- `pandas.read_html(url)` for `<table>` markup — one-liner.
- **`gh api`** for everything GitHub. Never scrape `github.com` HTML.

If deps aren't installed: `python -m venv .venv && .venv/bin/pip install httpx selectolax trafilatura`.

**Higher-level alternative:** [`crawl4ai`](https://github.com/unclecode/crawl4ai) bundles fetch + headless rendering + Markdown + schema-extraction in one CLI (`crwl <url> -o markdown`). Heavier dep, useful for "render this JS-heavy page and give me clean Markdown."

**LLM-per-page tools — use sparingly.** [ScrapeGraphAI](https://github.com/ScrapeGraphAI/Scrapegraph-ai) sends page content to an LLM for *every* extraction. Convenient for one-off irregular sites, expensive for repeat work. Prefer the generate-once-selectors pattern above.

## Anti-patterns

- Using an LLM (or `WebFetch`) to parse HTML when CSS selectors would do. Selectors are deterministic, free, 1000× faster.
- Reading full HTML into chat "just to look at the structure." Write a probe script.
- Scraping `github.com` HTML when `gh api` exists.
- Returning everything as one giant printed dict. Write to a file, show a head.
- Reinventing pagination logic when the site exposes `?page=N` JSON two clicks away in DevTools.
- Iterating on selectors interactively in chat. Pick one approach, write it once, run it.

## Reference files (load on demand)

- `references/specialized-recipes.md` — exact endpoints and selectors for Notion public pages, LinkedIn job postings, and YouTube transcripts. Load when scraping any of those.
- `references/heavy-crawl.md` — scroll-to-completion, detail-page follow, resume + per-domain concurrency. Load when crawling a whole site, scraping "all the X", or processing >100 URLs.

## Output expectations

When you finish:
- Output file path and format.
- Row/section count.
- 3–5 sample fields (not full content).
- Any URLs that failed.

The data lives on disk, not in chat.
