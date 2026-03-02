import numpy as np
import subprocess
import json


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


def main():
    file_path = "./audio_samples/Deftones_My_Own_Summer.wav"
    #meta = get_metadata(file_path)

    #print(meta)

    file_pcm = decode_to_pcm(file_path)
    print(file_pcm)

if __name__ == "__main__":
    main()