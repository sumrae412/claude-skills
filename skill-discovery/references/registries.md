# External Skill Registries

Search order: start broad (GitHub topic search) to find candidates across ecosystems, then drill into specific known repos. Always verify provenance before recommending an install.

## GitHub topic search (broadest)

Claude-compatible skills are conventionally tagged with the `claude-skill` or `claude-code-skill` topic.

```bash
# Find repos publishing skills
gh search repos --topic=claude-skill --sort=stars --limit=20

# Find a specific skill by filename pattern
gh search code "filename:SKILL.md <intent-keyword>" --limit=20

# Find issues/discussions about a capability
gh search issues "<capability> skill" --limit=10
```

**Rank results by:** star count, last-commit recency (< 6 months = active), author reputation (known orgs: anthropics, vercel-labs).

## Known registries

### `anthropics/skills` (official reference set)

Anthropic's reference skill set. Many are already installed locally as `anthropic-skills:*` (check the session-reminder list first).

```bash
# Browse the canonical set
gh repo view anthropics/skills
gh api repos/anthropics/skills/contents/skills --jq '.[].name'
```

Install path: usually via the Claude Code plugin system — check the repo README for current instructions rather than assuming.

### `vercel-labs/skills` (community registry + CLI)

Vercel's community skill registry. Ships with a CLI:

```bash
# Search the Vercel registry
npx skills search <keyword>

# View a specific skill's SKILL.md
npx skills show <skill-name>

# Install (confirm with user first)
npx skills install <skill-name>
```

Verify `npx skills` is available by running `npx skills --help` in the target directory before quoting commands to the user. If the CLI's interface has changed, `gh repo view vercel-labs/skills` is the fallback source of truth.

### `obra/superpowers` and other plugin packs

Installed plugin skills appear in the session list with a `plugin:skill` namespace (e.g. `superpowers:using-superpowers`, `pr-review-toolkit:review-pr`). To discover uninstalled plugins, search GitHub for `topic:claude-code-plugin`.

## Provenance checklist

Before recommending an external install:

- [ ] Repo has a visible README with purpose + install steps
- [ ] Last commit within 12 months (or explicit "stable" signal)
- [ ] Non-trivial star count OR known author (personal repos with 0 stars need stronger justification)
- [ ] SKILL.md is readable and matches the user's actual intent (don't guess from the name)
- [ ] No obvious red flags: shell-exec in frontmatter, undocumented network calls, vendored credentials
- [ ] Org/repo/CLI names cited in this doc were verified via `gh api repos/<org>/<repo>` or `<cli> --help` at author time, not recalled from memory — silent hallucination of third-party names is the primary failure mode for registry references

## Deferred verification pattern

If you quote a registry command the user will run, say so explicitly:

> "I haven't run `npx skills search X` in this session — this is the command to try. If the CLI has changed, fall back to browsing `vercel-labs/skills` on GitHub."

Do not assert an external skill exists without either (a) fetching its SKILL.md or (b) citing a specific repo + commit. Hallucinated skill names are the primary failure mode for this kind of discovery.
