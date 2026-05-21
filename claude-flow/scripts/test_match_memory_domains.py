"""Tests for deterministic memory-domain matching and expansion."""

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_match(memory_dir: Path, files: list[str], *extra: str) -> dict:
    """Run match_memory_domains.py and return decoded JSON output."""
    result = subprocess.run(
        [
            sys.executable,
            "scripts/match_memory_domains.py",
            str(memory_dir),
            *extra,
            *files,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def write_memory_index(memory_dir: Path) -> None:
    """Write a compact MEMORY.md fixture with service-domain entries."""
    memory_dir.mkdir(parents=True, exist_ok=True)
    (memory_dir / "MEMORY.md").write_text(
        "- [Client sync map](client_sync_map.md) - Keep maps centralized.\n"
        "- [Counts endpoint](counts_endpoint.md) - Use shared counts API.\n"
        "- [No aliases](no_aliases.md) - Use canonical names only.\n"
        "- [Phone dedup](phone_dedup.md) - Normalize phone data.\n"
        "- [Total vs active](total_vs_active.md) - Keep count semantics clear.\n"
    )


def test_direct_domain_matches_still_work(tmp_path):
    """A services path returns its configured direct MEMORY.md entries."""
    memory = tmp_path / "memory"
    write_memory_index(memory)

    result = run_match(memory, ["app/services/client_service.py"])

    keys = {entry["key"] for entry in result["matched_entries"]}
    assert "client-sync-map" in keys
    assert "counts-endpoint" in keys
    assert result["related_entries"] == []
    assert result["compiled_articles"] == []
    assert result["abandoned_entries"] == []


def test_related_entries_are_returned_with_direct_matches(tmp_path):
    """Related memory entries are added as deterministic one-hop expansion."""
    memory = tmp_path / "memory"
    reference = tmp_path / "memory-injection.md"
    memory.mkdir()
    reference.write_text(
        "| Domain | File Patterns | Gotcha Keys |\n"
        "|--------|---------------|-------------|\n"
        "| services | `services/*` | `client-sync-map` |\n"
    )
    (memory / "MEMORY.md").write_text(
        "- [Client sync map](client_sync_map.md) - Keep maps centralized.\n"
        "- [Counts endpoint](counts_endpoint.md) - Use shared counts API.\n"
    )
    (memory / "client_sync_map.md").write_text(
        "# Client sync map\n\n## Related\n"
        "- [counts_endpoint] - shared UI/API boundary\n"
    )

    result = run_match(
        memory,
        ["app/services/client_service.py"],
        "--reference",
        str(reference),
    )

    assert any(e["key"] == "client-sync-map" for e in result["matched_entries"])
    assert any(e["key"] == "counts-endpoint" for e in result["related_entries"])


def test_related_entries_are_capped_and_ranked_by_cocitation(tmp_path):
    """Related expansion is capped at 3 by co-citation count then slug."""
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "MEMORY.md").write_text(
        "- [Client sync map](client_sync_map.md) - Keep maps centralized.\n"
        "- [No aliases](no_aliases.md) - Use canonical names only.\n"
        "- [Alpha](alpha.md) - Alpha note.\n"
        "- [Beta](beta.md) - Beta note.\n"
        "- [Gamma](gamma.md) - Gamma note.\n"
        "- [Zeta](zeta.md) - Zeta note.\n"
    )
    (memory / "client_sync_map.md").write_text(
        "# Client sync map\n\n## Related\n"
        "- [zeta] - singly cited\n"
        "- [alpha] - co-cited\n"
        "- [beta] - co-cited\n"
    )
    (memory / "no_aliases.md").write_text(
        "# No aliases\n\n## Related\n"
        "- [alpha] - co-cited\n"
        "- [beta] - co-cited\n"
        "- [gamma] - singly cited\n"
    )

    result = run_match(memory, ["app/services/client_service.py"])

    assert [e["key"] for e in result["related_entries"]] == [
        "alpha",
        "beta",
        "gamma",
    ]


def test_compiled_articles_selected_by_source_domain_overlap(tmp_path):
    """Concept articles are selected when frontmatter sources match domains."""
    memory = tmp_path / "memory"
    write_memory_index(memory)
    concepts = memory / "knowledge" / "concepts"
    concepts.mkdir(parents=True)
    for idx in range(4):
        (concepts / f"service_pattern_{idx}.md").write_text(
            "---\n"
            f"title: Service pattern {idx}\n"
            f"updated: 2026-04-2{idx}\n"
            "sources:\n"
            "  - app/services/client_service.py\n"
            "---\n"
            "\n# Body\n"
        )
    (concepts / "ui_pattern.md").write_text(
        "---\n"
        "title: UI pattern\n"
        "updated: 2026-04-30\n"
        "sources:\n"
        "  - app/templates/client.html\n"
        "---\n"
    )

    result = run_match(memory, ["app/services/client_service.py"])

    articles = result["compiled_articles"]
    assert len(articles) == 3
    assert all(article["key"].startswith("service-pattern") for article in articles)


def test_abandoned_entries_are_recent_when_now_is_supplied(tmp_path):
    """Only abandoned approaches younger than 30 days are returned."""
    memory = tmp_path / "memory"
    write_memory_index(memory)
    abandoned = tmp_path / ".claude" / "abandoned"
    abandoned.mkdir(parents=True)
    (abandoned / "2026-04-20-fresh.md").write_text(
        "# Fresh\n\n## What was attempted\nTried fresh path.\n\n"
        "## Why abandoned\nIt broke the workflow.\n"
    )
    (abandoned / "2026-03-01-stale.md").write_text(
        "# Stale\n\n## What was attempted\nTried stale path.\n\n"
        "## Why abandoned\nIt was too old to trust.\n"
    )

    result = run_match(
        memory,
        ["app/services/client_service.py"],
        "--project-root",
        str(tmp_path),
        "--now",
        "2026-05-01T00:00:00+00:00",
    )

    assert [entry["key"] for entry in result["abandoned_entries"]] == [
        "2026-04-20-fresh"
    ]
