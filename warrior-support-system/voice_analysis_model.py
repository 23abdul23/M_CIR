"""
Advanced Voice Mental Health Analyzer
Extracts voice features for mental health assessment in military personnel
"""

import numpy as np
import librosa
import torch
from typing import Dict, List, Tuple, Optional

try:
    from transformers import Wav2Vec2Processor, Wav2Vec2Model
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class VoiceFeatureExtractor:
    """
    Voice feature extraction for mental health assessment
    Implements prosodic, spectral, temporal, and deep learning features
    """
    
    def __init__(self, device: str = 'auto'):
        """Initialize the voice feature extractor with GPU support"""
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
            
        self.sample_rate = 16000
        self.frame_length = 2048
        self.hop_length = 512
        
        # Feature component weights for mental health assessment
        self.feature_weights = {
            'prosodic': 0.35,      # Pitch, voice quality
            'spectral': 0.25,      # Timbre, frequency characteristics
            'temporal': 0.20,      # Speaking rate, pauses
            'deep_learning': 0.20  # Wav2Vec2 features
        }
        
        self._load_models()
        
    def _load_models(self):
        """Load pre-trained models for deep learning feature extraction"""
        if not TRANSFORMERS_AVAILABLE:
            self.wav2vec_processor = None
            self.wav2vec_model = None
            return
            
        try:
            self.wav2vec_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-xlsr-53")
            self.wav2vec_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-large-xlsr-53")
            self.wav2vec_model.to(self.device)
        except Exception as e:
            self.wav2vec_processor = None
            self.wav2vec_model = None
    
    def extract_prosodic_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract prosodic features including pitch patterns and voice quality"""
        features = {}
        
        # Fundamental frequency analysis
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7')
        )
        
        # Remove NaN values
        f0_clean = f0[~np.isnan(f0)]
        
        if len(f0_clean) > 0:
            features.update({
                'f0_mean': np.mean(f0_clean),
                'f0_std': np.std(f0_clean),
                'f0_range': np.max(f0_clean) - np.min(f0_clean),
                'voiced_ratio': np.mean(voiced_flag)
            })
            
            # Voice quality measures
            if len(f0_clean) > 1:
                f0_diff = np.diff(f0_clean)
                features['jitter'] = np.std(f0_diff) / np.mean(f0_clean) if np.mean(f0_clean) > 0 else 0
            else:
                features['jitter'] = 0
                
            # Energy-based shimmer approximation
            rms = librosa.feature.rms(y=audio)[0]
            if len(rms) > 1:
                rms_diff = np.diff(rms)
                features['shimmer'] = np.std(rms_diff) / np.mean(rms) if np.mean(rms) > 0 else 0
            else:
                features['shimmer'] = 0
        else:
            features.update({
                'f0_mean': 0, 'f0_std': 0, 'f0_range': 0, 'voiced_ratio': 0,
                'jitter': 0, 'shimmer': 0
            })
            
        return features
    
    def extract_spectral_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract spectral features for voice timbre and quality analysis"""
        features = {}
        
        # MFCCs for timbre analysis
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=5)
        for i in range(5):
            features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
            features[f'mfcc_{i}_std'] = np.std(mfccs[i])
        
        # Spectral characteristics
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
        
        features.update({
            'spectral_centroid_mean': np.mean(spectral_centroids),
            'spectral_centroid_std': np.std(spectral_centroids),
            'spectral_rolloff_mean': np.mean(spectral_rolloff),
            'spectral_rolloff_std': np.std(spectral_rolloff)
        })
        
        return features
    
    def extract_temporal_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract temporal features including speaking rate and pause analysis"""
        features = {}
        
        # Energy-based features
        rms = librosa.feature.rms(y=audio, frame_length=self.frame_length, hop_length=self.hop_length)[0]
        features.update({
            'rms_mean': np.mean(rms),
            'rms_std': np.std(rms),
            'energy_entropy': self._calculate_entropy(rms)
        })
        
        # Zero crossing rate for voice activity
        zcr = librosa.feature.zero_crossing_rate(audio, frame_length=self.frame_length, hop_length=self.hop_length)[0]
        features.update({
            'zcr_mean': np.mean(zcr),
            'zcr_std': np.std(zcr)
        })
        
        # Pause detection and analysis
        energy_threshold = np.mean(rms) * 0.1
        voiced_frames = rms > energy_threshold
        
        # Calculate pause statistics
        pause_frames = ~voiced_frames
        pause_segments = self._get_segments(pause_frames)
        
        if len(pause_segments) > 0:
            pause_durations = [(end - start) * self.hop_length / sr for start, end in pause_segments]
            features.update({
                'pause_rate': len(pause_segments) / (len(audio) / sr),
                'mean_pause_duration': np.mean(pause_durations),
                'pause_duration_std': np.std(pause_durations)
            })
        else:
            features.update({
                'pause_rate': 0,
                'mean_pause_duration': 0,
                'pause_duration_std': 0
            })
        
        # Speaking rate estimation
        speaking_frames = np.sum(voiced_frames)
        speaking_time = speaking_frames * self.hop_length / sr
        features['speaking_rate'] = speaking_time / (len(audio) / sr) if len(audio) > 0 else 0
        
        return features
    
    def extract_wav2vec_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract deep learning features using Wav2Vec2 model"""
        features = {}
        
        if self.wav2vec_model is None:
            return features
        
        try:
            # Resample if necessary
            if sr != 16000:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            
            # Process with Wav2Vec2
            inputs = self.wav2vec_processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
            
            with torch.no_grad():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                outputs = self.wav2vec_model(**inputs)
                hidden_states = outputs.last_hidden_state.cpu().numpy().flatten()
                
                features.update({
                    'wav2vec_mean': np.mean(hidden_states),
                    'wav2vec_std': np.std(hidden_states),
                    'wav2vec_skewness': self._calculate_skewness(hidden_states),
                    'wav2vec_kurtosis': self._calculate_kurtosis(hidden_states)
                })
                
        except Exception as e:
            pass
            
        return features
    
    def _calculate_entropy(self, signal: np.ndarray) -> float:
        """Calculate entropy of signal for complexity analysis"""
        hist, _ = np.histogram(signal, bins=50, density=True)
        hist = hist[hist > 0]
        return -np.sum(hist * np.log2(hist)) if len(hist) > 0 else 0
    
    def _get_segments(self, binary_array: np.ndarray) -> List[Tuple[int, int]]:
        """Extract continuous segments from binary array"""
        segments = []
        start = None
        
        for i, val in enumerate(binary_array):
            if val and start is None:
                start = i
            elif not val and start is not None:
                segments.append((start, i))
                start = None
        
        if start is not None:
            segments.append((start, len(binary_array)))
        
        return segments
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of data distribution"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of data distribution"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std) ** 4) - 3
    
    def extract_all_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract complete feature set from audio signal"""
        try:
            # Normalize audio
            audio = librosa.util.normalize(audio)
            
            # Extract all feature types
            prosodic_features = self.extract_prosodic_features(audio, sr)
            spectral_features = self.extract_spectral_features(audio, sr)
            temporal_features = self.extract_temporal_features(audio, sr)
            wav2vec_features = self.extract_wav2vec_features(audio, sr)
            
            # Combine all features
            all_features = {}
            all_features.update(prosodic_features)
            all_features.update(spectral_features)
            all_features.update(temporal_features)
            all_features.update(wav2vec_features)
            
            return all_features
            
        except Exception as e:
            return {}
