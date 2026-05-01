#!/usr/bin/env python3
"""URL → right script dispatcher. Picks article.py / github_repo.py /
webpage.py based on URL pattern, runs it, prints output to stdout.

Usage: python dispatch.py <url> [--render]

This removes a decision step: the agent runs `dispatch.py <url>` and gets
structured JSON without picking the right script first.
"""
from __future__ import annotations
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

GITHUB_RE = re.compile(r"^https?://(www\.)?github\.com/[^/]+/[^/?#]+/?(\?|#|$)")
# Article-shaped paths: blog/news/post/article/p/yyyy/mm/dd or .../<slug-with-words>
ARTICLE_HINTS = re.compile(
    r"(/blog/|/news/|/post/|/posts/|/article/|/articles/|/p/|/\d{4}/\d{2}/|substack\.com|medium\.com)",
    re.IGNORECASE,
)


def pick(url: str) -> str:
    if GITHUB_RE.match(url):
        return "github_repo.py"
    if ARTICLE_HINTS.search(url):
        return "article.py"
    return "webpage.py"


def main(url: str, extra: list[str]) -> None:
    script = pick(url)
    args = [sys.executable, os.path.join(HERE, script), url]
    if script == "github_repo.py" and "--files" not in extra:
        args.append("--files")
    args += extra
    print(f"# dispatch → {script}", file=sys.stderr)
    subprocess.run(args, check=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], [a for a in sys.argv[2:] if a not in ("--files",)])
