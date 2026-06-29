# Source

Imported from [github.com/coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @ `8bfcdff` (MIT license), 2026-06-29.

Original skill: `product-marketing/` (re-homed to repo root; upstream used a `skills/` prefix).

## Intentional deltas from upstream
- Added `user-invocable: true` frontmatter for slash-command registration.
- Tightened the `description` to claude-skills conventions (qualitative, "Use when..." triggers).

- Fixed the cwd-collision behavior: outputs write to a dedicated workspace dir, never inside a tracked repo.
- Dropped the upstream root `AGENTS.md`/`CLAUDE.md` (they instruct a once-per-session GitHub fetch of VERSIONS.md + `git pull` on confirm). Not copied; no skill body retains an outward-fetch instruction.

References: 0 file(s) carried over from upstream.
