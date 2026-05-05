#!/usr/bin/env python3
"""Dump a GitHub repo's structure + key files via `gh api`. No scraping.

Usage:
  python github_repo.py <owner/repo>           # full dump
  python github_repo.py <owner/repo> --files   # also fetch README + top-level docs
  python github_repo.py <url>                  # accepts github.com URLs too

Output JSON: {full_name, description, language, stars, default_branch,
              tree: [paths], readme?, files?: {path: content}}

Why: GitHub has a real API. Scraping the rendered HTML is wasteful when
`gh api repos/<r>` and `gh api repos/<r>/git/trees/HEAD?recursive=1` give
you everything cheaply.
"""
from __future__ import annotations
import json, re, subprocess, sys

KEY_DOC_PATTERNS = re.compile(
    r"^(README|CONTRIBUTING|CHANGELOG|ARCHITECTURE|ROADMAP|LICENSE|SKILL\.md)",
    re.IGNORECASE,
)


def gh(*args: str) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"gh failed: {r.stderr.strip()}")
    return r.stdout


def parse_repo(s: str) -> str:
    m = re.search(r"github\.com/([^/]+/[^/?#]+)", s)
    return (m.group(1) if m else s).rstrip("/").removesuffix(".git")


def main(repo: str, with_files: bool) -> None:
    repo = parse_repo(repo)
    meta = json.loads(gh("api", f"repos/{repo}"))
    out = {
        "full_name": meta["full_name"],
        "description": meta.get("description"),
        "language": meta.get("language"),
        "stars": meta.get("stargazers_count"),
        "default_branch": meta.get("default_branch"),
        "topics": meta.get("topics", []),
    }
    branch = out["default_branch"]
    tree = json.loads(gh("api", f"repos/{repo}/git/trees/{branch}?recursive=1"))
    paths = [t["path"] for t in tree.get("tree", []) if t["type"] == "blob"]
    out["tree"] = paths
    out["file_count"] = len(paths)

    if with_files:
        files = {}
        for p in paths:
            depth = p.count("/")
            if depth <= 1 and KEY_DOC_PATTERNS.match(p.split("/")[-1]):
                content = gh("api", f"repos/{repo}/contents/{p}", "--jq", ".content")
                import base64
                files[p] = base64.b64decode(content).decode("utf-8", errors="replace")
        out["files"] = files

    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], "--files" in sys.argv)
