#!/usr/bin/env python3
"""Generic structured extraction from any HTML page. No LLM, no browser.

Usage: python webpage.py <url> [--render]

Output JSON: {url, title, meta_description, headings: [{level, text}],
              paragraphs: [text], links: [{text, href}], jsonld: [...],
              og: {...}}

--render: use Playwright if the static HTML is empty (SPA fallback).

When the user wants "the data on this page" but you don't know the schema,
this dumps everything semantically meaningful in a compact form.
"""
from __future__ import annotations
import json, sys

try:
    import httpx
    from selectolax.parser import HTMLParser
except ImportError:
    sys.exit("pip install httpx selectolax")

UA = "Mozilla/5.0 (compatible; research-bot/1.0)"


def fetch_static(url: str) -> str:
    r = httpx.get(url, headers={"User-Agent": UA}, timeout=20, follow_redirects=True)
    r.raise_for_status()
    return r.text


def fetch_rendered(url: str) -> str:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        html = page.content()
        b.close()
    return html


def extract(html: str, url: str) -> dict:
    tree = HTMLParser(html)
    title = tree.css_first("title")
    md = tree.css_first('meta[name="description"]')
    og = {n.attributes.get("property", "")[3:]: n.attributes.get("content", "")
          for n in tree.css('meta[property^="og:"]') if n.attributes.get("property")}
    headings = [{"level": int(h.tag[1]), "text": h.text(strip=True)}
                for h in tree.css("h1,h2,h3,h4") if h.text(strip=True)]
    paragraphs = [p.text(strip=True) for p in tree.css("p") if len(p.text(strip=True)) > 30]
    links = [{"text": a.text(strip=True), "href": a.attributes.get("href", "")}
             for a in tree.css("a[href]")
             if a.text(strip=True) and a.attributes.get("href", "").startswith(("http", "/"))]
    jsonld = []
    for s in tree.css('script[type="application/ld+json"]'):
        try:
            jsonld.append(json.loads(s.text()))
        except Exception:
            pass
    return {
        "url": url,
        "title": title.text(strip=True) if title else None,
        "meta_description": md.attributes.get("content") if md else None,
        "og": og,
        "headings": headings,
        "paragraphs": paragraphs,
        "links": links[:200],  # cap noise; full list rarely needed
        "jsonld": jsonld,
    }


def main(url: str, render: bool) -> None:
    html = fetch_static(url)
    body_text_len = len(HTMLParser(html).body.text(strip=True)) if HTMLParser(html).body else 0
    if render or body_text_len < 200:
        html = fetch_rendered(url)
    json.dump(extract(html, url), sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], "--render" in sys.argv)
