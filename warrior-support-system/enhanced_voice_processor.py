"""
Enhanced Voice Processor with Whisper Integration
Handles audio transcription and preprocessing for voice analysis
"""

import os
import tempfile
import shutil
import librosa
import numpy as np
from typing import Dict, Optional

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

class EnhancedVoiceProcessor:
    """
    Enhanced voice processor with offline Whisper model integration
    Handles audio transcription and preprocessing for mental health analysis
    """
    
    def __init__(self, model_size: str = "base"):
        """Initialize the enhanced voice processor with Whisper model"""
        self.model_size = model_size
        self.whisper_model = None
        self.sample_rate = 16000
        
        if WHISPER_AVAILABLE:
            self._load_whisper_model()
    
    def _load_whisper_model(self):
        """Load Whisper model for offline transcription"""
        try:
            self.whisper_model = whisper.load_model(self.model_size)
        except Exception as e:
            self.whisper_model = None
    
    def transcribe_audio(self, audio_path: str, language_hint: str = "hi") -> Dict:
        """
        Transcribe audio file using Whisper model
        Optimized for Hinglish (Hindi-English code-switching) content
        """
        if not self.whisper_model:
            return {"transcription": "", "language": "unknown", "error": "Whisper model not available"}
        
        try:
            # Load and preprocess audio
            audio_data = self._preprocess_audio(audio_path)
            
            # Transcribe with Hindi language preference for Hinglish support
            result = self.whisper_model.transcribe(
                audio_path,
                language="hi",  # Force Hindi for better Hinglish support
                task="transcribe",
                fp16=False,  # Use FP32 for better compatibility
                verbose=False,
                word_timestamps=False,
                condition_on_previous_text=False  # Better for short audio clips
            )
            
            return {
                "transcription": result["text"].strip(),
                "language": result.get("language", "hi"),
                "confidence": self._estimate_confidence(result)
            }
            
        except Exception as e:
            return {"transcription": "", "language": "unknown", "error": str(e)}
    
    def _preprocess_audio(self, audio_path: str) -> np.ndarray:
        """Preprocess audio for optimal transcription quality"""
        try:
            # Load audio with librosa
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Normalize audio
            audio = librosa.util.normalize(audio)
            
            # Apply noise reduction if audio is very quiet
            if np.max(np.abs(audio)) < 0.1:
                audio = audio * 3.0  # Amplify quiet audio
            
            return audio
            
        except Exception as e:
            return np.array([])
    
    def _estimate_confidence(self, whisper_result: Dict) -> float:
        """Estimate transcription confidence based on result characteristics"""
        text = whisper_result.get("text", "")
        
        # Basic confidence estimation
        if len(text.strip()) == 0:
            return 0.0
        
        # Longer transcriptions generally have higher confidence
        length_factor = min(len(text) / 50, 1.0)
        
        # Check for repeated patterns (lower confidence)
        words = text.split()
        if len(words) > 1:
            unique_words = len(set(words))
            repetition_factor = unique_words / len(words)
        else:
            repetition_factor = 1.0
        
        # Combine factors
        confidence = (length_factor * 0.6 + repetition_factor * 0.4) * 0.85
        
        return round(confidence, 2)
    
    def extract_audio_features(self, audio_path: str) -> Dict[str, float]:
        """Extract basic audio features for quality assessment"""
        try:
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Basic audio characteristics
            duration = len(audio) / sr
            rms_energy = np.sqrt(np.mean(audio**2))
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio))
            
            # Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr))
            
            return {
                'duration': duration,
                'rms_energy': rms_energy,
                'zero_crossing_rate': zero_crossing_rate,
                'spectral_centroid': spectral_centroid,
                'spectral_rolloff': spectral_rolloff,
                'sample_rate': sr
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def validate_audio_quality(self, audio_path: str) -> Dict[str, bool]:
        """Validate audio quality for reliable transcription"""
        features = self.extract_audio_features(audio_path)
        
        if 'error' in features:
            return {'valid': False, 'reason': features['error']}
        
        # Quality checks
        checks = {
            'sufficient_duration': features.get('duration', 0) >= 0.5,  # At least 0.5 seconds
            'adequate_energy': features.get('rms_energy', 0) >= 0.01,   # Not too quiet
            'proper_sample_rate': features.get('sample_rate', 0) >= 8000,  # Adequate quality
            'speech_like': features.get('zero_crossing_rate', 0) < 0.5   # Not pure noise
        }
        
        all_passed = all(checks.values())
        
        return {
            'valid': all_passed,
            'checks': checks,
            'features': features
        }
    
    def process_audio_file(self, audio_path: str, language_hint: str = "hi") -> Dict:
        """
        Complete audio processing pipeline
        Includes quality validation, transcription, and feature extraction
        """
        # Validate audio quality
        quality_check = self.validate_audio_quality(audio_path)
        
        if not quality_check['valid']:
            return {
                'transcription': '',
                'quality_valid': False,
                'quality_issues': quality_check.get('checks', {}),
                'error': 'Audio quality insufficient for reliable transcription'
            }
        
        # Perform transcription
        transcription_result = self.transcribe_audio(audio_path, language_hint)
        
        # Extract audio features
        audio_features = self.extract_audio_features(audio_path)
        
        return {
            'transcription': transcription_result.get('transcription', ''),
            'language': transcription_result.get('language', 'unknown'),
            'confidence': transcription_result.get('confidence', 0.0),
            'quality_valid': True,
            'audio_features': audio_features,
            'processing_successful': 'error' not in transcription_result
        }
    
    def convert_audio_format(self, input_path: str, output_path: str = None) -> str:
        """Convert audio to optimal format for processing"""
        if output_path is None:
            output_path = input_path.replace(os.path.splitext(input_path)[1], '.wav')
        
        try:
            # Load and resample audio
            audio, sr = librosa.load(input_path, sr=self.sample_rate)
            
            # Save as WAV
            import soundfile as sf
            sf.write(output_path, audio, self.sample_rate)
            
            return output_path
            
        except Exception as e:
            return input_path  # Return original if conversion fails
