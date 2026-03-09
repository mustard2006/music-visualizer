from utils import decode_to_pcm, get_metadata
from analyzer import analyze_track
from visualizer import run as run_visualizer

FILE = "./audio_samples/Deftones_My_Own_Summer.wav"


def main():
    pcm = decode_to_pcm(FILE)
    print("PCM shape:", pcm.shape, "samples")

    metadata = get_metadata(FILE)
    print("Metadata:", metadata)

    result = analyze_track(pcm)
    print(f"Frames: {len(result['times'])}, beats: {len(result['beats'])}")

    run_visualizer(FILE)


if __name__ == "__main__":
    main()