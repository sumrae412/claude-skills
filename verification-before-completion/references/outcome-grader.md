# Higher-tier verification: separate outcome grader

This skill's default rule — "run the command, read the output, then claim" — is self-verification with cited evidence. For production agent deployments where the agent's own report is the only signal (long-running tasks, managed agent runs, multi-step CMA workflows), self-verification is structurally insufficient: the same model that decided "done" cannot reliably judge whether "done" matches the spec.

The cleaner pattern at that tier is an **outcome grader** — a separate model invocation that evaluates the agent's final output against explicit success criteria.

## Reference

Anthropic Claude Cookbook — `managed_agents/CMA_verify_with_outcome_grader.ipynb`
https://github.com/anthropics/claude-cookbooks/blob/main/managed_agents/CMA_verify_with_outcome_grader.ipynb

Walks through:
- Coordinating a primary agent with a separate grader model.
- Encoding success criteria in the grader prompt (acceptance checks, refusal conditions, format requirements).
- Using the grader's verdict to gate task completion or trigger a retry.

## When to reach for this pattern

- **Managed-agent / background-agent runs** where no human reviews each step. The grader is the only check between agent output and downstream consumers.
- **Multi-step tool-using agents** where intermediate steps may succeed but the final outcome can still miss the requirement (the agent rationalizes "close enough").
- **Production workflows that bill or notify users on completion** — false positives have real cost.

## When NOT to reach for it

- **Dev-loop work in this session** — the human partner is the grader. The default self-verification + evidence pattern is correct here.
- **Cheap, fast tasks** — doubling the model invocations on every "done" claim is over-engineering. Reserve the grader pattern for tasks where the cost of a false-positive completion exceeds the cost of an extra inference round-trip.
- **When acceptance criteria are not writable as a prompt** — if you can't articulate "this is what success looks like" precisely enough for a separate model to check, you also can't articulate it for the primary agent. Fix the criteria first.

## Relationship to the main skill

This is a **complement**, not a replacement. The Iron Law ("no completion claims without fresh verification evidence") still holds — the grader pattern just changes who runs the verification when no human is in the loop. In dev sessions, you're still the verifier; in production CMA deployments, the grader model is.
