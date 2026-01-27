from fastapi import FastAPI, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse
import uvicorn
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from wake_word import start_recording, stop_recording
from speech_to_text import transcribe_audio
from assistant import process_query
from text_to_speech import speak_text
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()
#new server using uvicorn


STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

app = FastAPI(title="Aurora Pi API")

@app.post("/record/start")
def start_recording_endpoint():
    start_recording()
    return {"status": "recording_started"}

@app.post("/record/stop")
def stop_recording_endpoint():
    filename = stop_recording()
    return {"status": "recording_stopped", "file": filename}

@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile):
   
    filepath = os.path.join(STORAGE_DIR, file.filename)
    with open(filepath, "wb") as f:
        while chunk := file.read(1024 * 1024): #1 megabyte
            f.write(chunk)
    transcript = await asyncio.get_event_loop().run_in_executor(executor, transcribe_audio, filepath)
    os.remove(filepath)
    return {"transcript": transcript}
@app.post("/ask")
async def ask_endpoint(text: str = Form(...)):
    response = await asyncio.get_event_loop().run_in_executor(executor, process_query, text)
    return {"answer": response}

@app.post("/speak")
async def speak_endpoint(background_tasks: BackgroundTasks, text: str = Form(...)):
    # Generate TTS audio and return file
    audio_file = speak_text(text, output_dir=STORAGE_DIR)
    background_tasks.add_task(os.remove, audio_file)
    return FileResponse(audio_file, media_type="audio/wav")

@app.get("/status")
def status():
    return {"status": "online"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
