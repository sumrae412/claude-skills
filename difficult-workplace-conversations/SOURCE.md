# Source

This skill was imported and adapted from the upstream template by **davila7**.

**Upstream repo:** [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates)

**Upstream path:** `cli-tool/components/skills/enterprise-communication/difficult-workplace-conversations/`

**Import date:** 2026-06-23

**Upstream commit at import:** Public main branch (exact SHA unavailable via API at import time — verify via `gh api repos/davila7/claude-code-templates/git/commits/main`)

---

## Adaptations Applied

The following changes were made during import; these are not present in the upstream source:

1. **Professional-help boundary added** — A prominent note at the top of `SKILL.md` and within `references/emotional-regulation.md` directs users to licensed professionals (employment attorney, therapist, HR) for serious situations: harassment, discrimination, legal disputes, safety issues, and persistent emotional-regulation patterns beyond individual-message scope.

2. **`/communication-safeguards` routing added** — A "Compose With /communication-safeguards First" section was added to `SKILL.md`, naming the upstream state/timing/intent gate that should run before this skill's structure/delivery layer. The three-skill sequence is documented: `/communication-safeguards` → this skill → `anthropic-skills:toneguard`.

3. **Cross-references swapped** — Upstream "See also" links pointed to sibling skills in the davila7 repo (`feedback-mastery`, `professional-effective-communication`). These were removed. New links point to Summer's own skill library: `../communication-safeguards/SKILL.md` (primary), `../writing-voice/SKILL.md` (secondary), and `../shared/communication-principles.md` (communication principles reference). All cross-references use relative paths per the cite-or-link rule.

4. **Communication principles integration** — A `Communication Principles` section was added to `SKILL.md` linking to `../shared/communication-principles.md` and naming the relevant principles (§1 audience-centered, §3 lead-with-conclusion, §7 preparation, §9 sameness-detector).

5. **Skill-linking cross-references** — The skill-linking hook ran after authoring and identified two meaningful neighbors: `career-practice` and `communication-safeguards`. Bidirectional `See also` links were added to both sibling skills.

---

## Files Imported

| File | Changes from upstream |
|---|---|
| `SKILL.md` | Substantial rewrite of frontmatter, added boundary note, added `/communication-safeguards` routing, swapped cross-refs, added communication-principles section |
| `references/conversation-framework.md` | Minor prose edits for house style; content substantially preserved |
| `references/preparation-template.md` | Added `/communication-safeguards` callout in the emotional-state check; otherwise preserved |
| `references/delivery-scripts.md` | Minor prose edits; content substantially preserved |
| `references/emotional-regulation.md` | Added professional-help boundary note at top and bottom; otherwise preserved |
