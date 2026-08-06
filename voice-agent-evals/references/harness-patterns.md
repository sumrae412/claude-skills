# Harness patterns

How to build the thing that produces the numbers. Covers the bot-to-bot
architecture, artifact capture, simulated-caller design, tiering for cost, and
the failure modes of the harness itself.

---

## The bot-to-bot architecture

Five components. Anything less produces numbers for a subset of the suite.

1. **Simulated caller** — a voice agent playing the human, given a goal, a
   persona, and a set of facts it is allowed to reveal when asked. Must speak
   over the real audio path, not inject text.
2. **Agent under test** — your production stack, unmodified, reached the way a
   caller reaches it.
3. **Tool executor** — returns deterministic responses from a scenario database.
   Determinism here is what makes V6 checkable and V7 gradeable: you know
   exactly what the tools returned.
4. **Validator** — discards conversations that failed for harness reasons
   (simulated caller went off-script, audio dropped, scenario never started)
   *before* scoring. Regenerate rather than score them.
5. **Metrics engine** — reads audio, transcripts, and tool logs together. Any
   engine that sees only transcripts cannot produce V1-V5.

**Why the validator is not optional.** Without it, harness failures land in your
results as agent failures, and the suite's noise floor swallows the effect
you're measuring. This is the single highest-leverage component and the one
most often skipped.

---

## Artifact capture

Capture per call, or the run is unreproducible and un-regradeable:

- **Audio, both channels, separately.** Mixed audio makes overlap
  unmeasurable — and overlap is V5.
- **Timestamped transcripts per turn**, with speaker attribution and start/end
  times.
- **LLM input/output pairs** with the prompt version that produced them.
- **Tool calls** with arguments and returned values.
- **Generated TTS audio** kept separately from the mixed call — V3 scores this.
- **Session metadata:** locale, device, network conditions, model and voice
  identifiers, and the SUT's temperature.

**Capture once, grade many times.** The expensive half of a voice eval is the
call; grading is cheap by comparison. A harness that stores complete artifacts
lets you fix a broken judge and rescore history for the price of judge tokens
instead of re-running every call. A harness that stores only scores forces a
full re-run every time a rubric changes — and rubrics change constantly.

Stamp any rescored result as derived, naming the source run and the judge
version. A regrade is valid when the *judge* changed; it is invalid when the
*agent* changed, and a scorecard that cannot tell you which is worse than none.

---

## Designing the simulated caller

The caller is the eval. A cooperative caller produces a suite that passes
everything and predicts nothing.

**Required scenario variants:**

| Variant | What it stresses |
|---|---|
| Happy path | Baseline. Cover your top ~20 intents. |
| Multi-intent | Context retention; the caller wants two things in one call. |
| Mid-call goal change | "Actually, make it Thursday instead." |
| Ambiguous / underspecified | Does it ask, or does it assume? |
| Interruption | V5. The caller cuts in mid-answer. |
| Code-switching | Language change mid-sentence. |
| Adversarial | V9. Jailbreaks, other people's data, injection read aloud. |
| Regression | Every production bug, converted into a permanent case. |

**Condition axes crossed over the above:** accent group, noise environment,
connection quality, speech rate.

**Persona discipline.** Give the simulated caller a goal and a fact sheet, not a
script. A scripted caller cannot respond to an agent that goes off the expected
path, which is exactly when the interesting failures happen. Give it a stop
condition so it does not converse forever.

**The caller must not be graded.** Its job is to produce a hard, valid
conversation. If it fails to do that, the validator drops the call.

---

## Cost control

Voice evals are expensive in a way text evals are not: real-time audio, two
agents, and audio-capable judges.

- **Tier ruthlessly.** Component tier (V1-V4) runs on clips, costs little, and
  catches most regressions. Reserve full conversations for release gates.
- **Cheap probe before full suite.** One scenario end to end proves the harness
  works. Never discover a broken harness at scenario 200.
- **Per-scenario invocation, not one full-sweep process.** A transient provider
  failure then forfeits one scenario's spend instead of the run's.
- **Cap the run.** A hard cost ceiling on the runner, not just in the brief.
- **Budget k.** pass^k multiplies cost by k. k=3 is the usual compromise; run
  the full corpus at k=1 nightly and the release-gate subset at k=3.
- **Retry once per unit** on transport errors. Transient 5xx and connection
  resets are routine in this stack, not a broken-run signal — but a run that
  aborts loses its in-process cost counter, so estimate and say so.

---

## Harness failure modes

The ways the harness lies to you.

| Symptom | Likely harness cause |
|---|---|
| An assertion flips across identical runs | SUT temperature unpinned — you are measuring sampling noise |
| WER suspiciously near zero | Reference transcript generated by the STT under test |
| Turn-taking scores with no timing data | Judge is inventing; should have returned insufficient evidence |
| Every refusal scores as a failure | Judge cannot see the production refusal path |
| Sudden collapse in one metric only | Suspect the instrument before the system; check same-run raw evidence |
| Pass rate rises after "fixing" the bypass path | The old number was the broken one; the new one is the first honest signal |
| Whole suite lost to one error | Full-sweep invocation; move to per-scenario |

**Rule:** an eval is production code. A grader with a written spec and no test
of its own is the least-reviewed code in the system and gates everything.

---

## Reporting

A voice eval result that omits any of these is not interpretable:

1. **Which tier produced it** — clip, text-injected, or full audio conversation.
2. **Both axes** — accuracy and experience, separately, never blended.
3. **The distribution** — P95/P99 for timing, worst cell for segmented metrics.
4. **k and both pass@k and pass^k** for any reliability claim.
5. **Judge model snapshot and rubric version** for anything model-scored.
6. **What was not run**, and why. Silent truncation reads as full coverage.
