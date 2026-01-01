import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import queue
import os

SAMPLE_RATE = 16000
CLIP_DURATION = 1.2
THRESHOLD = 0.02
AUDIO_QUEUE = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print("Audio Status: ", status)
    AUDIO_QUEUE.put(indata.copy())

def detect_wake_word():
    while True:
        if not AUDIO_QUEUE.empty():
            audio_chunk = AUDIO_QUEUE.get()
            rms = np.sqrt(np.mean(audio_chunk**2))
            if rms > THRESHOLD:
                print("wake word detected!")
                record_memory()
def record_memory():
    os.makedirs("training_data/user_memory", exist_ok=True)
    filename = os.path.join("training_data/user_memory", "memory.wav")
    audio = sd.rec(int(CLIP_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    write(filename, SAMPLE_RATE, audio)
    print(f"Saved memory to {filename}")

print("Starting wake listener...")
with sd.InputStream(device=1, samplerate=SAMPLE_RATE, channels=1, callback=audio_callback):
    print("Listening for wake word...")
    detect_wake_word()

