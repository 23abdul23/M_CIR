#!/usr/bin/env python3
"""
Mental State Analyzer using local CPU-based models
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.mental_health_analyzer import QWarriorMentalHealthAnalyzer
from utils.sentiment_analyzer import SentimentAnalyzer

class MentalStateAnalyzer:
    """
    Local CPU-based mental state analyzer for detecting various mental health conditions
    """
    
    def __init__(self):
        self.qwarrior_analyzer = QWarriorMentalHealthAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Mental state keywords for detection
        self.mental_state_keywords = {
            "depression": [
                "sad", "hopeless", "worthless", "empty", "depressed", "down", "low",
                "उदास", "निराश", "हताश", "खाली", "अवसाद", "दुखी"
            ],
            "anxiety": [
                "anxious", "worried", "nervous", "panic", "fear", "scared", "tense",
                "चिंतित", "परेशान", "घबराहट", "डर", "भय", "तनाव"
            ],
            "ptsd": [
                "nightmares", "flashbacks", "trauma", "combat", "memories", "avoidance",
                "बुरे सपने", "यादें", "आघात", "युद्ध", "स्मृति", "बचना"
            ],
            "stress": [
                "stressed", "overwhelmed", "pressure", "burden", "exhausted", "tired",
                "तनाव", "दबाव", "बोझ", "थका", "परेशानी", "भार"
            ],
            "anger": [
                "angry", "furious", "rage", "mad", "irritated", "frustrated",
                "गुस्सा", "क्रोध", "चिढ़", "नाराज", "गुस्से", "क्रोधित"
            ],
            "healthy": [
                "good", "fine", "okay", "normal", "stable", "balanced", "positive",
                "अच्छा", "ठीक", "सामान्य", "स्थिर", "संतुलित", "सकारात्मक"
            ]
        }
    
    def analyze_mental_state(self, text: str, language: str = "auto") -> dict:
        """
        Analyze mental state from text using local models
        
        Args:
            text: Input text to analyze
            language: Language of text ("hindi", "english", or "auto")
            
        Returns:
            Dictionary with mental state analysis results
        """
        try:
            # Get sentiment analysis first
            sentiment_result = self.sentiment_analyzer.analyze_sentiment(text, language)
            
            # Use QWarrior analyzer for comprehensive analysis
            qwarrior_result = self.qwarrior_analyzer.analyze_text_sentiment(
                text, 
                sentiment_result["language"]
            )
            
            # Detect specific mental states using keywords
            detected_states = self._detect_mental_states(text)
            
            # Determine primary mental state
            primary_state = self._determine_primary_state(
                detected_states, 
                sentiment_result, 
                qwarrior_result
            )
            
            # Calculate confidence score
            confidence = self._calculate_confidence(
                detected_states, 
                sentiment_result, 
                qwarrior_result
            )
            
            return {
                "detected_states": detected_states,
                "primary_state": primary_state,
                "confidence": confidence,
                "risk_level": qwarrior_result.get("risk_level", "normal"),
                "risk_score": qwarrior_result.get("risk_score", 0),
                "sentiment_analysis": sentiment_result,
                "keywords_found": qwarrior_result.get("keywords", {}),
                "military_factors": qwarrior_result.get("military_factors", {}),
                "language": sentiment_result["language"]
            }
            
        except Exception as e:
            # Fallback analysis
            return self._fallback_mental_state_analysis(text)
    
    def _detect_mental_states(self, text: str) -> list:
        """Detect mental states based on keyword matching"""
        text_lower = text.lower()
        detected_states = []
        
        for state, keywords in self.mental_state_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                detected_states.append({
                    "state": state,
                    "matches": matches,
                    "keywords": [kw for kw in keywords if kw in text_lower]
                })
        
        # Sort by number of matches
        detected_states.sort(key=lambda x: x["matches"], reverse=True)
        return detected_states
    
    def _determine_primary_state(self, detected_states: list, sentiment_result: dict, qwarrior_result: dict) -> str:
        """Determine the primary mental state"""
        if not detected_states:
            # Use sentiment to determine state
            sentiment = sentiment_result["sentiment"]
            if sentiment == "negative":
                return "mild_concern"
            elif sentiment == "positive":
                return "healthy"
            else:
                return "neutral"
        
        # Use the state with most matches
        primary = detected_states[0]["state"]
        
        # Adjust based on risk level
        risk_level = qwarrior_result.get("risk_level", "normal")
        if risk_level == "severe":
            if primary == "healthy":
                primary = "moderate_concern"
        elif risk_level == "moderate":
            if primary == "healthy":
                primary = "mild_concern"
        
        return primary
    
    def _calculate_confidence(self, detected_states: list, sentiment_result: dict, qwarrior_result: dict) -> float:
        """Calculate confidence score for the analysis"""
        base_confidence = sentiment_result.get("confidence", 0.5)
        
        # Increase confidence if multiple indicators align
        if detected_states:
            keyword_confidence = min(0.4, detected_states[0]["matches"] * 0.1)
            base_confidence += keyword_confidence
        
        # Factor in QWarrior confidence
        qwarrior_confidence = qwarrior_result.get("sentiment_confidence", 0.5)
        combined_confidence = (base_confidence + qwarrior_confidence) / 2
        
        return min(1.0, combined_confidence)
    
    def _fallback_mental_state_analysis(self, text: str) -> dict:
        """Fallback analysis when main models fail"""
        detected_states = self._detect_mental_states(text)
        
        if detected_states:
            primary_state = detected_states[0]["state"]
        else:
            primary_state = "neutral"
        
        return {
            "detected_states": [state["state"] for state in detected_states],
            "primary_state": primary_state,
            "confidence": 0.6,
            "risk_level": "normal",
            "risk_score": 1,
            "sentiment_analysis": {"sentiment": "neutral", "score": 0.0},
            "keywords_found": {},
            "military_factors": {},
            "language": "english"
        }
    
    def analyze_multiple_responses(self, responses: list) -> dict:
        """Analyze multiple responses to get overall mental state"""
        all_results = []
        
        for response in responses:
            if isinstance(response, dict) and "text" in response:
                result = self.analyze_mental_state(response["text"])
                all_results.append(result)
            elif isinstance(response, str):
                result = self.analyze_mental_state(response)
                all_results.append(result)
        
        if not all_results:
            return {"error": "No valid responses to analyze"}
        
        # Aggregate results
        all_states = []
        total_risk_score = 0
        total_confidence = 0
        
        for result in all_results:
            all_states.extend(result["detected_states"])
            total_risk_score += result["risk_score"]
            total_confidence += result["confidence"]
        
        # Calculate averages
        avg_risk_score = total_risk_score / len(all_results)
        avg_confidence = total_confidence / len(all_results)
        
        # Determine overall state
        state_counts = {}
        for result in all_results:
            state = result["primary_state"]
            state_counts[state] = state_counts.get(state, 0) + 1
        
        overall_state = max(state_counts.items(), key=lambda x: x[1])[0]
        
        return {
            "overall_state": overall_state,
            "average_risk_score": avg_risk_score,
            "average_confidence": avg_confidence,
            "individual_results": all_results,
            "state_distribution": state_counts,
            "total_responses": len(all_results)
        }
