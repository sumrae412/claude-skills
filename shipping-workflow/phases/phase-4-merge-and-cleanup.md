# Phase 4: Merge and Cleanup

## Goal

Merge the PR safely, verify the merged state, and hand off to cleanup.

## Process

- merge only after review and CI pass
- verify PR state is actually `MERGED`
- diagnose and retry if still open
- stop and inform the user if protection rules block merge
- delegate final teardown to `/cleanup`

## Rules

- No cleanup before merge state is known.
- Do not manually replicate `/cleanup` responsibilities.

## Output

Confirmed merge state plus cleanup handoff.
