import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import json
from datetime import datetime, timedelta, timezone

import pytest

from scripts.cache import Cache


def test_cache_round_trip(tmp_path):
    c = Cache(root=tmp_path)
    c.write("allegheny_pa", "parcels", {"rows": 5})
    assert c.read("allegheny_pa", "parcels") == {"rows": 5}


def test_cache_returns_none_when_missing(tmp_path):
    c = Cache(root=tmp_path)
    assert c.read("allegheny_pa", "parcels") is None


def test_cache_get_or_fetch_uses_fresh_cache(tmp_path):
    c = Cache(root=tmp_path)
    c.write("a", "x", {"v": 1})
    sentinel = c.get_or_fetch("a", "x", lambda: {"v": 999}, ttl_days=30)
    assert sentinel == {"v": 1}


def test_cache_get_or_fetch_calls_fetcher_when_stale(tmp_path, monkeypatch):
    c = Cache(root=tmp_path)
    # Write with a very old fetched_at
    old = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    payload = {"_fetched_at": old, "data": {"v": 1}}
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "x.json").write_text(json.dumps(payload))
    result = c.get_or_fetch("a", "x", lambda: {"v": 2}, ttl_days=30)
    assert result == {"v": 2}


def test_cache_falls_back_to_stale_when_fetcher_raises(tmp_path, caplog):
    c = Cache(root=tmp_path)
    c.write("a", "x", {"v": 1})
    # Force the cache to look stale
    path = tmp_path / "a" / "x.json"
    data = json.loads(path.read_text())
    data["_fetched_at"] = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    path.write_text(json.dumps(data))

    def boom():
        raise RuntimeError("network down")

    with caplog.at_level("WARNING"):
        result = c.get_or_fetch("a", "x", boom, ttl_days=30)
    assert result == {"v": 1}
    assert any("stale" in r.message.lower() or "fallback" in r.message.lower()
               for r in caplog.records)


def test_cache_reraises_when_no_cache_and_fetcher_raises(tmp_path):
    c = Cache(root=tmp_path)

    def boom():
        raise RuntimeError("network down")

    with pytest.raises(RuntimeError, match="network down"):
        c.get_or_fetch("a", "x", boom, ttl_days=30)
