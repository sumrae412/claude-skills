#!/usr/bin/env python3
"""Probe2: dump block id/type/title-summary, no full HTML."""
import json, urllib.request, re, sys

UA = "Mozilla/5.0 (compatible; research-bot/1.0)"
PID = "3528d2b9-402b-80c1-a1f4-c73db19ff356"
url = "https://loud-particle-7d0.notion.site/api/v3/loadPageChunk"
payload = {"page": {"id": PID}, "limit": 100, "cursor": {"stack": []}, "chunkNumber": 0, "verticalColumns": False}
req = urllib.request.Request(url, data=json.dumps(payload).encode(),
    headers={"User-Agent": UA, "Content-Type": "application/json"}, method="POST")
j = json.loads(urllib.request.urlopen(req, timeout=20).read())
rb = j["recordMap"]["block"]
print("total blocks:", len(rb))
types = {}
for k, v in rb.items():
    val = v.get("value", v)
    t = val.get("type")
    types[t] = types.get(t, 0) + 1
print("types:", types)
# print first 5 entries minimal
for i, (k, v) in enumerate(rb.items()):
    val = v.get("value", v)
    title = val.get("properties", {}).get("title")
    summary = ""
    if title and isinstance(title, list):
        try:
            summary = "".join(s[0] for s in title if isinstance(s, list) and s)[:80]
        except Exception:
            summary = "?"
    print(f"  {k} type={val.get('type')} content_len={len(val.get('content', []) or [])} title={summary!r}")
    if i >= 8:
        break
# find root
print("looking for root id ending with", PID.replace("-", "")[-12:])
for k, v in rb.items():
    val = v.get("value", v)
    if val.get("type") == "page":
        print("PAGE block:", k, "content_len=", len(val.get("content", []) or []))
