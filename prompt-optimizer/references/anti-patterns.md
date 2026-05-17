# Prompt Anti-Patterns Catalog

35 anti-patterns organized by category.

---

## Task Anti-Patterns (7)

1. **Vague task verb** — "Handle this," "deal with that." Use specific imperatives: Extract, Summarize, Generate, Classify, Rewrite, Evaluate.
2. **Missing success criteria** — No definition of "done." Fix: add acceptance criteria.
3. **Contradictory instructions without priority** — "Be concise but thorough" with no tiebreaker. Fix: state which wins.
4. **Scope creep invitation** — "Write about X" with no limits. Fix: bound it explicitly.
5. **The passive ask** — "Could you perhaps suggest..." vs. "Suggest 5 ideas." Imperatives produce better outputs.
6. **CoT on reasoning-native models** — Adding "think step by step" to O1/O3/O4-mini degrades output; they reason internally.
7. **Task buried after long context** — Question at top, document at bottom. Fix: long content first, question last.

---

## Context Anti-Patterns (6)

8. **Assumed shared knowledge** — Prompting as if the model knows your product, team, or prior conversation.
9. **Missing background** — No sentence of context. One line ("This is for a non-technical exec") changes output dramatically.
10. **No audience specification** — Model defaults to generic audience.
11. **Missing domain context** — For specialized domains, not specifying expertise level or jurisdiction.
12. **Stale context injection** — Including outdated info the model might contradict. Fix: use grounding constraints.
13. **Context overload without priority** — Too much background, no signal on what matters most.

---

## Format Anti-Patterns (6)

14. **No output format specified** — Model picks a format that doesn't fit your use case.
15. **No length guidance** — "Write a summary" could be 50 or 500 words.
16. **Style leakage** — Formatted prompt with headers/bullets → expects flowing prose back. Output mirrors input style.
17. **Negative-only format instructions** — "Don't use bullets, don't use jargon." Fix: state what TO do.
18. **Wrong template for the task** — Few-shot for a reasoning task; CoT for classification.
19. **Placeholder pollution** — Delivering a prompt with `[insert X here]` fields. Never do this.

---

## Scope Anti-Patterns (6)

20. **Infinite scope** — No mention of what's out of scope.
21. **Implicit scope from examples** — Model infers scope from examples and may be wrong.
22. **Gold plating** — Asking for tests + docs + error handling when the task is just "write a function."
23. **Recursive ambiguity** — "Improve this" without defining what improvement means.
24. **Missing exclusions** — For content tasks, not specifying what to omit.
25. **Silent agent scope** — For agentic tasks, no list of allowed vs. approval-required actions.

---

## Reasoning Anti-Patterns (5)

26. **No reasoning trigger** — Complex task on a non-reasoning model with no "think before answering."
27. **Competing reasoning cues** — Multiple reasoning instructions in one prompt. Pick one.
28. **Reasoning without grounding** — Analysis requested with no source material → hallucination.
29. **Missing assumptions check** — Ambiguous tasks with no instruction to state assumptions first.
30. **No confidence calibration** — Factual tasks with no request to flag uncertainty.

---

## Agentic Anti-Patterns (5)

31. **No stop conditions** — Agent doesn't know when to pause before irreversible actions.
32. **Missing allowed actions list** — Agent doesn't know its boundaries.
33. **No error handling instruction** — Agent keeps going when it hits an unexpected state.
34. **Single-shot agentic task** — Complex multi-step task with no checkpoints.
35. **Prompt injection surface** — Agent processes external content without guarding against embedded instructions.
