"""
Voice Processing Module for Hindi Speech-to-Text
CPU-ONLY, OFFLINE-CAPABLE VERSION
"""
import os
import tempfile
import wave
import json
from typing import Dict, Optional, List
import sys
from pathlib import Path

# Force CPU usage - NO GPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TORCH_USE_CUDA"] = "0"

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent.parent))
try:
    from config import MODELS_DIR, HINDI_MODELS, MODEL_CONFIG
except ImportError:
    # Fallback configuration
    MODELS_DIR = Path("data/models")
    MODELS_DIR.mkdir(exist_ok=True)
    MODEL_CONFIG = {"device": "cpu", "local_files_only": True}

try:
    import speech_recognition as sr
    import pydub
    from pydub import AudioSegment
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("Warning: speech_recognition and pydub not available. Voice processing will use fallback.")

try:
    import whisper
    # Force CPU usage for Whisper
    WHISPER_AVAILABLE = True
    print("Whisper available - will use CPU-only mode")
except ImportError:
    WHISPER_AVAILABLE = False
    print("Warning: whisper not available. Using alternative speech recognition.")

class HindiVoiceProcessor:
    """
    Processes Hindi voice input and converts to text
    """
    
    def __init__(self):
        self.recognizer = None
        self.whisper_model = None
        self.setup_speech_recognition()
    
    def setup_speech_recognition(self):
        """
        Setup speech recognition components
        """
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            
            # Configure for better Hindi recognition
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3
        
        # Try to load Whisper model for better accuracy (CPU-only)
        if WHISPER_AVAILABLE:
            try:
                # Auto-detect best device for Whisper
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                device_name = f"GPU ({torch.cuda.get_device_name(0)})" if device == "cuda" else "CPU"

                print(f"Loading Whisper model for Hindi speech recognition ({device_name})...")

                # Load model with auto-detected device
                self.whisper_model = whisper.load_model(
                    "base",
                    device=device,
                    download_root=str(MODELS_DIR / "whisper")
                )
                print(f"✓ Whisper model loaded successfully on {device_name}!")
            except Exception as e:
                print(f"✗ Failed to load Whisper model: {e}")
                print("⚠ Will use fallback speech recognition")
                self.whisper_model = None
    
    def record_audio(self, duration: int = 30, sample_rate: int = 16000) -> Optional[str]:
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Audio sample rate
            
        Returns:
            Path to recorded audio file or None if failed
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            print("Speech recognition not available")
            return None
        
        try:
            with sr.Microphone(sample_rate=sample_rate) as source:
                print("कृपया बोलना शुरू करें... (Please start speaking...)")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Record audio
                audio_data = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
                
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                with open(temp_file.name, 'wb') as f:
                    f.write(audio_data.get_wav_data())
                
                return temp_file.name
                
        except sr.WaitTimeoutError:
            print("रिकॉर्डिंग समय समाप्त (Recording timeout)")
            return None
        except Exception as e:
            print(f"रिकॉर्डिंग में त्रुटि (Recording error): {e}")
            return None
    
    def process_audio_file(self, audio_file_path: str) -> Dict[str, any]:
        """
        Process audio file and convert to text
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Dictionary with transcription results
        """
        if not os.path.exists(audio_file_path):
            return {
                "success": False,
                "error": "Audio file not found",
                "text": "",
                "confidence": 0.0
            }
        
        # Try Whisper first (better accuracy)
        if self.whisper_model:
            return self._transcribe_with_whisper(audio_file_path)
        
        # Fallback to Google Speech Recognition
        elif SPEECH_RECOGNITION_AVAILABLE:
            return self._transcribe_with_google(audio_file_path)
        
        # Final fallback - return empty result
        else:
            return {
                "success": False,
                "error": "No speech recognition method available",
                "text": "",
                "confidence": 0.0
            }
    
    def _transcribe_with_whisper(self, audio_file_path: str) -> Dict[str, any]:
        """
        Transcribe audio using Whisper model
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcription results
        """
        try:
            print("Whisper के साथ ट्रांसक्रिप्शन... (Transcribing with Whisper...)")
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(
                audio_file_path,
                language="hi",  # Hindi language code
                task="transcribe"
            )
            
            text = result["text"].strip()
            
            # Estimate confidence based on Whisper's internal scoring
            # Whisper doesn't provide direct confidence scores, so we estimate
            segments = result.get("segments", [])
            if segments:
                avg_confidence = sum(seg.get("no_speech_prob", 0.5) for seg in segments) / len(segments)
                confidence = 1.0 - avg_confidence  # Convert no_speech_prob to confidence
            else:
                confidence = 0.8 if text else 0.0
            
            return {
                "success": True,
                "text": text,
                "confidence": confidence,
                "method": "whisper",
                "language": "hindi",
                "segments": segments
            }
            
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }
    
    def _transcribe_with_google(self, audio_file_path: str) -> Dict[str, any]:
        """
        Transcribe audio using Google Speech Recognition
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcription results
        """
        try:
            print("Google Speech Recognition के साथ ट्रांसक्रिप्शन...")
            
            # Load audio file
            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.recognizer.record(source)
            
            # Try Google Speech Recognition with Hindi
            try:
                text = self.recognizer.recognize_google(
                    audio_data,
                    language="hi-IN"  # Hindi (India)
                )
                
                return {
                    "success": True,
                    "text": text,
                    "confidence": 0.7,  # Google doesn't provide confidence scores
                    "method": "google",
                    "language": "hindi"
                }
                
            except sr.UnknownValueError:
                return {
                    "success": False,
                    "error": "Could not understand audio",
                    "text": "",
                    "confidence": 0.0
                }
            except sr.RequestError as e:
                return {
                    "success": False,
                    "error": f"Google Speech Recognition service error: {e}",
                    "text": "",
                    "confidence": 0.0
                }
                
        except Exception as e:
            print(f"Google transcription error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }
    
    def convert_audio_format(self, input_path: str, output_path: str = None) -> Optional[str]:
        """
        Convert audio to WAV format for better processing
        
        Args:
            input_path: Input audio file path
            output_path: Output WAV file path (optional)
            
        Returns:
            Path to converted WAV file or None if failed
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            return None
        
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Convert to WAV with optimal settings for speech recognition
            audio = audio.set_frame_rate(16000)  # 16kHz sample rate
            audio = audio.set_channels(1)        # Mono
            audio = audio.set_sample_width(2)    # 16-bit
            
            # Generate output path if not provided
            if not output_path:
                output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
            
            # Export as WAV
            audio.export(output_path, format="wav")
            
            return output_path
            
        except Exception as e:
            print(f"Audio conversion error: {e}")
            return None
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """
        Clean up temporary audio files
        
        Args:
            file_paths: List of file paths to delete
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting temp file {file_path}: {e}")
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported audio formats
        
        Returns:
            List of supported file extensions
        """
        if SPEECH_RECOGNITION_AVAILABLE:
            return ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac']
        else:
            return ['.wav']  # Basic support only
    
    def validate_audio_file(self, file_path: str) -> Dict[str, any]:
        """
        Validate audio file for processing
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Validation results
        """
        if not os.path.exists(file_path):
            return {
                "valid": False,
                "error": "File does not exist"
            }
        
        try:
            # Check file size (max 50MB)
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:
                return {
                    "valid": False,
                    "error": "File too large (max 50MB)"
                }
            
            # Check file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.get_supported_formats():
                return {
                    "valid": False,
                    "error": f"Unsupported format: {file_ext}"
                }
            
            # Try to load audio file
            if SPEECH_RECOGNITION_AVAILABLE:
                try:
                    audio = AudioSegment.from_file(file_path)
                    duration = len(audio) / 1000  # Duration in seconds
                    
                    if duration > 300:  # Max 5 minutes
                        return {
                            "valid": False,
                            "error": "Audio too long (max 5 minutes)"
                        }
                    
                    return {
                        "valid": True,
                        "duration": duration,
                        "format": file_ext,
                        "size": file_size
                    }
                    
                except Exception as e:
                    return {
                        "valid": False,
                        "error": f"Invalid audio file: {e}"
                    }
            else:
                return {
                    "valid": True,
                    "format": file_ext,
                    "size": file_size
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }

# Global instance
hindi_voice_processor = HindiVoiceProcessor()

def process_voice_input(audio_file_path: str) -> Dict[str, any]:
    """
    Convenience function to process voice input
    
    Args:
        audio_file_path: Path to audio file
        
    Returns:
        Transcription results
    """
    return hindi_voice_processor.process_audio_file(audio_file_path)

def record_and_transcribe(duration: int = 30) -> Dict[str, any]:
    """
    Record audio and transcribe to text
    
    Args:
        duration: Recording duration in seconds
        
    Returns:
        Transcription results
    """
    # Record audio
    audio_file = hindi_voice_processor.record_audio(duration)
    
    if not audio_file:
        return {
            "success": False,
            "error": "Failed to record audio",
            "text": "",
            "confidence": 0.0
        }
    
    try:
        # Transcribe audio
        result = hindi_voice_processor.process_audio_file(audio_file)
        
        # Clean up temporary file
        hindi_voice_processor.cleanup_temp_files([audio_file])
        
        return result
        
    except Exception as e:
        # Clean up on error
        hindi_voice_processor.cleanup_temp_files([audio_file])
        return {
            "success": False,
            "error": str(e),
            "text": "",
            "confidence": 0.0
        }
