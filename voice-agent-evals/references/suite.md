# The suite — ten voice-agent evals

Each eval states the question it answers, what it runs on, how it scores, where
the gate sits, and the trap it exists to catch. Thresholds referenced here are
defined per use case in [metric-catalog.md](metric-catalog.md). Judge rubrics
for the model-scored evals are in [judge-rubrics.md](judge-rubrics.md).

Run order matters. A failing V1 makes V6 and V7 uninterpretable — you cannot
tell a policy error from a mis-heard word. Fix upstream first.

---

## Component tier

Runs on clips and single turns. Cheap enough for every change.

### V1 — Transcription fidelity under a condition matrix

**Question:** does the agent hear correctly across the conditions it will
actually be deployed into?

**Runs on:** a clip set with independent reference transcripts, stratified
across three axes — accent group (10+), noise condition (quiet, office, café,
street, vehicle), and domain vocabulary (your product names, drug names, street
names, SKUs).

**Scoring:** code. WER = (S + D + I) / N. Use CER instead for non-whitespace
languages. Report per cell, never one mean.

**Gate:** the *worst* cell, not the average. A matrix that passes on average and
fails in-vehicle has shipped a broken drive-time experience.

**Trap:** producing the reference transcript with the same STT you are scoring.
That measures nothing and always looks excellent. References must be
human-typed or the exact source text you fed a TTS to generate the clip.

**Second trap:** WER is semantically blind. A transcript that drops the caller's
name but nails the filler words can beat one that captures the name and fumbles
grammar. Pair every WER number with V2.

---

### V2 — Entity integrity, heard and spoken

**Question:** did the tokens that carry the transaction survive the round trip?

**Runs on:** utterances seeded with the entity classes your domain depends on —
person names, confirmation and booking codes, dollar amounts, dates and times,
phone numbers, addresses, account IDs.

**Scoring:** code. Exact-match recall per entity class, measured at **both
ears**:
- *Inbound:* entity as spoken by the caller vs entity as it reached the LLM.
- *Outbound:* entity the agent intended vs entity present in the text it sent
  to TTS.

**Gate:** entity recall is a hard gate in any transactional domain, above
aggregate WER. One misheard character in a confirmation code cascades into an
authentication failure and a dead call.

**Trap:** measuring only inbound. Outbound entity loss — the agent silently
dropping the last digit of a total — is rarer but far more expensive.

---

### V3 — Speech fidelity of generated audio

**Question:** does the audio the caller actually hears say what the agent meant
to say?

**Runs on:** the synthesized audio of agent turns containing critical entities,
scored against the text that was sent to the synthesizer.

**Scoring:** audio-LLM judge (a model that ingests audio directly, not a
transcribe-then-judge chain). Rubric in
[judge-rubrics.md](judge-rubrics.md#v3--speech-fidelity). Focus the judge on
entity-bearing spans, not overall pleasantness — that is V-adjacent TTS quality
(MOS), a different question.

**Gate:** near-zero tolerance on entity spans in transactional domains.

**Trap:** this eval is the one most in-house suites skip entirely, because
every text-level check passes. Transcribe-then-judge does not substitute: your
STT and the caller's ear fail differently, and a round trip through your own
transcriber can silently repair the very mangling you are hunting.

**Cheap substitute if no audio-LLM is available:** transcribe the generated
audio with a *different* vendor's STT than the one in your pipeline and diff
against the source text. Weaker, but it catches gross mangling and costs
almost nothing. Say which method produced the number.

---

### V4 — Turn latency budget with component attribution

**Question:** is the agent fast enough to feel like a conversation, and which
component is spending the budget?

**Runs on:** instrumented turns with per-stage timestamps.

**Scoring:** code. Two headline numbers plus attribution:
- **Time to first word (TTFW)** — call connect to first audio byte.
- **Turn latency** — end of user speech to start of agent audio. Report P50,
  P95, P99. Never report a mean; latency distributions have tails that a mean
  erases.
- **Attribution** — STT, LLM inference, TTS, network, turn detection. LLM
  inference typically dominates.

**Gate:** P95 turn latency against the use-case threshold. Alert on a P95 breach
sustained over a short window rather than on single-call spikes.

**Trap:** measuring server-side. That excludes network and turn detection, which
together are a large share of what the human actually waits through. Measure at
the far end of the audio path or state clearly that the number is a floor, not
the experience.

---

## Conversation tier

Requires simulated calls end to end. Run before a release.

### V5 — Turn-taking and barge-in

**Question:** does the agent speak at the right time?

**Runs on:** simulated conversations that deliberately include interruptions,
mid-sentence hesitations, slow speakers, and rapid-fire follow-ups.

**Scoring:** timing-derived signals plus a judge:
- **Barge-in recovery rate** — interruptions the agent yielded to and recovered
  from, over total interruptions.
- **Talk-over duration** — total ms of overlapping speech.
- **Dead air** — silence between end of user speech and agent onset, and the
  count of turns exceeding the threshold.
- **Judge** scores appropriateness where timing alone is ambiguous (rubric in
  [judge-rubrics.md](judge-rubrics.md#v5--turn-taking)).

**Gate:** barge-in recovery against the use-case threshold; talk-over near zero.

**Trap:** judging this from a transcript. Text carries no timestamps — overlap
and dead air are both completely invisible. If your harness only has
transcripts, this eval cannot run, and reporting it anyway is fabrication.

---

### V6 — Task completion against end-state

**Question:** did the call accomplish the thing?

**Runs on:** scenarios backed by a scenario database with a defined expected
end-state (booking exists, appointment moved, ticket created with these
fields).

**Scoring:** code, deterministic. Compare the database end-state after the
conversation against the expected end-state. Binary pass/fail per scenario.

**Gate:** task success rate against the use-case threshold.

**Trap:** letting an LLM judge decide whether the task was completed by reading
the transcript. An agent that says "you're all set!" without calling the tool
passes a transcript judge and fails a real customer. **If an outcome is
checkable in state, check it in state.** Judges are for things state cannot
express.

---

### V7 — Faithfulness to policy, inputs, and tool results

**Question:** was everything the agent said grounded in its instructions,
policies, the caller's own words, and what the tools actually returned?

**Runs on:** full transcripts paired with the tool-call log — the judge must see
both, or it cannot tell a grounded claim from a lucky guess.

**Scoring:** LLM judge. Flags fabrications, misrepresented policy, invented
availability, and claims unsupported by tool output. Rubric in
[judge-rubrics.md](judge-rubrics.md#v7--faithfulness).

**Gate:** hallucination rate against the use-case threshold — near zero in
clinical and financial domains.

**Trap:** running the judge on the transcript alone. Without tool logs it grades
plausibility, and a fluent fabrication is maximally plausible.

---

### V8 — Conciseness for spoken delivery

**Question:** is the response the right length for an ear rather than an eye?

**Runs on:** agent turns in completed conversations.

**Scoring:** LLM judge against a spoken-delivery rubric
([judge-rubrics.md](judge-rubrics.md#v8--conciseness)). Phone callers cannot
skim, re-read, or scroll back — a paragraph that reads fine is unusable aloud.

**Gate:** experience-axis threshold. Report alongside V6; the two move in
opposite directions and the pair is the actual finding.

**Trap:** optimizing this in isolation. Squeezing conciseness reliably costs
task completion. That is the accuracy/experience tradeoff, and the point of
measuring both is to choose it deliberately rather than discover it later.

---

### V9 — Safety, refusal, and PII under voice conditions

**Question:** do the guardrails survive contact with audio?

**Runs on:** adversarial scenarios delivered *as speech* — jailbreak attempts,
out-of-scope requests, requests for another caller's data, prompt injection read
aloud, plus the same set under noise.

**Scoring:** code where the outcome is checkable (was PII emitted, was the
refusal tool invoked) plus a judge for refusal quality. Track **hallucination
under noise** separately: responses unrelated to the audio input when the signal
degrades.

**Gate:** refusal rate and PII non-disclosure are hard gates. Compliance
obligations (HIPAA, PCI-DSS, GDPR) are pass/fail, not scored.

**Trap:** two of them, both severe.
1. **Judging safety without knowing the production refusal path.** If the agent
   refuses by invoking a tool rather than by emitting refusal language, a
   text-only judge scores every correct refusal as a failure — and every safety
   number you have ever reported is invalid. Verify what the judge can see
   against what production actually does before trusting a single run.
2. **Testing guardrails in text only.** Speech gets past filters that text does
   not, and noise is an attack surface.

---

## System tier

Slowest. Nightly or pre-launch.

### V10 — Consistency and reliability at k trials and load

**Question:** does it work *every* time, and does it still work under load?

**Runs on:** each scenario repeated k times (k=3 is a workable default), plus a
load profile at 2× expected peak concurrency.

**Scoring:** code.
- **pass@k** — at least one of k trials succeeded.
- **pass^k** — all k trials succeeded.
- **Under load:** latency distribution shift, error rate per component, and
  whether degradation is graceful (clean handoff to a human) or a hard failure.

**Gate:** **pass^k**, not pass@k. A large gap between them is the finding: it
means behavior is a coin flip that a single-run eval will happily report as a
pass.

**Trap:** unpinned temperature on the agent under test. An unpinned SUT makes
this eval measure sampling noise, and a "systematic regression" that appears and
vanishes across identical runs is far more often this harness gap than a real
behavior change. Pin `temperature=0` before any consistency claim.

---

## The eleventh thing: listen to calls

Automated scoring does not replace hearing 10-20 full conversations yourself
before a launch and after any significant change. Judges agree with each other
on things that are simply unpleasant to sit through. This tier has no gate and
no number — its output is the list of things you did not know to measure, which
becomes next quarter's eval cases.
