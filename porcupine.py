#official wake word detection. ignore all iterations of 'wake'.
import pvporcupine
import sounddevice as sd
from scipy.io.wavfile import write
from processor import create_memory_from_conversation
from datetime import time as datetime_time
import time
from assistant import process_query_api
from text_to_speech import speak_text
from speech_to_text import transcribe_audio
import queue
import os
import threading

SAMPLE_RATE = 16000 #what porcupine wants
CHUNK_SIZE = 512 #512 samples/frame

WAKEWORD_MODEL = "nemo_aurora/models/Hey-Nemo_en_raspberry-pi_v4_0_0.ppn"
USER_ID = "user_123" #sample user ID

AUDIO_QUEUE = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status: print(status)
    convert_to_16 = (indata[:,0] * 32767).astype('int16')
    AUDIO_QUEUE.put(convert_to_16)

#when using ctrl + f: wake, nemo, porcuipine, wakeword, wake word

def detect_wake_word():
    porcupine = pvporcupine.create(
        access_key=os.getenv("PORCUPINE_KEY"),
        keyword_paths=[WAKEWORD_MODEL]
    )

    with sd.InputStream(samplerate=SAMPLE_RATE, blocksize=CHUNK_SIZE, channels=1, callback=audio_callback):
        print("Listening for my name...")


        try:
            while True:

                if not AUDIO_QUEUE.empty():
                    audio_chunk = AUDIO_QUEUE.get()
                    result = porcupine.process(audio_chunk)

                    if result >= 0:
                        print("Nemo detected")
                        threading.Thread(target=handle_command).start() #anti-block
                else:
                    time.sleep(0.01)
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            porcupine.delete() #release resources


def handle_command():

    audio_file = record_audio(duration =6)
    transcript = transcribe_audio(audio_file)
    response = process_query_api(transcript, USER_ID)
    speak_text(response)
    create_memory_from_conversation(transcript, response, USER_ID, audio_file)

def record_audio(duration):
    os.makedirs("recordings", exist_ok=True)
    filename = os.path.join("recordings", f"command_{int(time.time())}.wav")
    print(f"Recording audio for {duration} seconds...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate = SAMPLE_RATE, channels=1, dtype = 'int16')
    sd.wait()
    write(filename, SAMPLE_RATE, audio)
    print(f"Saved audio to {filename}")
    return filename

if __name__ == "__main__":
    detect_wake_word()

