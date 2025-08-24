"""
Advanced Voice Mental Health Analyzer for SOLDIER SUPPORT SYSTEM
Integrates advanced voice analysis with existing assessment framework
"""

import numpy as np
import librosa
import torch
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Try to import transformers, handle gracefully if not available
try:
    from transformers import Wav2Vec2Processor, Wav2Vec2Model
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers not available - deep learning features disabled")

class AdvancedVoiceMentalHealthAnalyzer:
    """
    Advanced voice analyzer for mental health assessment
    Integrates with existing SOLDIER SUPPORT SYSTEM
    """
    
    def __init__(self, device: str = 'auto'):
        """Initialize the voice analyzer with GPU support if available"""
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
            
        print(f"🎯 Advanced Voice Analyzer initialized on: {self.device}")
        
        # Load pre-trained models
        self._load_models()
        
        # Audio processing parameters
        self.sample_rate = 16000
        self.frame_length = 2048
        self.hop_length = 512
        
        # Scoring weights for different features (matches DASS-21 categories)
        self.feature_weights = {
            'prosodic': 0.35,      # Pitch, rhythm, stress patterns
            'spectral': 0.25,      # Voice quality, timbre
            'temporal': 0.20,      # Speaking rate, pauses
            'deep_learning': 0.20  # Wav2Vec2 features
        }
        
    def _load_models(self):
        """Load pre-trained models for feature extraction"""
        if not TRANSFORMERS_AVAILABLE:
            self.wav2vec_processor = None
            self.wav2vec_model = None
            return
            
        try:
            # Load Wav2Vec2 for deep audio features
            model_name = "facebook/wav2vec2-large-xlsr-53"
            self.wav2vec_processor = Wav2Vec2Processor.from_pretrained(model_name)
            self.wav2vec_model = Wav2Vec2Model.from_pretrained(model_name).to(self.device)
            self.wav2vec_model.eval()
            print("✅ Wav2Vec2 model loaded successfully")
            
        except Exception as e:
            print(f"⚠️ Error loading Wav2Vec2: {e}")
            self.wav2vec_processor = None
            self.wav2vec_model = None
    
    def extract_prosodic_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract prosodic features (pitch, rhythm, stress patterns)"""
        features = {}
        
        # Fundamental frequency (F0) analysis
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
                'voiced_ratio': np.sum(voiced_flag) / len(voiced_flag)
            })
        else:
            features.update({
                'f0_mean': 0, 'f0_std': 0, 'f0_range': 0, 'voiced_ratio': 0
            })
        
        # Jitter and Shimmer (voice quality measures)
        if len(f0_clean) > 1:
            f0_diff = np.diff(f0_clean)
            features['jitter'] = np.mean(np.abs(f0_diff)) / np.mean(f0_clean) if np.mean(f0_clean) > 0 else 0
            
            rms = librosa.feature.rms(y=audio, frame_length=self.frame_length, hop_length=self.hop_length)[0]
            rms_clean = rms[rms > 0]
            if len(rms_clean) > 1:
                rms_diff = np.diff(rms_clean)
                features['shimmer'] = np.mean(np.abs(rms_diff)) / np.mean(rms_clean)
            else:
                features['shimmer'] = 0
        else:
            features['jitter'] = 0
            features['shimmer'] = 0
            
        return features
    
    def extract_spectral_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract spectral features (timbre, voice quality)"""
        features = {}
        
        # MFCCs (first 5 for efficiency)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=5)
        for i in range(5):
            features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
            features[f'mfcc_{i}_std'] = np.std(mfccs[i])
        
        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
        
        features.update({
            'spectral_centroid_mean': np.mean(spectral_centroids),
            'spectral_rolloff_mean': np.mean(spectral_rolloff),
            'zero_crossing_rate_mean': np.mean(zero_crossing_rate)
        })
        
        return features
    
    def extract_temporal_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract temporal features (rhythm, pauses, speaking rate)"""
        features = {}
        
        # Energy-based features
        rms = librosa.feature.rms(y=audio, frame_length=self.frame_length, hop_length=self.hop_length)[0]
        features.update({
            'rms_mean': np.mean(rms),
            'rms_std': np.std(rms)
        })
        
        # Pause detection
        energy_threshold = np.mean(rms) * 0.1
        silent_frames = rms < energy_threshold
        
        # Calculate pause statistics
        pause_segments = []
        in_pause = False
        pause_start = 0
        
        for i, is_silent in enumerate(silent_frames):
            if is_silent and not in_pause:
                in_pause = True
                pause_start = i
            elif not is_silent and in_pause:
                in_pause = False
                pause_length = (i - pause_start) * self.hop_length / sr
                if pause_length > 0.1:  # Only count pauses longer than 100ms
                    pause_segments.append(pause_length)
        
        if pause_segments:
            features.update({
                'num_pauses': len(pause_segments),
                'mean_pause_duration': np.mean(pause_segments),
                'pause_rate': len(pause_segments) / (len(audio) / sr)
            })
        else:
            features.update({
                'num_pauses': 0, 'mean_pause_duration': 0, 'pause_rate': 0
            })
        
        # Speaking rate approximation
        total_pause_time = sum(pause_segments) if pause_segments else 0
        speaking_time = (len(audio) / sr) - total_pause_time
        features['speaking_rate'] = speaking_time / (len(audio) / sr) if len(audio) > 0 else 0
        
        return features
    
    def extract_wav2vec_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract deep learning features using Wav2Vec2"""
        features = {}
        
        if self.wav2vec_model is None:
            return features
        
        try:
            # Resample if necessary
            if sr != 16000:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            
            # Process audio
            inputs = self.wav2vec_processor(
                audio, sampling_rate=16000, return_tensors="pt", padding=True
            )
            
            with torch.no_grad():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                outputs = self.wav2vec_model(**inputs)
                
                # Extract features from last hidden state
                hidden_states = outputs.last_hidden_state.cpu().numpy()[0]
                
                # Statistical features from hidden states
                features.update({
                    'wav2vec_mean': np.mean(hidden_states),
                    'wav2vec_std': np.std(hidden_states),
                    'wav2vec_skewness': self._calculate_skewness(hidden_states),
                    'wav2vec_kurtosis': self._calculate_kurtosis(hidden_states)
                })

        except Exception as e:
            print(f"⚠️ Error extracting Wav2Vec features: {e}")
            
        return features
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of data"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of data"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std) ** 4) - 3
    
    def analyze_audio_array(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Complete audio analysis pipeline"""
        try:
            # Normalize audio
            audio = librosa.util.normalize(audio)
            
            print(f"🎵 Analyzing audio: Duration: {len(audio)/sr:.2f}s, Sample Rate: {sr}Hz")
            
            # Extract all feature types
            all_features = {}
            
            # Prosodic features
            prosodic_features = self.extract_prosodic_features(audio, sr)
            all_features.update(prosodic_features)
            
            # Spectral features
            spectral_features = self.extract_spectral_features(audio, sr)
            all_features.update(spectral_features)
            
            # Temporal features
            temporal_features = self.extract_temporal_features(audio, sr)
            all_features.update(temporal_features)
            
            # Deep learning features
            wav2vec_features = self.extract_wav2vec_features(audio, sr)
            all_features.update(wav2vec_features)
            
            print(f"✅ Extracted {len(all_features)} features")
            return all_features
            
        except Exception as e:
            print(f"❌ Error analyzing audio: {e}")
            return {}
    
    def calculate_mental_health_scores(self, features: Dict[str, float]) -> Dict[str, Dict]:
        """
        Calculate mental health scores compatible with DASS-21 categories
        Returns scores for depression, anxiety, and stress
        """
        if not features:
            return {
                'depression': {'score': 0, 'severity': 'normal', 'confidence': 0.0},
                'anxiety': {'score': 0, 'severity': 'normal', 'confidence': 0.0},
                'stress': {'score': 0, 'severity': 'normal', 'confidence': 0.0}
            }
        
        # Calculate component scores
        prosodic_score = self._calculate_prosodic_score(features)
        spectral_score = self._calculate_spectral_score(features)
        temporal_score = self._calculate_temporal_score(features)
        deep_score = self._calculate_deep_learning_score(features)
        
        # Weighted combination
        depression_score = (
            prosodic_score['depression'] * self.feature_weights['prosodic'] +
            spectral_score['depression'] * self.feature_weights['spectral'] +
            temporal_score['depression'] * self.feature_weights['temporal'] +
            deep_score['depression'] * self.feature_weights['deep_learning']
        )
        
        anxiety_score = (
            prosodic_score['anxiety'] * self.feature_weights['prosodic'] +
            spectral_score['anxiety'] * self.feature_weights['spectral'] +
            temporal_score['anxiety'] * self.feature_weights['temporal'] +
            deep_score['anxiety'] * self.feature_weights['deep_learning']
        )
        
        stress_score = (
            prosodic_score['stress'] * self.feature_weights['prosodic'] +
            spectral_score['stress'] * self.feature_weights['spectral'] +
            temporal_score['stress'] * self.feature_weights['temporal'] +
            deep_score['stress'] * self.feature_weights['deep_learning']
        )
        
        return {
            'depression': {
                'score': round(depression_score, 2),
                'severity': self._score_to_severity(depression_score),
                'confidence': self._calculate_confidence(features)
            },
            'anxiety': {
                'score': round(anxiety_score, 2),
                'severity': self._score_to_severity(anxiety_score),
                'confidence': self._calculate_confidence(features)
            },
            'stress': {
                'score': round(stress_score, 2),
                'severity': self._score_to_severity(stress_score),
                'confidence': self._calculate_confidence(features)
            }
        }

    def _calculate_prosodic_score(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate prosodic-based mental health indicators"""
        f0_mean = features.get('f0_mean', 150)
        f0_std = features.get('f0_std', 20)
        jitter = features.get('jitter', 0)
        shimmer = features.get('shimmer', 0)

        # Depression indicators: monotone speech, low pitch variation
        depression_score = 0
        if f0_std < 10:  # Very monotone
            depression_score += 30
        elif f0_std < 15:  # Somewhat monotone
            depression_score += 15

        if f0_mean < 120:  # Lower pitch
            depression_score += 20

        # Anxiety indicators: pitch instability, trembling
        anxiety_score = 0
        if jitter > 0.02:  # High jitter indicates anxiety
            anxiety_score += 25
        if f0_std > 40:  # Very variable pitch
            anxiety_score += 20

        # Stress indicators: voice quality degradation
        stress_score = 0
        if shimmer > 0.1:  # High shimmer indicates stress
            stress_score += 25
        if jitter > 0.015:
            stress_score += 15

        return {
            'depression': min(depression_score, 100),
            'anxiety': min(anxiety_score, 100),
            'stress': min(stress_score, 100)
        }

    def _calculate_spectral_score(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate spectral-based mental health indicators"""
        spectral_centroid = features.get('spectral_centroid_mean', 2000)
        mfcc_0_mean = features.get('mfcc_0_mean', 0)
        mfcc_1_mean = features.get('mfcc_1_mean', 0)

        # Depression: reduced spectral energy, flat timbre
        depression_score = 0
        if spectral_centroid < 1500:  # Lower spectral centroid
            depression_score += 20
        if abs(mfcc_0_mean) < 5:  # Reduced energy
            depression_score += 15

        # Anxiety: higher frequency content, tense voice
        anxiety_score = 0
        if spectral_centroid > 2500:  # Higher spectral centroid
            anxiety_score += 20
        if mfcc_1_mean > 10:  # Spectral tilt changes
            anxiety_score += 15

        # Stress: voice quality changes
        stress_score = 0
        if spectral_centroid > 2200 or spectral_centroid < 1800:
            stress_score += 15

        return {
            'depression': min(depression_score, 100),
            'anxiety': min(anxiety_score, 100),
            'stress': min(stress_score, 100)
        }

    def _calculate_temporal_score(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate temporal-based mental health indicators"""
        speaking_rate = features.get('speaking_rate', 0.7)
        pause_rate = features.get('pause_rate', 0.1)
        mean_pause_duration = features.get('mean_pause_duration', 0.5)

        # Depression: slower speech, longer pauses
        depression_score = 0
        if speaking_rate < 0.5:  # Very slow speech
            depression_score += 30
        elif speaking_rate < 0.6:  # Slow speech
            depression_score += 15

        if mean_pause_duration > 1.0:  # Long pauses
            depression_score += 20

        # Anxiety: rapid speech, frequent pauses
        anxiety_score = 0
        if speaking_rate > 0.9:  # Very fast speech
            anxiety_score += 25
        if pause_rate > 0.3:  # Frequent pauses
            anxiety_score += 20

        # Stress: irregular rhythm
        stress_score = 0
        if pause_rate > 0.25 or pause_rate < 0.05:  # Irregular pausing
            stress_score += 20
        if speaking_rate > 0.85 or speaking_rate < 0.55:  # Irregular rate
            stress_score += 15

        return {
            'depression': min(depression_score, 100),
            'anxiety': min(anxiety_score, 100),
            'stress': min(stress_score, 100)
        }

    def _calculate_deep_learning_score(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate deep learning-based mental health indicators"""
        wav2vec_mean = features.get('wav2vec_mean', 0)
        wav2vec_std = features.get('wav2vec_std', 0)
        wav2vec_skewness = features.get('wav2vec_skewness', 0)

        # If no deep learning features available, return neutral scores
        if wav2vec_mean == 0 and wav2vec_std == 0:
            return {'depression': 10, 'anxiety': 10, 'stress': 10}

        # Depression: reduced semantic variation
        depression_score = 0
        if wav2vec_std < 0.1:  # Low variation in embeddings
            depression_score += 20
        if abs(wav2vec_skewness) > 2:  # Skewed distribution
            depression_score += 15

        # Anxiety: high variation, irregular patterns
        anxiety_score = 0
        if wav2vec_std > 0.3:  # High variation
            anxiety_score += 20
        if wav2vec_skewness > 1.5:  # Positive skew
            anxiety_score += 15

        # Stress: moderate indicators
        stress_score = 0
        if wav2vec_std > 0.25 or wav2vec_std < 0.05:
            stress_score += 15

        return {
            'depression': min(depression_score, 100),
            'anxiety': min(anxiety_score, 100),
            'stress': min(stress_score, 100)
        }

    def _score_to_severity(self, score: float) -> str:
        """Convert numerical score to DASS-21 compatible severity levels"""
        if score < 10:
            return 'normal'
        elif score < 25:
            return 'mild'
        elif score < 50:
            return 'moderate'
        elif score < 75:
            return 'severe'
        else:
            return 'extremely_severe'

    def _calculate_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence in the analysis based on feature quality"""
        # Base confidence on number of features extracted
        feature_count = len([v for v in features.values() if v != 0])
        total_expected = 20  # Expected number of meaningful features

        feature_confidence = min(1.0, feature_count / total_expected)

        # Adjust based on audio quality indicators
        f0_mean = features.get('f0_mean', 0)
        rms_mean = features.get('rms_mean', 0)

        quality_confidence = 1.0
        if f0_mean == 0:  # No pitch detected
            quality_confidence *= 0.7
        if rms_mean < 0.01:  # Very low energy
            quality_confidence *= 0.8

        return round(feature_confidence * quality_confidence, 2)
