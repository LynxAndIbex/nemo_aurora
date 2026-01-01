import subprocess
import os

STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

def transcribe_audio(audio_file_path):
    
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    cmd = [
        "./whisper.cpp/build/bin/whisper-cli",                  
        "-m", "./whisper.cpp/models/ggml-base.en.bin",
        "-f", audio_file_path,
        "--no-timestamps",
        "--print-colors"
    ]

    try:
        result = subprocess.check_output(cmd) 
        transcript = result.decode("utf-8").strip()
        lines = [line.strip() for line in transcript.split('\n')
            if line.strip() and not line.strip().startswith('[')] 
        return ' '.join(lines) if lines else ""
        # return transcript
    except subprocess.CalledProcessError as e:
        print("Whisper.cpp failed:", e)
        return ""
