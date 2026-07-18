# claude-skills

A personal library of [Claude Code](https://claude.com/claude-code) skills — reusable, on-demand instructions that extend how Claude approaches a task (code review, writing, debugging, research, planning, and more). Skills live as plain markdown, so any of them can be copied into your own project or plugin with no build step.

This repo isn't a distributed plugin — it's a working library. Browse it, take what's useful, leave the rest.

## What's in here

- **131 skills**, each a folder with a `SKILL.md` (instructions + trigger description) and optional `references/`, `scripts/`, or `phases/` subfolders for progressive disclosure.
- **[`CATEGORIES.md`](CATEGORIES.md)** — skills grouped by topic (defensive coding, communication, evals, etc.) for browsing.
- **[`COMMANDS.md`](COMMANDS.md)** — slash commands and workflow docs that live at repo root instead of in a skill folder.
- **[`NOTICE.md`](NOTICE.md)** — attributions for skills adapted from third-party repos (MIT-licensed, credited per upstream).
- **`scripts/`** — standalone tooling (`build_doc_graph.py`, `find_skill_neighbors.py`, `search_vault.py`) used to maintain the corpus itself.

## Quickstart — borrow a skill

Every skill is self-contained in its own folder, so borrowing one is a copy:

```bash
# 1. Clone (or just download the one folder via GitHub's "download" UI)
git clone https://github.com/sumrae412/claude-skills.git

# 2. Copy the skill(s) you want into your own project
cp -r claude-skills/debate-team ~/my-project/.claude/skills/

# 3. If the skill has a references/ or scripts/ subfolder, it comes along for free —
#    nothing else in the repo is required for that skill to work.
```

Claude Code auto-discovers skills placed under `.claude/skills/<name>/SKILL.md` in a project, or `~/.claude/skills/<name>/SKILL.md` for skills you want available in every project — no registration step, no plugin manifest required. If the `.claude/skills/` (or `~/.claude/skills/`) directory already existed when your session started, a newly-copied skill is picked up live, mid-session. If you're creating that directory for the first time, restart your session once so Claude Code starts watching it. ([Source](https://code.claude.com/docs/en/skills.md#live-change-detection))

**Before you copy, check the skill for:**
- A `See also` section at the bottom of `SKILL.md` — sibling skills it composes with. Copy those too if you want the full behavior, or note the gap if you're taking it standalone.
- A `references/` or `scripts/` subfolder — some skills are thin routers over lazy-loaded reference files; without them the skill degrades but the top-level instructions still work.
- **Inline `load ../shared/...` or `load shared/...` prose in the skill body** — not every cross-folder dependency is in a `See also` section. The 10 writing-family skills (`resume-tailor`, `writing-voice`, `ai-writing`, `writing-workshop`, `synthesis-brief`, `pitch-deck`, `startup-positioning`, `sme-voice`, `difficult-workplace-conversations`, `prd`) all instruct Claude to load [`shared/communication-principles.md`](shared/communication-principles.md) before drafting — that file is a repo-root sibling, not inside any of those skill folders, and copying just the skill folder alone will silently drop it. If you're borrowing one of these, copy `shared/communication-principles.md` alongside it (and keep the relative path, e.g. `<your-skills-dir>/shared/communication-principles.md`, or rewrite the `load` reference to wherever you put it).
- Whether it's listed in [`NOTICE.md`](NOTICE.md) — third-party-sourced skills carry their upstream license; keep the attribution if you redistribute.

Verified 2026-07-09: `grep -rl "shared/communication-principles" --include=SKILL.md .` returns exactly those 17 files; none of them surface the dependency in a `See also` block, only in prose mid-skill. The doc-graph script also won't catch it as a broken reference (it resolves the relative path correctly within this repo), so this is a borrow-time gotcha, not a repo-health one.

**Want more than one skill at a time?** Grep [`CATEGORIES.md`](CATEGORIES.md) for the topic you care about, then copy the whole set of folders it lists.

## Finding the right skill

- **Know roughly what you want?** Search [`CATEGORIES.md`](CATEGORIES.md) — it groups skills by surface area (frontend, backend, evals, personal/life-admin, communication, etc.) with a one-line trigger description each.
- **Not sure what exists?** Grep every `SKILL.md`'s `description:` frontmatter field — that's the exact text Claude itself matches against to decide whether a skill applies:
  ```bash
  grep -r "^description:" --include=SKILL.md . | less
  ```
- **Want the structural map instead of a manual browse?** Run the doc-graph (below) — it surfaces hub skills (heavily cross-referenced, core to the corpus) versus leaf skills (standalone, easy to lift out).

## Setting up the doc-graph

The doc-graph is a zero-dependency static analyzer (`scripts/build_doc_graph.py`, pure Python stdlib) that walks the markdown corpus and reports which files are hubs, which are true orphans, and which pairs of skills look related but aren't cross-linked yet. It's the fastest way to get oriented in 131 skill folders.

```bash
# From the repo root:
python3 scripts/build_doc_graph.py

# Or point it at any markdown corpus (this repo, a docs tree, a project memory dir):
python3 scripts/build_doc_graph.py --root /path/to/corpus
```

No install step — no `pip install`, no `requirements.txt`. Requires Python 3.

**Output:** writes `GRAPH_REPORT.md` to `.knowledge/` under the root you pointed it at (gitignored — it's a local, regenerable artifact, not checked-in content).

**Reading the report:**

| Section | What it means | What to do with it |
|---|---|---|
| Hubs (>10 inbound refs) | Load-bearing skills lots of others point to | Don't delete; consider splitting if it feels overloaded |
| True orphans | Nothing links to them | Real deletion candidates — but check nothing references them implicitly (e.g. a routing rule in a CLAUDE.md) first |
| Sinks | Referenced but link out to nothing | Usually fine as-is (specs, glossaries, leaf reference docs) |
| Suggested missing cross-links | Keyword overlap between two files | **Default assumption: they're complementary and missing a `See also` link, not duplicates to merge.** Read both before consolidating anything. |
| Suggested questions for review | Prompts for a human pass | Not action items — just things worth a second look |

Full usage details, flags (`--out`, `--json`, `--missing-threshold`), and the excluded-asset-class list live in [`doc-graph/SKILL.md`](doc-graph/SKILL.md).

## Repo conventions (if you're contributing back or forking)

- One skill = one folder = one `SKILL.md` with `name:` and `description:` frontmatter. Add `user-invocable: true` if it should register as a `/<name>` slash command.
- Keep `SKILL.md` lean; push long reference material into `references/` and load it on demand rather than keeping a 2000-line file resident in every session.
- Cross-reference sibling skills with a `See also` section — bare mentions of another skill by name aren't enough for the doc-graph to catch, and they don't help a human browsing either.
- If you import a skill from another repo, add an entry to [`NOTICE.md`](NOTICE.md) with the upstream source, commit, license, and any local modifications.

## License

Locally-authored skills in this repo have no separate license file attached; treat them as available to copy and adapt. Skills adapted from third-party repos carry their upstream license — see [`NOTICE.md`](NOTICE.md) for the specific terms per skill before redistributing those.
