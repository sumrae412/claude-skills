#!/usr/bin/env python3
"""Map a site's URL space cheaply, before crawling it. No headless browser.

Usage:
  python map_site.py <domain-or-url> [--filter <substring>] [--max N] [--json]

Behavior:
  1. Fetch /robots.txt and collect any `Sitemap:` lines.
  2. Fetch sitemap.xml (default location if robots.txt names none), and
     recurse one level into sitemap-index files (<sitemapindex><sitemap>).
  3. Normalize: strip fragments, dedup after stripping protocol + www.
  4. Optional --filter <substring> keeps only matching URLs; --max N caps
     the list (default 500; prints a truncation note on stderr if hit).
  5. Print URLs one per line, or JSON with --json.

Output (default): one URL per line.
Output (--json): {"domain": ..., "count": N, "truncated": bool, "urls": [...]}

Why: discover-by-crawling burns a fetch per page just to learn the URL
space exists. A sitemap gives you the whole space in 1-2 requests — map
first, then fetch only the pages that matter.

If no sitemap is found (missing/404), exits with a clear message instead
of a traceback — fall back to targeted fetches or a site: search.
"""
from __future__ import annotations
import json, re, sys
from urllib.parse import urljoin, urlparse, urlunparse

try:
    import httpx
except ImportError:
    sys.exit("pip install httpx")

UA = "Mozilla/5.0 (compatible; research-bot/1.0)"
DEFAULT_MAX = 500


def normalize_domain(s: str) -> str:
    """Accept a bare domain or a full URL; return a scheme+netloc base."""
    if not re.match(r"^https?://", s):
        s = f"https://{s}"
    p = urlparse(s)
    return f"{p.scheme}://{p.netloc}"


def normalize_url(url: str) -> str:
    """Strip fragment; used pre-dedup. Keeps scheme/www variants distinct
    at this stage — the dedup key (below) is what collapses those."""
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, p.path, p.params, p.query, ""))


def dedup_key(url: str) -> str:
    """Key used to collapse protocol/www variants of the same URL."""
    p = urlparse(url)
    netloc = p.netloc.lower().removeprefix("www.")
    path = p.path.rstrip("/") or "/"
    return f"{netloc}{path}?{p.query}"


def fetch(url: str) -> httpx.Response | None:
    try:
        r = httpx.get(url, headers={"User-Agent": UA}, timeout=15, follow_redirects=True)
        if r.status_code >= 400:
            return None
        return r
    except httpx.HTTPError:
        return None


def sitemaps_from_robots(base: str) -> list[str]:
    r = fetch(urljoin(base + "/", "robots.txt"))
    if not r:
        return []
    out = []
    for line in r.text.splitlines():
        line = line.strip()
        if line.lower().startswith("sitemap:"):
            out.append(line.split(":", 1)[1].strip())
    return out


def parse_sitemap_xml(xml_text: str) -> tuple[list[str], list[str]]:
    """Return (urls, nested_sitemap_urls) from a <urlset> or <sitemapindex>."""
    # Strip namespace prefixes so plain regex/string matching works without
    # a full XML-namespace-aware parser (stdlib xml.etree, no new deps).
    urls, nested = [], []
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_text)
        tag = root.tag.rsplit("}", 1)[-1]
        if tag == "sitemapindex":
            for sm in root:
                loc = sm.find("{*}loc")
                if loc is None:
                    loc = sm.find("loc")
                if loc is not None and loc.text:
                    nested.append(loc.text.strip())
        else:  # urlset
            for u in root:
                loc = u.find("{*}loc")
                if loc is None:
                    loc = u.find("loc")
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())
    except ET.ParseError:
        # Fall back to a permissive regex scrape if the XML is malformed.
        urls = re.findall(r"<loc>\s*(.*?)\s*</loc>", xml_text)
    return urls, nested


def collect(base: str, filter_sub: str | None, max_n: int) -> tuple[list[str], bool]:
    sitemap_urls = sitemaps_from_robots(base)
    if not sitemap_urls:
        sitemap_urls = [urljoin(base + "/", "sitemap.xml")]

    all_urls: list[str] = []
    seen_keys: set[str] = set()
    truncated = False

    def add(url: str) -> bool:
        """Return False (signal stop) once max_n reached."""
        nonlocal truncated
        norm = normalize_url(url)
        key = dedup_key(norm)
        if key in seen_keys:
            return True
        if filter_sub and filter_sub not in norm:
            return True
        seen_keys.add(key)
        all_urls.append(norm)
        if len(all_urls) >= max_n:
            truncated = True
            return False
        return True

    found_any_sitemap = False
    queue = list(sitemap_urls)
    depth_seen: set[str] = set()
    recursed_once = False

    while queue:
        sm_url = queue.pop(0)
        if sm_url in depth_seen:
            continue
        depth_seen.add(sm_url)
        r = fetch(sm_url)
        if not r:
            continue
        found_any_sitemap = True
        urls, nested = parse_sitemap_xml(r.text)
        for u in urls:
            if not add(u):
                return all_urls, truncated
        # Recurse exactly one level into sitemap-index files.
        if nested and not recursed_once:
            queue.extend(nested)
        elif nested and recursed_once:
            pass  # already recursed one level; don't go deeper
        if nested:
            recursed_once = True

    if not found_any_sitemap:
        sys.exit(
            f"no sitemap found for {base} — checked robots.txt and "
            f"{urljoin(base + '/', 'sitemap.xml')}. "
            "Fall back to targeted fetches or a site: search."
        )

    return all_urls, truncated


def main(argv: list[str]) -> None:
    if not argv:
        sys.exit(__doc__)
    target = argv[0]
    filter_sub = None
    max_n = DEFAULT_MAX
    as_json = "--json" in argv
    if "--filter" in argv:
        i = argv.index("--filter")
        filter_sub = argv[i + 1] if i + 1 < len(argv) else None
    if "--max" in argv:
        i = argv.index("--max")
        max_n = int(argv[i + 1]) if i + 1 < len(argv) else DEFAULT_MAX

    base = normalize_domain(target)
    urls, truncated = collect(base, filter_sub, max_n)

    if truncated:
        print(f"# truncated at --max {max_n}; more URLs may exist", file=sys.stderr)

    if as_json:
        json.dump(
            {"domain": base, "count": len(urls), "truncated": truncated, "urls": urls},
            sys.stdout, ensure_ascii=False, indent=2,
        )
    else:
        print("\n".join(urls))


if __name__ == "__main__":
    main(sys.argv[1:])
