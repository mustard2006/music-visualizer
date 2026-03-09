import numpy as np
import librosa as lrs

frame_len = 2048
hop_len = 512
BASS = (20, 250)
MID = (250, 4000)
TREBLE = (4000, 22050)

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

        bass[i] = np.sum(spec[(freqs >= BASS[0]) & (freqs < BASS[1])])
        mid[i] = np.sum(spec[(freqs >= MID[0]) & (freqs < MID[1])])
        # The upper bound of treble is capped by the nyquist frequency (half the sample rate) since thats the max FFT can resolve
        treble[i] = np.sum(spec[(freqs >= TREBLE[0]) & (freqs < min(TREBLE[1], nyquist))])

        
        # Each band (bass, mid, treble) is normalized by making the largest value become 1 and all other values are scaled accordingly, 
        # so it kind of nests the loudness within each band, like Matryoshka dolls, proportional to their own peaks.
        for arr in (bass, mid, treble):
            peak = np.max(arr)
            if peak > 0:
                arr /= peak

        
        # per frame timestamps (seconds)
        times = (np.arange(n_frames) * hop) / sr


        # beat times
        onset_env = librosa.onset.onset_strenght(y=pcm, sr=sr, hop_length=hop)
        beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop)
        beats = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop)

        return {
            "times": times,
            "bass": bass,
            "mid": mid,
            "treble": treble,
            "beats": beats
        }