#!/usr/bin/env python3
"""
Enhanced GPU-Powered Voice Processing for Army Mental Health Assessment
Supports Hinglish (Hindi-English mixed) voice-to-text conversion using Whisper
Transcribes Hindi speech to English transliteration (e.g., "mai acha hu")
"""

import logging
import numpy as np
import tempfile
import os
from typing import Dict, Optional, Tuple
import threading
import queue
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import GPU-accelerated libraries
try:
    import torch
    import whisper
    GPU_AVAILABLE = torch.cuda.is_available()
    logger.info(f"🚀 GPU Available: {GPU_AVAILABLE}")
    if GPU_AVAILABLE:
        logger.info(f"🎮 GPU Device: {torch.cuda.get_device_name(0)}")
except ImportError:
    GPU_AVAILABLE = False
    logger.warning("⚠️ PyTorch/Whisper not available. Install with: pip install torch whisper")

try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logger.warning("⚠️ Audio libraries not available. Install with: pip install sounddevice soundfile")

class EnhancedVoiceProcessor:
    """
    Enhanced voice processor with GPU acceleration and Hinglish support
    """
    
    def __init__(self):
        """Initialize the enhanced voice processor"""
        self.whisper_model = None
        self.is_initialized = False
        self.device = "cuda" if GPU_AVAILABLE else "cpu"
        self.recording = False
        self.audio_queue = queue.Queue()
        
        # Audio settings
        self.sample_rate = 16000  # Whisper's preferred sample rate
        self.channels = 1
        self.dtype = np.float32
        
        # Initialize components
        self._initialize_whisper()
        
    def _initialize_whisper(self):
        """Initialize Whisper model with GPU support"""
        try:
            if not GPU_AVAILABLE:
                logger.warning("🔄 GPU not available, using CPU for Whisper")
                # Use smaller model for CPU
                model_size = "base"
            else:
                logger.info("🚀 Initializing Whisper with GPU acceleration")
                # Use larger model for GPU
                model_size = "medium"  # Good balance of speed and accuracy
            
            # Load Whisper model with explicit GPU device
            if self.device == "cuda":
                self.whisper_model = whisper.load_model(model_size, device="cuda")
                logger.info(f"✅ Whisper model '{model_size}' loaded on GPU (CUDA)")
            else:
                self.whisper_model = whisper.load_model(model_size, device="cpu")
                logger.info(f"✅ Whisper model '{model_size}' loaded on CPU")

            # Verify GPU usage
            if self.device == "cuda":
                import torch
                if torch.cuda.is_available():
                    gpu_memory = torch.cuda.memory_allocated(0) / 1024**2
                    logger.info(f"🎮 GPU Memory after Whisper load: {gpu_memory:.1f}MB")
            
            self.is_initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Whisper: {e}")
            self.is_initialized = False
    
    def start_recording(self) -> bool:
        """Start recording audio from microphone"""
        if not AUDIO_AVAILABLE:
            logger.error("❌ Audio libraries not available")
            return False
        
        try:
            self.recording = True
            self.audio_queue = queue.Queue()
            
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            logger.info("🎤 Recording started...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start recording: {e}")
            self.recording = False
            return False
    
    def stop_recording(self) -> Optional[np.ndarray]:
        """Stop recording and return audio data"""
        if not self.recording:
            return None
        
        try:
            self.recording = False
            
            # Wait for recording thread to finish
            if hasattr(self, 'recording_thread'):
                self.recording_thread.join(timeout=2.0)
            
            # Collect all audio data
            audio_data = []
            while not self.audio_queue.empty():
                try:
                    chunk = self.audio_queue.get_nowait()
                    audio_data.append(chunk)
                except queue.Empty:
                    break
            
            if audio_data:
                # Concatenate all chunks
                full_audio = np.concatenate(audio_data, axis=0)
                logger.info(f"🎵 Recording stopped. Audio length: {len(full_audio)/self.sample_rate:.2f} seconds")
                return full_audio
            else:
                logger.warning("⚠️ No audio data recorded")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error stopping recording: {e}")
            return None
    
    def _record_audio(self):
        """Internal method to record audio in background thread"""
        try:
            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                if self.recording:
                    self.audio_queue.put(indata.copy().flatten())
            
            # Start recording stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                callback=audio_callback,
                blocksize=1024
            ):
                while self.recording:
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"❌ Recording thread error: {e}")
            self.recording = False
    
    def transcribe_audio(self, temp_path, language_hint: str = "hi") -> Dict:
        """
        Transcribe audio to text with Hinglish support
        
        Args:
            audio_data: Audio data as numpy array
            language_hint: Language hint ("hi" for Hindi/Hinglish, "en" for English)
            
        Returns:
            Dictionary with transcription results
        """
        if not self.is_initialized:
            return {"error": "Voice processor not initialized"}
        
        try:
            # # Save audio to temporary file
            # with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            #     sf.write(temp_file.name, audio_data, self.sample_rate)
            #     temp_path = temp_file.name
            
            # Transcribe with Whisper
            logger.info("🔄 Transcribing audio with Whisper...")
            
            # Force Hindi language for Hinglish transcription
            result = self.whisper_model.transcribe(
                temp_path,
                language="hi",  # Force Hindi for better Hinglish support
                task="transcribe",  # Always transcribe (not translate)
                fp16=GPU_AVAILABLE,  # Use FP16 for GPU acceleration
                verbose=False,
                word_timestamps=False,  # Disable word timestamps for faster processing
                condition_on_previous_text=False  # Disable context for more accurate short audio
            )
            
            # Don't delete the file here - let the caller handle cleanup
            # os.unlink(temp_path)
            
            # Extract transcription
            transcribed_text = result.get("text", "").strip()
            detected_language = result.get("language", "unknown")
            
            # Post-process for Hinglish
            processed_text = self._process_hinglish_text(transcribed_text, detected_language)
            
            logger.info(f"✅ Transcription completed: '{processed_text[:50]}...'")
            
            return {
                "transcription": processed_text,
                "original_text": transcribed_text,
                "detected_language": detected_language,
                "confidence": result.get("segments", [{}])[0].get("avg_logprob", 0) if result.get("segments") else 0,
                "processing_time": result.get("processing_time", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            return {"error": str(e)}
    
    def _process_hinglish_text(self, text: str, detected_language: str) -> str:
        """
        Process text for Hinglish support - convert Hindi to English transliteration
        
        Args:
            text: Original transcribed text
            detected_language: Detected language from Whisper
            
        Returns:
            Processed text in English transliteration
        """
        try:
            # If already in English or mixed, return as is
            if detected_language == "en":
                return text
            
            # For Hindi text, Whisper often provides good transliteration
            # Additional processing can be added here for better results
            
            # Basic cleanup and formatting
            processed = text.lower().strip()
            
            # Common Hindi-English word mappings for better context
            hinglish_mappings = {
                "मैं": "mai",
                "तुम": "tum", 
                "आप": "aap",
                "हाँ": "haan",
                "नहीं": "nahi",
                "अच्छा": "acha",
                "बुरा": "bura",
                "कैसे": "kaise",
                "क्या": "kya",
                "कहाँ": "kahan",
                "कब": "kab",
                "क्यों": "kyon"
            }
            
            # Apply mappings if needed (Whisper usually handles this well)
            for hindi, english in hinglish_mappings.items():
                processed = processed.replace(hindi, english)
            
            return processed
            
        except Exception as e:
            logger.warning(f"⚠️ Text processing failed: {e}")
            return text
    
    def transcribe_file(self, file_path: str, language_hint: str = "hi") -> Dict:
        """
        Transcribe audio file to text
        
        Args:
            file_path: Path to audio file
            language_hint: Language hint for transcription
            
        Returns:
            Dictionary with transcription results
        """
        if not self.is_initialized:
            return {"error": "Voice processor not initialized"}
        
        try:
            # Load audio file
            audio_data, sample_rate = sf.read(file_path)
            
            # Resample if needed
            if sample_rate != self.sample_rate:
                # Simple resampling (for production, use librosa for better quality)
                audio_data = np.interp(
                    np.linspace(0, len(audio_data), int(len(audio_data) * self.sample_rate / sample_rate)),
                    np.arange(len(audio_data)),
                    audio_data
                )
            
            return self.transcribe_audio(audio_data, language_hint)
            
        except Exception as e:
            logger.error(f"❌ File transcription failed: {e}")
            return {"error": str(e)}
    
    def get_available_microphones(self) -> list:
        """Get list of available microphone devices"""
        if not AUDIO_AVAILABLE:
            return []
        
        try:
            devices = sd.query_devices()
            microphones = []
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    microphones.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': device['default_samplerate']
                    })
            
            return microphones
            
        except Exception as e:
            logger.error(f"❌ Error getting microphones: {e}")
            return []
    
    def test_microphone(self, duration: float = 2.0) -> Dict:
        """
        Test microphone by recording a short sample
        
        Args:
            duration: Test duration in seconds
            
        Returns:
            Test results
        """
        try:
            logger.info(f"🧪 Testing microphone for {duration} seconds...")
            
            if not self.start_recording():
                return {"error": "Failed to start recording"}
            
            # Record for specified duration
            time.sleep(duration)
            
            audio_data = self.stop_recording()
            
            if audio_data is not None:
                # Analyze audio quality
                rms = np.sqrt(np.mean(audio_data**2))
                max_amplitude = np.max(np.abs(audio_data))
                
                return {
                    "success": True,
                    "duration": len(audio_data) / self.sample_rate,
                    "rms_level": float(rms),
                    "max_amplitude": float(max_amplitude),
                    "quality": "good" if rms > 0.01 else "low" if rms > 0.001 else "very_low"
                }
            else:
                return {"error": "No audio recorded"}
                
        except Exception as e:
            logger.error(f"❌ Microphone test failed: {e}")
            return {"error": str(e)}

# Utility functions
def initialize_enhanced_voice_processor() -> EnhancedVoiceProcessor:
    """Initialize and return enhanced voice processor"""
    return EnhancedVoiceProcessor()

def install_voice_dependencies():
    """Install required dependencies for voice processing"""
    import subprocess
    import sys
    
    dependencies = [
        "torch",
        "whisper", 
        "sounddevice",
        "soundfile"
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            logger.info(f"✅ Installed {dep}")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install {dep}: {e}")

if __name__ == "__main__":
    # Test the enhanced voice processor
    processor = initialize_enhanced_voice_processor()
    
    if processor.is_initialized:
        print("✅ Enhanced Voice Processor initialized successfully!")
        print(f"🎮 Using device: {processor.device}")
        
        # Test microphone
        mics = processor.get_available_microphones()
        print(f"🎤 Available microphones: {len(mics)}")
        for mic in mics:
            print(f"   - {mic['name']}")
    else:
        print("❌ Failed to initialize Enhanced Voice Processor")
