"""Disk-backed JSON cache for county-adapter fetches.

Layout: ``<root>/<county>/<source>.json`` with each payload wrapped as
``{"_fetched_at": <iso8601>, "data": <payload>}``.

`get_or_fetch` is the policy hub: serve fresh cache, otherwise call the
fetcher; on fetcher failure fall back to stale cache if any exists, else
re-raise. Logs a warning when serving stale.
"""

from __future__ import annotations

import json
import logging
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Cache keys must look like safe filename segments — no path separators, no
# ".." traversal, no shell metacharacters. Validated in `_path` against both
# `county` and `source`.
_SAFE_KEY_RE = re.compile(r"[A-Za-z0-9_-]+")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Cache:
    """JSON-on-disk cache, namespaced by (county, source)."""

    root: Path

    def _path(self, county: str, source: str) -> Path:
        for arg in (county, source):
            if not isinstance(arg, str) or not _SAFE_KEY_RE.fullmatch(arg):
                raise ValueError(f"invalid cache key: {arg!r}")
        return Path(self.root) / county / f"{source}.json"

    def _read_envelope(
        self, county: str, source: str
    ) -> tuple[datetime | None, Any | None]:
        """Return (fetched_at, payload). Returns (None, None) on missing/malformed."""
        path = self._path(county, source)
        if not path.exists():
            return None, None
        try:
            envelope = json.loads(path.read_text())
        except json.JSONDecodeError:
            logger.warning("cache: corrupted JSON at %s; ignoring", path)
            return None, None
        if (
            not isinstance(envelope, dict)
            or "_fetched_at" not in envelope
            or "data" not in envelope
        ):
            logger.warning("cache: malformed envelope at %s; ignoring", path)
            return None, None
        try:
            ts = datetime.fromisoformat(envelope["_fetched_at"])
        except (TypeError, ValueError):
            # Treat as infinitely old but still return the payload.
            return None, envelope["data"]
        return ts, envelope["data"]

    def read(self, county: str, source: str) -> Any | None:
        """Return the stored payload (unwrapped from the timestamp envelope) or None."""
        return self._read_envelope(county, source)[1]

    def write(self, county: str, source: str, payload: Any) -> None:
        """Store `payload` wrapped with the current UTC timestamp (atomically)."""
        path = self._path(county, source)
        path.parent.mkdir(parents=True, exist_ok=True)
        envelope = {"_fetched_at": _now_iso(), "data": payload}
        # Atomic write: write to temp file in same directory, then rename.
        fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(envelope, f)
            os.replace(tmp_name, path)
        except Exception:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
            raise

    def get_or_fetch(
        self,
        county: str,
        source: str,
        fetcher: Callable[[], Any],
        ttl_days: int,
    ) -> Any:
        """Serve fresh cache or call fetcher; fall back to stale on fetcher failure."""
        fetched_at, cached = self._read_envelope(county, source)
        if fetched_at is not None and cached is not None:
            age = datetime.now(timezone.utc) - fetched_at
            if age <= timedelta(days=ttl_days):
                return cached

        try:
            fresh = fetcher()
        except Exception as exc:
            if cached is not None:
                logger.warning(
                    "fetcher for %s/%s failed (%s); serving stale cache as fallback",
                    county,
                    source,
                    exc,
                )
                return cached
            raise

        self.write(county, source, fresh)
        return fresh
