# Third-party attributions

This repository contains skills and patterns adapted from third-party sources.
Attribution and license terms for each are reproduced below as required by the
respective licenses. The previous per-skill `SOURCE.md` files have been
consolidated here; vetting notes and local-modification details for each import
are preserved in this single document.

---

## Skills imported from `alirezarezvani/claude-skills`

**Upstream:** https://github.com/alirezarezvani/claude-skills
**Upstream commit (all skills below unless noted):** `f567c61def3fb86046d7242b4bf27fceb63ad8b4`
**License:** MIT

> Copyright (c) 2025 Alireza Rezvani
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in
> all copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

### Imports and local modifications

| Local skill | Upstream path | Imported | Local modifications |
|---|---|---|---|
| `dependency-auditor/` | `engineering/dependency-auditor/` | 2026-04-17 | Description tightened (upstream was the title string, blocked routing). Body verbatim. |
| `fda-consultant-specialist/` | `ra-qm-team/fda-consultant-specialist/` | 2026-04-17 | None. Verbatim. |
| `gdpr-dsgvo-expert/` | `ra-qm-team/gdpr-dsgvo-expert/` | 2026-04-17 | None. Verbatim. |
| `information-security-manager-iso27001/` | `ra-qm-team/information-security-manager-iso27001/` | 2026-04-17 | None. Verbatim. |
| `llm-cost-optimizer/` | `engineering/llm-cost-optimizer/` | 2026-04-17 | Dropped `.claude-plugin/plugin.json`. Replaced dangling cross-refs to non-local sibling skills (`senior-prompt-engineer`, `observability-designer`, `performance-profiler`, `api-design-reviewer`) with `prompt-governance` and `claude-api`. |
| `migration-architect/` | `engineering/migration-architect/` | 2026-04-17 | Description tightened (upstream was the title string, blocked routing). Body verbatim. |
| `prompt-governance/` | `engineering/prompt-governance/` | 2026-04-17 | Dropped `.claude-plugin/plugin.json`. Replaced dangling cross-refs (`senior-prompt-engineer`, `ci-cd-pipeline-builder`, `observability-designer`) with `prompt-optimization`. |
| `rag-architect/` | `engineering/rag-architect/` | 2026-04-17 | None. Verbatim. |
| `skill-security-auditor/` | `engineering/skill-security-auditor/` | 2026-04-16 | `scripts/skill_security_auditor.py` patched: (1) `tempfile.mkdtemp(dir=...)` pinned to system tmpdir + path-prefix assert before any `shutil.rmtree` (defense against poisoned `$TMPDIR`), (2) `--` separator on `git clone` argv (defense against hostile URLs resembling git options). Both findings from a security review of the upstream script. |
| `soc2-compliance/` | `ra-qm-team/soc2-compliance/` | 2026-04-17 | None. Verbatim. |

All imports passed `skill-security-auditor` scan with 0 findings. Python scripts
verified as self-contained local CLIs with no network calls, no API keys, and
no hardcoded paths.

---

## Skill imported from `ibelick/ui-skills`

**Upstream:** https://github.com/ibelick/ui-skills
**Upstream commit:** `df4eb34c5dee830e8e36490d6fde3451c187339b` (2026-02-19)
**License:** MIT

> Copyright (c) 2025 Julien Thibeaut / ibelick
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in
> all copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

### Imports and local modifications

| Local skill | Upstream path | Imported | Local modifications |
|---|---|---|---|
| `fixing-accessibility/` | `skills/fixing-accessibility/` | 2026-04-29 | Added "Framework-agnostic" note in `## how to use` for non-React stacks (Jinja, Alpine.js) pointing to `defensive-ui-flows`. Added `## related skills` section. Replaced curly-quote `"click here"` with straight quote (downstream-parser survivability for ATS / plain-text contexts). Body otherwise verbatim. |

`baseline-ui`, `fixing-metadata`, and `fixing-motion-performance` were
deliberately not imported (stack mismatch / no surface / low ROI — see
`feedback_ibelick_ui_skills_evaluation` in the project memory for the
4-axis rubric used).

---

## `token-economy` — patterns distilled from multiple sources

This skill is **principles-only**: no upstream code or prose was copied
verbatim. Patterns and ideas were re-expressed in this repository's voice.
Techniques and patterns are not copyrightable (17 U.S.C. § 102(b)); only
expression is.

### Primary source — WithWoz/wozcode-plugin

**Upstream:** https://github.com/WithWoz/wozcode-plugin
**Plugin version referenced:** `woz@wozcode-marketplace` v0.3.43
**License:** Proprietary — © WozCode. All rights reserved. Use is subject to
WozCode's Terms of Service.
**Inspiration date:** 2026-04-20

The agent-prompt discipline (from `agents/explore.md`, `agents/plan.md`,
`agents/code.md`) and the tool-description principles (from `Search` and `Edit`
MCP tools — batching, combined discover+read, mtime-aware caching, targeted
ranges) were **read and re-expressed** for orthodox Claude Code tools. No
upstream text was copied. Woz-tool-specific guidance (Search parameters,
Edit `edits[]` array, Sql introspection) was deliberately dropped — those
would be dead pointers without the proprietary plugin.

### Pattern 11 inspiration — JuliusBrussee/caveman

**Upstream:** https://github.com/JuliusBrussee/caveman (specifically the
`caveman-compress` subcommand)
**License:** MIT
**Inspiration date:** 2026-04-23

> Copyright (c) JuliusBrussee — MIT license terms as published in upstream
> repository.

**What was taken:** the *idea* that always-loaded memory files pay a recurring
token cost and benefit from one-time prose compression with a human-readable
backup kept alongside. **What was deliberately left behind:** caveman-speak
style (articles dropped, fragment grammar, 文言文 mode). Our pattern uses dense
professional prose, not telegraphic shorthand.

### Pattern 12 inspiration — Opencode-DCP/opencode-dynamic-context-pruning

**Upstream:** https://github.com/Opencode-DCP/opencode-dynamic-context-pruning
**License:** AGPL-3.0-or-later
**Inspiration date:** 2026-05-01

**What was taken:** two principles — (1) some tool-output categories carry
irreplaceable signal and should never be compressed away (translated to
TodoWrite, skill outputs, Write/Edit results, Plan content on the Claude Code
surface); (2) errored tool calls have a high-bulk / low-signal asymmetry where
the error message is load-bearing and the input payload can be dropped.
**What was deliberately left behind:** DCP's actual implementation (`compress`
tool, range/message modes, nested compressions, decompress-by-ID, soft-threshold
nudge frequency, per-model context overrides). All operate at the LLM-request-
rewrite layer, which Claude Code's harness owns; skills cannot intercept and
rewrite messages this way. **No AGPL code was copied** — only the underlying
ideas, which are not copyrightable per 17 U.S.C. § 102(b). Therefore the AGPL
terms do not apply to this skill.

---

## How to update this file

When importing or distilling new skills:

1. Add a row to the appropriate license section (or create a new section for a
   new upstream).
2. Record upstream URL, commit/version, license + copyright holder, import date,
   and a one-line summary of local modifications.
3. For principles-only imports from copyleft sources, explicitly document what
   was taken vs left behind to support the §102(b) defense.

The MIT, Apache-2.0, and BSD-style licenses require the copyright notice be
preserved; this file satisfies that obligation in one place rather than
fragmented across per-skill `SOURCE.md` files.
