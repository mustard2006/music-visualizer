import numpy as np
import librosa

frame_len = 2048
hop_len = 512
BASS = (20, 250)
MID = (250, 4000)
TREBLE = (4000, 22050)

NUM_BARS = 256

def analyze_track(pcm: np.ndarray, sr: int = 44100) -> dict:
    n_fft = frame_len
    hop = hop_len
    freqs = np.fft.rfftfreq(n_fft, 1.0/sr)
    nyquist = sr/2

    n_frames = 1 + (len(pcm) - n_fft) // hop
    window = np.hanning(n_fft)

    # all frames at once: shape (n_frames, n_fft)
    frames = np.lib.stride_tricks.sliding_window_view(pcm, n_fft)[::hop][:n_frames]
    frames = frames * window

    # FFT all frames in one call: shape (n_frames, n_fft//2+1)
    spec_all = np.abs(np.fft.rfft(frames, axis=-1))

    # bin into NUM_BARS by reshape + mean — no Python loop
    bins_per_bar = spec_all.shape[1] // NUM_BARS
    usable = bins_per_bar * NUM_BARS
    spectrum = spec_all[:, :usable].reshape(n_frames, NUM_BARS, bins_per_bar).mean(axis=-1)

    # band energies — vectorized across all frames
    bass = np.sum(spec_all[:, (freqs >= BASS[0]) & (freqs < BASS[1])], axis=1)
    mid = np.sum(spec_all[:, (freqs >= MID[0]) & (freqs < MID[1])], axis=1)
    treble = np.sum(spec_all[:, (freqs >= TREBLE[0]) & (freqs < min(TREBLE[1], nyquist))], axis=1)

        
    # normalize to [0, 1] so the visualizer doesn't need to care about absolute amplitudes
    peak = np.max(spectrum)
    if peak > 0:
        spectrum /= peak

        
    # per frame timestamps (seconds)
    times = (np.arange(n_frames) * hop) / sr

    # beat times
    onset_env = librosa.onset.onset_strength(y=pcm, sr=sr, hop_length=hop)
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop)
    beats = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop)

    return {
        "times": times,
        "bass": bass,
        "mid": mid,
        "treble": treble,
        "spectrum": spectrum,
        "beats": beats
    }


def get_frame_index_for_time(t: float, times: np.ndarray) -> int:
    # floor search — gives us the last frame that started at or before t
    idx = np.searchsorted(times, t, side="right") - 1
    return max(0, idx)


def is_beat_near(t: float, beats: np.ndarray, window: float) -> bool:
    return np.any(np.abs(beats - t) <= window)