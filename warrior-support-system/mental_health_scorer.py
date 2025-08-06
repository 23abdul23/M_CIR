"""
Mental Health Scoring System
Converts voice features to DASS-21 compatible mental health scores
"""

import numpy as np
from typing import Dict

class MentalHealthScorer:
    """
    Converts voice features to mental health scores compatible with DASS-21 assessment
    Provides depression, anxiety, and stress scoring based on voice characteristics
    """
    
    def __init__(self):
        """Initialize the mental health scoring system"""
        # Component weights for final score calculation
        self.component_weights = {
            'prosodic': 0.35,      # Pitch patterns, voice quality
            'spectral': 0.25,      # Voice timbre characteristics  
            'temporal': 0.20,      # Speaking patterns, pauses
            'deep_learning': 0.20  # Advanced ML features
        }
    
    def calculate_mental_health_scores(self, features: Dict[str, float]) -> Dict[str, Dict]:
        """
        Calculate mental health scores from voice features
        Returns DASS-21 compatible scores for depression, anxiety, and stress
        """
        if not features:
            return {
                'depression': {'score': 0, 'severity': 'normal', 'confidence': 0.0},
                'anxiety': {'score': 0, 'severity': 'normal', 'confidence': 0.0},
                'stress': {'score': 0, 'severity': 'normal', 'confidence': 0.0}
            }
        
        # Calculate component scores
        prosodic_scores = self._calculate_prosodic_score(features)
        spectral_scores = self._calculate_spectral_score(features)
        temporal_scores = self._calculate_temporal_score(features)
        deep_learning_scores = self._calculate_deep_learning_score(features)
        
        # Weighted combination of all components
        final_scores = {}
        for condition in ['depression', 'anxiety', 'stress']:
            weighted_score = (
                prosodic_scores[condition] * self.component_weights['prosodic'] +
                spectral_scores[condition] * self.component_weights['spectral'] +
                temporal_scores[condition] * self.component_weights['temporal'] +
                deep_learning_scores[condition] * self.component_weights['deep_learning']
            )
            final_scores[condition] = min(weighted_score, 100)
        
        # Convert to DASS-21 compatible format
        return {
            'depression': {
                'score': round(final_scores['depression'], 1),
                'severity': self._score_to_severity(final_scores['depression'], 'depression'),
                'confidence': self._calculate_confidence(features)
            },
            'anxiety': {
                'score': round(final_scores['anxiety'], 1),
                'severity': self._score_to_severity(final_scores['anxiety'], 'anxiety'),
                'confidence': self._calculate_confidence(features)
            },
            'stress': {
                'score': round(final_scores['stress'], 1),
                'severity': self._score_to_severity(final_scores['stress'], 'stress'),
                'confidence': self._calculate_confidence(features)
            }
        }

    def _calculate_prosodic_score(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate mental health indicators from prosodic features"""
        f0_mean = features.get('f0_mean', 150)
        f0_std = features.get('f0_std', 20)
        jitter = features.get('jitter', 0)
        shimmer = features.get('shimmer', 0)

        # Depression indicators: monotone speech, reduced pitch variation
        depression_score = 0
        if f0_std < 15:  # Low pitch variation
            depression_score += 25
        if f0_mean < 120:  # Low pitch
            depression_score += 20
        if jitter > 0.02:  # Voice instability
            depression_score += 15

        # Anxiety indicators: pitch instability, voice trembling
        anxiety_score = 0
        if jitter > 0.015:  # High jitter indicates anxiety
            anxiety_score += 30
        if shimmer > 0.1:  # Amplitude variation
            anxiety_score += 25
        if f0_std > 40:  # High pitch variation
            anxiety_score += 20

        # Stress indicators: voice quality degradation
        stress_score = 0
        if jitter > 0.01:
            stress_score += 20
        if shimmer > 0.08:
            stress_score += 25
        if features.get('voiced_ratio', 1) < 0.6:  # Breathy voice
            stress_score += 20

        return {
            'depression': min(depression_score, 100),
            'anxiety': min(anxiety_score, 100),
            'stress': min(stress_score, 100)
        }

    def _calculate_spectral_score(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate mental health indicators from spectral features"""
        spectral_centroid = features.get('spectral_centroid_mean', 2000)
        mfcc_0_mean = features.get('mfcc_0_mean', 0)
        mfcc_1_mean = features.get('mfcc_1_mean', 0)

        # Depression: reduced spectral energy, flat timbre
        depression_score = 0
        if spectral_centroid < 1500:  # Low spectral centroid
            depression_score += 25
        if abs(mfcc_0_mean) < 5:  # Low energy
            depression_score += 20

        # Anxiety: spectral irregularities
        anxiety_score = 0
        if spectral_centroid > 3000:  # High spectral centroid
            anxiety_score += 20
        spectral_std = features.get('spectral_centroid_std', 0)
        if spectral_std > 500:  # High spectral variation
            anxiety_score += 25

        # Stress: voice quality changes
        stress_score = 0
        if spectral_centroid > 2500:
            stress_score += 15
        if features.get('spectral_rolloff_std', 0) > 1000:
            stress_score += 20

        return {
            'depression': min(depression_score, 100),
            'anxiety': min(anxiety_score, 100),
            'stress': min(stress_score, 100)
        }

    def _calculate_temporal_score(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate mental health indicators from temporal features"""
        speaking_rate = features.get('speaking_rate', 0.7)
        pause_rate = features.get('pause_rate', 0.1)
        mean_pause_duration = features.get('mean_pause_duration', 0.5)

        # Depression: slower speech, longer pauses
        depression_score = 0
        if speaking_rate < 0.5:  # Slow speech
            depression_score += 30
        if mean_pause_duration > 1.0:  # Long pauses
            depression_score += 25
        if pause_rate > 0.3:  # Frequent pauses
            depression_score += 20

        # Anxiety: rapid speech or irregular patterns
        anxiety_score = 0
        if speaking_rate > 0.9:  # Fast speech
            anxiety_score += 25
        if pause_rate > 0.4:  # Very frequent pauses
            anxiety_score += 20
        pause_std = features.get('pause_duration_std', 0)
        if pause_std > 0.5:  # Irregular pause patterns
            anxiety_score += 15

        # Stress: irregular speaking patterns
        stress_score = 0
        if speaking_rate < 0.4 or speaking_rate > 0.95:  # Extreme rates
            stress_score += 20
        if pause_rate > 0.35:
            stress_score += 15
        if mean_pause_duration > 0.8:
            stress_score += 10

        return {
            'depression': min(depression_score, 100),
            'anxiety': min(anxiety_score, 100),
            'stress': min(stress_score, 100)
        }

    def _calculate_deep_learning_score(self, features: Dict[str, float]) -> Dict[str, float]:
        """Calculate mental health indicators from deep learning features"""
        wav2vec_mean = features.get('wav2vec_mean', 0)
        wav2vec_std = features.get('wav2vec_std', 0)
        wav2vec_skewness = features.get('wav2vec_skewness', 0)

        # If no deep learning features available, return neutral scores
        if wav2vec_mean == 0 and wav2vec_std == 0:
            return {'depression': 10, 'anxiety': 10, 'stress': 10}

        # Advanced pattern recognition for mental health indicators
        depression_score = 0
        if wav2vec_mean < -0.1:  # Low activation patterns
            depression_score += 20
        if wav2vec_std < 0.5:  # Low variation in neural patterns
            depression_score += 15

        anxiety_score = 0
        if abs(wav2vec_skewness) > 1.0:  # Asymmetric patterns
            anxiety_score += 25
        if wav2vec_std > 1.5:  # High variation
            anxiety_score += 20

        stress_score = 0
        kurtosis = features.get('wav2vec_kurtosis', 0)
        if abs(kurtosis) > 2.0:  # Extreme distributions
            stress_score += 20
        if wav2vec_mean > 0.1:  # High activation
            stress_score += 15

        return {
            'depression': min(depression_score, 100),
            'anxiety': min(anxiety_score, 100),
            'stress': min(stress_score, 100)
        }

    def _score_to_severity(self, score: float, condition: str) -> str:
        """Convert numerical score to DASS-21 compatible severity levels"""
        if condition == 'depression':
            if score <= 9: return 'normal'
            elif score <= 13: return 'mild'
            elif score <= 20: return 'moderate'
            elif score <= 27: return 'severe'
            else: return 'extremely_severe'
        elif condition == 'anxiety':
            if score <= 7: return 'normal'
            elif score <= 9: return 'mild'
            elif score <= 14: return 'moderate'
            elif score <= 19: return 'severe'
            else: return 'extremely_severe'
        else:  # stress
            if score <= 14: return 'normal'
            elif score <= 18: return 'mild'
            elif score <= 25: return 'moderate'
            elif score <= 33: return 'severe'
            else: return 'extremely_severe'

    def _calculate_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence in the analysis based on feature quality"""
        feature_count = len([v for v in features.values() if v != 0])
        total_expected = 20
        
        feature_confidence = min(1.0, feature_count / total_expected)
        
        # Adjust based on audio quality indicators
        f0_mean = features.get('f0_mean', 0)
        rms_mean = features.get('rms_mean', 0)
        
        quality_confidence = 1.0
        if f0_mean == 0:
            quality_confidence *= 0.7
        if rms_mean < 0.01:
            quality_confidence *= 0.8
        
        return round(feature_confidence * quality_confidence, 2)
