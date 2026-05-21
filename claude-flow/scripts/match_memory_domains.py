#!/usr/bin/env python3
"""
Mechanical file-pattern → domain → gotcha-key matching for memory-injection.

Replaces the LLM-prose Steps 3-4 in claude-flow/references/memory-injection.md
with deterministic glob matching against the domain table in the same file.

Inputs:
- A list of file paths (one per arg or via stdin)
- The memory-injection.md reference file (parsed for the domain table)
- The MEMORY.md file (parsed for one-line gotcha entries by semantic key)

Output (JSON to stdout):
{
  "matched_domains": ["models", "services"],
  "matched_keys": ["client-sync-map", "is-primary-contact", ...],
  "matched_entries": [
    {"key": "is-primary-contact", "line": "- [...](...) — ...", "topic_file": "is_primary_contact.md"},
    ...
  ],
  "skipped": []
}

The LLM caller assembles the final PROJECT_GOTCHAS block from this output.
Stdlib only.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import fnmatch
import json
import re
import sys
from pathlib import Path


def parse_domain_table(reference_file: Path) -> list[dict]:
    """Parse the markdown domain table from memory-injection.md.

    Expected table format:
        | Domain | File Patterns | Gotcha Keys |
        |--------|--------------|-------------|
        | models | `models/*`, `alembic/*` | `key1`, `key2`, `key3` |
    """
    if not reference_file.exists():
        return []
    rows = []
    in_table = False
    for raw in reference_file.read_text().splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            in_table = False
            continue
        if "Domain" in line and "File Patterns" in line and "Gotcha Keys" in line:
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if not in_table:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        domain = cells[0]
        patterns = [p.strip().strip("`") for p in cells[1].split(",") if p.strip()]
        keys = [k.strip().strip("`") for k in cells[2].split(",") if k.strip()]
        rows.append({"domain": domain, "patterns": patterns, "keys": keys})
    return rows


def match_files_to_domains(file_paths: list[str], domain_table: list[dict]) -> tuple[list[str], list[str]]:
    matched_domains: set[str] = set()
    matched_keys: set[str] = set()
    for fp in file_paths:
        for row in domain_table:
            for pat in row["patterns"]:
                # Convert simple glob (`models/*`) to fnmatch (`*models/*`) so it
                # matches any prefix on the path
                if fnmatch.fnmatch(fp, pat) or fnmatch.fnmatch(fp, f"*/{pat}"):
                    matched_domains.add(row["domain"])
                    matched_keys.update(row["keys"])
                    break
    return sorted(matched_domains), sorted(matched_keys)


def parse_memory_index(memory_md: Path) -> dict[str, dict]:
    """Return {semantic_key: {"line": ..., "topic_file": slug}} where semantic
    key is derived from the topic-file slug (filename stem with underscores
    converted to hyphens, lowercase). This matches the convention in the
    memory-injection.md domain table."""
    if not memory_md.exists():
        return {}
    entries = {}
    link_re = re.compile(r"\[([^\]]+)\]\(([a-z][a-z0-9_-]+)\.md\)")
    for raw in memory_md.read_text().splitlines():
        if not raw.startswith("- "):
            continue
        m = link_re.search(raw)
        if not m:
            continue
        slug = m.group(2)
        key = slug.replace("_", "-")
        entries[key] = {"line": raw.rstrip(), "topic_file": f"{slug}.md"}
    return entries


def _slug_to_key(slug: str) -> str:
    return slug.replace("_", "-").lower()


def _entry_for_slug(memory_index: dict[str, dict], slug: str) -> dict | None:
    key = _slug_to_key(slug)
    if key not in memory_index:
        return None
    return {"key": key, **memory_index[key]}


def _related_slugs(memory_file: Path) -> list[str]:
    if not memory_file.exists():
        return []

    slugs = []
    in_related = False
    link_re = re.compile(r"^-\s*\[([A-Za-z0-9_-]+)\]")
    for raw in memory_file.read_text().splitlines():
        line = raw.strip()
        if line.lower() == "## related":
            in_related = True
            continue
        if in_related and line.startswith("## "):
            break
        if not in_related:
            continue
        match = link_re.match(line)
        if match:
            slugs.append(match.group(1))
    return slugs


def expand_related(
    memory_dir: Path,
    matched_entries: list[dict],
    limit: int = 3,
) -> list[dict]:
    """Return deterministic one-hop related MEMORY.md entries."""
    memory_index = parse_memory_index(memory_dir / "MEMORY.md")
    matched_files = {entry["topic_file"] for entry in matched_entries}
    matched_keys = {entry["key"] for entry in matched_entries}
    citation_counts: dict[str, int] = {}

    for entry in matched_entries:
        topic_file = memory_dir / entry["topic_file"]
        for slug in _related_slugs(topic_file):
            key = _slug_to_key(slug)
            topic = f"{slug}.md"
            if key in matched_keys or topic in matched_files:
                continue
            if key not in memory_index:
                continue
            citation_counts[key] = citation_counts.get(key, 0) + 1

    ranked = sorted(citation_counts, key=lambda k: (-citation_counts[k], k))
    entries = []
    for key in ranked[:limit]:
        topic_slug = memory_index[key]["topic_file"].removesuffix(".md")
        entry = _entry_for_slug(memory_index, topic_slug)
        if entry is not None:
            entry["source"] = "related"
            entry["citation_count"] = citation_counts[key]
            entries.append(entry)
    return entries


def _parse_frontmatter(path: Path) -> dict:
    text = path.read_text()
    if not text.startswith("---\n"):
        return {}
    try:
        _, raw, _ = text.split("---", 2)
    except ValueError:
        return {}

    data: dict[str, str | list[str]] = {}
    current_list: str | None = None
    for raw_line in raw.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") and current_list:
            value = line[4:].strip().strip('"').strip("'")
            cast_list = data.setdefault(current_list, [])
            if isinstance(cast_list, list):
                cast_list.append(value)
            continue
        current_list = None
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if value:
            data[key] = value
        else:
            data[key] = []
            current_list = key
    return data


def select_compiled_articles(
    memory_dir: Path,
    matched_domains: list[str],
    domain_table: list[dict],
    limit: int = 3,
) -> list[dict]:
    """Select compiled concept articles whose sources overlap task domains."""
    concepts_dir = memory_dir / "knowledge" / "concepts"
    if not concepts_dir.exists():
        return []

    matched_domain_set = set(matched_domains)
    articles = []
    for path in sorted(concepts_dir.glob("*.md")):
        frontmatter = _parse_frontmatter(path)
        sources = frontmatter.get("sources", [])
        if isinstance(sources, str):
            sources = [sources]
        source_domains, _ = match_files_to_domains(list(sources), domain_table)
        overlap = matched_domain_set.intersection(source_domains)
        if not overlap:
            continue
        articles.append({
            "key": path.stem.replace("_", "-"),
            "topic_file": str(path.relative_to(memory_dir)),
            "title": frontmatter.get("title", path.stem.replace("_", " ")),
            "updated": frontmatter.get("updated", ""),
            "matching_source_count": len(overlap),
        })

    return sorted(
        articles,
        key=lambda item: (
            -int(item["matching_source_count"]),
            str(item["updated"]),
            str(item["key"]),
        ),
        reverse=False,
    )[:limit]


def _default_project_root(memory_dir: Path) -> Path:
    if memory_dir.name == "memory" and memory_dir.parent.name == ".claude":
        return memory_dir.parent.parent
    return memory_dir.parent


def _parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _date_from_abandoned_name(path: Path) -> datetime | None:
    match = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
    if not match:
        return None
    parsed = datetime.fromisoformat(match.group(1))
    return parsed.replace(tzinfo=timezone.utc)


def _section_text(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return ""
    lines = [line.strip() for line in match.group(1).splitlines()]
    return " ".join(line for line in lines if line)


def select_abandoned(
    project_root_or_memory_dir: Path,
    now: datetime | None = None,
    limit: int = 3,
) -> list[dict]:
    """Select fresh abandoned approach notes, capped by newest first."""
    root = project_root_or_memory_dir
    abandoned_dir = root / ".claude" / "abandoned"
    if not abandoned_dir.exists():
        root = _default_project_root(project_root_or_memory_dir)
        abandoned_dir = root / ".claude" / "abandoned"
    if not abandoned_dir.exists():
        return []

    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=30)
    entries = []
    for path in sorted(abandoned_dir.glob("*.md")):
        entry_date = _date_from_abandoned_name(path)
        if entry_date is None or entry_date < cutoff:
            continue
        text = path.read_text()
        entries.append({
            "key": path.stem,
            "topic_file": str(path.relative_to(root)),
            "date": entry_date.date().isoformat(),
            "attempted": _section_text(text, "What was attempted"),
            "why_abandoned": _section_text(text, "Why abandoned"),
        })

    return sorted(entries, key=lambda item: item["date"], reverse=True)[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("memory_dir", type=Path, help="Directory containing MEMORY.md")
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path(__file__).parent.parent / "references" / "memory-injection.md",
        help="memory-injection.md reference file (defaults to claude-flow's copy)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root containing .claude/abandoned (optional).",
    )
    parser.add_argument(
        "--now",
        default=None,
        help="Current timestamp for abandoned-entry freshness checks.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="File paths to match (touched files in current task). If empty, read one path per line from stdin.",
    )
    if hasattr(parser, "parse_intermixed_args"):
        args = parser.parse_intermixed_args()
    else:
        args = parser.parse_args()

    file_paths = args.files
    if not file_paths and not sys.stdin.isatty():
        file_paths = [line.strip() for line in sys.stdin if line.strip()]

    domain_table = parse_domain_table(args.reference)
    matched_domains, matched_keys = match_files_to_domains(file_paths, domain_table)

    memory_index = parse_memory_index(args.memory_dir / "MEMORY.md")
    matched_entries = []
    skipped = []
    for key in matched_keys:
        if key in memory_index:
            matched_entries.append({"key": key, **memory_index[key]})
        else:
            skipped.append(key)

    related_entries = expand_related(args.memory_dir, matched_entries)
    compiled_articles = select_compiled_articles(
        args.memory_dir,
        matched_domains,
        domain_table,
    )
    abandoned_root = args.project_root or args.memory_dir
    abandoned_entries = select_abandoned(abandoned_root, _parse_now(args.now))

    output = {
        "matched_domains": matched_domains,
        "matched_keys": matched_keys,
        "matched_entries": matched_entries,
        "related_entries": related_entries,
        "compiled_articles": compiled_articles,
        "abandoned_entries": abandoned_entries,
        "skipped": skipped,
        "input_file_count": len(file_paths),
    }
    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
