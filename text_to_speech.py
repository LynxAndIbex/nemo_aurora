import subprocess

def speak(text):
    with open("output.txt", "w") as f:
        f.write(text)

    subprocess.run([
        "/usr/local/bin/piper/piper",
        "--model", "models/en_US-amy-medium.onnx",
        "--output_file", "output.wav"
    ], input=text.encode("utf-8"))

    subprocess.run(["aplay", "output.wav"])


def speak_text(text):
    """alias for speak() because it will break if i try to fix every instance """
    speak(text)
