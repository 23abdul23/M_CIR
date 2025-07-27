import os
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import soundfile as sf
import whisper

from fastapi.middleware.cors import CORSMiddleware
from models.enhanced_voice_processor import EnhancedVoiceProcessor



app = FastAPI()
model = whisper.load_model("base")  # You can use 'small', 'medium', or 'large' for more accuracy but slower


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for all origins (not recommended for prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/translate")
async def translate_audio(audio: UploadFile = File(...)):

    # Save uploaded file to a temp file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmpfile:
            shutil.copyfileobj(audio.file, tmpfile)
            tmp_path = tmpfile.name

        processor = EnhancedVoiceProcessor()

        transcript = processor.transcribe_audio(tmp_path)

        print(transcript['transcription'])
        
        # # Transcribe audio using whisper
        # # Whisper will automatically convert using ffmpeg if needed
        # result = model.transcribe(tmp_path, language="en")
        # transcript = result.get("text", "").strip()

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return {"transcript": transcript['transcription']}
