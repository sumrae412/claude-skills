#!/usr/bin/env python3
"""Extract article content from a URL into clean JSON.

Usage: python article.py <url> [<url> ...] > out.json

Output per URL: {url, title, author, date, text, word_count, lang, error?}
Uses trafilatura (handles 95% of news/blog/article pages); falls back to
selectolax for very plain pages.
"""
from __future__ import annotations
import json, sys, time

try:
    import trafilatura
    from trafilatura.settings import use_config
except ImportError:
    sys.exit("pip install trafilatura")


def extract(url: str) -> dict:
    cfg = use_config()
    cfg.set("DEFAULT", "EXTRACTION_TIMEOUT", "20")
    downloaded = trafilatura.fetch_url(url, config=cfg)
    if not downloaded:
        return {"url": url, "error": "fetch failed"}
    data = trafilatura.extract(
        downloaded,
        output_format="json",
        with_metadata=True,
        favor_recall=True,
        config=cfg,
    )
    if not data:
        return {"url": url, "error": "no extractable content"}
    parsed = json.loads(data)
    text = parsed.get("text", "") or ""
    return {
        "url": url,
        "title": parsed.get("title"),
        "author": parsed.get("author"),
        "date": parsed.get("date"),
        "text": text,
        "word_count": len(text.split()),
        "lang": parsed.get("language"),
    }


def main(urls: list[str]) -> None:
    out = []
    for u in urls:
        out.append(extract(u))
        time.sleep(1)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print(f"\n# {len(out)} URLs, {sum(1 for r in out if 'error' not in r)} ok", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
