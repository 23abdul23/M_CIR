"""
Weighted AI Assessment Engine for Warrior Support System
Combines voice analysis, sentiment analysis, keyword matching, and facial analysis
with proper weightings to generate comprehensive mental health scores
"""

import numpy as np
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeightedAIAssessmentEngine:
    """
    Comprehensive AI assessment engine with weighted scoring
    Integrates multiple AI components for robust mental health assessment
    """
    
    def __init__(self):
        """Initialize the weighted assessment engine"""
        
        # Component weights based on accuracy and reliability
        # Voice analysis gets highest weight as it's most advanced
        self.component_weights = {
            'voice_analysis': 0.40,        # 40% - Advanced voice features
            'sentiment_analysis': 0.25,    # 25% - Text sentiment from speech
            'keyword_matching': 0.20,      # 20% - Mental health keywords
            'facial_analysis': 0.15        # 15% - Facial behavior (less reliable)
        }
        
        # DASS-21 compatible severity thresholds
        self.severity_thresholds = {
            'depression': {
                'normal': (0, 9),
                'mild': (10, 13),
                'moderate': (14, 20),
                'severe': (21, 27),
                'extremely_severe': (28, 100)
            },
            'anxiety': {
                'normal': (0, 7),
                'mild': (8, 9),
                'moderate': (10, 14),
                'severe': (15, 19),
                'extremely_severe': (20, 100)
            },
            'stress': {
                'normal': (0, 14),
                'mild': (15, 18),
                'moderate': (19, 25),
                'severe': (26, 33),
                'extremely_severe': (34, 100)
            }
        }
        
        logger.info("🎯 Weighted AI Assessment Engine initialized")
    
    def calculate_comprehensive_scores(self, 
                                     voice_results: Optional[Dict] = None,
                                     sentiment_results: Optional[Dict] = None,
                                     keyword_results: Optional[Dict] = None,
                                     facial_results: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive mental health scores from all AI components
        
        Args:
            voice_results: Results from advanced voice analysis
            sentiment_results: Results from sentiment analysis
            keyword_results: Results from keyword matching
            facial_results: Results from facial analysis
            
        Returns:
            Comprehensive assessment with weighted scores
        """
        
        # Initialize component scores
        component_scores = {
            'voice_analysis': {'depression': 0, 'anxiety': 0, 'stress': 0, 'confidence': 0},
            'sentiment_analysis': {'depression': 0, 'anxiety': 0, 'stress': 0, 'confidence': 0},
            'keyword_matching': {'depression': 0, 'anxiety': 0, 'stress': 0, 'confidence': 0},
            'facial_analysis': {'depression': 0, 'anxiety': 0, 'stress': 0, 'confidence': 0}
        }
        
        # Process voice analysis results
        if voice_results:
            component_scores['voice_analysis'] = self._process_voice_results(voice_results)
        
        # Process sentiment analysis results
        if sentiment_results:
            component_scores['sentiment_analysis'] = self._process_sentiment_results(sentiment_results)
        
        # Process keyword matching results
        if keyword_results:
            component_scores['keyword_matching'] = self._process_keyword_results(keyword_results)
        
        # Process facial analysis results
        if facial_results:
            component_scores['facial_analysis'] = self._process_facial_results(facial_results)
        
        # Calculate weighted final scores
        final_scores = self._calculate_weighted_scores(component_scores)
        
        # Generate comprehensive report
        comprehensive_report = {
            'final_scores': final_scores,
            'component_scores': component_scores,
            'component_weights': self.component_weights,
            'recommendations': self._generate_recommendations(final_scores),
            'risk_assessment': self._assess_risk_level(final_scores),
            'confidence_metrics': self._calculate_overall_confidence(component_scores)
        }
        
        logger.info(f"✅ Comprehensive assessment completed - Risk Level: {comprehensive_report['risk_assessment']['overall_risk']}")
        
        return comprehensive_report
    
    def _process_voice_results(self, voice_results: Dict) -> Dict[str, float]:
        """Process voice analysis results into standardized format"""
        if not voice_results:
            return {'depression': 0, 'anxiety': 0, 'stress': 0, 'confidence': 0}
        
        # Extract scores from voice analysis
        depression_score = voice_results.get('depression', {}).get('score', 0)
        anxiety_score = voice_results.get('anxiety', {}).get('score', 0)
        stress_score = voice_results.get('stress', {}).get('score', 0)
        confidence = voice_results.get('depression', {}).get('confidence', 0.5)
        
        return {
            'depression': min(depression_score, 100),
            'anxiety': min(anxiety_score, 100),
            'stress': min(stress_score, 100),
            'confidence': confidence
        }
    
    def _process_sentiment_results(self, sentiment_results: Dict) -> Dict[str, float]:
        """Process sentiment analysis results into mental health scores"""
        if not sentiment_results:
            return {'depression': 0, 'anxiety': 0, 'stress': 0, 'confidence': 0}
        
        # Extract sentiment scores
        negative_score = sentiment_results.get('negative', 0)
        positive_score = sentiment_results.get('positive', 0)
        neutral_score = sentiment_results.get('neutral', 0)
        
        # Convert sentiment to mental health indicators
        # High negative sentiment correlates with depression/anxiety
        depression_score = negative_score * 80  # Scale to 0-80
        anxiety_score = negative_score * 70 + (1 - neutral_score) * 20  # Anxiety from negativity and uncertainty
        stress_score = negative_score * 60 + (1 - positive_score) * 30  # Stress from negativity and lack of positivity
        
        # Confidence based on sentiment clarity
        confidence = max(negative_score, positive_score, neutral_score)
        
        return {
            'depression': min(depression_score, 100),
            'anxiety': min(anxiety_score, 100),
            'stress': min(stress_score, 100),
            'confidence': confidence
        }
    
    def _process_keyword_results(self, keyword_results: Dict) -> Dict[str, float]:
        """Process keyword matching results into mental health scores"""
        if not keyword_results:
            return {'depression': 0, 'anxiety': 0, 'stress': 0, 'confidence': 0}
        
        # Extract keyword counts/scores
        depression_keywords = keyword_results.get('depression_indicators', 0)
        anxiety_keywords = keyword_results.get('anxiety_indicators', 0)
        stress_keywords = keyword_results.get('stress_indicators', 0)
        total_words = keyword_results.get('total_words', 1)
        
        # Calculate scores based on keyword density
        depression_score = min((depression_keywords / total_words) * 500, 100)  # Scale appropriately
        anxiety_score = min((anxiety_keywords / total_words) * 500, 100)
        stress_score = min((stress_keywords / total_words) * 500, 100)
        
        # Confidence based on total keyword matches
        total_keywords = depression_keywords + anxiety_keywords + stress_keywords
        confidence = min(total_keywords / 10, 1.0)  # Max confidence at 10+ keywords
        
        return {
            'depression': depression_score,
            'anxiety': anxiety_score,
            'stress': stress_score,
            'confidence': confidence
        }
    
    def _process_facial_results(self, facial_results: Dict) -> Dict[str, float]:
        """Process facial analysis results into mental health scores"""
        if not facial_results:
            return {'depression': 0, 'anxiety': 0, 'stress': 0, 'confidence': 0}
        
        # Extract facial emotion scores
        sadness = facial_results.get('sadness', 0)
        fear = facial_results.get('fear', 0)
        anger = facial_results.get('anger', 0)
        happiness = facial_results.get('happiness', 0)
        
        # Map emotions to mental health indicators
        depression_score = sadness * 80 + (1 - happiness) * 20
        anxiety_score = fear * 70 + sadness * 20
        stress_score = anger * 60 + fear * 30
        
        # Confidence based on emotion detection quality
        confidence = max(sadness, fear, anger, happiness)
        
        return {
            'depression': min(depression_score, 100),
            'anxiety': min(anxiety_score, 100),
            'stress': min(stress_score, 100),
            'confidence': confidence
        }
    
    def _calculate_weighted_scores(self, component_scores: Dict) -> Dict[str, Any]:
        """Calculate final weighted scores from all components"""
        
        final_scores = {'depression': 0, 'anxiety': 0, 'stress': 0}
        total_weight = 0
        
        # Calculate weighted average for each mental health category
        for component, weight in self.component_weights.items():
            if component in component_scores:
                scores = component_scores[component]
                confidence = scores.get('confidence', 0)
                
                # Weight by both component weight and confidence
                effective_weight = weight * confidence
                total_weight += effective_weight
                
                final_scores['depression'] += scores['depression'] * effective_weight
                final_scores['anxiety'] += scores['anxiety'] * effective_weight
                final_scores['stress'] += scores['stress'] * effective_weight
        
        # Normalize by total weight
        if total_weight > 0:
            for category in list(final_scores.keys()):  # Create a copy of keys to avoid iteration issues
                final_scores[category] = round(final_scores[category] / total_weight, 2)

        # Add severity classifications
        categories = ['depression', 'anxiety', 'stress']  # Use fixed list instead of iterating over changing dict
        for category in categories:
            score = final_scores[category]
            severity = self._score_to_severity(score, category)
            final_scores[f'{category}_severity'] = severity
        
        return final_scores
    
    def _score_to_severity(self, score: float, category: str) -> str:
        """Convert numerical score to DASS-21 severity level"""
        thresholds = self.severity_thresholds.get(category, self.severity_thresholds['depression'])
        
        for severity, (min_score, max_score) in thresholds.items():
            if min_score <= score <= max_score:
                return severity
        
        return 'normal'
    
    def _generate_recommendations(self, final_scores: Dict) -> List[str]:
        """Generate recommendations based on final scores"""
        recommendations = []
        
        # Check each category for recommendations
        for category in ['depression', 'anxiety', 'stress']:
            score = final_scores.get(category, 0)
            severity = final_scores.get(f'{category}_severity', 'normal')
            
            if severity in ['severe', 'extremely_severe']:
                recommendations.append(f"Immediate professional consultation recommended for {category}")
            elif severity == 'moderate':
                recommendations.append(f"Consider professional support for {category} management")
            elif severity == 'mild':
                recommendations.append(f"Monitor {category} levels and practice self-care techniques")
        
        if not recommendations:
            recommendations.append("Mental health indicators appear normal - continue healthy practices")
        
        return recommendations
    
    def _assess_risk_level(self, final_scores: Dict) -> Dict[str, Any]:
        """Assess overall risk level based on final scores"""
        
        # Get highest severity level
        severities = [
            final_scores.get('depression_severity', 'normal'),
            final_scores.get('anxiety_severity', 'normal'),
            final_scores.get('stress_severity', 'normal')
        ]
        
        severity_levels = ['normal', 'mild', 'moderate', 'severe', 'extremely_severe']
        max_severity_index = max([severity_levels.index(s) for s in severities])
        overall_severity = severity_levels[max_severity_index]
        
        # Map to risk levels
        risk_mapping = {
            'normal': 'low',
            'mild': 'low',
            'moderate': 'medium',
            'severe': 'high',
            'extremely_severe': 'critical'
        }
        
        return {
            'overall_risk': risk_mapping[overall_severity],
            'highest_severity': overall_severity,
            'requires_attention': overall_severity in ['moderate', 'severe', 'extremely_severe']
        }
    
    def _calculate_overall_confidence(self, component_scores: Dict) -> Dict[str, float]:
        """Calculate overall confidence metrics"""
        
        confidences = []
        for component, scores in component_scores.items():
            if scores.get('confidence', 0) > 0:
                confidences.append(scores['confidence'])
        
        if not confidences:
            return {'overall_confidence': 0.0, 'component_count': 0}
        
        return {
            'overall_confidence': round(np.mean(confidences), 2),
            'component_count': len(confidences),
            'confidence_range': {
                'min': round(min(confidences), 2),
                'max': round(max(confidences), 2)
            }
        }
