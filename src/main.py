from analyzer import analyze_track, get_frame_index_for_time, is_beat_near
from utils import *

def main():
    file_path = "./audio_samples/Deftones_My_Own_Summer.wav"

    file_pcm = decode_to_pcm(file_path)
    print(file_pcm)

if __name__ == "__main__":
    main()