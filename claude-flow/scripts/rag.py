"""rag.py — RAG 2.0 experience retrieval pipeline for claude-flow.

Dependencies: openai (embedding API), numpy (vector math).
VectorStore: index.json (chunk metadata) + embeddings.npy (float32 array).
"""

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import openai


# ---------------------------------------------------------------------------
# Chunk dataclass
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    text: str
    source_phase: str
    source_type: str
    timestamp: str
    project_fingerprint: dict
    outcome_quality: float


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

# Map exploration-log field name → source_type label
_PHASE_FIELDS: list[tuple[str, str]] = [
    ("patterns_found",     "patterns_found"),
    ("gaps",               "gaps"),
    ("failed_approaches",  "failed_approaches"),
    ("discoveries",        "discoveries"),
    ("decisions_made",     "decisions_made"),
    ("patterns_escalated", "patterns_escalated"),
    ("feedback",           "feedback"),
]


def extract_chunks(exploration_log: dict) -> list[Chunk]:
    """Extract embeddable text chunks from an exploration-log JSON dict."""
    phases: dict = exploration_log.get("phases", {})
    if not phases:
        return []

    fingerprint = exploration_log.get("project_fingerprint", {})
    chunks: list[Chunk] = []

    for phase_name, phase_data in phases.items():
        if not isinstance(phase_data, dict):
            continue
        ts = phase_data.get("timestamp", "")
        quality = phase_data.get("outcome_quality", 0.0)

        for field, source_type in _PHASE_FIELDS:
            entries = phase_data.get(field, [])
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if isinstance(entry, str) and entry.strip():
                    chunks.append(Chunk(
                        text=entry,
                        source_phase=phase_name,
                        source_type=source_type,
                        timestamp=ts,
                        project_fingerprint=fingerprint,
                        outcome_quality=quality,
                    ))

    return chunks


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def embed_chunks(chunks: list[Chunk], api_key: str) -> list[list[float]]:
    """Batch-embed chunks via OpenAI text-embedding-3-small (1536-dim)."""
    client = openai.OpenAI(api_key=api_key)
    texts = [c.text for c in chunks]
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]


# ---------------------------------------------------------------------------
# VectorStore
# ---------------------------------------------------------------------------

class VectorStore:
    """Local file-based vector store: index.json (metadata) + embeddings.npy."""

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.mkdir(parents=True, exist_ok=True)
        self._index_file = self._path / "index.json"
        self._embed_file = self._path / "embeddings.npy"
        self._index: list[dict] = []
        self._embeddings: np.ndarray | None = None
        self._load()

    def _load(self) -> None:
        if self._index_file.exists():
            self._index = json.loads(self._index_file.read_text())
        if self._embed_file.exists():
            self._embeddings = np.load(self._embed_file).astype(np.float32)

    def _save(self) -> None:
        self._index_file.write_text(json.dumps(self._index, indent=2))
        if self._embeddings is not None:
            np.save(self._embed_file, self._embeddings.astype(np.float32))

    @property
    def size(self) -> int:
        return len(self._index)

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Append chunks + vectors, save to disk."""
        for c in chunks:
            self._index.append(asdict(c))

        new_arr = np.array(vectors, dtype=np.float32)
        if self._embeddings is None:
            self._embeddings = new_arr
        else:
            self._embeddings = np.vstack([self._embeddings, new_arr])

        self._save()

    def query(self, query_vector: list[float], top_k: int = 20) -> list[tuple[Chunk, float]]:
        """Return top-K (Chunk, cosine_score) pairs ordered by descending score."""
        if self._embeddings is None or len(self._index) == 0:
            return []

        q = np.array(query_vector, dtype=np.float32)
        q_norm = q / (np.linalg.norm(q) + 1e-9)

        norms = np.linalg.norm(self._embeddings, axis=1, keepdims=True) + 1e-9
        normed = self._embeddings / norms
        scores = normed @ q_norm  # shape: (N,)

        k = min(top_k, len(self._index))
        top_indices = np.argpartition(scores, -k)[-k:]
        top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

        results = []
        for idx in top_indices:
            meta = self._index[idx]
            chunk = Chunk(
                text=meta["text"],
                source_phase=meta["source_phase"],
                source_type=meta["source_type"],
                timestamp=meta["timestamp"],
                project_fingerprint=meta["project_fingerprint"],
                outcome_quality=meta["outcome_quality"],
            )
            results.append((chunk, float(scores[idx])))
        return results


# ---------------------------------------------------------------------------
# Re-ranking
# ---------------------------------------------------------------------------

def _jaccard(a: dict, b: dict) -> float:
    """Jaccard similarity between two fingerprint dicts (flattened to tag sets)."""
    def flatten(fp: dict) -> set:
        tags: set[str] = set()
        for k, v in fp.items():
            if isinstance(v, list):
                tags.update(str(x) for x in v)
            elif isinstance(v, bool):
                tags.add(f"{k}={'true' if v else 'false'}")
            else:
                tags.add(f"{k}={v}")
        return tags
    ta, tb = flatten(a), flatten(b)
    union = ta | tb
    return len(ta & tb) / len(union) if union else 0.0


def _recency_score(timestamp: str, current_time: datetime) -> float:
    """Exponential decay: week=1.0, month≈0.5, older→0.2 floor."""
    try:
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        days = (current_time - ts).total_seconds() / 86400
    except Exception:
        return 0.2
    if days <= 7:
        return 1.0
    if days <= 30:
        # linear interpolation from 1.0 → 0.5 over days 7–30
        return 1.0 - 0.5 * (days - 7) / 23
    # exponential decay below 0.5, floored at 0.2
    return max(0.2, 0.5 * math.exp(-0.02 * (days - 30)))


def rerank(
    candidates: list[tuple[Chunk, float]],
    query_fingerprint: dict,
    query_phase: str,
    current_time: datetime,
) -> list[Chunk]:
    """5-signal weighted re-ranking; returns top-5 Chunk objects."""
    if not candidates:
        return []

    # Weights from design doc
    W_SIM, W_FP, W_REC, W_QUAL, W_PHASE = 0.3, 0.25, 0.2, 0.15, 0.1

    scored: list[tuple[float, Chunk]] = []
    for chunk, sim_score in candidates:
        fp_score = _jaccard(chunk.project_fingerprint, query_fingerprint)
        rec_score = _recency_score(chunk.timestamp, current_time)
        qual_score = float(chunk.outcome_quality)
        phase_score = 1.0 if chunk.source_phase == query_phase else 0.0

        combined = (
            W_SIM   * sim_score
            + W_FP  * fp_score
            + W_REC * rec_score
            + W_QUAL * qual_score
            + W_PHASE * phase_score
        )
        scored.append((combined, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:5]]


# ---------------------------------------------------------------------------
# Prompt injection
# ---------------------------------------------------------------------------

def format_for_injection(chunks: list[Chunk]) -> str:
    """Format top chunks as a PRIOR EXPERIENCE prompt block."""
    if not chunks:
        return ""

    lines = ["## PRIOR EXPERIENCE\n"]
    for i, c in enumerate(chunks, 1):
        lines.append(
            f"{i}. [{c.source_phase} / {c.source_type}] {c.text}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _chunk_from_dict(data: dict[str, Any]) -> Chunk:
    """Build a Chunk from JSON-decoded metadata."""
    return Chunk(
        text=data["text"],
        source_phase=data["source_phase"],
        source_type=data["source_type"],
        timestamp=data["timestamp"],
        project_fingerprint=data["project_fingerprint"],
        outcome_quality=data["outcome_quality"],
    )


def _read_chunks_jsonl(path: Path) -> list[Chunk]:
    """Read Chunk records from a JSONL file."""
    if not path.exists():
        return []
    chunks = []
    for line in path.read_text().splitlines():
        if line.strip():
            chunks.append(_chunk_from_dict(json.loads(line)))
    return chunks


def _write_chunks_jsonl(path: Path, chunks: list[Chunk]) -> None:
    """Write Chunk records to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(asdict(chunk), sort_keys=True) for chunk in chunks]
    path.write_text("\n".join(lines) + ("\n" if lines else ""))


def _store_available(path: Path) -> bool:
    """Return true when a vector store has both metadata and embeddings."""
    return (
        path.exists()
        and (path / "index.json").exists()
        and (path / "embeddings.npy").exists()
    )


def _cmd_extract(args: argparse.Namespace) -> int:
    log = json.loads(args.log.read_text())
    _write_chunks_jsonl(args.out, extract_chunks(log))
    return 0


def _cmd_format(args: argparse.Namespace) -> int:
    chunks = _read_chunks_jsonl(args.chunks)[:args.limit]
    block = format_for_injection(chunks)
    if block:
        print(block)
    return 0


def _cmd_query(args: argparse.Namespace) -> int:
    store_path = args.store
    if not _store_available(store_path):
        return 0

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            "RAG query skipped: OPENAI_API_KEY is not set",
            file=sys.stderr,
        )
        return 0

    fingerprint = json.loads(args.fingerprint)
    query_chunk = Chunk(
        text=args.text,
        source_phase=args.phase,
        source_type="query",
        timestamp=datetime.now(timezone.utc).isoformat(),
        project_fingerprint=fingerprint,
        outcome_quality=0.0,
    )
    query_vector = embed_chunks([query_chunk], api_key=api_key)[0]
    store = VectorStore(store_path)
    candidates = store.query(query_vector, top_k=max(args.limit, 20))
    chunks = rerank(candidates, fingerprint, args.phase, datetime.now(timezone.utc))
    block = format_for_injection(chunks[:args.limit])
    if block:
        print(block)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the RAG CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract = subparsers.add_parser("extract")
    extract.add_argument("--log", required=True, type=Path)
    extract.add_argument("--out", required=True, type=Path)
    extract.set_defaults(func=_cmd_extract)

    format_cmd = subparsers.add_parser("format")
    format_cmd.add_argument("--chunks", required=True, type=Path)
    format_cmd.add_argument("--limit", default=5, type=int)
    format_cmd.set_defaults(func=_cmd_format)

    query = subparsers.add_parser("query")
    query.add_argument("--store", required=True, type=Path)
    query.add_argument("--text", required=True)
    query.add_argument("--phase", required=True)
    query.add_argument("--fingerprint", required=True)
    query.add_argument("--limit", default=5, type=int)
    query.set_defaults(func=_cmd_query)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the RAG CLI."""
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
