import numpy as np
import librosa

frame_len = 2048
hop_len = 512
BASS = (20, 250)
MID = (250, 4000)
TREBLE = (4000, 22050)

NUM_BARS = 64

def analyze_track(pcm: np.ndarray, sr: int = 44100) -> dict:
    n_fft = frame_len
    hop = hop_len
    freqs = np.fft.rfftfreq(n_fft, 1.0/sr)
    nyquist = sr/2

    # Frame audio + FFT + Band energies
    n_frames = 1 + (len(pcm) - n_fft) // hop
    bass = np.zeros(n_frames)
    mid = np.zeros(n_frames)
    treble = np.zeros(n_frames)
    # to not get any loud bumps at the beginning or end of each frame that is procesed
    window = np.hanning(n_fft)

    # 
    spectrum = np.zeros((n_frames, NUM_BARS))

    # loop though frames
    for i in range(n_frames):
        start = i*hop # 0*hop, 1*hop, ...; starting position for new frame
        frame = pcm[start : start+n_fft] # get the pcm values for the frame [start to start+2048]

        if len(frame) < n_fft: # if frame length is less than n_fft(default frame length) happens at the end, break
            break

        # avoids sharp jumps at frame borders
        frame = frame * window

        # compute the magnitude of the FFT for the current windowed frame,
        # that gives amplitude for each frequency bin in this frame.
        spec = np.abs(np.fft.rfft(frame))

        bins_per_bar = len(spec) // NUM_BARS

        for b in range(NUM_BARS):
            start_bin = b * bins_per_bar
            end_bin = start_bin + bins_per_bar
            spectrum[i, b] = np.mean(spec[start_bin:end_bin])

        bass[i] = np.sum(spec[(freqs >= BASS[0]) & (freqs < BASS[1])])
        mid[i] = np.sum(spec[(freqs >= MID[0]) & (freqs < MID[1])])
        # The upper bound of treble is capped by the nyquist frequency (half the sample rate) since thats the max FFT can resolve
        treble[i] = np.sum(spec[(freqs >= TREBLE[0]) & (freqs < min(TREBLE[1], nyquist))])

        
    # Each band (bass, mid, treble) is normalized by making the largest value become 1 and all other values are scaled accordingly, 
    # so it kind of nests the loudness within each band, like Matryoshka dolls, proportional to their own peaks.
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


# return the index of the frame whose time is closest to t without exceeding it.
def get_frame_index_for_time(t: float, times: np.ndarray) -> int:

    # searchsorted returns the index where t should be inserted to maintain order
    idx = np.searchsorted(times, t, side="right") - 1
    
    if idx < 0:
        idx = 0
    return idx


# check if any beat falls within window seconds of t
def is_beat_near(t: float, beats: np.ndarray, window: float) -> bool:
    """
    t (float) - time (in seconds) to check around.
    beats (np array) - array of beat times (in seconds).
    window (float) - time window (in seconds) within which to check for a nearby beat.

    Returns True if there is at least one beat within [t - window, t + window]
    """
    return np.any(np.abs(beats - t) <= window)