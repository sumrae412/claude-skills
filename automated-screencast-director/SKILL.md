---
name: automated-screencast-director
description: Use when the user asks to record a demo/screencast/walkthrough/tutorial video with narrated browser actions on macOS. Converts a written script into a self-contained Python program that records the screen with ffmpeg, drives the browser with Playwright, and narrates with the macOS `say` command, synchronized end-to-end. Triggers include "make a screencast", "record a demo video", "automate a walkthrough", "narrated browser recording".
---

# Automated Screencast Director

You are a Senior Automation Engineer. Convert a user's narrative script into a self-contained Python program that records a narrated, automated browser screencast on macOS.

## Tool stack (macOS only)

| Concern | Tool |
|---------|------|
| Screen capture | `ffmpeg` with `avfoundation` input |
| Browser actions | Playwright (sync API, **headed** mode) |
| Narration | macOS `say` command |

**Prereqs the user must have installed:**

- `brew install ffmpeg`
- `pip install playwright && playwright install chromium`
- Screen Recording permission granted to the terminal running the script (System Settings → Privacy & Security → Screen Recording).

## Logic flow

1. Start `ffmpeg` as a background subprocess with `stdin=PIPE` so it can be stopped later.
2. Pause ~2s so the recording is live before any action.
3. Launch Playwright `chromium` in headed mode (`headless=False`, optionally `slow_mo=100` for visible pacing).
4. For each scripted beat: perform the Playwright action **and** call `speak(...)` with the line. The `speak` helper blocks for an estimated duration so the narration finishes before the next visual step.
5. Close the browser.
6. Send `q` to ffmpeg's stdin to stop it gracefully, wait for flush.
7. Print the absolute path of the saved `.mp4`.

## Canonical template

**Always start from the template at [scripts/screencast_template.py](scripts/screencast_template.py) — do not reinvent the scaffold.** Read it, then insert the user's actions into the marked block.

Key invariants to preserve when adapting:

- `start_recording()` returns a `subprocess.Popen` with `stdin=subprocess.PIPE`.
- `stop_recording(proc)` sends `b'q'` via `communicate()`, then `proc.wait()`.
- `speak(text)` estimates duration as `len(text.split()) / 3.0 + 1.0` seconds and blocks for that long so narration finishes before the next step.
- The ffmpeg command stays: `-f avfoundation -framerate 30 -i "1" -pix_fmt yuv420p` — device index `1` is the primary screen on most Macs, but tell the user how to verify (see below).
- Headed Chromium, `slow_mo=100` default (so viewers can follow the cursor).
- `yuv420p` pixel format — required for broad player compatibility (QuickTime, Chrome, Slack preview).

## Conversion procedure

When the user hands you a script:

1. **Parse the narrative into beats.** Each beat = one narration line + the visual action(s) it covers.
2. **For each beat, generate a pair of calls:**
   - The Playwright action(s): `page.goto(...)`, `page.get_by_role(...).click()`, `page.fill(...)`, `page.wait_for_load_state(...)`, etc.
   - A `speak(...)` call whose text is the narration for that beat.
3. **Order them for sync.** Put `speak(...)` *before* a long-running visual step if the narration should cover the wait; put it *after* if the narration describes what just happened. The `speak` duration estimate will naturally pace the next step.
4. **If a visual step is slower than the narration,** add an explicit `page.wait_for_*` or a short `time.sleep(...)` after `speak` so audio doesn't run out before the UI catches up.
5. **Never use `headless=True`.** A headless browser won't appear in the recording — the point of the screencast is seeing the browser.

### Template insertion point

In the template, insert your Playwright + `speak` sequence between the `--- AUTOMATION ACTIONS START ---` and `--- AUTOMATION ACTIONS END ---` markers. Example body:

```python
speak("First, we navigate to the landing page.")
page.goto("https://example.com")
page.wait_for_load_state("networkidle")

speak("Next, we click the Get Started button.")
page.get_by_role("link", name="Get Started").click()
page.wait_for_load_state("networkidle")

speak("Now we'll fill in the sign-up form with a test email.")
page.fill("input[name='email']", "demo@example.com")
page.fill("input[name='password']", "hunter2demo")

speak("And submit.")
page.get_by_role("button", name="Sign up").click()
page.wait_for_load_state("networkidle")
```

## Sync tuning

The narration duration estimate is `words / 3.0 + 1.0` seconds (≈180 wpm, which matches the default macOS `say` rate). This is approximate:

- **If audio runs past the next visual step:** the narration was longer than estimated — raise the constant buffer (e.g. `+ 1.5` or `+ 2.0`), or break the line into two `speak(...)` calls with actions in between.
- **If audio finishes before the visual step:** add `time.sleep(...)` or `page.wait_for_*` after `speak` so the screen isn't silent.
- **If you need more precision,** set a fixed rate via `subprocess.Popen(['say', '-r', '180', text])` and compute duration as `words / (rate/60) + buffer`.

## Verifying the ffmpeg screen device index

`-i "1"` is correct on most Macs but not universal. Tell the user how to verify before running:

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

The output lists video devices — find the one named `Capture screen 0` (or similar) and use its index. If the default `1` doesn't work, change the `-i "1"` argument in `start_recording()`.

## Output

- File: `screencast_output.mp4` in the script's working directory (configurable via the `OUTPUT_FILE` constant at the top of the script).
- Format: H.264 MP4, yuv420p, 30fps. Plays in QuickTime, Chrome, and uploads cleanly to Slack/Loom/YouTube.
- Audio: **not included** — macOS `say` plays through the system output, not captured by `avfoundation` video-only capture. If the user needs narration baked into the file, either (a) capture system audio with a tool like BlackHole/Loopback and add it as a second ffmpeg input, or (b) record `say` to an AIFF with `say -o narration.aiff ...` per beat and mux afterward. Call this out to the user up front — the default output is silent video with audio playing live during recording.

## When NOT to use this skill

- **Non-macOS hosts** — `avfoundation` and `say` are Mac-only. For Linux use `x11grab` + `espeak-ng`; for Windows use `gdigrab` + PowerShell `System.Speech`. Those require a different template.
- **Recording needs to include system audio** — see note above; this skill records silent video by default.
- **Multi-monitor screencasts where you need a specific display** — the user must pick the right device index first.
- **Just want to interact with a page** — use `playwright-test` or `website-tester` instead; no recording overhead.

## Deliverable

When the user supplies the script, produce a single file (e.g. `make_screencast.py`) built from the template with the parsed beats inserted. Tell the user:

1. Exact command to run: `python make_screencast.py`.
2. How to verify the screen device index if the output is wrong.
3. Where the output lands (`./screencast_output.mp4`).
4. That narration audio plays live but is **not** in the recording unless they mux it in separately.
