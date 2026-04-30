#!/usr/bin/env python3
"""BM25 ranker over a skill corpus.

Pure Python — no external deps. Implements Okapi BM25 (Robertson 1994) over
`name + description` text per skill. Standard parameters: k1=1.5, b=0.75.

Usage:
    bm25_rank.py --corpus skill_corpus.jsonl --query "fix auth route bug" --top 5

    # As a module:
    from bm25_rank import BM25, load_corpus
    corpus = load_corpus(Path("skill_corpus.jsonl"))
    bm25 = BM25(corpus)
    hits = bm25.search("...", top=10)  # → [(skill_dict, score), ...]
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

# Lowercase + alphanumeric tokens of length ≥ 2. Sufficient for skill text.
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9]+")

# Common stopwords. BM25 tolerates them but trimming sharpens scores on short
# descriptions where every term carries weight.
STOPWORDS = frozenset(
    "a an and are as at be by for from has have if in is it its of on or "
    "that the this to use used uses using when where which with you your".split()
)


def tokenize(text: str) -> list[str]:
    return [
        t.lower() for t in TOKEN_RE.findall(text)
        if t.lower() not in STOPWORDS
    ]


@dataclass
class BM25:
    """Okapi BM25 ranker.

    Each corpus entry must be a dict with at least a 'name' and 'description'
    field; the searchable text is the concatenation. Pass `text_fields` to
    customize.
    """
    corpus: list[dict]
    k1: float = 1.5
    b: float = 0.75
    text_fields: tuple[str, ...] = ("name", "description")

    def __post_init__(self) -> None:
        self._docs: list[list[str]] = [
            tokenize(" ".join(str(d.get(f, "")) for f in self.text_fields))
            for d in self.corpus
        ]
        self._doc_lens = [len(d) for d in self._docs]
        self._avgdl = sum(self._doc_lens) / len(self._docs) if self._docs else 0.0
        # Document frequency for each term
        df: Counter[str] = Counter()
        for doc in self._docs:
            for term in set(doc):
                df[term] += 1
        n = len(self._docs)
        # Okapi BM25 IDF (clamped at 0 so very common terms don't go negative)
        self._idf: dict[str, float] = {
            term: max(0.0, math.log((n - freq + 0.5) / (freq + 0.5) + 1.0))
            for term, freq in df.items()
        }
        # Per-document term frequencies (sparse)
        self._tf: list[Counter[str]] = [Counter(doc) for doc in self._docs]

    def score(self, query_terms: list[str], doc_idx: int) -> float:
        score = 0.0
        tf = self._tf[doc_idx]
        dl = self._doc_lens[doc_idx]
        for term in query_terms:
            if term not in tf:
                continue
            idf = self._idf.get(term, 0.0)
            f = tf[term]
            denom = f + self.k1 * (1 - self.b + self.b * dl / self._avgdl)
            score += idf * f * (self.k1 + 1) / denom
        return score

    def search(self, query: str, top: int = 10) -> list[tuple[dict, float]]:
        terms = tokenize(query)
        if not terms or not self.corpus:
            return []
        scored = [(self.corpus[i], self.score(terms, i)) for i in range(len(self.corpus))]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s in scored[:top] if s[1] > 0]


def load_corpus(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON instead of human-readable lines.")
    args = parser.parse_args(argv)

    corpus = load_corpus(args.corpus)
    bm25 = BM25(corpus)
    hits = bm25.search(args.query, top=args.top)

    if args.json:
        print(json.dumps([{"slug": h[0]["slug"], "score": round(h[1], 3)}
                          for h in hits]))
        return 0

    if not hits:
        print("(no hits)")
        return 0
    for skill, score in hits:
        desc = skill.get("description", "")
        if len(desc) > 80:
            desc = desc[:77] + "..."
        print(f"{score:6.2f}  {skill['slug']:<48} {desc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
