#!/usr/bin/env python3
"""Screencast QC: timestamped incident log for pacing, stumbles, fillers, dead air, and visual issues.

Usage:
    python screencast_qc.py <local-path-or-url> [options]

Examples:
    python screencast_qc.py demo.mp4
    python screencast_qc.py https://app.frame.io/... --cookies cookies.txt
    python screencast_qc.py demo.mp4 --model small --json > cutlist.json
    python screencast_qc.py demo.mp4 --no-visual   # audio-only, faster
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict

FILLER_WORDS = {"um", "uh", "ah", "er", "like", "basically", "so"}

# Words that signal the narrator is about to / just did transition to a new view.
# Used to cross-reference against scene changes in the video track.
TRANSITION_WORDS = {
    "now", "next", "let's", "lets", "switching", "switch", "move", "moving",
    "open", "click", "go", "navigate", "here", "this", "that",
}

DEFAULT_SILENCE_NOISE = "-35dB"
DEFAULT_SILENCE_DURATION = 2.0
DEFAULT_STUMBLE_WINDOW = 15.0
DEFAULT_LOOP_THRESHOLD = 60.0
DEFAULT_CONFIDENCE_FLOOR = 0.5
DEFAULT_STUMBLE_DEDUP = 3.0
DEFAULT_SCENE_THRESHOLD = 0.4
DEFAULT_FREEZE_DURATION = 2.0
DEFAULT_FREEZE_NOISE = 0.003
DEFAULT_BLACK_DURATION = 0.5
DEFAULT_AV_WINDOW = 3.0


def is_url(s: str) -> bool:
    return s.startswith(("http://", "https://"))


def download_video(url: str, out_path: str, cookies: str | None) -> None:
    cmd = ["yt-dlp", "-o", out_path, url]
    if cookies:
        cmd = ["yt-dlp", "--cookies", cookies, "-o", out_path, url]
    print(f"--- Downloading {url} ---", file=sys.stderr)
    subprocess.run(cmd, check=True)


def get_media_duration(video: str) -> float:
    """True media duration from ffprobe — not Whisper's last segment end, which
    stops at the last transcribed word and undercounts trailing silence."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", video,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def get_silence_timestamps(video: str, noise: str, duration: float) -> list[tuple[float, float]]:
    """Return list of (start, duration) for every silent stretch."""
    print("--- Scanning for silence ---", file=sys.stderr)
    cmd = [
        "ffmpeg", "-i", video,
        "-af", f"silencedetect=noise={noise}:d={duration}",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    starts = [float(m) for m in re.findall(r"silence_start: (\-?\d+\.?\d*)", result.stderr)]
    durs = [float(m) for m in re.findall(r"silence_duration: (\d+\.?\d*)", result.stderr)]
    ends = [float(m) for m in re.findall(r"silence_end: (\d+\.?\d*)", result.stderr)]
    if len(durs) < len(starts):
        durs = durs + [0.0] * (len(starts) - len(durs))
    return list(zip(starts, durs))


def get_visual_events(
    video: str,
    scene_threshold: float,
    freeze_duration: float,
    freeze_noise: float,
    black_duration: float,
    media_duration: float,
) -> dict:
    """Run three ffmpeg filters in separate passes: scene-change, freeze, black.

    Separate passes because each filter writes to stderr in its own format and
    mixing them requires a more complex filter graph that's harder to parse
    reliably. The cost is three reads of the video track — still cheap vs
    Whisper.
    """
    print("--- Scanning for visual events ---", file=sys.stderr)

    # Scene changes — showinfo prints pts_time for every selected frame.
    cmd = [
        "ffmpeg", "-i", video,
        "-vf", f"select='gt(scene,{scene_threshold})',showinfo",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    scene_times = [float(m) for m in re.findall(r"pts_time:(\d+\.?\d*)", result.stderr)]

    # Freeze frames — stretches where the frame doesn't change.
    cmd = [
        "ffmpeg", "-i", video,
        "-vf", f"freezedetect=n={freeze_noise}:d={freeze_duration}",
        "-map", "0:v:0", "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    freeze_starts = [float(m) for m in re.findall(r"freeze_start:\s*(\-?\d+\.?\d*)", result.stderr)]
    freeze_durs = [float(m) for m in re.findall(r"freeze_duration:\s*(\d+\.?\d*)", result.stderr)]
    # When a freeze spans to end-of-clip, ffmpeg emits freeze_start but no freeze_duration.
    # Infer the tail duration from media_duration so the report isn't misleading.
    while len(freeze_durs) < len(freeze_starts):
        tail_start = freeze_starts[len(freeze_durs)]
        freeze_durs.append(max(0.0, media_duration - tail_start))
    freezes = list(zip(freeze_starts, freeze_durs))

    # Black frames — unintentional fades / black cuts.
    cmd = [
        "ffmpeg", "-i", video,
        "-vf", f"blackdetect=d={black_duration}:pix_th=0.1",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    black_starts = [float(m) for m in re.findall(r"black_start:(\d+\.?\d*)", result.stderr)]
    black_durs = [float(m) for m in re.findall(r"black_duration:(\d+\.?\d*)", result.stderr)]
    if len(black_durs) < len(black_starts):
        black_durs = black_durs + [0.0] * (len(black_starts) - len(black_durs))
    blacks = list(zip(black_starts, black_durs))

    return {"scenes": scene_times, "freezes": freezes, "blacks": blacks}


def detect_av_mismatches(
    word_history: list[tuple[float, str]],
    scene_times: list[float],
    window: float,
) -> list[dict]:
    """Heuristic: flag narration/visual disagreement.

    Two directions:
      1. Narrator says a transition word ("now", "click", "let's go to") but
         no scene change happens within ±window seconds → expected visual
         change didn't occur (wrong tab showing, cursor stuck).
      2. Scene change happens but no transition word within ±window seconds
         → unexpected visual change (accidental tab switch, alt-tab, notification
         popup).

    This is a heuristic, not a multimodal understanding — it flags candidates
    for human review, nothing more. False positives are expected on lively
    narration ("now this is where it gets interesting" has no visual intent).
    """
    incidents: list[dict] = []
    transition_word_times = [t for t, w in word_history if w in TRANSITION_WORDS]

    for t, word in word_history:
        if word in TRANSITION_WORDS:
            if not any(abs(s - t) < window for s in scene_times):
                incidents.append({
                    "time": t,
                    "type": "AV_MISMATCH",
                    "detail": f"Narration '{word}' but no visual change within ±{window:.0f}s",
                })

    for s in scene_times:
        if not any(abs(t - s) < window for t in transition_word_times):
            incidents.append({
                "time": s,
                "type": "AV_MISMATCH",
                "detail": "Scene change with no narration cue (possible accidental view switch)",
            })

    return incidents


def format_timestamp(seconds: float) -> str:
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"


def _cluster_stumbles(raw_stumbles: list[dict], dedup_window: float) -> list[dict]:
    """Collapse runs of STUMBLEs within `dedup_window` seconds into one event.

    Root cause: a single sentence restart of N words triggers N-2 overlapping
    trigram matches (iteration-1 eval found 4 fires for one restart). Clustering
    keeps the first timestamp and merges trailing matches into a span in `detail`.
    """
    if not raw_stumbles:
        return []
    raw_stumbles = sorted(raw_stumbles, key=lambda x: x["time"])
    clustered: list[dict] = []
    current = dict(raw_stumbles[0])
    current["span_end"] = current["time"]
    current["phrases"] = [raw_stumbles[0]["detail"]]

    for inc in raw_stumbles[1:]:
        if inc["time"] - current["span_end"] <= dedup_window:
            current["span_end"] = inc["time"]
            current["phrases"].append(inc["detail"])
        else:
            clustered.append(_finalize_stumble(current))
            current = dict(inc)
            current["span_end"] = inc["time"]
            current["phrases"] = [inc["detail"]]
    clustered.append(_finalize_stumble(current))
    return clustered


def _finalize_stumble(cluster: dict) -> dict:
    start, end = cluster["time"], cluster["span_end"]
    if end - start < 0.01:
        detail = cluster["phrases"][0]
    else:
        detail = f"Repeated phrase span {format_timestamp(start)}–{format_timestamp(end)} ({cluster['phrases'][0]})"
    return {"time": start, "type": "STUMBLE", "detail": detail, "span_end": end}


def analyze_speech(
    video: str,
    model_name: str,
    stumble_window: float,
    loop_threshold: float,
    confidence_floor: float,
    stumble_dedup: float,
):
    """Transcribe and return (incidents, word_history, whisper_result)."""
    print(f"--- Transcribing with Whisper ({model_name}) ---", file=sys.stderr)
    import whisper  # deferred so --help works without whisper installed

    model = whisper.load_model(model_name)
    result = model.transcribe(video, word_timestamps=True)

    incidents: list[dict] = []
    raw_stumbles: list[dict] = []
    word_history: list[tuple[float, str]] = []

    for segment in result["segments"]:
        for w in segment.get("words", []):
            raw = w["word"]
            word = raw.lower().strip().strip(".,!?;:")
            start = w["start"]
            prob = w.get("probability", 1.0)
            word_history.append((start, word))

            if word in FILLER_WORDS:
                incidents.append({"time": start, "type": "FILLER", "detail": f"'{word}'"})

            if "inaudible" in word or "music" in word or prob < confidence_floor:
                incidents.append({"time": start, "type": "INAUDIBLE", "detail": "(Unclear audio)"})

    phrase_seen: dict[str, list[float]] = defaultdict(list)
    for i in range(len(word_history) - 2):
        phrase = f"{word_history[i][1]} {word_history[i+1][1]} {word_history[i+2][1]}"
        if all(p in FILLER_WORDS or p == "" for p in phrase.split()):
            continue
        t = word_history[i][0]
        for prior_t in phrase_seen[phrase]:
            gap = t - prior_t
            if 0 < gap < stumble_window:
                raw_stumbles.append({"time": t, "detail": f"'{phrase}'"})
                break
            elif gap > loop_threshold:
                incidents.append({
                    "time": t,
                    "type": "LOOP",
                    "detail": f"'{phrase}' (previously at {format_timestamp(prior_t)})",
                })
                break
        phrase_seen[phrase].append(t)

    incidents.extend(_cluster_stumbles(raw_stumbles, stumble_dedup))
    return incidents, word_history, result


def run_qc(args: argparse.Namespace) -> int:
    tmpdir = None
    cleanup_path = None
    try:
        if is_url(args.source):
            tmpdir = tempfile.mkdtemp(prefix="qc_")
            video_path = os.path.join(tmpdir, "qc_video.mp4")
            download_video(args.source, video_path, args.cookies)
            cleanup_path = video_path
        else:
            video_path = args.source
            if not os.path.exists(video_path):
                print(f"Error: file not found: {video_path}", file=sys.stderr)
                return 2

        media_duration = get_media_duration(video_path)

        silence_pairs = get_silence_timestamps(
            video_path, args.silence_noise, args.silence_duration
        )
        silence_incidents = [
            {"time": t, "type": "SILENCE", "detail": f"{d:.1f}s dead air"}
            for t, d in silence_pairs
        ]

        speech_incidents, word_history, transcript = analyze_speech(
            video_path,
            args.model,
            args.stumble_window,
            args.loop_threshold,
            args.confidence_floor,
            args.stumble_dedup,
        )

        visual_incidents: list[dict] = []
        scene_times: list[float] = []
        if not args.no_visual:
            visual = get_visual_events(
                video_path,
                args.scene_threshold,
                args.freeze_duration,
                args.freeze_noise,
                args.black_duration,
                media_duration,
            )
            scene_times = visual["scenes"]

            for t, d in visual["freezes"]:
                visual_incidents.append({
                    "time": t, "type": "FREEZE",
                    "detail": f"{d:.1f}s of no visual change (stuck view / wrong tab?)",
                })
            for t, d in visual["blacks"]:
                visual_incidents.append({
                    "time": t, "type": "BLACK_FRAME",
                    "detail": f"{d:.1f}s of black frames (unintentional fade?)",
                })
            visual_incidents.extend(
                detect_av_mismatches(word_history, scene_times, args.av_window)
            )

        all_incidents = sorted(
            silence_incidents + speech_incidents + visual_incidents,
            key=lambda x: x["time"],
        )

        if args.json:
            out = {
                "source": args.source,
                "media_duration_seconds": media_duration,
                "incidents": [
                    {
                        "time_seconds": i["time"],
                        "time_display": format_timestamp(i["time"]),
                        "type": i["type"],
                        "detail": i["detail"],
                        **({"span_end_seconds": i["span_end"]} if "span_end" in i else {}),
                    }
                    for i in all_incidents
                ],
                "scene_changes_seconds": scene_times,
            }
            print(json.dumps(out, indent=2))
            return 0

        print("\n=== QC NOTATION LOG ===")
        print(f"Source: {args.source}")
        print(f"Media duration: {media_duration:.1f}s\n")
        for item in all_incidents:
            print(f"[ {format_timestamp(item['time'])} ] {item['type']}: {item['detail']}")

        word_count = sum(len(seg["text"].split()) for seg in transcript["segments"])
        wpm = (word_count / media_duration) * 60 if media_duration > 0 else 0
        silence_total = sum(min(d, media_duration) for _, d in silence_pairs)
        silence_ratio = min(silence_total / media_duration, 1.0) * 100 if media_duration > 0 else 0

        print("\n--- SUMMARY ---")
        print(f"Total Incidents: {len(all_incidents)}")
        print(f"Speaking Rate: {int(wpm)} WPM")
        print(f"Silence Ratio: {silence_ratio:.1f}%")
        if not args.no_visual:
            print(f"Scene Changes: {len(scene_times)}")

        return 0
    finally:
        if cleanup_path and os.path.exists(cleanup_path):
            os.remove(cleanup_path)
        if tmpdir and os.path.exists(tmpdir):
            try:
                os.rmdir(tmpdir)
            except OSError:
                pass


def main() -> int:
    p = argparse.ArgumentParser(description="Screencast QC: timestamped incident log")
    p.add_argument("source", help="Local video path or URL (Frame.io, YouTube, Vimeo, direct)")
    p.add_argument("--cookies", help="cookies.txt path for private URLs (yt-dlp)")
    p.add_argument("--model", default="base",
                   help="Whisper model: tiny, base, small, medium, large (default: base)")

    audio = p.add_argument_group("audio thresholds")
    audio.add_argument("--silence-noise", default=DEFAULT_SILENCE_NOISE,
                       help=f"Silence noise floor (default: {DEFAULT_SILENCE_NOISE})")
    audio.add_argument("--silence-duration", type=float, default=DEFAULT_SILENCE_DURATION,
                       help=f"Min silence duration in seconds (default: {DEFAULT_SILENCE_DURATION})")
    audio.add_argument("--stumble-window", type=float, default=DEFAULT_STUMBLE_WINDOW,
                       help=f"Stumble repetition window seconds (default: {DEFAULT_STUMBLE_WINDOW})")
    audio.add_argument("--stumble-dedup", type=float, default=DEFAULT_STUMBLE_DEDUP,
                       help=f"Merge stumbles within N seconds into one event (default: {DEFAULT_STUMBLE_DEDUP})")
    audio.add_argument("--loop-threshold", type=float, default=DEFAULT_LOOP_THRESHOLD,
                       help=f"Loop repetition threshold seconds (default: {DEFAULT_LOOP_THRESHOLD})")
    audio.add_argument("--confidence-floor", type=float, default=DEFAULT_CONFIDENCE_FLOOR,
                       help=f"Whisper confidence floor for INAUDIBLE (default: {DEFAULT_CONFIDENCE_FLOOR})")

    visual = p.add_argument_group("visual thresholds")
    visual.add_argument("--no-visual", action="store_true",
                        help="Skip the visual QC pass (audio-only, faster)")
    visual.add_argument("--scene-threshold", type=float, default=DEFAULT_SCENE_THRESHOLD,
                        help=f"Scene-change sensitivity 0–1 (default: {DEFAULT_SCENE_THRESHOLD}; lower = more changes flagged)")
    visual.add_argument("--freeze-duration", type=float, default=DEFAULT_FREEZE_DURATION,
                        help=f"Min freeze-frame duration in seconds (default: {DEFAULT_FREEZE_DURATION})")
    visual.add_argument("--freeze-noise", type=float, default=DEFAULT_FREEZE_NOISE,
                        help=f"Freeze-detect noise tolerance (default: {DEFAULT_FREEZE_NOISE})")
    visual.add_argument("--black-duration", type=float, default=DEFAULT_BLACK_DURATION,
                        help=f"Min black-frame duration in seconds (default: {DEFAULT_BLACK_DURATION})")
    visual.add_argument("--av-window", type=float, default=DEFAULT_AV_WINDOW,
                        help=f"Audio/visual correlation window seconds (default: {DEFAULT_AV_WINDOW})")

    p.add_argument("--json", action="store_true", help="Emit incidents as JSON (for cut list import)")
    args = p.parse_args()
    return run_qc(args)


if __name__ == "__main__":
    sys.exit(main())
