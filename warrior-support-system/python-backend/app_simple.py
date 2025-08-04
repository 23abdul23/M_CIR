"""
Simple FastAPI app to test basic functionality
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Warrior Support System - Python Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Warrior Support System Python Backend is running!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "python-backend",
        "version": "1.0.0"
    }

@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "Python backend API is working",
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
