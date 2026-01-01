from nemo import start_recording, stop_recording
import time

print("Say 'Hey Nemo' now...")
start_recording()

time.sleep(10)

audio_file = stop_recording()
print(f"Done! Audio file: {audio_file}")
print(f"Detected: {audio_file is not None}")
