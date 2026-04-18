# Usefulness Interview Prompt

Executed at the end of every cell in Phase 4 (after outcome is known, before writing the transcript). One LLM call per cell.

## Purpose

Capture the persona's in-character reflection on whether the app actually addresses their `goals_in_app`. Three distinct signals:

- **Usable** (can they operate it?) — covered by outcome (`success` vs `stuck`).
- **UI quality** (did they hit snags?) — covered by per-step `ui_observations`.
- **Useful** (do they actually want this?) — the gap this interview fills.

A persona can complete a flow successfully, hit no UI snags, and still say "I'd never bother using this." That last signal is what pre-launch beta testing exists to catch — and it's often the product-market-fit signal, not a bug signal.

## Prompt template

Append after the cell's step loop terminates (regardless of outcome):

```
Stepping back from that interaction:

Imagine a friend asked you about this app. In your own voice, not as a test user —
would you actually use it?

Give me:
- A 1–5 rating of how useful this app is to you, specifically.
  - 5: I'd use this regularly — it solves a real problem for me.
  - 4: I'd try it and probably stick with it.
  - 3: It's fine but I'd forget about it.
  - 2: I'd use it once and move on.
  - 1: Not useful to me at all.
- Would you actually use it: yes / no / maybe?
- What was the biggest draw? (or null if nothing)
- What would keep you from using it? (or null if nothing)
- 2–3 sentences in your own voice — how would you actually describe this app to that friend?

Rate the app itself, not this test run. Don't penalize based on bugs you hit or
things you were deliberately testing.
```

## Return schema

```json
{
  "rating": 1,
  "would_use": "yes | no | maybe",
  "quote": "2-3 sentences, in persona voice",
  "biggest_draw": "string | null",
  "biggest_blocker": "string | null"
}
```

## Why in-character

A persona saying *"this app saves me four hours a week, I'm sold"* is more valuable than them rating 4/5 in abstract. The quote is often the most useful output — it's usable verbatim in product meetings. Phase 6 surfaces quotes, not just numbers.

## Bias caveats

- **Testing-style bias.** Personas assigned the `invalid` habit saw a lot of error handling and will under-rate. Explicit instruction ("rate the app, not the test run") mitigates, doesn't eliminate. Phase 6 averages a persona's ratings for the same flow across styles before clustering.
- **Sycophancy.** LLMs skew toward positive ratings, compressing the range (everyone rates 3–4). If Phase 6 sees range compression across a run, harshen the rating anchors and re-run the interview pass.
- **Character drift.** A cranky persona shouldn't score everything charitably. If `usefulness_reflection.quote` doesn't match the persona's `communication_style`, Phase 5's `linguistic_habits` task will catch it and the transcript fails the fidelity gate.

## Model choice

Use the same `persona_player` model that ran the cell. Don't switch — the persona's voice should be continuous between their actions and their reflection.

## Placement

After outcome determination, before persisting the transcript. One call per cell. Default run (50 cells) → 50 additional LLM calls.
