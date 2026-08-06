"""Voice sample summarizer.

Computes deterministic stats from 1-3 writing samples to seed the LLM-side voice
profile generation. This is intentionally a thin Python-side helper — the actual
voice profile authoring is done by the orchestrating Claude session at outreach
time. We just produce inputs the LLM consumes.

NO LLM calls, NO heavy NLP — just regex sentence splitting and a small built-in
stopword list.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

# ~30 common English stopwords — kept small on purpose. Outreach drafting is the
# discriminator, not vocabulary purity.
_STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
        "for", "from", "has", "have", "he", "her", "his", "i", "in", "is",
        "it", "its", "my", "of", "on", "or", "she", "that", "the", "their",
        "them", "they", "this", "to", "was", "we", "were", "will", "with",
        "you", "your", "me", "our", "us", "do", "did", "had",
    }
)

# Sentence splitter: ., !, ? followed by whitespace or end-of-string.
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

# Word extractor: contiguous alphabetic runs (keeps "don't" as "don" + "t" —
# acceptable for the stats we surface).
_WORD_RE = re.compile(r"[A-Za-z]+")


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]


def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text)


def _first_n_words(text: str, n: int) -> str:
    tokens = text.strip().split()
    return " ".join(tokens[:n])


def _last_n_words(text: str, n: int) -> str:
    tokens = text.strip().split()
    return " ".join(tokens[-n:]) if tokens else ""


def summarize_samples(samples: list[str]) -> dict[str, Any]:
    """Compute deterministic stats from voice samples to seed the voice profile.

    Returns:
        {
            "sample_count": int,
            "total_words": int,
            "avg_sentence_length_words": float,
            "top_content_words": list[tuple[str, int]],  # (word, count), top 20
            "sample_openers": list[str],  # first 6 words of each sample
            "sample_closers": list[str],  # last 6 words of each sample
        }
    """
    if not samples:
        return {
            "sample_count": 0,
            "total_words": 0,
            "avg_sentence_length_words": 0.0,
            "top_content_words": [],
            "sample_openers": [],
            "sample_closers": [],
        }

    all_words: list[str] = []
    sentence_lengths: list[int] = []
    openers: list[str] = []
    closers: list[str] = []

    for sample in samples:
        words = _words(sample)
        all_words.extend(words)

        for sent in _split_sentences(sample):
            sent_words = _words(sent)
            if sent_words:
                sentence_lengths.append(len(sent_words))

        openers.append(_first_n_words(sample, 6))
        closers.append(_last_n_words(sample, 6))

    content_words = [w.lower() for w in all_words if w.lower() not in _STOPWORDS]
    top_content_words = Counter(content_words).most_common(20)

    avg_sentence_length = (
        sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0.0
    )

    return {
        "sample_count": len(samples),
        "total_words": len(all_words),
        "avg_sentence_length_words": avg_sentence_length,
        "top_content_words": top_content_words,
        "sample_openers": openers,
        "sample_closers": closers,
    }
