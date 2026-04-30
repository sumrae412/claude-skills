#!/usr/bin/env python3
"""Evaluate BM25 retrieval against the 12 gold-labeled dispatches.

For each row in 2026-04-29-gold-labels.md, build a query from the PR title +
file paths, run BM25 over the 205-skill corpus, and check whether the gold
skill appears in top-1, top-5, top-10. Reports recall@K — the upper bound on
what variants C1/C2/C3 can possibly achieve before the model is even called.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))

from bm25_rank import BM25, load_corpus  # noqa: E402
from replay_skill_selection import parse_gold_labels, fetch_pr_files  # noqa: E402

GOLD_LABELS = REPO_ROOT / "docs" / "experiments" / "2026-04-29-gold-labels.md"
CORPUS = REPO_ROOT / ".claude" / "experiments" / "skill_corpus.jsonl"
COURIERFLOW_REPO = Path.home() / "claude_code" / "courierflow"


def main() -> int:
    rows = parse_gold_labels(GOLD_LABELS)
    corpus = load_corpus(CORPUS)
    bm25 = BM25(corpus)

    print(f"corpus size: {len(corpus)} skills | dispatches: {len(rows)}\n")
    print(f"{'row':<4} {'pr':<6} {'gold':<28} {'rank':<6} {'top-5 hits':<60}")
    print("-" * 110)

    hits_at_1 = hits_at_5 = hits_at_10 = 0
    hits_at_5_courierflow_only = 0
    for r in rows:
        files = fetch_pr_files(COURIERFLOW_REPO, r.pr) if not r.files else r.files
        query = r.title + " " + " ".join(files)
        # Strip generic words that pollute the query
        query = re.sub(r"\b(feat|fix|chore|docs|test|tests)\b", "", query)

        results = bm25.search(query, top=20)
        ranked_slugs = [s["slug"] for s, _ in results]

        if r.gold_skill == "none":
            # Recall@K is 1 trivially when gold is none — the agent should
            # decline regardless of what BM25 surfaces. Mark as N/A.
            print(f"{r.idx:<4} {r.pr:<6} {'(none — N/A)':<28} {'—':<6} "
                  f"{', '.join(ranked_slugs[:5])[:60]}")
            continue

        try:
            rank = ranked_slugs.index(r.gold_skill) + 1
        except ValueError:
            rank = 999

        top5 = ", ".join(ranked_slugs[:5])
        print(f"{r.idx:<4} {r.pr:<6} {r.gold_skill:<28} {rank:<6} {top5[:60]}")

        if rank <= 1:
            hits_at_1 += 1
        if rank <= 5:
            hits_at_5 += 1
            # Tighter: gold appears AND only courierflow-* skills appear ahead
            ahead = ranked_slugs[:rank - 1]
            if all(s.startswith("courierflow-") for s in ahead):
                hits_at_5_courierflow_only += 1
        if rank <= 10:
            hits_at_10 += 1

    n_with_gold = sum(1 for r in rows if r.gold_skill != "none")
    print(f"\nrecall@1  = {hits_at_1}/{n_with_gold} = {hits_at_1/n_with_gold*100:.1f}%")
    print(f"recall@5  = {hits_at_5}/{n_with_gold} = {hits_at_5/n_with_gold*100:.1f}%")
    print(f"recall@10 = {hits_at_10}/{n_with_gold} = {hits_at_10/n_with_gold*100:.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
