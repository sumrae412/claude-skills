# Extraction Guide — Phase A

How to read SME samples and fill the 9-axis profile template at [`profile-template.md`](profile-template.md).

## Minimum sample threshold

2 samples, ≥500 words total. If samples are below this, STOP and ask Summer for more rather than fabricating axes. State the gap concretely:

> "I have N words across M samples. Below the 500-word / 2-sample minimum — give me one more sample of roughly [target] words."

Fabricating axes from thin material produces a profile that sounds confident but isn't grounded in the SME's actual voice. The voice-fidelity pass in Phase B then gives false-positive signals. Don't.

## Reading the samples

1. **Read every sample end-to-end before filling any axis.** Skimming produces shallow profiles built on first-impressions, not patterns.
2. **Track concrete evidence for each axis as you read.** Every axis claim in the final profile must be backed by a quote or count from the samples.
3. **Note sample type.** If a sample is a transcript with filler words ("um", "you know"), decide whether to count or discount the filler when assessing rhythm. Default: discount filler, but note its presence under §2 if it's part of the SME's spoken voice.
4. **Watch for mode shifts.** SMEs often write differently in a script vs an email vs a slide. Note which mode each sample represents.

## Filling each axis

### §1 Register
Look for: technical depth (does this person derive equations or quote results?), jargon density (count per 100 words is fine), formality markers (contractions or not, "let us" vs "let's"). One paragraph, evidence-backed.

### §2 Sentence rhythm
Measure: average sentence length (a 50-sentence sample is enough), variance (short-punchy or long-flowing or both), spoken-vs-written cadence. Quote 2 short samples (5-10 sentences each) that capture the rhythm well. The quotes are the diff target — pick representative ones, not flashy ones.

### §3 Pronouns
Note the primary subject ("we" / "you" / "I" / passive) and when it shifts. Many instructors use "we" for derivations ("we differentiate the cost function") and "you" when handing off to the learner ("you'll notice that..."). Capture the pattern, not just the frequency.

### §4 Pedagogical moves
The hardest axis. Look for **sequences of 3-5 sentences that repeat across samples**:
- "Names the concept → one-sentence intuition → formal definition → one worked example → restates intuition"
- "Asks an apparent paradox → presents the obvious wrong answer → walks the correct reasoning"
- "States a result → walks the derivation → caveats edge cases"

The move sequence is what makes lessons feel like *this person taught them*. Capture 2-3 distinct moves.

### §5 Signature phrases
Look for openers, transitions, idioms appearing in ≥2 samples. Don't promote one-offs — a phrase that appears once isn't signature, it's just a sentence the person wrote. List 5-10 with frequency notes ("frequent" / "occasional" / "always when handing off to code").

### §6 Examples & analogies
Note the *category* the SME reaches for — math, real-world (which domain?), historical, code, personal anecdote — not specific examples. Andrew Ng reaches for housing-price prediction. Karpathy reaches for character-level text. The pattern is the signal.

### §7 Hedging patterns
Where do they soften ("you might think of it as...", "one way to see this is..."), where do they commit ("this is wrong", "this is the right way to think about it"). Pattern, not exhaustive list.

### §8 What they never do
Hard rules the voice-fidelity pass will grep against. Each line must be greppable — concrete tokens or short phrases, not vague style notes. Examples:
- `Never uses emoji`
- `Never opens a section with a question mark`
- `Never says "obviously" / "clearly" / "trivially"`

If you're inferring an anti-pattern from absence rather than seeing it explicitly violated, flag the inference to Summer.

### §9 Exemplar passages
2-3 quoted passages (100-300 words each) that are the north-star. Criteria: each passage should embody the rhythm, register, and at least one signature pedagogical move. Label each with a short tag ("intro to backprop", "Q&A response on overfitting").

## Profile echo step

Before saving, paste the filled profile back to Summer for correction. Specifically flag:

- **Any axis you couldn't fill confidently** — call it out, don't invent
- **Any anti-pattern you're inferring but aren't certain about** — Summer knows the SME, you don't
- **Any signature phrase that appeared only once** — don't promote one-offs
- **Sample-mode mismatch** — if all 3 samples were transcripts and she's editing a written script, flag the mode gap

## Saving

After Summer approves:

1. **Slugify the name:** lowercase, hyphens for spaces, no special chars. "Andrew Ng" → `andrew-ng.md`. "Andrew Ng (DLAI)" → `andrew-ng.md` (drop disambiguators unless needed).
2. **Check for collisions:** `ls ~/claude_code/agent-vault/sme-voices/` for an existing file at that slug. If one exists, ask Summer before overwriting — could be the same person (refresh) or a different person with the same first name (use `andrew-ng.md` vs `andrew-trask.md`).
3. **Write the file** to `~/claude_code/agent-vault/sme-voices/<slug>.md`.
4. **Commit in agent-vault:**

```bash
cd ~/claude_code/agent-vault && \
  git status && \
  git add sme-voices/<slug>.md && \
  git commit -m "Add SME voice profile: [Name]" && \
  env -u GH_TOKEN git push
```

Per the project CLAUDE.md gotchas: cross-repo `cd` chains need to be in a single bash call; `env -u GH_TOKEN` prevents the keyring-override 403 failure. If agent-vault is on a non-main branch with WIP, ask Summer how to handle the commit before pushing.

## Promoting an ad-hoc profile

If this build is being promoted from a Phase B ad-hoc session (where Summer asked for an SME edit without a saved profile and the skill extracted one on the fly):

1. The ad-hoc profile already exists in the session context. Re-read the corrected version Summer endorsed.
2. Fill any missing axes the ad-hoc skipped (Phase B often skips §9 exemplars to save time — fill them now).
3. Save as in the section above.
4. Note in the source list that the profile was promoted from an ad-hoc session on [date].
