---
name: voice-agent-evals
description: Use when evaluating a voice or telephony agent — anything where speech is the input, the output, or both. Triggers on "eval my voice agent", "test our phone agent", "WER", "word error rate", "barge-in", "turn-taking", "time to first word", "latency budget", "STT accuracy", "TTS quality", "MOS", "speech fidelity", "voice AI benchmark", "call containment", "IVR replacement", or a request to score recorded or simulated calls. NOT for text-only chat agents (use evals), tuning one judge prompt's wording (use prompt-optimizer), or production LLM spend (use llm-cost-optimizer).
user-invocable: true
---

# Voice Agent Evals

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad
exploration, repeated file reads, multi-file scans, or heavy reference loading.
Load one reference file at a time; the suite is designed to be run tier by tier.

## Overview

**The transcript is not the artifact. The call is.**

Every failure mode unique to voice lives in the gap between what the transcript
says and what actually happened on the line: a confirmation code the caller
heard as "B" when the agent meant "D", a correct answer that arrived two
seconds late, a barge-in the agent talked straight through. Grade the
transcript and all three score clean.

This skill owns what is voice-specific. Generic eval machinery — golden
datasets, judge calibration, regression gates, production sampling — belongs to
the sibling skill and is not repeated here.

**REQUIRED BACKGROUND:** Use `evals` for the underlying eval design. In
particular [judge-calibration.md](../evals/references/judge-calibration.md)
before trusting any LLM judge in this suite, and
[evaluator-selection-and-rubrics.md](../evals/references/evaluator-selection-and-rubrics.md)
for choosing code-based vs model-based scoring per metric.

## The three things text evals never have to model

1. **The pipeline is a cascade and errors propagate.** STT → LLM → TTS. A
   flawless policy model behind a 15% WER transcriber fails calls, and a
   transcript-level eval credits the model for the failure. Score each stage
   AND the joint outcome, or you cannot tell which one to fix.
2. **Latency is a correctness property, not a performance property.** Humans
   leave 200-300ms between turns. Industry median voice-agent response is
   1.4-1.7s. A right answer delivered late is a conversational failure, and no
   accuracy metric will show it.
3. **The output is audio, so "what it said" ≠ "what it meant to say."** TTS
   mangles exactly the tokens that matter — confirmation codes, dollar amounts,
   flight numbers, drug names, addresses. This is the failure mode almost every
   in-house voice eval misses, because catching it requires listening to the
   generated audio, not reading the text that was sent to the synthesizer.

## Two axes, reported separately

Accuracy (did it do the job) and experience (was it bearable to talk to) trade
off against each other — agents that top task completion tend to score worse on
turn-taking and conciseness, and vice versa. **Never blend them into one
number.** A single composite score hides the tradeoff you are actually making.
Report an accuracy figure and an experience figure side by side, always.

## The suite

Ten evals in three tiers. Run the tier that matches what you are about to
change. Full definitions — inputs, scoring, gates, and the trap each one
exists to catch — are in [suite.md](references/suite.md).

| ID | Eval | Tier | Axis | Scoring |
|---|---|---|---|---|
| V1 | Transcription fidelity under a condition matrix | Component | Accuracy | Code (WER/CER) |
| V2 | Entity integrity, heard and spoken | Component | Accuracy | Code (exact/fuzzy) |
| V3 | Speech fidelity of generated audio | Component | Accuracy | Audio-LLM judge |
| V4 | Turn latency budget with component attribution | Component | Experience | Code (timing) |
| V5 | Turn-taking and barge-in | Conversation | Experience | Timing + judge |
| V6 | Task completion against end-state | Conversation | Accuracy | Code (deterministic) |
| V7 | Faithfulness to policy, inputs, and tool results | Conversation | Accuracy | LLM judge |
| V8 | Conciseness for spoken delivery | Conversation | Experience | LLM judge |
| V9 | Safety, refusal, and PII under voice conditions | Conversation | Accuracy | Code + judge |
| V10 | Consistency and reliability at k trials and load | System | Both | Code (pass@k / pass^k) |

**Tier discipline.** Component tier runs on clips and is cheap — run it on
every change. Conversation tier requires simulated calls and is expensive — run
it before a release. System tier is the slowest — run it nightly or pre-launch.

## Harness shape

The credible harness is **bot-to-bot over real audio**: a simulated caller with
a defined goal talks to your agent through the actual audio path, a tool
executor returns deterministic responses from a scenario database, a validator
discards malformed conversations before scoring, and the metrics engine reads
audio, transcripts, and tool-call logs together.

Text-injection shortcuts — feeding your agent typed user turns and grading the
reply — are a legitimate cheap tier for V6/V7/V8, but they cannot produce
V1-V5 or V10 at all. Say which tier a number came from whenever you report one.

Setup, artifact capture, simulated-caller design, and cost control are in
[harness-patterns.md](references/harness-patterns.md).

## Gates

Thresholds are use-case dependent, not universal — appointment scheduling and
clinical triage do not share a bar. The per-use-case threshold tables, the
component latency budget, and the full metric definitions are in
[metric-catalog.md](references/metric-catalog.md).

Judge rubrics for the five model-scored metrics (V3, V5, V7, V8, V9) are in
[judge-rubrics.md](references/judge-rubrics.md).

## Traps

The failure modes that make a voice eval report confident and wrong.

| Trap | Why it fools you | Fix |
|---|---|---|
| Reference transcript produced by your own STT | Scores the transcriber against itself, always near 0% WER | Reference must be independent: human-typed, or the source text you fed the TTS |
| Grading the transcript instead of the audio | TTS entity mangling is invisible — the text was correct | V3 listens to the generated audio |
| One averaged WER | Café and street conditions add 10-20 points; the mean hides the cliff | Segment by accent, noise, and domain vocabulary; gate on the worst segment |
| Latency measured server-side | Excludes network and turn-detection, the two largest human-perceived chunks | Measure end of user speech to first agent audio byte, at the far end |
| A cooperative simulated caller | Every metric looks good because nothing was ever hard | Multi-intent, mid-call goal changes, interruptions, and adversarial variants |
| Turn-taking judged from a transcript | Text has no timestamps; overlap and dead air are both invisible | Judge from timing data or audio, never text alone |
| Blended accuracy + experience score | Hides the documented tradeoff between them | Report both axes separately |
| pass@k reported without pass^k | pass@3 = 90% with pass^3 = 40% means you shipped a coin flip | Report both; gate on pass^k |
| Temperature unpinned on the agent under test | Measures sampling noise, not behavior | Pin `temperature=0` on the SUT before any consistency claim |

The last one recurs: a "systematic regression" that flips across identical runs
is an unpinned-temperature harness gap far more often than a real behavior
change.

## When NOT to use this skill

- Text-only chat or email agents → `evals`
- Improving one judge prompt's wording → `prompt-optimizer`
- Production model spend → `llm-cost-optimizer`
- ASR model selection with no agent attached → this suite's V1 alone is enough;
  the other nine evals assume an agent that acts

## Sources

Synthesized 2026-08-04 from:

- [Hamming — voice agent evaluation metrics guide](https://hamming.ai/resources/voice-agent-evaluation-metrics-guide) (threshold tables, latency budget, use-case benchmarks)
- [ServiceNow EVA](https://github.com/ServiceNow/eva) and [the EVA writeup](https://huggingface.co/blog/ServiceNow-AI/eva) (bot-to-bot architecture, EVA-A/EVA-X split, speech fidelity, pass@k vs pass^k)
- [ElevenLabs — six pillars](https://elevenlabs.io/blog/voice-agent-evaluation-framework-6-pillars-explained) (pillar taxonomy, fallback rate, load testing at 2x peak)
- [AssemblyAI — evals for voice AI](https://www.assemblyai.com/blog/evals-voice-ai) (WER's semantic blindness, entity recall, the vibe-check tier)
- [Langfuse — evaluating voice AI agents](https://langfuse.com/blog/2025-01-22-evaluating-voice-ai-agents) (tracing, single vs multi-turn)
- [Braintrust — voice agent cookbook](https://www.braintrust.dev/docs/cookbook/recipes/VoiceAgent) (direct-audio scoring, audio attachments in traces)
- [Voice AI evaluation infrastructure guide](https://www.linkedin.com/pulse/edition-58-voice-ai-evaluation-infrastructure-developers-guide-yoasc) (artifact capture, synthetic scenario tiers, tooling)
- [Ringg — evaluating AI voice agents](https://www.ringg.ai/blog/evaluating-ai-voice-agents) (code-switching, carrier/answer-rate effects, TCO)
