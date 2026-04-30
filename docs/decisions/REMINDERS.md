# Decision-record reminders

Scheduled-task fallback reminders. Any session that loads this file should check whether listed dates are due and run the listed command if so.

## Variant B soak check — fire at 2026-05-06T15:00:00+00:00

**Source:** [decision record](2026-04-29-ship-forced-selection-phase5.md)

On or after the fire date, run:

```bash
cd ~/claude_code/claude-skills && python3 claude-flow/scripts/analyze_skill_selection.py --log .claude/experiments/skill_selection_ab.jsonl --by-row > docs/decisions/2026-05-06-variant-b-soak-results.md 2>&1 && printf '\n\n--- Soak check complete: %s ---\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> docs/decisions/2026-05-06-variant-b-soak-results.md
```

Then update the decision record's follow-ups section with the result.
