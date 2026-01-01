"""this broke on the pi. to future rishabh: do not use this anymore!"""

import openwakeword
import sounddevice as sd
import numpy as np
import time
import os
import threading
import queue
import wave

STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

class WakeWordEngine:
    def __init__(self, model_path="models/aurora.tflite", threshold=0.85):
        self.model_path = model_path
        self.model = openwakeword.Model(wakeword_models=[model_path])
        self.threshold = threshold
        self.detected = False

        self.model_key = os.path.basename(model_path)  # "aurora.tflite"
        self._stream = None
        self._thread = None
        self._q = queue.Queue()
        self.filename = None

    def _callback(self, indata, frames, time_info, status):
        audio_frame = indata[:, 0]
        self._q.put(audio_frame)

        pred = self.model.predict(audio_frame)
        if pred.get(self.model_key, 0) > self.threshold:
            print("Wake word detected!")
            self.detected = True

    def _record_loop(self):
        """Record until stop_recording() is called"""
        self.detected = False
        self.filename = os.path.join(STORAGE_DIR, f"recording_{int(time.time())}.wav")

        frames = []

        with sd.InputStream(
            channels=1,
            samplerate=16000,
            callback=self._callback,
            dtype="float32"
        ):
            while not self.detected:
                time.sleep(0.01)

            # Collect any queued frames (optional, here we just save silence until detected)
            while not self._q.empty():
                frames.append(self._q.get())

        # Save recorded audio
        if frames:
            frames_np = np.concatenate(frames)
        else:
            frames_np = np.zeros(16000) 
        
        audio_int16 = np.int16(frames_np * 32767)

        with wave.open(self.filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_int16.tobytes())

    def start_recording(self):
        
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._record_loop)
            self._thread.start()
        return {"status": "recording_started"}

    def stop_recording(self):
       
        if self._thread is not None:
            self._thread.join()
        return self.filename


engine = WakeWordEngine()

def start_recording():
    return engine.start_recording()

def stop_recording():
    return engine.stop_recording()
