from analyzer import analyze_track, get_frame_index_for_time, is_beat_near
from utils import decode_to_pcm, get_metadata

SR = 44100

def main():
    # get the file
    file_path = "./audio_samples/Deftones_My_Own_Summer.wav"

    # decode to pcm
    pcm = decode_to_pcm(file_path)
    print("PCM shape:", pcm.shape, "samples")

    # get metadata (mostly optional)
    metadata = get_metadata(file_path)
    print("Metadata:", metadata)

    #
    

if __name__ == "__main__":
    main()