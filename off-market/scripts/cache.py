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
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class Cache:
    """JSON-on-disk cache, namespaced by (county, source)."""

    root: Path

    def _path(self, county: str, source: str) -> Path:
        return Path(self.root) / county / f"{source}.json"

    def read(self, county: str, source: str) -> dict | None:
        """Return the stored payload (unwrapped from the timestamp envelope) or None."""
        path = self._path(county, source)
        if not path.exists():
            return None
        envelope = json.loads(path.read_text())
        if isinstance(envelope, dict) and "data" in envelope and "_fetched_at" in envelope:
            return envelope["data"]
        # Backwards-compat / hand-written payload: return as-is.
        return envelope

    def write(self, county: str, source: str, payload: dict) -> None:
        """Store `payload` wrapped with the current UTC timestamp."""
        path = self._path(county, source)
        path.parent.mkdir(parents=True, exist_ok=True)
        envelope = {
            "_fetched_at": datetime.now(timezone.utc).isoformat(),
            "data": payload,
        }
        path.write_text(json.dumps(envelope))

    def _fetched_at(self, county: str, source: str) -> datetime | None:
        path = self._path(county, source)
        if not path.exists():
            return None
        envelope = json.loads(path.read_text())
        ts = envelope.get("_fetched_at") if isinstance(envelope, dict) else None
        if not ts:
            return None
        try:
            return datetime.fromisoformat(ts)
        except ValueError:
            return None

    def get_or_fetch(
        self,
        county: str,
        source: str,
        fetcher: Callable[[], dict],
        ttl_days: int,
    ) -> dict:
        """Serve fresh cache or call fetcher; fall back to stale on fetcher failure."""
        fetched_at = self._fetched_at(county, source)
        if fetched_at is not None:
            age = datetime.now(timezone.utc) - fetched_at
            if age <= timedelta(days=ttl_days):
                cached = self.read(county, source)
                if cached is not None:
                    return cached

        try:
            fresh = fetcher()
        except Exception as exc:
            stale = self.read(county, source)
            if stale is not None:
                logger.warning(
                    "fetcher for %s/%s failed (%s); serving stale cache as fallback",
                    county,
                    source,
                    exc,
                )
                return stale
            raise

        self.write(county, source, fresh)
        return fresh
