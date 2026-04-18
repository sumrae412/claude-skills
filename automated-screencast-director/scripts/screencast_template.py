"""Automated screencast template — macOS.

Records the screen with ffmpeg, drives the browser with Playwright (headed),
and narrates with the macOS `say` command. Narration is synchronized to
actions by blocking for an estimated duration per line.

Prereqs:
    brew install ffmpeg
    pip install playwright
    playwright install chromium

    System Settings -> Privacy & Security -> Screen Recording -> allow your terminal.

Run:
    python screencast_template.py

Output:
    ./screencast_output.mp4 (H.264 / yuv420p / 30fps, silent video).
    Narration plays live through the system speakers during recording but is
    NOT captured into the file by default. Mux it in afterward if needed.
"""

import os
import subprocess
import time

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "screencast_output.mp4"


def start_recording() -> subprocess.Popen:
    """Start ffmpeg recording the primary screen.

    Verify the screen device index on your machine with:
        ffmpeg -f avfoundation -list_devices true -i ""
    and adjust the `-i "1"` argument if needed.
    """
    cmd = [
        "ffmpeg", "-y",
        "-f", "avfoundation",
        "-framerate", "30",
        "-i", "1",
        "-pix_fmt", "yuv420p",
        OUTPUT_FILE,
    ]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def stop_recording(proc: subprocess.Popen) -> None:
    """Stop ffmpeg gracefully by sending 'q' to its stdin."""
    proc.communicate(input=b"q")
    proc.wait()


def speak(text: str) -> None:
    """Play narration via macOS `say` and block for an estimated duration.

    Estimate assumes ~180 wpm (3 words/sec) plus a 1s buffer. If narration runs
    past the next visual step, increase the buffer or split into multiple calls.
    """
    duration = len(text.split()) / 3.0 + 1.0
    subprocess.Popen(["say", text])
    time.sleep(duration)


def run_demo() -> None:
    print("Starting recording...")
    rec_proc = start_recording()
    time.sleep(2)  # let the recording settle before any action

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()

        # --- AUTOMATION ACTIONS START ---

        # [Claude inserts the parsed beats here: Playwright actions + speak() calls]

        # --- AUTOMATION ACTIONS END ---

        browser.close()

    print("Stopping recording...")
    stop_recording(rec_proc)
    print(f"Video saved to: {os.path.abspath(OUTPUT_FILE)}")


if __name__ == "__main__":
    run_demo()
