# Red Flags — STOP and Check Yourself

If you catch yourself thinking any of these, you're rationalizing. STOP and follow the process.

| Thought | Reality |
|---------|---------|
| "This is basically a fast-path" | If you're justifying it, it's not. Use full workflow. |
| "I don't need 2 architects for this" | Complexity hides behind familiarity. Do the scale check. |
| "Tests can come after, I know this works" | TDD is Phase 5's hard gate. No exceptions. |
| "User seems impatient, skip clarification" | Phase 3 exists because skipping costs more time later. |
| "I'll just start coding and figure it out" | That's Phase 5 without Phase 2-4. You'll rework it. |
| "The exploration was enough, skip requirements" | Exploration answers WHAT exists. Phase 3 answers WHAT to build. Different questions. |
| "One more implementation attempt" (after 2+ failures) | 3 failures = wrong architecture, not wrong code. See 3-Strike Rule. |
| "I'll fix the review findings later" | CRITICAL/WARNING findings block shipping. Fix now or escalate. |
| "Skip the evidence gathering, I can see the problem" | Seeing symptoms ≠ understanding root cause. Gather evidence first. |
| "I scaffolded the files, that proves it works" | Scaffolding ≠ working. No real call against a real consumer = no signal. See Phase 6 verification ladder rung 4. |
| "The status endpoint says healthy, we're done" | Health ≠ correct. Status endpoints can return 200 while the durable contract is broken. See `references/lookup-detectors.md` § durable introspection. |
| "Option B is just Option A but cleaner" | That's one architecture, not two. Re-derive Option B from a different optimization target or skip Phase 4's debate entirely (LITE PATH). |
| "Last feature looked like this, copy the shape" | Static-chain drift. Re-derive layout from this feature's data flow, not from the previous diff. |
| "MEMORY says this MCP tool is available" | MEMORY is not runtime truth. Check the Phase 0.6 environment doctor probe — the tool may not be loaded this session. |
