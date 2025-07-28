import os
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import soundfile as sf
import whisper
from typing import Dict
import cv2
from fastapi.middleware.cors import CORSMiddleware
from models.enhanced_voice_processor import EnhancedVoiceProcessor
from models.facial_behavior_analyzer import EnhancedFacialBehaviorAnalyzer

from app_voice_enhanced import *
# from fucntions import * 

curr_path = os.getcwd()


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


SESSIONS: Dict[str, list] = {}  # Stores frame paths per session
DURATION = 0

@app.post("/api/stream_frame")
async def stream_frame(frame: UploadFile = File(...), session_id: str = Form(...), duration : int = Form(...)):
    global DURATION
    try:
        session_dir = f"sessions/{session_id}"
        os.makedirs(session_dir, exist_ok=True)
        file_path = os.path.join(session_dir, frame.filename)

        
        with open(file_path, "wb") as f:
            f.write(await frame.read())

        DURATION = duration

        if session_id not in SESSIONS:
            SESSIONS[session_id] = []
        SESSIONS[session_id].append(file_path)

        print(f"Received frame {len(SESSIONS[session_id])} for session {session_id}")

        
        
        return {"status": "frame received", "frame_count": len(SESSIONS[session_id])}
    
    except Exception as e:
        print(f"Error processing frame: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/final_score")
def get_final_score(session_id: str):
    global DURATION
    frame_paths = SESSIONS.get(session_id, [])
    
    if not frame_paths:
        return {"error": "No frames found for this session"}
    
    analyzer = EnhancedFacialBehaviorAnalyzer()

    emotion_stress_weights = {
        'happy': 0.1,       # Very low stress
        'neutral': 0.3,     # Low stress
        'surprise': 0.4,    # Mild stress
        'disgust': 0.6,     # Moderate stress
        'angry': 0.8,       # High stress
        'fear': 0.85,       # Very high stress
        'sad': 0.9          # Highest stress
    }
    frame_count = len(frame_paths)
    frame_stress_scores = []
    frame_emotions = []
    frame_confidences = []
    for f in frame_paths:
        frame = cv2.imread(f, cv2.IMREAD_COLOR)

        frame_result = analyzer.analyze_frame(frame)
        frame_stress = calculate_frame_stress_score(frame_result, emotion_stress_weights)
        frame_stress_scores.append(frame_stress)

        # Store frame data
        dominant_emotions = [e["dominant_emotion"] for e in frame_result.get("emotions", [])]
        frame_emotions.extend(dominant_emotions)

        avg_confidence = sum(e["confidence"] for e in frame_result.get("emotions", [])) / len(frame_result.get("emotions", []))
        frame_confidences.append(avg_confidence)
    
    base_path = os.path.join(curr_path, 'sessions')

    # Iterate through all subdirectories
    for subdir in os.listdir(base_path):
        subdir_path = os.path.join(base_path, subdir)
        
        if os.path.isdir(subdir_path):
            # Remove all contents of the subdirectory
            for item in os.listdir(subdir_path):
                item_path = os.path.join(subdir_path, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)  # remove file or symlink
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # remove directory
        
    final_results = calculate_final_stress_analysis(
        frame_stress_scores,
        frame_emotions,
        frame_confidences,
        frame_count,
        DURATION,
        'general_assessment'
    )
    
    return {
        "session_id": session_id,
        "frame_count": len(frame_paths),
        'results': final_results
    }
