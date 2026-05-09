# Commands and top-level workflows

Slash commands and workflow docs at the repo root. These are a different asset class than skills (which live in `<name>/SKILL.md` directories) — they're invoked directly by name or used as standalone references.

## Slash commands

Files with frontmatter (`name:`, `description:`) — these register as slash commands the harness can invoke.

| Command | Purpose |
|---|---|
| [`quick-ci.md`](quick-ci.md) | Run the project's quick CI validation (`./scripts/quick_ci.sh`) before merging or deploying. |
| [`seed-data.md`](seed-data.md) | Guide database seeding for dev/test environments. Lists available seed scripts. (`disable-model-invocation: true` — call directly, not via auto-routing.) |

## Workflow references

Plain markdown docs at the repo root — referenced by other docs/skills, not auto-invoked.

| Doc | Purpose |
|---|---|
| [`deploy.md`](deploy.md) | Railway deployment procedure for production. |
| [`discover.md`](discover.md) | Structured discovery session — one-question-at-a-time requirements exploration before proposing solutions. |
| [`docs-cleanup.md`](docs-cleanup.md) | Update project documentation based on completed work, then prune outdated files. |
| [`pre-deploy.md`](pre-deploy.md) | Pre-deployment validation checks (`./scripts/quick_ci.sh --core`). |

## Project-context registries

| Doc | Purpose |
|---|---|
| [`active-files.md`](active-files.md) | Inventory of files in active development (CourierFlow-context). Everything else is in `_archived/` and should not be imported, modified, or referenced. |

---

## Why this index exists

The `scripts/build_doc_graph.py` doc-graph spike flagged these 7 top-level files as "true orphans" because they had zero markdown cross-references. They aren't skills (skills live in `<name>/SKILL.md` dirs and the script's progressive-disclosure detection knows about that pattern). They're commands and workflow references — a different asset class — and weren't connected to anything else in the corpus.

This file gives them legitimate inbound references and improves human discoverability. The doc-graph script also now classifies repo-root `.md` files as "command files" rather than orphans.

To regenerate the doc-graph report: `python3 scripts/build_doc_graph.py`.
