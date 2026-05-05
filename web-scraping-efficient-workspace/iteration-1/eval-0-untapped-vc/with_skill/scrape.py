#!/usr/bin/env python3
"""Scrape a public Notion page via the loadPageChunk API and emit structured JSON."""
import json
import re
import sys
import urllib.request
import urllib.error

PAGE_URL = "https://loud-particle-7d0.notion.site/Untapped-VC-Request-for-Startups-3528d2b9402b80c1a1f4c73db19ff356"
OUT = sys.argv[1] if len(sys.argv) > 1 else "outputs/extracted.json"

UA = "Mozilla/5.0 (compatible; research-bot/1.0; contact: sumrae412@gmail.com)"


def page_id_from_url(url: str) -> str:
    m = re.search(r"([0-9a-f]{32})", url.replace("-", ""))
    if not m:
        raise ValueError("no page id in url")
    h = m.group(1)
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": UA,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def load_page(page_id: str) -> dict:
    # Public Notion API endpoint used by notion.site
    url = "https://loud-particle-7d0.notion.site/api/v3/loadPageChunk"
    payload = {
        "page": {"id": page_id},
        "limit": 100,
        "cursor": {"stack": []},
        "chunkNumber": 0,
        "verticalColumns": False,
    }
    blocks = {}
    chunk = 0
    while True:
        payload["chunkNumber"] = chunk
        resp = post_json(url, payload)
        rb = resp.get("recordMap", {}).get("block", {})
        if not rb:
            break
        for k, v in rb.items():
            # Notion wraps as { spaceId, value: { value: {...}, role } }
            inner = v
            for _ in range(3):
                if isinstance(inner, dict) and "value" in inner and isinstance(inner["value"], dict) and "type" not in inner:
                    inner = inner["value"]
                else:
                    break
            blocks[k] = inner
        cursor = resp.get("cursor", {})
        if not cursor.get("stack"):
            break
        payload["cursor"] = cursor
        chunk += 1
        if chunk > 20:
            break
    return blocks


def text_from_title(title) -> tuple[str, list[dict]]:
    """Notion title is list of [text, [[formats]]]. Returns (plain_text, links)."""
    if not title:
        return "", []
    parts = []
    links = []
    for seg in title:
        if not isinstance(seg, list) or not seg:
            continue
        text = seg[0]
        parts.append(text)
        if len(seg) > 1 and isinstance(seg[1], list):
            for fmt in seg[1]:
                if isinstance(fmt, list) and fmt and fmt[0] == "a" and len(fmt) > 1:
                    links.append({"text": text, "href": fmt[1]})
    return "".join(parts), links


def main():
    page_id = page_id_from_url(PAGE_URL)
    blocks = load_page(page_id)
    if not blocks:
        print("no blocks fetched", file=sys.stderr)
        sys.exit(2)

    # Find root page block
    root = None
    for bid, b in blocks.items():
        if b.get("type") == "page" and bid.replace("-", "") == page_id.replace("-", ""):
            root = b
            break
    if root is None:
        # fallback: first page-type block
        for b in blocks.values():
            if b.get("type") == "page":
                root = b
                break

    page_title, _ = text_from_title((root or {}).get("properties", {}).get("title")) if root else ("", [])
    content_ids = (root or {}).get("content", []) if root else []

    sections = []
    all_links = []
    current = {"heading": None, "level": None, "body": [], "lists": [], "links": []}

    def flush():
        if current["heading"] is None and not current["body"] and not current["lists"]:
            return
        sections.append({
            "heading": current["heading"],
            "level": current["level"],
            "body": "\n".join(current["body"]).strip(),
            "list_items": list(current["lists"]),
            "links": list(current["links"]),
        })

    HEADING_TYPES = {"header": 1, "sub_header": 2, "sub_sub_header": 3}
    LIST_TYPES = {"bulleted_list", "numbered_list", "to_do"}

    for cid in content_ids:
        b = blocks.get(cid)
        if not b:
            continue
        btype = b.get("type")
        title = b.get("properties", {}).get("title")
        text, links = text_from_title(title)
        all_links.extend(links)

        if btype in HEADING_TYPES:
            flush()
            current = {
                "heading": text,
                "level": HEADING_TYPES[btype],
                "body": [],
                "lists": [],
                "links": list(links),
            }
        elif btype in LIST_TYPES:
            if text:
                current["lists"].append(text)
            current["links"].extend(links)
        elif btype in ("text", "quote", "callout", "toggle"):
            if text:
                current["body"].append(text)
            current["links"].extend(links)
        elif btype == "divider":
            continue
        else:
            if text:
                current["body"].append(text)
            current["links"].extend(links)

    flush()

    result = {
        "url": PAGE_URL,
        "page_title": page_title,
        "sections": sections,
        "links": all_links,
        "stats": {
            "sections": len(sections),
            "links": len(all_links),
            "blocks": len(content_ids),
        },
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"wrote {OUT}: {len(sections)} sections, {len(all_links)} links, {len(content_ids)} blocks", file=sys.stderr)


if __name__ == "__main__":
    main()
