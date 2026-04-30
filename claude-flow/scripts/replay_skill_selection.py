#!/usr/bin/env python3
"""Replay harness for the skill-selection A/B experiment.

For each row in docs/experiments/2026-04-29-gold-labels.md, build a Phase-5
subagent prompt under variant A (control: progressive disclosure) and variant
B (forced selection), invoke `claude -p` to get the model's response, parse
the loaded skill, and append a row to the JSONL log via log_skill_selection.

Usage:
    replay_skill_selection.py --courierflow-repo ~/claude_code/courierflow
    replay_skill_selection.py --rows 1,4,12     # subset for smoke testing
    replay_skill_selection.py --variant b       # one variant only
    replay_skill_selection.py --dry-run         # build prompts, skip model

Plan: docs/plans/2026-04-29-skill-selection-vs-progressive-disclosure.md
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLD_LABELS = REPO_ROOT / "docs" / "experiments" / "2026-04-29-gold-labels.md"
LOGGER = Path(__file__).parent / "log_skill_selection.py"
SKILL_CORPUS = REPO_ROOT / ".claude" / "experiments" / "skill_corpus.jsonl"

SKILLS = [
    ("courierflow-ui", "Templates, CSS, Jinja, Alpine.js"),
    ("courierflow-api", "Routes, services, FastAPI"),
    ("courierflow-data", "Models, migrations, SQLAlchemy"),
    ("courierflow-integrations", "Calendar, Twilio, AI, DocuSeal"),
    ("courierflow-security", "Auth, permissions, secrets"),
]

VARIANT_A_HEADER = """\
You are a Phase 5 subagent implementing the change described below. The following
courierflow-* skills are available — you may invoke any if you find it useful,
but you are not required to load any. Proceed with implementation.

Available skills (load on demand):
"""

VARIANT_B_HEADER = """\
You are a Phase 5 subagent implementing the change described below. Before any
tool calls, output exactly one line of the form:

    SELECTED_SKILL: <name|none>

where <name> is one of the listed skills below, or "none" if the task is fully
solvable without loading any skill content. After your SELECTED_SKILL line,
the orchestrator will inject that skill's full content (or none). You commit
once — no mid-task switching.

Available skills (pick one):
"""

TASK_BODY = """\

---
Task:
The following pull request landed in courierflow. You are being asked to
implement the SAME change from scratch (you do not see the merged diff).
Below is the PR title and the file paths it touched. Use this to plan your
implementation approach.

PR title: {title}
Files touched:
{files}
"""

VARIANT_A_TAIL = """
Do NOT write code. Instead, in one or two sentences, state which courierflow-*
skill (if any) you would load before starting, and why. If you would not load
any skill, say so explicitly.
"""

VARIANT_B_TAIL = """
Do NOT write code. First emit your `SELECTED_SKILL:` line as instructed above,
then in one sentence explain why.
"""


@dataclass
class Row:
    idx: int
    pr: str
    title: str
    gold_skill: str
    baseline_pass: bool
    files: list[str] = field(default_factory=list)


def parse_gold_labels(path: Path) -> list[Row]:
    """Parse the markdown table from the worksheet."""
    text = path.read_text()
    rows: list[Row] = []
    for line in text.splitlines():
        m = re.match(
            r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*`?([\w-]+)`?\s*\|\s*(true|false)\s*\|",
            line,
        )
        if m:
            rows.append(
                Row(
                    idx=int(m.group(1)),
                    pr=m.group(2),
                    title=m.group(3),
                    gold_skill=m.group(4),
                    baseline_pass=m.group(5) == "true",
                )
            )
    if not rows:
        raise SystemExit(f"no rows parsed from {path}")
    return rows


def fetch_pr_files(repo: Path, pr_number: str) -> list[str]:
    """Fetch the file paths a PR touched via `gh pr view`."""
    result = subprocess.run(
        ["gh", "pr", "view", pr_number, "--json", "files",
         "--jq", ".files | map(.path) | .[]"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"warning: gh pr view {pr_number} failed: {result.stderr}", file=sys.stderr)
        return []
    return [p for p in result.stdout.splitlines() if p.strip()]


def candidates_for_variant(variant: str, row: Row) -> list[tuple[str, str]]:
    """Return the (name, description) tuples to expose for this variant."""
    if variant in ("a", "b"):
        return SKILLS

    # Variants that need the full corpus
    from bm25_rank import BM25, load_corpus
    corpus = load_corpus(SKILL_CORPUS)

    if variant == "b150":
        return [(s["slug"], s["description"]) for s in corpus]

    if variant in ("c1", "c3"):
        bm25 = BM25(corpus)
        query = (row.title + " " + " ".join(row.files)).strip()
        query = re.sub(r"\b(feat|fix|chore|docs|test|tests)\b", "", query)
        if variant == "c1":
            hits = bm25.search(query, top=5)
            return [(s["slug"], s["description"]) for s, _ in hits]
        # C3: BM25 → top-50 → haiku rerank → top-5
        top50 = bm25.search(query, top=50)
        return rerank_with_haiku(query, [s for s, _ in top50])[:5]

    raise ValueError(f"unknown variant: {variant}")


def rerank_with_haiku(query: str, candidates: list[dict]) -> list[tuple[str, str]]:
    """Cheap LLM rerank of BM25 top-50 candidates. Returns (slug, desc) list."""
    listing = "\n".join(
        f"{i}. {s['slug']} — {s['description']}" for i, s in enumerate(candidates)
    )
    prompt = (
        "You are a skill-selection ranker. The task below names a coding change "
        "to implement. Rank the candidate skills from most to least useful for "
        "this specific task. Output a single line: a comma-separated list of "
        "the top 5 candidate numbers, in order, like:\n\n"
        "RANKED: 7, 3, 12, 1, 24\n\n"
        f"Task: {query}\n\nCandidates:\n{listing}\n"
    )
    result = subprocess.run(
        ["claude", "-p", "--model", "haiku", prompt],
        capture_output=True, text=True, check=False, timeout=120,
    )
    m = re.search(r"RANKED:\s*([\d,\s]+)", result.stdout)
    if not m:
        # rerank failed — fall back to BM25 order
        return [(s["slug"], s["description"]) for s in candidates[:5]]
    indices = [int(x.strip()) for x in m.group(1).split(",") if x.strip().isdigit()]
    seen: set[int] = set()
    ranked: list[dict] = []
    for i in indices:
        if 0 <= i < len(candidates) and i not in seen:
            seen.add(i)
            ranked.append(candidates[i])
        if len(ranked) >= 5:
            break
    # Pad with leftover BM25 order if rerank gave fewer than 5
    for s in candidates:
        if len(ranked) >= 5:
            break
        if candidates.index(s) not in seen:
            ranked.append(s)
    return [(s["slug"], s["description"]) for s in ranked]


def build_prompt(variant: str, row: Row) -> str:
    """Compose the per-variant subagent prompt."""
    candidates = candidates_for_variant(variant, row)
    skills_block = "\n".join(f"- {n} — {d}" for n, d in candidates)
    # All forced-selection variants (b, b150, c1, c3) use the variant-B header.
    # Only variant a uses the loose "load on demand" header.
    if variant == "a":
        header, tail = VARIANT_A_HEADER, VARIANT_A_TAIL
    else:
        header, tail = VARIANT_B_HEADER, VARIANT_B_TAIL
    files_block = "\n".join(f"  {p}" for p in row.files) or "  (no file list available)"
    return header + skills_block + TASK_BODY.format(
        title=row.title,
        files=files_block,
    ) + tail


def parse_loaded_skill(variant: str, response: str) -> str:
    """Extract the loaded skill from the model response.

    Variant B: look for the explicit SELECTED_SKILL: <name|none> line.
    Variant A: prefer SELECTED_SKILL line if model emitted one (defensive —
      should not happen with the split prompts but catches leakage); otherwise
      look for an explicit "would not load" / "no skill" disclaimer, else
      take the first mentioned courierflow-* skill name as the load.
    """
    selected = re.search(r"SELECTED_SKILL:\s*([\w-]+|none)", response)
    if variant == "b":
        return selected.group(1).lower().strip() if selected else "none"

    # Variant A
    if selected:
        return selected.group(1).lower().strip()

    # Disclaimers that indicate "no load" should win over an incidental skill mention.
    no_load_patterns = [
        r"\bwould not load\b",
        r"\bno skill\b",
        r"\bnone of the\b",
        r"\bdo not need\b",
        r"\bdon[' ]t need\b",
        r"\bbuilt-in tools? (?:are|is) sufficient\b",
        r"\bno courierflow-\* skill\b",
    ]
    for pat in no_load_patterns:
        if re.search(pat, response, re.IGNORECASE):
            return "none"

    skill_names = [n for n, _ in SKILLS]
    m = re.search(
        r"\b(" + "|".join(re.escape(n) for n in skill_names) + r")\b",
        response,
        re.IGNORECASE,
    )
    return m.group(1).lower() if m else "none"


def run_claude(prompt: str, model: str = "sonnet") -> str:
    """Invoke `claude -p` non-interactively and return stdout."""
    result = subprocess.run(
        ["claude", "-p", "--model", model, prompt],
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    if result.returncode != 0:
        print(f"warning: claude exited {result.returncode}: {result.stderr[:200]}",
              file=sys.stderr)
    return result.stdout


def log_trial(row: Row, variant: str, loaded: str, end_pass: bool, log_path: Path) -> None:
    """Call log_skill_selection.py to append a JSONL record."""
    subprocess.run(
        [
            sys.executable, str(LOGGER),
            "--dispatch-id", f"pr-{row.pr}",
            "--variant", variant,
            "--loaded-skill", loaded,
            "--gold-skill", row.gold_skill,
            "--baseline-skill-free-pass", "true" if row.baseline_pass else "false",
            "--end-task-pass", "true" if end_pass else "false",
            "--log", str(log_path),
        ],
        check=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--courierflow-repo", type=Path,
                        default=Path.home() / "claude_code" / "courierflow",
                        help="Path to courierflow repo for `gh pr view`.")
    parser.add_argument("--rows", default="all",
                        help="Comma-separated row indices (1-12) or 'all'.")
    parser.add_argument("--variant", default="both",
                        help="Comma-separated: a,b,b150,c1,c3 — or 'both' (a,b).")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--log", type=Path,
                        default=REPO_ROOT / ".claude" / "experiments" /
                        "skill_selection_ab.jsonl")
    parser.add_argument("--prompts-dir", type=Path,
                        default=REPO_ROOT / ".claude" / "experiments" / "prompts",
                        help="Where to save generated prompts + responses.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Build prompts but skip model invocation.")
    args = parser.parse_args(argv)

    rows = parse_gold_labels(GOLD_LABELS)
    if args.rows != "all":
        wanted = {int(x) for x in args.rows.split(",")}
        rows = [r for r in rows if r.idx in wanted]
    if not rows:
        print("no rows selected", file=sys.stderr)
        return 1

    if args.variant == "both":
        variants = ["a", "b"]
    else:
        variants = [v.strip() for v in args.variant.split(",") if v.strip()]
    valid = {"a", "b", "b150", "c1", "c3"}
    bad = set(variants) - valid
    if bad:
        print(f"unknown variants: {bad}", file=sys.stderr)
        return 1
    args.prompts_dir.mkdir(parents=True, exist_ok=True)

    print(f"running {len(rows)} rows × {len(variants)} variants = "
          f"{len(rows) * len(variants)} trials")

    for row in rows:
        if not row.files:
            row.files = fetch_pr_files(args.courierflow_repo, row.pr)
        for variant in variants:
            prompt = build_prompt(variant, row)
            stem = f"row{row.idx:02d}-pr{row.pr}-variant{variant}"
            (args.prompts_dir / f"{stem}.prompt.txt").write_text(prompt)

            if args.dry_run:
                print(f"[dry-run] {stem}: prompt written, skipping model")
                continue

            print(f"running {stem}...", end=" ", flush=True)
            response = run_claude(prompt, model=args.model)
            (args.prompts_dir / f"{stem}.response.txt").write_text(response)

            loaded = parse_loaded_skill(variant, response)
            # end_task_pass is unknowable without actually running the diff;
            # set false by default and let the analyzer step or human review
            # update it. The replay measures selection behavior, not pass-rate.
            log_trial(row, variant, loaded, end_pass=False, log_path=args.log)
            print(f"loaded={loaded}")

    print(f"\ndone. log: {args.log}")
    print(f"prompts + responses: {args.prompts_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
