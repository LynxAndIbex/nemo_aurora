#this was the old wake word before wake.py

import time
import subprocess
import numpy
import soundfile as sf
import tflite_runtime.interpreter as tflite

interpreter = tflite.Interpreter(model_path="models./aurora.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def record_chunk(filename="chunk.wav", duration=1):
    subprocess.run([
        "rec", "-q", filename, "trim", "0", str(duration)
])

def predict_wakeword(audio_file):
    audio, sr = sf.read(audio_file)
    input_data = np.expand_dims(audio, axis=0).astype(np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    return output_data[0][0]


THRESHOLD = 0.7

while True:
    record_chunk("chunk.wav", duration=1)
    score = predict_wakeword("chunk.wav")
    if score > THRESHOLD:
        print("Nemo detected!")
    time.sleep(0.1)


