# play audio with miniaudio + draw reactive graphics with pyglet.

import time

import miniaudio
import pyglet
from pyglet import shapes

from analyzer import get_frame_index_for_time

WIDTH, HEIGHT = 1200, 600
NUM_BARS = 256
MARGIN = 40


def _lerp(a, b, t):
    return tuple(int(a[j] + (b[j] - a[j]) * t) for j in range(3))

def bar_color(i):
    # blue (treble) -> green (mid) -> red (bass) -> green (mid) -> blue (treble)
    half = NUM_BARS // 2
    t = i / (half - 1) if i < half else (NUM_BARS - 1 - i) / (half - 1)
    if t < 0.5:
        return _lerp((30, 140, 255), (50, 210, 80), t * 2)
    return _lerp((50, 210, 80), (255, 60, 30), (t - 0.5) * 2)


def run(file_path: str, result: dict):
    times = result["times"]
    spectrum = result["spectrum"]
    duration = float(times[-1])
    print(f"Ready. Duration: {duration:.1f}s")

    playing = False
    start_time = 0.0
    device = None

    def start_playback():
        nonlocal playing, start_time, device
        if playing:
            return
        playing = True
        start_time = time.time()
        stream = miniaudio.stream_file(file_path)
        device = miniaudio.PlaybackDevice()
        device.start(stream)

    def stop_playback():
        nonlocal playing, device
        if not playing:
            return
        playing = False
        if device is not None:
            device.stop()
            device = None

    window = pyglet.window.Window(WIDTH, HEIGHT, "Music Visualizer — Press SPACE to play")

    batch = pyglet.graphics.Batch()
    bars = [
        shapes.Rectangle(0, MARGIN, 1, 10, color=bar_color(i), batch=batch)
        for i in range(NUM_BARS)
    ]

    @window.event
    def on_key_press(symbol, _):
        if symbol == pyglet.window.key.SPACE:
            if not playing:
                start_playback()
                window.set_caption("Music Visualizer")
            else:
                stop_playback()
                window.set_caption("Music Visualizer — Press SPACE to play")
        elif symbol == pyglet.window.key.ESCAPE:
            window.close()

    @window.event
    def on_draw():
        window.clear()

        bar_w = (window.width - 2 * MARGIN) / NUM_BARS
        bar_h = window.height - 2 * MARGIN
        half = NUM_BARS // 2

        if playing:
            t = min(time.time() - start_time, duration)
            frame_idx = get_frame_index_for_time(t, times)
            frame = spectrum[frame_idx]
        else:
            frame = [0.05] * NUM_BARS

        for i, bar in enumerate(bars):
            freq_idx = (half - 1 - i) if i < half else (i - half)
            prev_height = getattr(bar, "prev_height", bar.height)
            target = 20 + frame[freq_idx] * bar_h
            bar.height = prev_height * 0.7 + target * 0.3
            bar.prev_height = bar.height
            bar.x = MARGIN + i * bar_w
            bar.width = max(1, bar_w - 1)

        batch.draw()

    pyglet.clock.schedule_interval(lambda dt: window.dispatch_event('on_draw'), 1/60)
    pyglet.app.run()
