"""
Weighted AI Assessment Engine
Combines multiple AI assessment components with configurable weights
"""

import numpy as np
from typing import Dict, Optional

class WeightedAssessmentEngine:
    """
    Weighted assessment engine that combines multiple AI analysis components
    Implements configurable weighting system for comprehensive mental health assessment
    """
    
    def __init__(self):
        """Initialize the weighted assessment engine with default component weights"""
        # Component weights - voice analysis has highest priority as requested
        self.component_weights = {
            'voice_analysis': 0.40,      # Highest weight for voice tone analysis
            'sentiment_analysis': 0.25,   # Text sentiment analysis
            'keyword_analysis': 0.20,     # Mental health keyword detection
            'facial_analysis': 0.15       # Lowest weight as requested
        }
        
        # DASS-21 compatible severity thresholds
        self.severity_thresholds = {
            'depression': {'normal': 9, 'mild': 13, 'moderate': 20, 'severe': 27},
            'anxiety': {'normal': 7, 'mild': 9, 'moderate': 14, 'severe': 19},
            'stress': {'normal': 14, 'mild': 18, 'moderate': 25, 'severe': 33}
        }
    
    def calculate_comprehensive_scores(self, 
                                     voice_results: Optional[Dict] = None,
                                     sentiment_results: Optional[Dict] = None,
                                     keyword_results: Optional[Dict] = None,
                                     facial_results: Optional[Dict] = None) -> Dict:
        """
        Calculate comprehensive weighted mental health scores
        Combines all available AI assessment components with configured weights
        """
        try:
            # Initialize component scores
            component_scores = {
                'depression': {},
                'anxiety': {},
                'stress': {}
            }
            
            # Extract voice analysis scores (highest weight: 40%)
            if voice_results:
                for condition in ['depression', 'anxiety', 'stress']:
                    if condition in voice_results:
                        score = voice_results[condition].get('score', 0)
                        component_scores[condition]['voice'] = score
            
            # Extract sentiment analysis scores (25% weight)
            if sentiment_results:
                sentiment_scores = self._convert_sentiment_to_scores(sentiment_results)
                for condition in ['depression', 'anxiety', 'stress']:
                    component_scores[condition]['sentiment'] = sentiment_scores[condition]
            
            # Extract keyword analysis scores (20% weight)
            if keyword_results:
                keyword_scores = self._convert_keywords_to_scores(keyword_results)
                for condition in ['depression', 'anxiety', 'stress']:
                    component_scores[condition]['keyword'] = keyword_scores[condition]
            
            # Extract facial analysis scores (lowest weight: 15%)
            if facial_results:
                facial_scores = self._convert_facial_to_scores(facial_results)
                for condition in ['depression', 'anxiety', 'stress']:
                    component_scores[condition]['facial'] = facial_scores[condition]
            
            # Calculate weighted final scores
            final_scores = self._calculate_weighted_scores(component_scores)
            
            # Determine overall risk assessment
            risk_assessment = self._assess_overall_risk(final_scores)
            
            return {
                'final_scores': final_scores,
                'component_scores': component_scores,
                'component_weights': self.component_weights,
                'risk_assessment': risk_assessment,
                'assessment_quality': self._assess_quality(component_scores)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _convert_sentiment_to_scores(self, sentiment_results: Dict) -> Dict[str, float]:
        """Convert sentiment analysis results to mental health scores"""
        negative_score = sentiment_results.get('negative', 0)
        positive_score = sentiment_results.get('positive', 0)
        neutral_score = sentiment_results.get('neutral', 0)
        
        # Higher negative sentiment indicates higher mental health risk
        base_score = negative_score * 50
        
        # Adjust based on positive sentiment (protective factor)
        adjustment = positive_score * 10
        
        return {
            'depression': max(0, base_score - adjustment),
            'anxiety': max(0, base_score * 0.8 - adjustment),
            'stress': max(0, base_score * 0.9 - adjustment)
        }
    
    def _convert_keywords_to_scores(self, keyword_results: Dict) -> Dict[str, float]:
        """Convert keyword analysis results to mental health scores"""
        total_words = keyword_results.get('total_words', 1)
        
        # Calculate keyword density for each condition
        depression_density = keyword_results.get('depression_indicators', 0) / total_words
        anxiety_density = keyword_results.get('anxiety_indicators', 0) / total_words
        stress_density = keyword_results.get('stress_indicators', 0) / total_words
        
        # Convert density to scores (0-100 scale)
        return {
            'depression': min(depression_density * 200, 100),
            'anxiety': min(anxiety_density * 200, 100),
            'stress': min(stress_density * 200, 100)
        }
    
    def _convert_facial_to_scores(self, facial_results: Dict) -> Dict[str, float]:
        """Convert facial analysis results to mental health scores"""
        sadness = facial_results.get('sadness', 0)
        fear = facial_results.get('fear', 0)
        anger = facial_results.get('anger', 0)
        happiness = facial_results.get('happiness', 0)
        
        # Convert facial emotions to mental health indicators
        return {
            'depression': min(sadness * 80 + (1 - happiness) * 20, 100),
            'anxiety': min(fear * 70 + sadness * 30, 100),
            'stress': min(anger * 60 + fear * 40, 100)
        }
    
    def _calculate_weighted_scores(self, component_scores: Dict) -> Dict:
        """Calculate final weighted scores from all components"""
        final_scores = {'depression': 0, 'anxiety': 0, 'stress': 0}
        total_weight = 0
        
        # Weight mapping for components
        weight_mapping = {
            'voice': self.component_weights['voice_analysis'],
            'sentiment': self.component_weights['sentiment_analysis'],
            'keyword': self.component_weights['keyword_analysis'],
            'facial': self.component_weights['facial_analysis']
        }
        
        # Calculate weighted sum for each condition
        for condition in ['depression', 'anxiety', 'stress']:
            weighted_sum = 0
            condition_weight = 0
            
            for component, score in component_scores[condition].items():
                if component in weight_mapping:
                    weight = weight_mapping[component]
                    weighted_sum += score * weight
                    condition_weight += weight
            
            if condition_weight > 0:
                final_scores[condition] = weighted_sum / condition_weight
            
            total_weight = max(total_weight, condition_weight)
        
        # Add severity classifications
        categories = ['depression', 'anxiety', 'stress']
        for category in categories:
            score = final_scores[category]
            severity = self._score_to_severity(score, category)
            final_scores[f'{category}_severity'] = severity
        
        return final_scores
    
    def _score_to_severity(self, score: float, condition: str) -> str:
        """Convert numerical score to DASS-21 compatible severity level"""
        thresholds = self.severity_thresholds[condition]
        
        if score <= thresholds['normal']:
            return 'normal'
        elif score <= thresholds['mild']:
            return 'mild'
        elif score <= thresholds['moderate']:
            return 'moderate'
        elif score <= thresholds['severe']:
            return 'severe'
        else:
            return 'extremely_severe'
    
    def _assess_overall_risk(self, final_scores: Dict) -> Dict:
        """Assess overall mental health risk based on final scores"""
        depression_score = final_scores.get('depression', 0)
        anxiety_score = final_scores.get('anxiety', 0)
        stress_score = final_scores.get('stress', 0)
        
        max_score = max(depression_score, anxiety_score, stress_score)
        avg_score = (depression_score + anxiety_score + stress_score) / 3
        
        # Determine risk level
        if max_score >= 50 or avg_score >= 35:
            risk_level = 'high'
        elif max_score >= 25 or avg_score >= 20:
            risk_level = 'moderate'
        elif max_score >= 15 or avg_score >= 10:
            risk_level = 'low'
        else:
            risk_level = 'minimal'
        
        return {
            'overall_risk': risk_level,
            'max_score': max_score,
            'average_score': avg_score,
            'primary_concern': self._identify_primary_concern(final_scores)
        }
    
    def _identify_primary_concern(self, final_scores: Dict) -> str:
        """Identify the primary area of mental health concern"""
        scores = {
            'depression': final_scores.get('depression', 0),
            'anxiety': final_scores.get('anxiety', 0),
            'stress': final_scores.get('stress', 0)
        }
        
        return max(scores, key=scores.get)
    
    def _assess_quality(self, component_scores: Dict) -> Dict:
        """Assess the quality and completeness of the assessment"""
        total_components = len(self.component_weights)
        available_components = 0
        
        # Check which components provided data
        sample_condition = 'depression'
        for component in ['voice', 'sentiment', 'keyword', 'facial']:
            if component in component_scores[sample_condition]:
                available_components += 1
        
        completeness = available_components / total_components
        
        # Determine quality level
        if completeness >= 0.75:
            quality = 'high'
        elif completeness >= 0.5:
            quality = 'moderate'
        elif completeness >= 0.25:
            quality = 'low'
        else:
            quality = 'insufficient'
        
        return {
            'completeness': completeness,
            'quality': quality,
            'available_components': available_components,
            'total_components': total_components
        }
