# Official wake word detection
import pvporcupine
import sounddevice as sd
from scipy.io.wavfile import write
from processor import create_memory_from_conversation
import time
from assistant import process_query_api
from text_to_speech import speak_text
from speech_to_text import transcribe_audio
import queue
import os
import threading

SAMPLE_RATE = 16000  # what porcupine wants
CHUNK_SIZE = 512  # 512 samples/frame

WAKEWORD_MODEL = "C:\\Projects\\nemo_aurora\\models\\Hey-Nemo_en_raspberry-pi_v4_0_0.ppn"
USER_ID = "user_123"  # sample user ID

AUDIO_QUEUE = queue.Queue()
is_processing = threading.Lock()  # Prevent multiple simultaneous commands

def audio_callback(indata, frames, cb_time, status):
    """Callback for audio input stream"""
    if status:
        print(f"Audio callback status: {status}")
    convert_to_16 = (indata[:, 0] * 32767).astype('int16')
    AUDIO_QUEUE.put(convert_to_16)

def detect_wake_word():
    """Main wake word detection loop"""
    porcupine = None
    stream = None
    
    try:
        porcupine = pvporcupine.create(
            access_key=os.getenv("PORCUPINE_KEY"),
            keyword_paths=[WAKEWORD_MODEL]
        )
        
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE, 
            blocksize=CHUNK_SIZE, 
            channels=1, 
            callback=audio_callback
        )
        
        stream.start()
        print("Listening for my name...")
        
        while True:
            try:
                # Use blocking get with timeout instead of checking empty()
                audio_chunk = AUDIO_QUEUE.get(timeout=0.1)
                result = porcupine.process(audio_chunk)
                
                if result >= 0:
                    print("Nemo detected!")
                    # Only start new command if not already processing
                    if is_processing.acquire(blocking=False):
                        threading.Thread(target=handle_command, daemon=True).start()
                    else:
                        print("Already processing a command, ignoring...")
                        
            except queue.Empty:
                continue  # No audio data available, continue listening
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error in wake word detection: {e}")
    finally:
        # Clean up resources
        if stream is not None:
            stream.stop()
            stream.close()
        if porcupine is not None:
            porcupine.delete()
        print("Resources cleaned up")

def handle_command():
    """Process voice command"""
    try:
        audio_file = record_audio(duration=6)
        transcript = transcribe_audio(audio_file)
        print(f"Transcribed: {transcript}")
        
        response = process_query_api(transcript, USER_ID)
        print(f"Response: {response}")
        
        speak_text(response)
        create_memory_from_conversation(transcript, response, USER_ID, audio_file)
        
    except Exception as e:
        print(f"Error handling command: {e}")
    finally:
        is_processing.release()  # Always release the lock

def record_audio(duration):
    """Record audio for specified duration"""
    os.makedirs("recordings", exist_ok=True)
    filename = os.path.join("recordings", f"command_{int(time.time())}.wav")
    print(f"Recording audio for {duration} seconds...")
    
    audio = sd.rec(
        int(duration * SAMPLE_RATE), 
        samplerate=SAMPLE_RATE, 
        channels=1, 
        dtype='int16'
    )
    sd.wait()
    write(filename, SAMPLE_RATE, audio)
    print(f"Saved audio to {filename}")
    return filename

if __name__ == "__main__":
    detect_wake_word()

