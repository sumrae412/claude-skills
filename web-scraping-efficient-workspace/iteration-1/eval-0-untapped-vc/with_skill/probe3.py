#!/usr/bin/env python3
import json, urllib.request, sys
UA = "Mozilla/5.0 (compatible; research-bot/1.0)"
PID = "3528d2b9-402b-80c1-a1f4-c73db19ff356"
url = "https://loud-particle-7d0.notion.site/api/v3/loadPageChunk"
payload = {"page": {"id": PID}, "limit": 100, "cursor": {"stack": []}, "chunkNumber": 0, "verticalColumns": False}
req = urllib.request.Request(url, data=json.dumps(payload).encode(),
    headers={"User-Agent": UA, "Content-Type": "application/json"}, method="POST")
j = json.loads(urllib.request.urlopen(req, timeout=20).read())
rb = j["recordMap"]["block"]
# print top-level keys of first record
k0 = next(iter(rb))
v0 = rb[k0]
print("first record top-level keys:", list(v0.keys()))
print("first record subkeys preview:")
for kk in v0.keys():
    sub = v0[kk]
    if isinstance(sub, dict):
        print(f"  {kk}: keys={list(sub.keys())[:10]}")
    else:
        print(f"  {kk}: type={type(sub).__name__} val_short={str(sub)[:80]}")
