
import time
from nemo import start_recording, stop_recording #from nemo.py, the wake word engine
from speech_to_text import transcribe_audio
from assistant import process_query
from text_to_speech import speak_text

def main():
    print("=" * 50) #top barrier
    print("Nemo Starting...") 
    print("=" * 50) 
    
    speak_text("Nemo is now active. Say Hey Nemo to talk to me.") 
    while True:
        try:
           #listen for wake word
           print("\n[Listening for my name...]")
           start_recording()
           while True:
               time.sleep(0.1)
               wake_audio = stop_recording()
               if wake_audio:
                   break

           print("[Wake word detected!]")
 
           print("[Listening for command...]")
           start_recording()
           time.sleep(4)
           audio_file = stop_recording()
           if not audio_file:
                print("No audio detected! Trying again...")
                continue


           print("[Transcribing...]")
           transcript = transcribe_audio(audio_file)
           transcript = transcript.lower().replace("hey nemo", "").replace("nemo", "").strip()
           print(f"[Cleaned transcript: {transcript}]")  # Debug line



           if not transcript or len(transcript.strip()) == 0:
                print("No speech detected, listening again...")
                speak_text("I didn't quite catch that. Can you repeat it please?")
                continue

           print(f"[You said: {transcript}]")
  
           print("[Processing...]") 
           response = process_query(transcript)
           print(f"[Nemo: {response}]")

        
           print("[Speaking response...]") 
           speak_text(response)
           from processor import create_memory_from_conversation

           try:
               create_memory_from_conversation(transcript, response, audio_file)
           except Exception as e:
               print(f"Failed to save memory: {e}")
          
           time.sleep(1) 

        except KeyboardInterrupt:
            print("\n\nShutting down...")
            speak_text("Shutting down. Goodbye!")
            break
       

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
