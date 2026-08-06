# Metric catalog and gates

Definitions, formulas, and published thresholds. Treat every number here as a
starting gate to be re-derived against your own traffic — they are industry
reference points, not laws. Where sources disagree the range is shown.

---

## Accuracy — hearing

| Metric | Formula | Reference targets | Catches |
|---|---|---|---|
| Word Error Rate (WER) | (S + D + I) / N | <5% enterprise · 5-10% good · 10-15% fair · >15% poor | Transcription errors cascading downstream |
| Character Error Rate (CER) | same, per character | Use for Mandarin, Japanese, Thai | Character-level entity damage |
| Sentence Error Rate (SER) | sentences with any error / total | Track alongside WER | Whole-utterance breakdowns |
| Entity recall | correct entities / total entities, per class | Hard gate in transactional domains | The failure WER averages away |
| Intent recognition accuracy | correct classifications / utterances | 95%+ production · 90-95% acceptable · <90% investigate | Goal misunderstood despite clean transcription |

**Noise degradation reference.** WER increase over quiet baseline: office +3-5,
café +10-15, street +15-20, vehicle +10-20, airport +20-25 points. Budget for
the environment your callers are actually in, and gate on that cell.

---

## Accuracy — doing

| Metric | Formula | Reference targets | Catches |
|---|---|---|---|
| Task success rate (TSR) | successful completions / total | >85% good · 75-85% warning · <75% critical | Goals unmet despite clean audio |
| First call resolution (FCR) | resolved on first contact / contacts | >75% excellent · 65-75% fair · <65% poor | Repeat contacts; verify over a 48-72h window |
| Containment rate | handled by AI / total calls | 40-60% month 1 · 60-75% month 3 · 75-85%+ month 6 | Unnecessary escalation; ramp, not a launch bar |
| Fallback rate | fallbacks / total interactions × 100 | Track trend, not an absolute | Repeated clarification requests |
| Hallucination rate | hallucinated responses / total | <1% good · 1-3% warning · >3% critical | Fabrication presented as fact |
| Hallucination under noise (HUN) | responses unrelated to audio input | <2% | Generation decoupled from the actual input |

A working definition of a hallucination at the transcription layer: five or
more consecutive insertions, substitutions, or deletions.

---

## Experience — timing

| Metric | Measured as | Reference targets |
|---|---|---|
| Time to first word (TTFW) | connect → first audio byte | <400ms good · 400-600ms warning · >800ms critical |
| Turn latency | end of user speech → agent audio onset | P95 <800ms good · 800-1500ms warning · >1500ms critical |
| End-to-end response | user request → TTS first byte | Industry median 1.4-1.7s; human expectation ~300ms |
| Real-time factor (RTF) | processing time / audio duration | <1.0 required; >1.0 cannot keep pace |
| Barge-in recovery | recovered / total interruptions | >90% good · 80-90% warning · <80% critical |

**Human baseline:** 200-300ms between turns in natural conversation. Everything
above is measured against a bar humans set, not one the industry currently
meets.

### Component latency budget

| Stage | Typical | Optimized |
|---|---|---|
| STT | 200-400ms | 100-200ms |
| LLM inference | 300-1000ms | 200-400ms |
| TTS | 150-500ms | 100-250ms |
| Network | 100-300ms | 50-150ms |
| Turn detection | 200-800ms | 200-400ms |
| Processing | 50-200ms | 20-50ms |

LLM inference is usually the largest single share. Turn detection is the most
commonly un-instrumented, and it sits directly in the perceived gap.

---

## Experience — speech quality

| Metric | Measured as | Reference targets |
|---|---|---|
| Mean Opinion Score (MOS) | human panel, 1-5, ITU-T P.800 | 4.3-4.5 excellent · 3.8-4.2 production · <3.5 rework |
| Predicted MOS | UTMOS, NISQA, MOSNet | Automated stand-in when panels are impractical |
| Mel-cepstral distortion (MCD) | spectral distance, real vs synthetic | Technical quality regression signal |
| Pronunciation error rate | domain-term mispronunciations / occurrences | Hard gate for clinical and legal vocabulary |

MOS answers "is this pleasant." It does **not** answer "did it say the right
thing" — that is V3 speech fidelity, and a high-MOS voice can confidently
mispronounce a confirmation code.

---

## Safety and compliance

| Metric | Target |
|---|---|
| Safety refusal rate | 99%+ |
| PII non-disclosure | 99%+ |
| Compliance adherence (SOC 2, HIPAA, PCI-DSS, GDPR/CCPA) | 100%, pass/fail |

Compliance is not scored on a curve. Either the obligation is met or the
deployment is not permissible.

---

## Reliability and cost

| Metric | Reference |
|---|---|
| Uptime | 99.9%+ |
| Load test | 2× expected peak concurrency |
| Audio packet loss | <1% |
| Cost per minute | $0.01-0.25 voice AI; human agent $5-8 per call |
| Cost per resolved interaction | The number that actually matters — pairs cost with containment |

Cost per minute flatters a system that fails to resolve. Always report cost per
*resolved* interaction next to it.

---

## Use-case gate tables

Thresholds diverge sharply by domain. Pick the row that matches, then tighten.

| Use case | Task completion | FCR | Containment | Turn latency P95 | WER | Other |
|---|---|---|---|---|---|---|
| Contact center support | >75% | >70% | >65% | <1000ms | <8% | — |
| Appointment scheduling | >90% | >85% | >80% | <800ms | <5% | — |
| Healthcare / clinical | >85% | — | — | <1200ms | <5% | Hallucination <0.5%, compliance >99% |
| E-commerce / order taking | >85% | — | >75% | <700ms | <6% | Upsell success >15% |

---

## Choosing a gate you can defend

1. **Segment before you gate.** A single aggregate number is the most common way
   a voice eval passes while the product fails. Gate the worst cell.
2. **Gate on the tail.** P95 and P99, never the mean, for anything time-based.
3. **Gate on pass^k, not pass@k,** for anything you claim is reliable.
4. **Separate hard gates from tracked metrics.** Entity recall, PII, refusal, and
   compliance are hard gates. MOS, conciseness, and containment are tracked and
   trended — gating a ramp metric like containment at launch guarantees a false
   failure in month one.
5. **Re-derive against your own traffic** once you have it. Published thresholds
   describe someone else's callers.
