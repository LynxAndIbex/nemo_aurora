import pvporcupine
import sounddevice as sd
import numpy as np
import time
import os
import threading
import queue
import wave
import struct
import resampy

STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

class WakeWordEngine:
    def __init__(self, access_key=None, keyword_path="models/nemo_en_raspberry-pi_v4_0_0.ppn", threshold=0.5, input_sample_rate = 44100):
        
        self.access_key = access_key or os.getenv("PORCUPINE_KEY")
        if not self.access_key:
            raise ValueError("need access key")
        
        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keyword_paths=[keyword_path],
            sensitivities=[threshold]
        )
        
        self.input_sample_rate = input_sample_rate
        self.porcupine_sample_rate = self.porcupine.sample_rate


        self.detected = False
        self._thread = None
        self._q = queue.Queue()
        self._recording_audio = []
        self.filename = None
        self._stop_flag = threading.Event()
        self._resample_buffer = np.array([], dtype=np.int16)

    def _callback(self, indata, frames, time_info, status):
        """sounddevice callback - queues audio for processing"""
        if status:
            print(f"Audio callback status: {status}")


        self._recording_audio.append(indata.copy())
        
	#do resampling using resampy
        audio_float = indata[:, 0].astype(np.float32) / 32768.0
        resampled = resampy.resample(audio_float, self.input_sample_rate, self.porcupine_sample_rate)
        resampled_int16 = (resampled * 32767).astype(np.int16)

        self._resample_buffer = np.concatenate([self._resample_buffer, resampled_int16])

	#processing:
        while len(self._resample_buffer) >= self.porcupine.frame_length:
                frame = self._resample_buffer[:self.porcupine.frame_length]
                self._resample_buffer = self._resample_buffer[self.porcupine.frame_length:]
                self._q.put(frame)




    def _record_loop(self):
        """record and detect wake word"""
        self.detected = False
        self._recording_audio = []
        self._resample_buffer = np.array([], dtype=np.int16)
        self._stop_flag.clear()
        self.filename = os.path.join(STORAGE_DIR, f"recording_{int(time.time())}.wav")
        print("listening for wake word...")
        
        with sd.InputStream(
            channels=1,
            samplerate=self.input_sample_rate,
           # blocksize=self.porcupine.frame_length,
            callback=self._callback,
            dtype="int16"
        ):
            while not self.detected and not self._stop_flag.is_set():
                if not self._q.empty():
                    audio_frame = self._q.get()
                    pcm = list(audio_frame)
	                
                    keyword_index = self.porcupine.process(pcm)
                    if keyword_index >= 0:
                        print("wake word detected!")
                        self.detected = True
                else:
                    time.sleep(0.01)

        # Save recorded audio
        if self._recording_audio:
            frames_np = np.concatenate(self._recording_audio)
            
            with wave.open(self.filename, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2) 
                wf.setframerate(self.input_sample_rate) #saves at the 44100 kHz instead, better than sox
                wf.writeframes(frames_np.tobytes())
            
            print(f"Saved recording: {self.filename}")

    def start_recording(self):

        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._record_loop, daemon=True)
            self._thread.start()
        return {"status": "recording_started"}

    def stop_recording(self):
        self._stop_flag.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        return self.filename
    
    def __del__(self):
    
        if hasattr(self, 'porcupine'):
            self.porcupine.delete()


# Global instance for server
engine = WakeWordEngine(
    access_key=os.getenv("PORCUPINE_KEY"),  
    keyword_path="models/Hey-Nemo_en_raspberry-pi_v4_0_0.ppn", 
    threshold=0.3, #default is still 0.5
    input_sample_rate=44100 
)


def start_recording():
    return engine.start_recording()

def stop_recording():
    return engine.stop_recording()


if __name__ == "__main__":
    print("Starting wake word detection...")
    start_recording()

    #keeping main alive!
    try:
       while True:
          time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        stop_recording()


