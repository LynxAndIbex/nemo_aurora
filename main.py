from nemo import start_recording, stop_recording
from speech_to_text import transcribe_audio
from chatbot import process_query
from text_to_speech import speak
import time

def main():
    print("Nemo starting...")

    while True:
        #wait for wakeword
        print("\n[Listening for wake word...]")
        start_recording()


        while True:
            time.sleep(0.1)
            wake_audio = stop_recording()
            if wake_audio:
                break

        

        print(f"[wake word detected! File: {audio_file}]")
        print("[listening for the command...]")
        #listening for the actual command
        start_recording()
        time.sleep(6) #6 seconds to speak command. TO INCREASE TIME, INCREASE THIS NUMBER
        command_audio = stop_recording()

        if not command_audio:
            print("no command recorded")
            continue




        #now transcribe
        user_text = transcribe_audio(audio_file)
        print("User said: ", user_text)
        if not user_text.strip():
            continue

        #feed the AI
        reply = process_query(user_text)
        print("Nemo: ", reply)

        #talk
        speak(reply)


if __name__ == "__main__":
    main()


