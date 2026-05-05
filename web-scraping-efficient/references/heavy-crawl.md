# Heavy-crawl patterns

Load this when the user asks to crawl a whole site, scrape "all the X", or process more than ~100 URLs. Skip for one-off scrapes.

## 1. Scroll-to-completion (infinite scroll)

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

## 2. Detail-page follow

Many list pages only render summaries; the real content lives on per-item detail pages. Two-phase scrape:

1. Walk the list and collect `(id, summary, detail_url)` tuples — cheap, one fetch per list page.
2. For each tuple, fetch the detail URL, parse, merge into the row. Polite delay (2–5s) between detail fetches.

Write intermediate results to disk after every N detail fetches so a crash doesn't lose progress.

## 3. Resume + concurrency for long crawls

For crawls that take more than a few minutes, build in:

- **Checkpointing.** After each successful fetch, append the URL to `done.txt` (one URL per line) and the row to `out.jsonl`. On startup, read `done.txt` into a set and skip URLs already there. A `Ctrl+C` mid-crawl loses at most one in-flight fetch.
- **Bounded concurrency with a per-domain cap.** A global `asyncio.Semaphore(N)` controls total in-flight requests; a `defaultdict(lambda: asyncio.Semaphore(M))` keyed by host caps per-domain. Typical defaults: global 5–10, per-domain 1–2. Without per-domain caps, even 5 workers can hammer a single host.
- **Exponential backoff on retryable errors.** 5xx and timeouts: retry up to 3× with `2 ** attempt` seconds plus jitter. 4xx (except 429): don't retry, log and skip.

Keep these in the same script that does the scraping; don't pull in a framework for a few hundred URLs.

## Save the script next to the data

When you finish a non-trivial scrape, save the final scraper script in the same directory as its output:

```
scrapes/acme-products-2026-05-01/
  scrape_acme_products.py    # the actual scraper used
  products.jsonl              # the data
  README.md                   # 3 lines: source URL, run date, row count
```

Future-you (or the user) re-runs the same scrape with one command, and the selectors you reverse-engineered aren't lost in chat history.
