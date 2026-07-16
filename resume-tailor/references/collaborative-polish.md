# Collaborative Polish Mode — Claude ↔ GPT-5.6 Sol loop (opt-in)

Two top-tier models collaboratively refine the JD analysis and the tailored draft
through a **sequential, converge-to-consensus loop** — not a debate. Off by default;
runs only when the user explicitly asks (see triggers below).

## The loop

```
seed  (turn 1) : Claude reads the JD + fact-inventory → writes the first version
round 1 (turn 2): GPT-5.6 Sol polishes it, hands back
round 2 (turn 3): Claude polishes, hands back
round 3 (turn 4): GPT-5.6 Sol polishes
round 4 (turn 5): Claude polishes  ← ends on Claude (best writer, last word)
```

- **Cap:** 4 polish rounds after the seed (`--rounds`, default 4). Total ≤ 5 model calls.
- **Early stop:** the loop halts as soon as **two consecutive parseable turns both
  report `converged: true`** — genuine consensus, not one model rubber-stamping.
- **Ends on Claude** whenever `--rounds` is even (the default), so the strongest prose
  model gets the final pass.

## Models (via OpenRouter — one transport, per-request slug)

| Role | Slug | Override |
|---|---|---|
| Claude (writing lead) | `anthropic/claude-opus-4.8` | `--claude-model` |
| ChatGPT | `openai/gpt-5.6-sol` | `--gpt-model` |

Requires `OPENROUTER_API_KEY` in the environment (present in `~/.claude/.local.env`;
**populate it — it is currently empty**). Keys are read only from the environment.

## Where it runs (both points — "multiple points")

1. **Phase 1 — JD analysis** (`--stage jd-analysis`): the loop produces the structured
   job profile (recap, weighted focus areas, ATS keyword tiers, seniority/scope signals,
   hiring-risk sentence). Feed the result into the Phase 1 checkpoint you show the user.
2. **Phase 2 / 4 — draft polish** (`--stage draft-polish`, plus `--artifact <draft>`):
   the loop refines the tailored bullets/summary produced by the matching + positioning
   passes. Feed the result into the Phase 4 output.
3. **Cover letter** (`--stage cover-letter`, plus `--artifact <draft>`): opt-in, only when
   a cover letter is in scope — polishes an existing cover-letter draft.

Run Phase 1 first; its consensus profile informs the draft the loop polishes in Phase 2.

## The models must obey the skill's principles (binding, injected every turn)

The two models are collaborators, not free agents — they must follow **all** the resume and
cover-letter skill principles, exactly as the in-session Claude does. The script injects the
governing docs verbatim into every turn's system prompt via `--principles-file` (repeatable)
and instructs both models to treat them as HARD constraints: banned bullet patterns, plain-
language / no-marketing-jargon voice, "I help" + audience-centered framing, lead-with-the-
conclusion ordering, cover-letter opener rules (never "I was excited"; career-thesis lead;
never all-about-me), never attacking other companies/products, and the §9 sameness generic-
swap test each turn. A polish that reads better but breaks any rule is a **defect**.

**Always pass the governing files** (do NOT paraphrase them into flags — pass the real docs so
they stay the single source of truth and can't drift):

| Stage | `--principles-file` to pass |
|---|---|
| `jd-analysis` | `shared/communication-principles.md` |
| `draft-polish` | `shared/communication-principles.md`, `resume-tailor/references/writing-quality.md`, `resume-tailor/references/resume-bullet-bans.md` |
| `cover-letter` | `shared/communication-principles.md`, `resume-tailor/references/cover-letter-review.md` |

If you run the loop with **no** `--principles-file`, the script prints a WARNING and the models
polish without the house rules — never ship that output. Opener + no-attack rules are also baked
into the `cover-letter` stage brief as a backstop, but the real docs are authoritative.

Collaborative Polish **augments, never bypasses** the skill's own phases: still load the same
references for the in-session passes, still run the human checkpoints, and still run the §9
sameness pass + bullet-ban + `resume-qa` coherence check on the consensus output before Phase 5.

## Truth preservation is a HARD constraint

This is the resume analog of the SMS 160-char cap that collapsed the cross-provider
polish pipeline on 2026-07-15 (see `docs/plans/2026-07-15-openrouter-streamlining-plan.md`
in the henry repo). An LLM-judged "better" draft that fabricates is a regression, not a win.

- Both models receive the **canonical fact-inventory as immutable context** and are
  forbidden to introduce any employer, title, date, degree, metric, number, tool, or
  skill not present in it.
- Anything a model is not certain traces to the inventory is tagged inline `[verify]`.
- A **post-loop guard** diffs the consensus artifact's proper nouns / numbers against the
  inventory and prints any additions as `⚠️ TRUTH-GUARD REVIEW` on stderr. These are
  review candidates (JD keywords legitimately appear too) — **surface every flagged item
  to the user before finalizing**; never ship a flagged number or employer unresolved.

## How to run

```bash
SKILLS=~/claude_code/claude-skills

# Phase 1 — JD analysis
python3 $SKILLS/tools/resume-collab/collab_polish.py \
    --stage jd-analysis \
    --jd-file jd.md \
    --fact-inventory resume.md \
    --principles-file $SKILLS/shared/communication-principles.md \
    --output out/jd-profile.md

# Phase 2/4 — draft polish (after matching + positioning produce a draft)
python3 $SKILLS/tools/resume-collab/collab_polish.py \
    --stage draft-polish \
    --jd-file jd.md \
    --fact-inventory resume.md \
    --artifact out/draft-bullets.md \
    --principles-file $SKILLS/shared/communication-principles.md \
    --principles-file $SKILLS/resume-tailor/references/writing-quality.md \
    --principles-file $SKILLS/resume-tailor/references/resume-bullet-bans.md \
    --output out/polished-bullets.md

# Cover letter (opt-in, only when a cover letter is in scope)
python3 $SKILLS/tools/resume-collab/collab_polish.py \
    --stage cover-letter \
    --jd-file jd.md \
    --fact-inventory resume.md \
    --artifact out/cover-letter-draft.md \
    --principles-file $SKILLS/shared/communication-principles.md \
    --principles-file $SKILLS/resume-tailor/references/cover-letter-review.md \
    --output out/cover-letter.md
```

The consensus artifact is written to `--output`; the turn-by-turn transcript, convergence
markers, and truth-guard warnings print to stderr. Read the transcript — if the final turn
reports `remaining_concerns`, resolve them with the user rather than shipping silently.

## Failure handling (script already does this — know what to expect)

- **Empty / missing key** → exit 2 with a clear message. Populate `OPENROUTER_API_KEY`.
- **A model call fails** (429/5xx after retries, timeout) → the loop stops and ships the
  **last good artifact** reached so far, rather than nothing. Treat that as a partial run
  and re-run when the provider recovers.
- **JSON contract broken** (a model returns prose instead of the JSON object — GPT did
  exactly this in the cfb spike) → the raw text is used as the artifact for that turn,
  the turn is marked `[JSON-broken→raw]`, and its convergence signal is NOT trusted.

## When to use / not use

- **Use** when the user explicitly asks for the two-model collaborative polish, or when a
  single high-stakes role justifies the extra model spend and the user opts in.
- **Do NOT** run it by default (cost: two flagship models per session), on every JD in
  Multi-JD Mode (run it only on the one role the user tailors fully), or as a substitute
  for the human checkpoints — it augments Phases 1/2/4, it does not replace them.
