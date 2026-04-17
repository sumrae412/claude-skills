# Source & attribution

Imported from [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) at `engineering/skill-security-auditor/`.

- **Upstream commit:** `f567c61def3fb86046d7242b4bf27fceb63ad8b4`
- **License:** MIT (Copyright (c) 2025 Alireza Rezvani)
- **Imported on:** 2026-04-16

## Local modifications

`scripts/skill_security_auditor.py` patched in `clone_repo()` and `main()` finally block:

1. `tempfile.mkdtemp(dir=...)` pinned to system tmpdir + path-prefix assert before any `shutil.rmtree`. Prevents a poisoned `$TMPDIR` from directing the recursive cleanup at a sensitive directory.
2. Added `--` separator on `git clone` argv to defuse hostile URLs that resemble git options.

Both findings surfaced by a security review of the upstream script before adoption. SKILL.md and `references/threat-model.md` are verbatim from upstream.
