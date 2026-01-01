import sounddevice as sd
import numpy as np
import soundfile as sf

#added imports:
from scipy.signal import resample_poly #imports resample to change freq.


#from scipy.io.wavfile import write
import os

#original sample rate line is below
#SAMPLE_RATE = 16000
#SAMPLE_RATE = 44100 
NATIVE_SAMPLE_RATE = 44100 #detected by headphones
TARGET_SAMPLE_RATE = 16000  #required by OWW


def record_clip(filename, duration=1.2):
    print(f"Recording: {filename}")
    print("Speak NOW...")
    #native sample rate instead
    audio = sd.rec(int(duration * NATIVE_SAMPLE_RATE), samplerate=NATIVE_SAMPLE_RATE, channels=1, dtype='float32')	
    sd.wait() #wait call
    #added this line vvvvv to initialize remaster
    audio = np.squeeze(audio)
    #remaster to OWW
    audio_16k = resample_poly(audio, TARGET_SAMPLE_RATE, NATIVE_SAMPLE_RATE)
    sf.write(filename, audio, TARGET_SAMPLE_RATE)
    print("Saved:", filename)

def record_batch(folder, phrase_name, count=15):
    os.makedirs(folder, exist_ok=True)
    for i in range(count):
        input(f"\nPress Enter to record sample {i+1}/{count} for '{phrase_name}'...")
        record_clip(os.path.join(folder, f"{phrase_name}_{i+1}.wav"))

if __name__ == "__main__":
    print("=== Wake Word Recording Tool ===")
    print("record wake word samples first.")

    record_batch("training_data/aurora", "aurora", count=20)

    print("\nNow recording NOT-aurora background/noise/random speech samples.")
    print("just talk randomly or be silent — doesn't matter.")

    record_batch("training_data/not_aurora", "noise", count=20)

    print("\ndataset is ready.")
