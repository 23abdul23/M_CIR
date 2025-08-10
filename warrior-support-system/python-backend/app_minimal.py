"""
Minimal Python Backend for Warrior Support System
This version works with basic dependencies and gracefully handles missing packages
"""

import os
import tempfile
import json
import base64
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(title="Warrior Support System - Python Backend (Minimal)")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Feature availability flags
WHISPER_AVAILABLE = False
ANALYTICS_AVAILABLE = False
PLOTTING_AVAILABLE = False
IMAGE_PROCESSING_AVAILABLE = False

# Try to import optional dependencies
try:
    import whisper
    WHISPER_AVAILABLE = True
    print("✅ Whisper available for speech recognition")
except ImportError:
    print("⚠️ Whisper not available - speech recognition disabled")

try:
    import pandas as pd
    import numpy as np
    from joblib import load
    ANALYTICS_AVAILABLE = True
    print("✅ Analytics libraries available")
except ImportError:
    print("⚠️ Analytics libraries not available")

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTTING_AVAILABLE = True
    print("✅ Plotting libraries available")
except ImportError:
    print("⚠️ Plotting libraries not available")

try:
    import cv2
    from PIL import Image
    IMAGE_PROCESSING_AVAILABLE = True
    print("✅ Image processing libraries available")
except ImportError:
    print("⚠️ Image processing libraries not available")

@app.get("/")
async def root():
    return {
        "message": "Warrior Support System Python Backend (Minimal)",
        "features": {
            "whisper_available": WHISPER_AVAILABLE,
            "analytics_available": ANALYTICS_AVAILABLE,
            "plotting_available": PLOTTING_AVAILABLE,
            "image_processing_available": IMAGE_PROCESSING_AVAILABLE
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "python-backend-minimal",
        "version": "1.0.0",
        "features": {
            "whisper_available": WHISPER_AVAILABLE,
            "analytics_available": ANALYTICS_AVAILABLE,
            "plotting_available": PLOTTING_AVAILABLE,
            "image_processing_available": IMAGE_PROCESSING_AVAILABLE
        }
    }

@app.post("/api/translate")
async def translate_audio(audio: UploadFile = File(...)):
    if not WHISPER_AVAILABLE:
        return JSONResponse(
            content={"error": "Speech recognition not available - Whisper not installed"}, 
            status_code=503
        )
    
    # Implementation would go here when Whisper is available
    return JSONResponse(
        content={"message": "Speech recognition endpoint - implementation pending"}, 
        status_code=200
    )

@app.post("/api/analyze")
async def analyze_data(data: dict):
    if not ANALYTICS_AVAILABLE:
        return JSONResponse(
            content={"error": "Analytics not available - required libraries not installed"}, 
            status_code=503
        )
    
    return JSONResponse(
        content={"message": "Analytics endpoint - implementation pending"}, 
        status_code=200
    )

@app.get("/api/features")
async def get_available_features():
    return {
        "speech_recognition": WHISPER_AVAILABLE,
        "data_analytics": ANALYTICS_AVAILABLE,
        "visualization": PLOTTING_AVAILABLE,
        "image_processing": IMAGE_PROCESSING_AVAILABLE,
        "message": "Feature availability status"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
