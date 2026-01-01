import time
from nemo import start_recording, stop_recording
from speech_to_text import transcribe_audio
from assistant import process_query
from text_to_speech import speak_text

def main():
    print("=" * 50)
    print("Aurora Voice Assistant Starting...")
    print("=" * 50)

    speak_text("Hi, I'm Nemo! Say Hey Nemo to talk to me.")
    while True:
        try:
            print("\n[Listening for wake word...]")
            start_recording()
            time.sleep(0.5)

            audio_file = stop_recording()
            if not audio_file:
                print("No audio recorded, trying again...")
                continue

            print(f"Wake word detected! Recorded: {audio_file}]")

            print("[Transcribing...]")
            transcript = transcribe_audio(audio_file)

            if not transcript or len(transcript.strip()) == 0:
                print("No speech detected, listening again...")
                speak("I didn't quite catch that. Can you please repeat that?")
                continue

            print(f"[You said: {transcript}]")

            print("[Processing...]")
            response = process_query(transcript)
            print(f"[Nemo: {response}]")

            print("[Speaking response...]")
            speak_text(response)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nShutting down Nemo...")
        speak_text("Goodbye!")
        break

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)


if __name__ == "__main__":
    main()
