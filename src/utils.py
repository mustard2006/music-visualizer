import numpy as np
import librosa
import subprocess
import json

# Main methods
def decode_to_pcm(file):
    cmd = [
        "ffmpeg",
        "-i", file,
        "-f", "f32le",
        "-ac", "1",
        "-ar", "44100",
        "-"
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    audio_bytes = process.stdout.read()

    audio = np.frombuffer(audio_bytes, dtype=np.float32)

    return audio


# Secondary
def get_metadata(file):
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-select_streams", "a:0", 
        "-show_entries", "stream=duration,sample_rate,channels,channel_layout", 
        "-of", "json",
        file
    ]

    # ffprobe and capture stdout (capture_output=True)
    res = subprocess.run(cmd, capture_output=True, text=True)

    # parse json
    info = json.loads(res.stdout)
    stream = info['streams'][0]

    metadata = {
        "duration": float(stream["duration"]),
        "sample_rate": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "channel_layout": stream.get("channel_layout", None)
    }

    return metadata



# =============================================================================
# ANALYZER — Plain-language explanation
# =============================================================================
#
# 1. What you have: a long list of numbers (samples) — the "waveform".
#    Each number is how loud the air is at one instant. 44100 samples per second.
#
# 2. FFT (Fast Fourier Transform):
#    FFT answers: "Which PITCHES (frequencies) are in this chunk of sound?"
#    - Input: a short chunk of samples (e.g. 2048 samples ≈ 46 ms at 44.1 kHz).
#    - Output: for each frequency bin (e.g. 20 Hz, 40 Hz, 60 Hz, ... up to 22050 Hz),
#      how much of that pitch is present (magnitude).
#    So instead of "loudness over time" you get "how much bass vs mid vs high" in that chunk.
#
# 3. Per-frame:
#    We don't FFT the whole song at once. We cut the audio into overlapping WINDOWS
#    (frames). Each frame = one short chunk (e.g. 2048 samples). We move forward by
#    HOP_LEN (e.g. 512 samples) so frames overlap. So we get one "snapshot" of the
#    spectrum every ~11.6 ms. That's "per-frame": one set of numbers per time slice.
#
# 4. Band energies:
#    We don't care about every single frequency. We group them into three BANDS:
#    - BASS   (20–250 Hz):   kick, bass guitar, low rumble
#    - MID    (250–4000 Hz): vocals, snare, most instruments
#    - HIGH   (4000–22050 Hz): cymbals, hi-hat, brightness
#    For each frame we SUM the FFT magnitudes in each band. So per frame we get
#    three numbers: (bass_energy, mid_energy, high_energy). That's "band energies".
#
# 5. Why this matters for the visualizer:
#    At playback time t (e.g. 1.5 seconds), we look up the frame that contains t,
#    read its (bass, mid, high), and map those to colors (e.g. bass=red, mid=green,
#    high=blue, or mix them for one RGB). So the picture changes with the music.
#
# 6. Precompute:
#    We run FFT + band sums for EVERY frame once when the track loads, and save
#    the results. When the video is playing we only do a lookup (time → frame index
#    → bands), no FFT in the draw loop. That keeps the visualizer smooth.
#
# =============================================================================



# FFT frame settings
FRAME_LEN = 2048   # samples per window
HOP_LEN = 512     # step between windows

# Frequency bands in Hz (for 44.1 kHz, Nyquist = 22050)
BASS = (20, 250)
MID = (250, 4000)
HIGH = (4000, 22050)


#def beat_and_onset_times(audio: np.ndarray, sr: int):