# Phase 4: Repo Gotchas

Load this phase only when the current change touches shells, file paths,
aggregation logic, or other known failure modes.

## Shell + LLM Boundaries

- Put long prompts in sibling `.txt` files, not inline shell strings.
- Prefer stdin over argv for large prompts.
- Cross shell -> Python boundaries with env vars, not heredoc
  interpolation.

## Cleanup Discipline

- Register cleanup traps before creating temp files, symlinks, or
  background processes.

## Path Safety

- Any path derived from untrusted input must be resolved and verified to
  remain inside the trusted root before access.

## Idempotency

- Any aggregator or shared artifact updater that may rerun must dedup on a
  stable key.

## Output

Focused warning list for the exact gotchas relevant to the current task.
