# Baseline-delta evals: is this change worth it?

When the thing under test is an **instruction-set** — a skill, a system
prompt, a tool-description rewrite, a model swap — the question isn't
"what's the pass rate?" but "**does this change beat the baseline, and
is the gain worth its cost?**" The pass rate alone can't answer that;
the *delta* against a baseline can.

This generalizes the with/without-skill loop that
[`anthropic-skills:skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
automates for Claude Skills. Use `skill-creator` when the artifact is a
Skill and you want the loop run for you; use this reference for the
method and for the prompt / model / tool-description cases skill-creator
doesn't cover.

## The core move: run each task against two arms

Run the *same* tasks through two (or three) configurations:

- **treatment** — with the new skill / new prompt / new model.
- **baseline** — without it, OR the **previous version** when iterating
  on something that already exists. Snapshot the old version first so
  the baseline doesn't move under you.

The **delta between arms is the signal.** A treatment that scores the
same as baseline added nothing — no matter how high its absolute pass
rate. Use **paired** analysis (same tasks both arms) — see
`phases/phase-4-running-and-interpreting.md` "Interpreting deltas."

## Measure cost alongside quality

A change buys quality and costs resources. Record both per arm so you
can judge the trade:

| | pass rate | tokens | latency |
| --- | --- | --- | --- |
| treatment | 0.83 | 3800 | 45s |
| baseline | 0.33 | 2100 | 32s |
| **delta** | **+0.50** | +1700 | +13s |

`+50pts for +13s` is an easy yes. `+2pts for 2× tokens` is probably a
no. Report the delta table, not a bare pass rate — "better but triples
cost" is a different decision than "better and cheaper."

## Assertions come after the first run

Write the cases (prompt + expected-output + any input files) first; add
the **assertions after you see the first outputs** — you usually don't
know what "good" looks like until the artifact has run once. Keep
assertions specific and observable ("chart has labeled axes"), not
brittle ("output contains the exact phrase X") and not vague ("output is
good"). Reserve human review for qualities that don't decompose into
pass/fail.

## Prune assertions that don't discriminate

After a run, drop assertions that **pass in both arms** — the base model
handles them without the change, so they inflate the treatment score
without reflecting its value. Investigate assertions that **fail in both
arms** (broken assertion, or task too hard). The signal lives in
assertions that **pass with the change and fail without** — study *why*,
that's where the artifact earns its keep.

## Deprecation check: disable and re-test

Periodically run the eval with the skill/prompt **disabled**. If the
base model now passes natively (models improve underneath you), the
artifact adds only latency and maintenance surface — **deprecate it.**
A skill that no longer beats its own baseline is dead weight.

## See also

- `phases/phase-4-running-and-interpreting.md` — paired-difference
  analysis, repetitions, saturation.
- `phases/phase-1-design.md` — capability vs regression tagging; a
  saturated capability eval is the same "no signal" failure as an
  assertion that passes in both arms.
- `references/agent-type-graders.md` — the efficiency dimensions to put
  in the cost columns.

Sources: agentskills.io "Evaluating skill output quality"; philschmid
"Testing skills"; Hamel Husain "Evals skills for coding agents";
Anthropic / Google Cloud / OpenAI skill-eval writeups.
