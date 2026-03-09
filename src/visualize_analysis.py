#!/usr/bin/env python3
# gpt generated to understand better whats happening here
"""
Visualize the analyzer output: bass, mid, treble over time, plus beat markers.
Run from src/: python visualize_analysis.py
"""
import matplotlib.pyplot as plt

from utils import decode_to_pcm
from analyzer import analyze_track

FILE = "./audio_samples/Deftones_My_Own_Summer.wav"

# Show first N seconds (None = full track)
ZOOM_SECONDS = 60


def main():
    pcm = decode_to_pcm(FILE)
    result = analyze_track(pcm)

    times = result["times"]
    bass = result["bass"]
    mid = result["mid"]
    treble = result["treble"]
    beats = result["beats"]

    if ZOOM_SECONDS is not None:
        mask = times <= ZOOM_SECONDS
        times = times[mask]
        bass = bass[mask]
        mid = mid[mask]
        treble = treble[mask]
        beats = beats[beats <= ZOOM_SECONDS]

    fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=True)

    # Bass
    axes[0].fill_between(times, bass, alpha=0.5, color="#c0392b")
    axes[0].plot(times, bass, color="#c0392b", linewidth=1)
    axes[0].vlines(beats, 0, 1, colors="black", linewidth=0.4, alpha=0.3)
    axes[0].set_ylabel("Bass\n(20–250 Hz)")
    axes[0].set_ylim(0, 1.05)
    axes[0].set_title("Kick, bass guitar", fontsize=10, color="gray")

    # Mid
    axes[1].fill_between(times, mid, alpha=0.5, color="#2980b9")
    axes[1].plot(times, mid, color="#2980b9", linewidth=1)
    axes[1].vlines(beats, 0, 1, colors="black", linewidth=0.4, alpha=0.3)
    axes[1].set_ylabel("Mid\n(250–4000 Hz)")
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title("Vocals, guitars, snare", fontsize=10, color="gray")

    # Treble
    axes[2].fill_between(times, treble, alpha=0.5, color="#27ae60")
    axes[2].plot(times, treble, color="#27ae60", linewidth=1)
    axes[2].vlines(beats, 0, 1, colors="black", linewidth=0.4, alpha=0.3)
    axes[2].set_ylabel("Treble\n(4000–22050 Hz)")
    axes[2].set_ylim(0, 1.05)
    axes[2].set_title("Cymbals, hi-hats", fontsize=10, color="gray")

    axes[2].set_xlabel("Time (seconds)")
    fig.suptitle("Frequency bands over time — thin vertical lines = beats", fontsize=12)
    plt.tight_layout()

    plt.savefig("analysis_preview.png", dpi=120)
    print("Saved analysis_preview.png")
    plt.show()


if __name__ == "__main__":
    main()
