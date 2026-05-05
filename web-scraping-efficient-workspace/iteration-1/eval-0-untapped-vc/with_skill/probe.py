#!/usr/bin/env python3
"""Probe: try loadPageChunk variants and print only counts/keys, no HTML."""
import json, urllib.request, sys

UA = "Mozilla/5.0 (compatible; research-bot/1.0)"
PID = "3528d2b9-402b-80c1-a1f4-c73db19ff356"

ENDPOINTS = [
    "https://loud-particle-7d0.notion.site/api/v3/loadPageChunk",
    "https://www.notion.so/api/v3/loadPageChunk",
    "https://loud-particle-7d0.notion.site/api/v3/loadCachedPageChunk",
]

payload = {
    "page": {"id": PID},
    "limit": 100,
    "cursor": {"stack": []},
    "chunkNumber": 0,
    "verticalColumns": False,
}

for url in ENDPOINTS:
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read()
            j = json.loads(body)
            rm = j.get("recordMap", {})
            print(f"OK {url}: bytes={len(body)} block_count={len(rm.get('block', {}))} keys={list(j.keys())[:6]}")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} {url}: {e.reason}")
    except Exception as e:
        print(f"ERR {url}: {type(e).__name__}: {e}")
