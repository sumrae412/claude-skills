---
name: video-edit
description: Use when the user wants QC/cut-list/pacing analysis of a screencast, tutorial, or narrated recording — generates a timestamped incident log of stumbles, repeated phrases, filler words ("um", "uh", "like"), dead air, inaudible audio, and visual issues (frozen view, stuck cursor, wrong tab, black frames, audio-visual mismatch) without modifying the source video. Triggers include "review this video for pacing", "check for stumbles", "generate a cut list", "analyze this screencast for errors", "find dead air in this recording", "where did I fumble in this take", "did the cursor get stuck", "is the wrong tab showing", "audio doesn't match visuals". Companion to automated-screencast-director — that skill records screencasts, this one QCs them.
---

# Screencast Pacing & Repetition Notator

Automated QC for screencasts and tutorials. Produces a chronological incident report so the user can prepare a cut list in their editor. Does not touch the source video.

## Tool stack

| Concern | Tool | Why |
|---------|------|-----|
| Video retrieval | `yt-dlp` | Handles Frame.io, YouTube, Vimeo, direct URLs, and cookie-auth'd private links |
| True media duration | `ffprobe` | Whisper's last-segment-end undercounts trailing silence |
| Silence detection | `ffmpeg silencedetect` filter | Reliable dB-threshold dead-air detection |
| Scene changes | `ffmpeg select='gt(scene,X)'` + `showinfo` | Frame-difference detection of view switches |
| Frozen view / stuck cursor | `ffmpeg freezedetect` | Stretches where nothing on screen changes |
| Black frames | `ffmpeg blackdetect` | Unintentional fades / dropped frames |
| Speech transcription | `openai-whisper` | Word-level timestamps + per-word confidence |
| Analysis | Python stdlib | Pattern matching for stumbles / loops / fillers / AV mismatches |

**Prereqs:**

- `brew install ffmpeg yt-dlp`
- `pip install openai-whisper`
- ~2 GB disk for the `base` Whisper model (auto-downloaded on first run)

## Input forms

Accept any of:

1. **Local path** to an `.mp4` / `.mov` / `.mkv` — skip the download step.
2. **Frame.io / YouTube / Vimeo URL** — hand off to `yt-dlp`.
3. **Private URL with a `cookies.txt`** file — pass `--cookies cookies.txt` to `yt-dlp`.

Ask the user which form they're providing if it's ambiguous. Never guess a URL.

## Workflow

1. **Acquire** — if the input is a URL, download with `yt-dlp -o <tmp>/qc_video.mp4 <url>`. If local, skip.
2. **True duration** — `ffprobe` the container. Used for silence-ratio math so we don't divide by Whisper's last-word timestamp.
3. **Silence scan** — `ffmpeg -i <video> -af silencedetect=noise=-35dB:d=2.0 -f null -` (stderr). Parse `silence_start: <t>` lines.
4. **Transcribe** — `whisper.load_model("base").transcribe(<video>, word_timestamps=True)`. Upgrade to `small` or `medium` if the user reports accuracy issues.
5. **Visual scan** (skippable with `--no-visual`) — three ffmpeg passes on the video track:
   - `select='gt(scene,0.4)',showinfo` — record every frame-difference spike as a scene change.
   - `freezedetect=n=0.003:d=2.0` — record stretches where the frame barely changes.
   - `blackdetect=d=0.5:pix_th=0.1` — record black-frame stretches.
6. **Detect incidents** (seven types, in one pass over the word stream plus correlation with visual events):
   - **FILLER** — word matches `{um, uh, ah, er, like, basically, so}` (casefolded, trimmed).
   - **INAUDIBLE** — Whisper emitted `[INAUDIBLE]` / `[MUSIC]` tokens, or per-word probability < 0.5.
   - **STUMBLE** — identical 3-word phrase repeats within a 15-second window; consecutive overlapping matches inside a 3-second dedup window collapse into a single incident with a span.
   - **LOOP** — identical 3-word phrase repeats after >60 seconds (user accidentally re-explaining a concept).
   - **FREEZE** — `freezedetect` stretch exceeds `--freeze-duration` (default 2.0 s): stuck cursor, non-responsive app, or the narrator is talking through a static view.
   - **BLACK_FRAME** — `blackdetect` stretch exceeds `--black-duration` (default 0.5 s): unintended fade or dropped frames.
   - **AV_MISMATCH** — heuristic correlation between narration and scene changes:
     - Narrator says a transition word (`now`, `next`, `click`, `open`, `let's`, `switch`, `navigate`, `go`, `here`, `this`, `that`, …) but no scene change lands within ±`--av-window` (default 3.0 s) → *expected* visual change didn't happen (wrong tab showing, cursor stuck, dialog not dismissed).
     - Scene change lands but no transition word within ±`--av-window` → *unexpected* visual change (accidental alt-tab, notification popup, view switch the narrator didn't flag).
7. **Merge + sort** silence, speech, and visual incidents into one chronological log.
8. **Report** — print the log plus summary stats (total incidents, WPM, silence ratio, scene-change count).

## Output format

```
=== QC NOTATION LOG ===
Source: <filename or URL>
Media duration: 312.4s

[ 00:12 ] STUMBLE: 'and then we run'
[ 00:45 ] AV_MISMATCH: Narration 'click' but no visual change within ±3s
[ 01:05 ] INAUDIBLE: (Unclear audio)
[ 01:20 ] FILLER: 'um'
[ 02:10 ] SILENCE: 2.5s dead air
[ 02:30 ] FREEZE: 4.2s of no visual change (stuck view / wrong tab?)
[ 03:15 ] BLACK_FRAME: 0.8s of black frames (unintentional fade?)
[ 04:50 ] LOOP: 'save the file' (previously at 01:30)

--- SUMMARY ---
Total Incidents: 8
Speaking Rate: 142 WPM
Silence Ratio: 8.2%
Scene Changes: 14
```

If the user asks for a cut list they can paste into an NLE, offer a machine-readable variant (`--json`) that dumps the same incidents as a JSON array.

## Detection thresholds

Defaults chosen for talking-head screencasts. Offer to adjust if the user reports noise:

| Type | Default | When to tune |
|------|---------|-------------|
| Silence noise floor | `-35 dB` | Lower to `-40 dB` for very quiet rooms; raise to `-30 dB` if background hiss triggers false positives |
| Silence min duration | `2.0 s` | Drop to `1.0 s` for tight tutorials; raise to `3.0 s` for deliberate pacing |
| Stumble window | `15 s` | Shorter = stricter (catches only immediate restarts); longer = catches hedge-then-retry |
| Stumble dedup window | `3.0 s` | Raise if multi-trigram restarts are still double-reporting; drop if separate nearby restarts are getting merged |
| Loop threshold | `60 s` | Raise if the video has intentional recaps |
| Whisper confidence | `0.5` | Lower to `0.3` if INAUDIBLE noise overwhelms real content |
| Scene threshold | `0.4` | Lower (e.g. `0.25`) to catch subtle view changes; raise (e.g. `0.6`) on fast-moving demo content |
| Freeze duration | `2.0 s` | Drop for stricter stuck-cursor detection; raise on content with intentional static diagrams |
| Freeze noise | `0.003` | Raise if subtle animations trigger false-negatives; lower for pure-static detection |
| Black duration | `0.5 s` | Raise if intentional fades shouldn't be flagged |
| AV window | `3.0 s` | Raise if narration runs ahead/behind visuals; drop for tight sync expectations |

## Canonical script

**Start from [scripts/screencast_qc.py](scripts/screencast_qc.py).** It's a CLI wrapper — pass a local path or URL; it handles download/analysis/cleanup and prints the report. Read it before adapting; most user requests are single-flag tweaks (change the silence threshold, swap Whisper model size, output JSON), not rewrites.

Invariants to preserve:

- Temp video file downloaded via `yt-dlp` is deleted in `finally:` — never leak gigabytes into `/tmp`.
- Media duration comes from `ffprobe`, not the last transcribed word. Whisper's segment end stops at the last recognized word, so trailing silence goes uncounted and silence-ratio math can exceed 100% without this.
- Silence parsing uses `re.findall(r"silence_start: (\-?\d+\.?\d*)", stderr)` — Whisper's own VAD is not a substitute (misses sub-model silences at segment boundaries). The negative-sign permission matters: ffmpeg reports small negative starts when the clip begins in silence.
- Silence ratio is capped at 100% (`min(ratio, 1.0)`) so reporting bugs are visible at read time rather than producing nonsense percentages.
- Stumble detection emits raw trigram hits to an intermediate list, then `_cluster_stumbles()` collapses overlapping hits within `--stumble-dedup` seconds into a single event. One sentence restart produces one incident, not N-2.
- Visual QC runs three separate ffmpeg passes (scene / freeze / black) rather than a combined filter graph. Cost is three reads of the video track; gain is reliable stderr parsing.
- AV-mismatch is a heuristic, not multimodal vision. It emits candidates for human review — expect false positives on lively narration (`now this is where it gets interesting` has no visual intent). Use `--av-window` and the transition-word list as escape hatches.
- Word-level loop detection walks the transcript once with a rolling window — not O(n²) nested comparison.
- Whisper model name is a CLI flag (`--model`), defaulted to `base`. Don't hardcode.
- Visual QC is on by default and opt-out via `--no-visual`. Making it opt-in would hide exactly the failure modes the user most often asks about.

## Limitations (be upfront with the user)

- **Visual QC is heuristic, not vision.** The skill does not see what's on screen. It detects *change* (scene cuts, freezes, black frames) and correlates change against narration cues — it won't read the text in a tab, identify a wrong icon, or tell you the cursor is in the wrong button. For those, a human has to scrub the flagged timestamps. For true multimodal review, pair this log with a vision-capable model looking at frames at those timestamps.
- **AV-mismatch false positives are common on lively narration.** "Now this is interesting" counts as a transition word but has no visual intent; tight demos with fast cutting produce many orphan scene changes. Treat AV_MISMATCH as candidate-for-review, not verdict. Tune `--av-window` up if your narration runs slightly ahead or behind the visual.
- **No editing.** Output is a report, not a cut. Users paste timestamps into DaVinci Resolve / Premiere / Final Cut themselves.
- **Whisper `base` has an accent/jargon floor.** If the user has a strong accent, heavy technical vocabulary, or poor mic quality, bump to `small` / `medium` — report quality is bounded by transcription quality.
- **Filler list is English.** Add language-specific fillers (`euh`, `eh`, `etto`, `neh`) before running on non-English content. Transition-word list (for AV_MISMATCH) is also English.
- **Stumble heuristic is lexical, not semantic.** "Save the file and save the state" is two different sentences that share a 3-word prefix — it will false-positive. Review the log, don't apply it blindly.
- **Freeze detection is track-wide.** If the app under demo legitimately holds still for 30 seconds (reading a long doc, waiting for a build), that will be flagged. The user decides whether each FREEZE is a problem or just the pacing.

## When to use which skill

- **Recording a new screencast** → use `automated-screencast-director` (script → automated narrated recording).
- **QC'ing an existing screencast** → this skill.
- **Cutting or re-editing the video itself** → not in scope for either; the user does that in their NLE using this skill's cut list as input.
