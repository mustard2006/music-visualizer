# play audio with miniaudio + draw reactive graphics with pyglet.

import time

import miniaudio
import pyglet
from pyglet import shapes

from utils import decode_to_pcm
from analyzer import analyze_track, get_frame_index_for_time, is_beat_near

# window size
WIDTH, HEIGHT = 1200, 600
BASE_RADIUS = 80
BASS_SCALE = 120
BEAT_WINDOW = 0.08
BEAT_FLASH_DECAY = 0.92

# bar layout 64 bars, margin so they dont touch the edges
NUM_BARS = 64
BAR_WIDTH = (WIDTH // NUM_BARS)
MARGIN = 40


def run(file_path: str):
    # load the song and analyze it (bass, mid, treble, spectrum, beats)
    print("Loading and analyzing...")
    pcm = decode_to_pcm(file_path)
    result = analyze_track(pcm)
    times = result["times"]
    bass = result["bass"]
    mid = result["mid"]
    treble = result["treble"]
    spectrum = result["spectrum"]
    beats = result["beats"]
    duration = float(times[-1])
    print(f"Ready. Duration: {duration:.1f}s, beats: {len(beats)}")

    # playback state
    playing = False
    start_time = 0.0
    beat_flash = 0.0

    def start_playback():
        nonlocal playing, start_time
        if playing:
            return
        playing = True
        start_time = time.time()
        # start audio playback
        stream = miniaudio.stream_file(file_path)
        device = miniaudio.PlaybackDevice()
        device.start(stream)

    def stop_playback():
        nonlocal playing
        if not playing:
            return
        playing = False
        # stop the audio device
        try:
            if device is not None:
                device.stop()
                device = None
        except Exception as e:
            print(f"Warning: Failed to stop playback: {e}")

    # create window and bars
    window = pyglet.window.Window(WIDTH, HEIGHT, "Music Visualizer")

    bars = []
    for i in range(NUM_BARS):
        bar = shapes.Rectangle(
            MARGIN+i*BAR_WIDTH,
            MARGIN,
            BAR_WIDTH-2,
            10,
            color=(100, 200, 255)
        )
        bars.append(bar)

    @window.event
    def on_key_press(symbol, _):
        if symbol == pyglet.window.key.SPACE:
            if not playing:
                start_playback()
            else:
                stop_playback()
        elif symbol == pyglet.window.key.ESCAPE:
            window.close()

    @window.event
    def on_draw():
        nonlocal beat_flash
        window.clear()
        # current playback time in seconds
        t = time.time() - start_time if playing else -1.0

        if not playing or t < 0:
            # idle screen
            pyglet.text.Label(
                "Press SPACE to play",
                font_size=24,
                x=WIDTH // 2,
                y=HEIGHT // 2,
                anchor_x="center",
                anchor_y="center",
            ).draw()
            return

        t = min(t, duration)
        frame_idx = get_frame_index_for_time(t, times)
        bass_val = float(bass[frame_idx])
        mid_val = float(mid[frame_idx])
        treble_val = float(treble[frame_idx])
        on_beat = is_beat_near(t, beats, BEAT_WINDOW)

        # update bar heights from spectrum (each bar = one frequency bin)
        for i, bar in enumerate(bars):
            frame_idx = get_frame_index_for_time(t, times)
            value = spectrum[frame_idx][i]
            bar.height = min(HEIGHT - 2*MARGIN, 20 + value * 400)

        if on_beat:
            beat_flash = 1.0
        else:
            beat_flash *= BEAT_FLASH_DECAY

        # render
        for bar in bars:
            bar.draw()

    pyglet.app.run()
