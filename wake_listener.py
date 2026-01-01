#another broken wake word file :(
import numpy as np
import sounddevice as sd
from openwakeword.model import Model

#config stuff
SAMPLE_RATE = 16000 #required by oww
CHUNK_SIZE = 1280 #80 ms at 16kHz

model = Model(
    wakeword_models=["models/aurora.tflite"], 
    inference_framework="tflite"
)

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio = indata[:,0]
    prediction = model.predict(audio)
    score = prediction["hey_jarvis"]
    if score > 0.5:
        print("WAKE WORD DETECTED")

print("Listening for wakeword...")
with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels = 1,
    blocksize=CHUNK_SIZE,
    callback=audio_callback
):

    while True:
        sd.sleep(100)

