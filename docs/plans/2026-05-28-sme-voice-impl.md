# `sme-voice` skill — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the `sme-voice` skill that captures another person's writing voice from samples (Phase A) and applies it when ghostwriting/editing in their voice (Phase B).

**Architecture:** Thin router `SKILL.md` + three lazy-loaded reference files (`profile-template.md`, `extraction-guide.md`, `application-guide.md`). Saved profiles live outside the repo in `~/claude_code/agent-vault/sme-voices/`. No code — pure markdown skill following the progressive-disclosure pattern from `defensive-ui-flows` and the design pattern from sibling `writing-voice`.

**Tech Stack:** Markdown only. Skill loaded by Claude Code via `Skill` tool or `/sme-voice` slash command (frontmatter `user-invocable: true`).

**Design doc:** [docs/plans/2026-05-28-sme-voice-design.md](2026-05-28-sme-voice-design.md)

**Validation approach:** No automated tests (markdown skill). Smoke-test post-build by running one real Phase A build (Summer provides 2 SME samples → skill produces profile) and one real Phase B apply (Summer corrects, saves, then asks for a short edit in that voice).

---

## Task 1: Scaffold skill directory and confirm agent-vault path exists

**Files:**
- Create: `sme-voice/` (directory)
- Create: `sme-voice/references/` (directory)
- Ensure: `~/claude_code/agent-vault/sme-voices/` exists with a `.gitkeep`

**Step 1:** Create the skill directory structure.

```bash
cd /Users/summerrae/claude_code/claude-skills
mkdir -p sme-voice/references
```

**Step 2:** Ensure the agent-vault profile directory exists with a placeholder so the dir is committed.

```bash
mkdir -p ~/claude_code/agent-vault/sme-voices
test -f ~/claude_code/agent-vault/sme-voices/.gitkeep || touch ~/claude_code/agent-vault/sme-voices/.gitkeep
ls -la ~/claude_code/agent-vault/sme-voices/
```

**Step 3:** Commit agent-vault placeholder separately (different repo).

```bash
cd ~/claude_code/agent-vault
git add sme-voices/.gitkeep
git diff --cached --stat
git commit -m "Add sme-voices/ directory for sme-voice skill saved profiles"
git push
```

Expected: one file added, push succeeds. If `gh auth` issues, `env -u GH_TOKEN gh ...` per CLAUDE.md gotcha.

---

## Task 2: Write `references/profile-template.md` (the blank 9-axis profile)

**Files:**
- Create: `sme-voice/references/profile-template.md`

**Step 1:** Write the template. It MUST be a fillable template the skill can copy as the starting point for any new profile.

```markdown
# Voice Profile: [SME Name]

> Built [DATE] from [N] samples totaling [WORDCOUNT] words. Source files / URLs listed at bottom.

## 1. Register

[Technical depth, jargon density, formality. One paragraph. Concrete — "uses calculus notation when explaining gradient descent but switches to plain English for intuition" beats "moderately technical".]

## 2. Sentence rhythm

[Average length, short-punchy vs long-flowing, lecture vs conversational. Quote 2 short samples that capture the rhythm.]

> "Sample 1 quoted verbatim."

> "Sample 2 quoted verbatim."

## 3. Pronouns

[Primary subject: "we" / "you" / "I" / passive. Note when they switch and why. E.g., "we" for derivations, "you" when handing off to the learner.]

## 4. Pedagogical moves

[How they introduce a concept, when they hedge, when they assert, how they hand off to an example. The *move sequence* is the load-bearing part. E.g., "Names the concept → gives one-sentence intuition → drops the formal definition → walks one example → restates intuition."]

## 5. Signature phrases / vocabulary

[Top 5-10 recurring openers, transitions, idioms with frequency notes.]

- "It turns out that..." (frequent — uses to introduce non-obvious results)
- "Let's take a look at..." (always when handing off to a code example)
- [etc.]

## 6. Examples & analogies

[The *kind* they reach for: math, real-world (which domain?), historical, code, personal anecdote. Not specific examples — the *category preference*.]

## 7. Hedging patterns

[Where they soften ("you might think of it as..."), where they commit ("this is wrong"). Pattern, not list.]

## 8. What they never do

[Explicit anti-patterns. Each line is a hard rule for the voice-fidelity pass to grep against.]

- Never uses emoji
- Never opens a section with a question
- Never says "obviously" / "clearly" / "trivially"
- [etc.]

## 9. Exemplar passages

[2-3 quoted samples (100-300 words each) that are the north-star for the voice. These are the diff target for the voice-fidelity pass.]

### Exemplar 1 — [short label, e.g. "intro to backprop"]

> [Verbatim passage]

### Exemplar 2 — [short label]

> [Verbatim passage]

---

## Sources

- [Path or URL] — [N words] — [brief description]
- [Path or URL] — [N words] — [brief description]
```

**Step 2:** Verify the template renders cleanly.

```bash
cat sme-voice/references/profile-template.md | head -20
```

**Step 3:** Commit.

```bash
git add sme-voice/references/profile-template.md
git commit -m "Add profile-template.md — blank 9-axis SME voice profile"
```

---

## Task 3: Write `references/extraction-guide.md` (Phase A guidance)

**Files:**
- Create: `sme-voice/references/extraction-guide.md`

**Step 1:** Write the guide. It walks the agent through: read all samples → fill each of the 9 axes with evidence → echo profile to Summer → save to agent-vault path → commit + push to agent-vault.

Sections to include:

```markdown
# Extraction Guide — Phase A

How to read SME samples and fill the 9-axis profile template.

## Minimum sample threshold

2 samples, ≥500 words total. If samples are below this, STOP and ask for more rather than fabricating axes. State the gap explicitly: "I have N words across M samples. Below the 500-word / 2-sample minimum — give me one more sample of roughly [target] words."

## Reading the samples

1. Read every sample end-to-end before filling any axis. Skimming produces shallow profiles.
2. Track concrete evidence for each axis as you read. Every axis claim in the final profile must be backed by a quote or count from the samples.
3. If a sample is a transcript with filler words, note that and decide whether to count or discount the filler when assessing rhythm.

## Filling each axis

[Per-axis guidance, ~1 paragraph each. The pedagogical-moves axis and the signature-phrases axis are the hardest — give explicit "look for sequences of 3-5 sentences that repeat across samples" instructions.]

## Profile echo step

Before saving, paste the filled profile in chat for Summer to correct. Specifically flag:
- Any axis you couldn't fill confidently (call it out, don't invent)
- Any anti-pattern you're inferring but aren't sure about
- Any signature phrase that appeared only once (don't promote one-offs)

## Saving

After Summer approves:

1. Slugify the name: lowercase, hyphens for spaces, no special chars. "Andrew Ng" → "andrew-ng.md".
2. Check `~/claude_code/agent-vault/sme-voices/` for an existing file at that slug. If one exists, ask before overwriting.
3. Write the file.
4. Commit in agent-vault: `cd ~/claude_code/agent-vault && git add sme-voices/<slug>.md && git commit -m "Add SME voice profile: [Name]" && git push`.

## Promoting an ad-hoc profile

If this build is being promoted from a Phase B ad-hoc session, the profile already exists in memory. Re-read the corrected version Summer endorsed, fill any missing axes, then save as above.
```

**Step 2:** Verify and commit.

```bash
wc -l sme-voice/references/extraction-guide.md
git add sme-voice/references/extraction-guide.md
git commit -m "Add extraction-guide.md — Phase A workflow for building SME profiles"
```

---

## Task 4: Write `references/application-guide.md` (Phase B guidance + voice-fidelity pass)

**Files:**
- Create: `sme-voice/references/application-guide.md`

**Step 1:** Write the guide. Cover: profile lookup, ad-hoc fallback, write the draft, run the 4-step voice-fidelity pass, output format.

Sections to include:

```markdown
# Application Guide — Phase B

How to apply a saved SME voice profile when ghostwriting or editing.

## Profile lookup

1. Slugify the SME name as in extraction-guide.md.
2. Read `~/claude_code/agent-vault/sme-voices/<slug>.md` end-to-end.
3. If the file doesn't exist:
   - Ad-hoc mode: extract voice from the current document Summer is editing using the 9-axis template, flag the missing profile to her, offer to promote to saved after one correction.
   - If there's no current document either, STOP and ask Summer to either point at samples or name an existing SME.

## Shared-communication-principles handling (INVERTED from writing-voice)

`writing-voice` always loads `shared/communication-principles.md`. **This skill does not.**

Rule:
- After reading the SME profile, check whether the SME's exemplar passages follow the shared principles (lead-with-the-conclusion, plain language, no hollow openers, etc.).
- If they do, you may load the shared file and apply it.
- If they don't — SME register wins. Flag the conflict to Summer in a one-line note ("note: this SME buries the lede / uses em-dashes heavily / opens with anecdote — honoring SME voice over shared principles"). Do not override the SME.

## Writing the draft

Standard Smart-Brevity-when-appropriate / SME-register-when-not. The profile is source of truth, not a checklist. Anti-overfitting reminder applies: three SME tendencies used naturally beats ten forced in.

## Voice-fidelity pass (before returning the draft)

Run all four checks. Output a 4-line note appended after the draft.

### 1. Rhythm match
Sentence-length distribution of the draft vs exemplar passages. If draft mean is materially shorter or longer (>30% deviation on average sentence length), flag.

### 2. Register match
Jargon density and formality markers. Flag drift in either direction.

### 3. Signature-phrase usage
List signature phrases used in the draft. Flag if zero used (sounds generic), flag if forced/overused (sounds like impersonation).

### 4. Never-does check (grep)
For each line in the profile's "What they never do" list, grep the draft. Any hit = BLOCK, do not return the draft until fixed.

### Output format

```
[Draft text]

---
**Voice-fidelity pass:**
- Rhythm: [PASS / FLAG — note]
- Register: [PASS / FLAG — note]
- Signature phrases used: [list, or "none — consider adding"]
- Never-does check: [PASS / BLOCK — what hit]
```

## Anti-overfitting close

Always end with the self-check:

> Does this sound like something [name] would actually write — or does it sound like AI trying very hard to imitate them?

If it feels forced, revise toward inhabitation, not imitation.

## Promoting an ad-hoc profile to saved

After Summer corrects an ad-hoc draft once, offer:

> "Want me to promote this ad-hoc profile to a saved one at `~/claude_code/agent-vault/sme-voices/<slug>.md`?"

If yes, hand off to extraction-guide.md's "Promoting an ad-hoc profile" section.
```

**Step 2:** Verify and commit.

```bash
wc -l sme-voice/references/application-guide.md
git add sme-voice/references/application-guide.md
git commit -m "Add application-guide.md — Phase B workflow + voice-fidelity pass"
```

---

## Task 5: Write `SKILL.md` (the router)

**Files:**
- Create: `sme-voice/SKILL.md`

**Step 1:** Write the SKILL.md. Mirror the structure of `writing-voice/SKILL.md` but adapted for two-phase + per-SME profile loading.

Required sections (in order):
1. Frontmatter (from design doc §Frontmatter — `user-invocable: true`)
2. Title
3. What this skill does (2-3 lines)
4. Phase detection — how to tell Phase A vs Phase B from Summer's request
5. Phase A path — point at `references/extraction-guide.md` and `references/profile-template.md`
6. Phase B path — point at `references/application-guide.md`
7. Boundary with `writing-voice` (link both directions)
8. Anti-overfitting reminder

Reference the design doc for content. Keep the router under ~80 lines — references hold the detail.

**Step 2:** Verify frontmatter validates (check `user-invocable: true` present, description ends with the Do-NOT-use clause).

```bash
head -25 sme-voice/SKILL.md
wc -l sme-voice/SKILL.md
```

Expected: SKILL.md ~60-80 lines, frontmatter clean.

**Step 3:** Commit.

```bash
git add sme-voice/SKILL.md
git commit -m "Add sme-voice SKILL.md router with Phase A/B routing"
```

---

## Task 6: Update `writing-voice/SKILL.md` to point at `sme-voice`

**Files:**
- Modify: `writing-voice/SKILL.md`

**Step 1:** Read the current Do-NOT-use section (lines 17-19).

```bash
sed -n '17,19p' writing-voice/SKILL.md
```

**Step 2:** Edit: change `"editing an SME's course content where you're preserving their voice"` to link explicitly to `sme-voice`:

```
Do NOT use this skill when: editing an SME's course content where
you're preserving their voice (use sme-voice instead), ghostwriting
entirely in someone else's voice (use sme-voice), running ToneGuard
analysis, or summarizing/analyzing documents.
```

**Step 3:** Verify diff.

```bash
git diff writing-voice/SKILL.md
```

Expected: 2-3 line change in the Do-NOT-use clause.

**Step 4:** Commit.

```bash
git add writing-voice/SKILL.md
git commit -m "Link writing-voice → sme-voice in Do-NOT-use boundary"
```

---

## Task 7: Run sibling cross-link pass

**Files:**
- Modify: `sme-voice/SKILL.md` (likely — add See-also)
- Modify: other skill SKILL.md files surfaced by the script (likely candidates: `writing-voice`, `prd`, `writing-workshop`, `synthesis-brief`)

**Step 1:** Run the neighbors script.

```bash
cd /Users/summerrae/claude_code/claude-skills
python3 scripts/find_skill_neighbors.py sme-voice/SKILL.md --top 5
```

**Step 2:** For each candidate with non-generic `shared_keywords` overlap (skip generic words like "skill", "user", "voice" only if it's the *only* overlap), add a bidirectional **See also** cross-reference.

**Step 3:** Verify and commit.

```bash
git diff --stat
git add -p   # review and stage each change
git commit -m "Add bidirectional See-also links between sme-voice and siblings"
```

If `candidate_count: 0`, skip silently.

---

## Task 8: Update MEMORY.md index entry

**Files:**
- Modify: `/Users/summerrae/.claude/projects/-Users-summerrae-claude-code-claude-skills/memory/MEMORY.md` (under "Process patterns" or a new "Skill design" section)

**Step 1:** Add a one-line index entry pointing to the design doc as a reference for future skill designs that need persistent per-subject profiles synced across machines.

Example line (keep <150 chars):

```markdown
- [Per-subject profile skill pattern](skill_pattern_per_subject_persistent_profiles.md) — sme-voice design: 9-axis template, agent-vault storage, ad-hoc → saved promotion
```

**Step 2:** Create the memory file at the path above with frontmatter and a 5-10 line summary linking to the design doc.

**Step 3:** Commit the memory file. (Note: memory dir is project-local; per CLAUDE.md "Project-memory files in ~/.claude/projects/*/memory/ are gitignored by policy" — this commit may be no-op. If `git add` reports the file ignored, accept it as local-only.)

---

## Task 9: Smoke test — Phase A build

**Inputs:** Summer provides 2 real SME samples (any one DLAI instructor she works with).

**Step 1:** Invoke `/sme-voice` (or trigger via "build a voice profile for [name]").

**Step 2:** Verify the skill:
- Reads `references/extraction-guide.md` and `references/profile-template.md`
- Asks for samples if not provided, OR processes pasted/file samples
- Fills all 9 axes with evidence-backed content
- Echoes profile for correction before saving
- Saves to `~/claude_code/agent-vault/sme-voices/<slug>.md`
- Commits + pushes the profile in agent-vault

**Step 3:** Summer corrects any axis that's off. Skill updates and re-saves.

**Expected result:** A saved profile at the agent-vault path that Summer would actually use.

---

## Task 10: Smoke test — Phase B apply

**Inputs:** Summer asks for a short edit in the SME's voice on a real script paragraph.

**Step 1:** Trigger via "edit this in [name]'s voice" or "/sme-voice apply [name]".

**Step 2:** Verify the skill:
- Reads the saved profile
- Reads `references/application-guide.md`
- Honors the shared-principles inversion rule (only loads shared principles if SME follows them; flags conflict otherwise)
- Writes the draft
- Runs the 4-step voice-fidelity pass
- Outputs draft + 4-line fidelity note

**Step 3:** Summer judges: does it sound like the SME?

**Expected result:** A draft Summer would actually ship after minor edits, with a fidelity note that's informative not theatrical.

---

## Task 11: Ship

**Step 1:** Sanity-check the worktree state.

```bash
git status
git log --oneline origin/main..HEAD
```

**Step 2:** Push and open PR.

```bash
env -u GH_TOKEN gh pr create --title "Add sme-voice skill — capture and apply SME writing voice" --body "$(cat <<'EOF'
## Summary

New `sme-voice` skill — captures another person's writing voice from samples (Phase A) and applies it when ghostwriting/editing in their voice (Phase B). Primarily for SME (subject-matter expert) scripts at DLAI.

Sibling to `writing-voice`; the two now explicitly link each other in their Do-NOT-use boundaries.

Saved profiles live in `~/claude_code/agent-vault/sme-voices/<slug>.md` (private repo, syncs across machines).

## Design

See [docs/plans/2026-05-28-sme-voice-design.md](docs/plans/2026-05-28-sme-voice-design.md) for full design.

## Test plan

- [ ] Phase A smoke test: build a profile from 2 real SME samples
- [ ] Summer reviews and corrects
- [ ] Profile saved + committed in agent-vault
- [ ] Phase B smoke test: apply profile to a short script edit
- [ ] Voice-fidelity pass output is informative not theatrical
- [ ] `writing-voice` boundary update points at sme-voice (and vice versa)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

**Step 3:** Run review pass per `claude-skills` shipping pattern (CodeRabbit if wired up, otherwise self-verify diff against this plan).

**Step 4:** Merge after review.

---

## Notes for the executor

- This is a markdown-only skill. No tests, no code. The validation is the two smoke tests (Tasks 9-10), which require Summer's input.
- The agent-vault profile dir commit (Task 1, Step 3) is a *separate repo* operation. Use `cd ~/claude_code/agent-vault && git ...` — see CLAUDE.md "Worktree-session OR cross-repo chained-cd gotcha". Prepend `cd` to every chain.
- Don't paraphrase the design doc's behavioral rules in SKILL.md prose — link to the references for detail. The router stays thin.
- The inverted shared-principles rule (Task 4) is the load-bearing behavioral difference from `writing-voice`. Make it visible in both the router and the application guide.
