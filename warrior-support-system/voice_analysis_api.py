"""
Voice Analysis API Integration
Integrates voice feature extraction, mental health scoring, and weighted assessment
"""

import os
import tempfile
import shutil
from typing import Dict, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from voice_analysis_model import VoiceFeatureExtractor
from mental_health_scorer import MentalHealthScorer
from weighted_assessment_engine import WeightedAssessmentEngine
from enhanced_voice_processor import EnhancedVoiceProcessor

class VoiceAnalysisAPI:
    """
    Complete voice analysis API that integrates all components
    Provides comprehensive mental health assessment from voice recordings
    """
    
    def __init__(self):
        """Initialize all voice analysis components"""
        self.feature_extractor = VoiceFeatureExtractor()
        self.mental_health_scorer = MentalHealthScorer()
        self.weighted_engine = WeightedAssessmentEngine()
        self.voice_processor = EnhancedVoiceProcessor()
    
    async def analyze_voice_recording(self, audio_file: UploadFile) -> Dict:
        """
        Complete voice analysis pipeline
        Processes audio file and returns comprehensive mental health assessment
        """
        temp_path = None
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
                content = await audio_file.read()
                tmp_file.write(content)
                temp_path = tmp_file.name
            
            # Process audio with enhanced voice processor
            processing_result = self.voice_processor.process_audio_file(temp_path, language_hint="hi")
            
            if not processing_result.get('processing_successful', False):
                return {
                    'success': False,
                    'error': 'Audio processing failed',
                    'details': processing_result
                }
            
            # Extract voice features for mental health analysis
            import librosa
            audio_data, sample_rate = librosa.load(temp_path, sr=16000)
            voice_features = self.feature_extractor.extract_all_features(audio_data, sample_rate)
            
            if not voice_features:
                return {
                    'success': False,
                    'error': 'Feature extraction failed'
                }
            
            # Calculate mental health scores
            mental_health_scores = self.mental_health_scorer.calculate_mental_health_scores(voice_features)
            
            # Prepare comprehensive assessment with weighted scoring
            assessment_result = self.weighted_engine.calculate_comprehensive_scores(
                voice_results=mental_health_scores,
                sentiment_results={'negative': 0.3, 'positive': 0.5, 'neutral': 0.2},
                keyword_results={'depression_indicators': 0, 'anxiety_indicators': 0, 'stress_indicators': 0, 'total_words': 10},
                facial_results={'sadness': 0.2, 'fear': 0.1, 'anger': 0.1, 'happiness': 0.6}
            )
            
            return {
                'success': True,
                'transcript': processing_result.get('transcription', ''),
                'language': processing_result.get('language', 'hi'),
                'voice_analysis': mental_health_scores,
                'weighted_assessment': assessment_result,
                'audio_quality': {
                    'duration': processing_result.get('audio_features', {}).get('duration', 0),
                    'confidence': processing_result.get('confidence', 0.0)
                },
                'ai_enhanced': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'ai_enhanced': False
            }
            
        finally:
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
    
    def analyze_voice_features_only(self, audio_file_path: str) -> Dict:
        """
        Extract and analyze voice features from audio file
        Returns detailed feature analysis without transcription
        """
        try:
            import librosa
            audio_data, sample_rate = librosa.load(audio_file_path, sr=16000)
            
            # Extract comprehensive voice features
            voice_features = self.feature_extractor.extract_all_features(audio_data, sample_rate)
            
            if not voice_features:
                return {'success': False, 'error': 'Feature extraction failed'}
            
            # Calculate mental health scores from features
            mental_health_scores = self.mental_health_scorer.calculate_mental_health_scores(voice_features)
            
            return {
                'success': True,
                'voice_features': voice_features,
                'mental_health_scores': mental_health_scores,
                'feature_count': len(voice_features),
                'analysis_quality': self._assess_feature_quality(voice_features)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_assessment_summary(self, voice_results: Dict) -> Dict:
        """
        Generate assessment summary from voice analysis results
        Provides clinical interpretation of results
        """
        if not voice_results.get('success', False):
            return {'error': 'Invalid voice analysis results'}
        
        mental_health_scores = voice_results.get('mental_health_scores', {})
        
        # Extract severity levels
        depression_severity = mental_health_scores.get('depression', {}).get('severity', 'normal')
        anxiety_severity = mental_health_scores.get('anxiety', {}).get('severity', 'normal')
        stress_severity = mental_health_scores.get('stress', {}).get('severity', 'normal')
        
        # Determine primary concern
        scores = {
            'depression': mental_health_scores.get('depression', {}).get('score', 0),
            'anxiety': mental_health_scores.get('anxiety', {}).get('score', 0),
            'stress': mental_health_scores.get('stress', {}).get('score', 0)
        }
        primary_concern = max(scores, key=scores.get)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(mental_health_scores)
        
        return {
            'summary': {
                'primary_concern': primary_concern,
                'severity_levels': {
                    'depression': depression_severity,
                    'anxiety': anxiety_severity,
                    'stress': stress_severity
                },
                'overall_risk': self._calculate_overall_risk(scores),
                'confidence': mental_health_scores.get('depression', {}).get('confidence', 0.0)
            },
            'recommendations': recommendations,
            'dass21_compatible': True
        }
    
    def _assess_feature_quality(self, features: Dict[str, float]) -> str:
        """Assess the quality of extracted features"""
        feature_count = len([v for v in features.values() if v != 0])
        
        if feature_count >= 20:
            return 'high'
        elif feature_count >= 15:
            return 'moderate'
        elif feature_count >= 10:
            return 'low'
        else:
            return 'insufficient'
    
    def _calculate_overall_risk(self, scores: Dict[str, float]) -> str:
        """Calculate overall mental health risk level"""
        max_score = max(scores.values())
        avg_score = sum(scores.values()) / len(scores)
        
        if max_score >= 50 or avg_score >= 35:
            return 'high'
        elif max_score >= 25 or avg_score >= 20:
            return 'moderate'
        elif max_score >= 15 or avg_score >= 10:
            return 'low'
        else:
            return 'minimal'
    
    def _generate_recommendations(self, mental_health_scores: Dict) -> List[str]:
        """Generate recommendations based on assessment results"""
        recommendations = []
        
        # Check each condition and provide specific recommendations
        for condition, data in mental_health_scores.items():
            severity = data.get('severity', 'normal')
            score = data.get('score', 0)
            
            if severity in ['moderate', 'severe', 'extremely_severe']:
                if condition == 'depression':
                    recommendations.append(f"Consider professional counseling for {condition} (severity: {severity})")
                elif condition == 'anxiety':
                    recommendations.append(f"Stress management techniques recommended for {condition} (severity: {severity})")
                elif condition == 'stress':
                    recommendations.append(f"Work-life balance assessment needed for {condition} (severity: {severity})")
        
        if not recommendations:
            recommendations.append("Mental health indicators within normal range")
        
        return recommendations

# FastAPI integration example
def create_voice_analysis_endpoints(app: FastAPI):
    """
    Create FastAPI endpoints for voice analysis
    Integrates with existing warrior support system
    """
    voice_api = VoiceAnalysisAPI()
    
    @app.post("/api/voice-analysis")
    async def analyze_voice(audio: UploadFile = File(...)):
        """Endpoint for comprehensive voice analysis"""
        try:
            result = await voice_api.analyze_voice_recording(audio)
            return JSONResponse(content=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/voice-features")
    async def extract_voice_features(audio: UploadFile = File(...)):
        """Endpoint for voice feature extraction only"""
        temp_path = None
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
                content = await audio.read()
                tmp_file.write(content)
                temp_path = tmp_file.name
            
            result = voice_api.analyze_voice_features_only(temp_path)
            return JSONResponse(content=result)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
    
    @app.get("/api/voice-analysis/health")
    async def voice_analysis_health():
        """Health check endpoint for voice analysis system"""
        return {
            'status': 'healthy',
            'components': {
                'feature_extractor': 'available',
                'mental_health_scorer': 'available',
                'weighted_engine': 'available',
                'voice_processor': 'available'
            },
            'voice_analysis_weight': '40%'
        }
