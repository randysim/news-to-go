import os

os.environ["SUNO_OFFLOAD_CPU"] = "True"
os.environ["SUNO_USE_SMALL_MODELS"] = "True"

from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav

preload_models()

def generate_audio_file(text, name, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    audio = generate_audio(text, history_prompt="v2/en_speaker_6")
    write_wav(f"{directory}/{name}.wav", SAMPLE_RATE, audio)

if __name__ == "__main__":
    generate_audio_file("This is a test of the audio generation system.", "test_audio", "audio")
    