#!/usr/bin/env python3
"""Hybrid retrieval over a markdown memory corpus.

Combines BM25 keyword scoring with entity-overlap boost to rank files
relevant to a query. Pure stdlib — no vector DB, no LLM, no embeddings.

Default roots cover the user's cross-cutting knowledge surfaces:

    ~/claude_code/agent-vault/agent/
    ~/claude_code/agent-vault/projects/
    ~/claude_code/agent-vault/people/
    ~/.claude/projects/<project>/memory/

Usage:

    python3 scripts/search_vault.py "kimi model id" --top 5
    python3 scripts/search_vault.py "parallel session race" --root ~/claude_code/agent-vault
    python3 scripts/search_vault.py "PR #66" --json

The entity boost matters when keyword overlap is low but a high-signal
token (PR ref, repo path, skill slug, CAPITALIZED noun) lands a direct
hit. Entities are weighted ~3x a plain term to reflect that.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache"}

STOP = set(
    """a an and are as at be but by for from has have if in into is it its
of on or that the their then there these they this to was were what when where
which who will with you your yours we our us not no can do does did had how use
using used uses see also via per case eg ie""".split()
)

WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{2,}")

# Entity extractors — high-signal tokens that beat bag-of-words on precision.
# Each yields normalized strings (lowercase where case is not meaningful).
ENTITY_PATTERNS = [
    # PR / issue references — keep the # for unambiguous matching
    (re.compile(r"#\d{1,5}\b"), lambda m: m.group(0)),
    # Repo paths in markdown links: [repo#N](url) → repo#N
    (re.compile(r"\b([a-z0-9_.-]+#\d{1,5})\b"), lambda m: m.group(1).lower()),
    # File paths with extensions (relative or absolute)
    (re.compile(r"\b([A-Za-z0-9_./~-]+\.(?:py|ts|tsx|js|jsx|md|json|yml|yaml|sh))\b"), lambda m: m.group(1)),
    # Backticked identifiers: `function_name`, `CONSTANT_NAME`, `slug-name`
    (re.compile(r"`([A-Za-z][A-Za-z0-9_.-]{2,})`"), lambda m: m.group(1)),
    # Quoted env vars / constants: ALL_CAPS_WITH_UNDERSCORES
    (re.compile(r"\b([A-Z][A-Z0-9_]{3,})\b"), lambda m: m.group(1)),
    # CamelCase proper nouns: CourierFlow, ToneGuard, Mem0
    (re.compile(r"\b([A-Z][a-z]+(?:[A-Z][a-z0-9]+)+)\b"), lambda m: m.group(1)),
    # URLs (full or github-relative)
    (re.compile(r"https?://[^\s)]+"), lambda m: m.group(0).rstrip(".,;:")),
]


def collect_md(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*.md"):
            rel_parts = p.relative_to(root).parts if p.is_relative_to(root) else p.parts
            if any(part in SKIP_DIRS for part in rel_parts):
                continue
            out.append(p)
    # Dedup (a symlinked path can show up twice)
    seen = set()
    unique = []
    for p in out:
        rp = p.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        unique.append(p)
    return unique


def tokenize(text: str) -> list[str]:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    return [w.lower() for w in WORD_RE.findall(text) if w.lower() not in STOP and len(w) > 2]


def extract_entities(text: str) -> set[str]:
    ents: set[str] = set()
    for pat, norm in ENTITY_PATTERNS:
        for m in pat.finditer(text):
            ents.add(norm(m))
    return ents


def build_index(paths: list[Path]) -> dict:
    docs = {}
    for p in paths:
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        tokens = tokenize(text)
        docs[p] = {
            "tokens": tokens,
            "tf": Counter(tokens),
            "length": len(tokens),
            "entities": extract_entities(text),
        }
    n_docs = len(docs)
    avg_len = sum(d["length"] for d in docs.values()) / max(n_docs, 1)
    df: Counter = Counter()
    for d in docs.values():
        for term in set(d["tokens"]):
            df[term] += 1
    return {"docs": docs, "n": n_docs, "avg_len": avg_len, "df": df}


def bm25_score(query_terms: list[str], doc: dict, idx: dict, k1: float = 1.5, b: float = 0.75) -> float:
    score = 0.0
    for q in query_terms:
        df = idx["df"].get(q, 0)
        if df == 0:
            continue
        idf = math.log((idx["n"] - df + 0.5) / (df + 0.5) + 1.0)
        tf = doc["tf"].get(q, 0)
        denom = tf + k1 * (1 - b + b * doc["length"] / max(idx["avg_len"], 1))
        score += idf * (tf * (k1 + 1)) / max(denom, 1e-9)
    return score


def search(query: str, idx: dict, entity_weight: float = 3.0) -> list[tuple[float, Path, dict]]:
    query_terms = tokenize(query)
    query_entities = extract_entities(query)
    results = []
    for path, doc in idx["docs"].items():
        kw_score = bm25_score(query_terms, doc, idx)
        ent_hits = query_entities & doc["entities"]
        ent_score = entity_weight * len(ent_hits)
        total = kw_score + ent_score
        if total <= 0:
            continue
        results.append((total, path, {"bm25": round(kw_score, 3), "entity_hits": sorted(ent_hits)}))
    results.sort(key=lambda x: x[0], reverse=True)
    return results


def default_roots() -> list[Path]:
    home = Path.home()
    roots = [
        home / "claude_code" / "agent-vault" / "agent",
        home / "claude_code" / "agent-vault" / "projects",
        home / "claude_code" / "agent-vault" / "people",
        home / "claude_code" / "agent-vault" / "sme-voices",
    ]
    projects_dir = home / ".claude" / "projects"
    if projects_dir.exists():
        for project_dir in projects_dir.iterdir():
            mem = project_dir / "memory"
            if mem.is_dir():
                roots.append(mem)
    return roots


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("query", help="Search query — natural-language phrase or specific tokens")
    ap.add_argument("--root", type=Path, action="append", help="Override default roots (repeatable)")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--entity-weight", type=float, default=3.0)
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of a text table")
    args = ap.parse_args()

    roots = args.root if args.root else default_roots()
    paths = collect_md([r.expanduser() for r in roots])
    if not paths:
        print(f"no .md files found under: {', '.join(str(r) for r in roots)}")
        return

    idx = build_index(paths)
    results = search(args.query, idx, entity_weight=args.entity_weight)[: args.top]

    if args.json:
        print(
            json.dumps(
                {
                    "query": args.query,
                    "n_files_indexed": idx["n"],
                    "results": [
                        {"path": str(p), "score": round(s, 3), **meta} for s, p, meta in results
                    ],
                },
                indent=2,
            )
        )
        return

    print(f"# indexed {idx['n']} files across {len(roots)} root(s); top {len(results)} for: {args.query!r}\n")
    if not results:
        print("(no matches — try fewer or different terms)")
        return
    for score, path, meta in results:
        ents = ", ".join(meta["entity_hits"][:5]) if meta["entity_hits"] else "—"
        print(f"  {score:6.2f}  {path}")
        print(f"          bm25={meta['bm25']}  entity_hits=[{ents}]")


if __name__ == "__main__":
    main()
