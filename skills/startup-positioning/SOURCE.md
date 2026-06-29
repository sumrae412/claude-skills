# Source

Imported from: https://github.com/ferdinandobons/startup-skill

Upstream path: `startup-positioning/`

License: MIT

Commit: b1377b93

Import date: 2026-06-29

## Changes from upstream

- Added `user-invocable: true` frontmatter so the skill registers as `/startup-positioning` in the Claude Code CLI
- Tightened description: qualitative phrasing, removed hard-coded counts, named domain artifacts (Dunford, JTBD, Moore, Neumeier)
- Added Communication Principles load pointer (writing-centric skill: load `shared/communication-principles.md` and run §9 sameness-detector on tagline candidates)
- Fixed cwd-collision flaw: all output files now write to `~/Documents/<project-name>-positioning/` workspace, never inside a tracked git repo
- Updated all output path references in SKILL.md and reference files from `{project-name}/` to `<workspace>/` to match the workspace dir convention
- Dropped pitch-deck cross-reference (skill does not exist in this repo)
- Reference files carried over verbatim from upstream; no content changes to research protocols or framework definitions
