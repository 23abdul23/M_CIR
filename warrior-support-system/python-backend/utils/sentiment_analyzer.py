#!/usr/bin/env python3
"""
Sentiment Analyzer using local CPU-based models
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.hindi_sentiment import analyze_hindi_sentiment, get_emotion_analysis
from models.mental_health_analyzer import QWarriorMentalHealthAnalyzer

class SentimentAnalyzer:
    """
    Local CPU-based sentiment analyzer for both Hindi and English text
    """
    
    def __init__(self):
        self.qwarrior_analyzer = QWarriorMentalHealthAnalyzer()
        
    def analyze_sentiment(self, text: str, language: str = "auto") -> dict:
        """
        Analyze sentiment of text using local models
        
        Args:
            text: Input text to analyze
            language: Language of text ("hindi", "english", or "auto")
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            # Auto-detect language if not specified
            if language == "auto":
                language = self._detect_language(text)
            
            if language == "hindi" or self._contains_hindi(text):
                # Use Hindi sentiment analyzer
                result = analyze_hindi_sentiment(text)
                
                return {
                    "sentiment": result["sentiment_label"].lower(),
                    "score": result["sentiment_score"],
                    "confidence": result["confidence_score"],
                    "language": "hindi",
                    "raw_result": result
                }
            else:
                # Use QWarrior analyzer for English
                analysis = self.qwarrior_analyzer.analyze_text_sentiment(text, "english")
                
                # Convert to standardized format
                sentiment_score = analysis["sentiment_score"]
                if sentiment_score > 0.1:
                    sentiment = "positive"
                elif sentiment_score < -0.1:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                
                return {
                    "sentiment": sentiment,
                    "score": sentiment_score,
                    "confidence": analysis["sentiment_confidence"],
                    "language": "english",
                    "raw_result": analysis
                }
                
        except Exception as e:
            # Fallback to simple keyword-based analysis
            return self._fallback_sentiment_analysis(text)
    
    def _detect_language(self, text: str) -> str:
        """Detect if text is Hindi or English"""
        if self._contains_hindi(text):
            return "hindi"
        else:
            return "english"
    
    def _contains_hindi(self, text: str) -> bool:
        """Check if text contains Hindi characters"""
        hindi_range = range(0x0900, 0x097F)  # Devanagari Unicode range
        return any(ord(char) in hindi_range for char in text)
    
    def _fallback_sentiment_analysis(self, text: str) -> dict:
        """Fallback sentiment analysis using keywords"""
        positive_keywords = [
            "good", "great", "excellent", "happy", "positive", "wonderful", "amazing",
            "अच्छा", "खुश", "बेहतर", "सुखी", "प्रसन्न", "उत्तम"
        ]
        
        negative_keywords = [
            "bad", "terrible", "awful", "sad", "negative", "horrible", "depressed",
            "बुरा", "दुखी", "परेशान", "चिंतित", "उदास", "निराश"
        ]
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_keywords if word in text_lower)
        neg_count = sum(1 for word in negative_keywords if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            score = 0.7
        elif neg_count > pos_count:
            sentiment = "negative"
            score = -0.7
        else:
            sentiment = "neutral"
            score = 0.0
        
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": 0.6,
            "language": self._detect_language(text),
            "raw_result": {"pos_count": pos_count, "neg_count": neg_count}
        }
    
    def get_emotion_analysis(self, text: str) -> dict:
        """Get detailed emotion analysis"""
        if self._contains_hindi(text):
            return get_emotion_analysis(text)
        else:
            # Use QWarrior analyzer for English emotion analysis
            analysis = self.qwarrior_analyzer.analyze_text_sentiment(text, "english")
            return {
                "sentiment_analysis": self.analyze_sentiment(text),
                "emotion_indicators": analysis.get("keywords", {}),
                "risk_level": analysis.get("risk_level", "normal")
            }
    
    def batch_analyze(self, texts: list) -> list:
        """Analyze multiple texts"""
        results = []
        for text in texts:
            results.append(self.analyze_sentiment(text))
        return results
