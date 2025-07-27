#!/usr/bin/env python3
"""
Advanced Mental Health Analyzer using RoBERTa and AI4Indic models
Similar to culture project implementation with local GPU models
"""

import logging
import torch
import numpy as np
from typing import Dict, List, Optional, Tuple
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedMentalHealthAnalyzer:
    """
    Advanced mental health analyzer using multiple local models
    """
    
    def __init__(self):
        """Initialize the advanced analyzer"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sentiment_model = None
        self.emotion_model = None
        self.hinglish_model = None
        self.is_initialized = False

        # Configure proxy settings for model downloads
        self._configure_proxy()

        logger.info(f"🧠 Advanced Mental Health Analyzer initializing on {self.device}")
        self._initialize_models()

    def _configure_proxy(self):
        """Configure proxy settings for model downloads"""
        import os

        # Set proxy environment variables
        proxy_url = "http://iit2024036:Mayank%402005@172.31.2.4:8080"

        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url

        # Also set for requests library used by transformers
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['CURL_CA_BUNDLE'] = ''

        logger.info("🌐 Proxy configured for model downloads")
    
    def _initialize_models(self):
        """Initialize models with offline-first approach"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
            import torch
            import os
            from pathlib import Path

            logger.info(f"🚀 Initializing models on {self.device} (offline-first mode)")

            # Initialize all models as None first
            self.sentiment_tokenizer = None
            self.sentiment_model = None
            self.emotion_pipeline = None
            self.mental_health_pipeline = None
            self.multilingual_pipeline = None

            models_loaded = []

            # Check if sentiment model exists in cache before trying to load
            try:
                logger.info("📦 Checking for cached sentiment model...")

                # Quick cache check first
                cache_dir = Path.home() / ".cache" / "huggingface" / "transformers"
                sentiment_cache_exists = False

                if cache_dir.exists():
                    for item in cache_dir.iterdir():
                        if "twitter-roberta-base-sentiment" in item.name.lower():
                            sentiment_cache_exists = True
                            break

                if sentiment_cache_exists:
                    logger.info("📁 Found sentiment model in cache, loading...")
                    self.sentiment_tokenizer = AutoTokenizer.from_pretrained(
                        "cardiffnlp/twitter-roberta-base-sentiment-latest",
                        local_files_only=True
                    )
                    self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
                        "cardiffnlp/twitter-roberta-base-sentiment-latest",
                        local_files_only=True,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    )

                    if self.device == "cuda":
                        self.sentiment_model = self.sentiment_model.to(self.device)

                    models_loaded.append("sentiment")
                    logger.info("✅ Sentiment model loaded from cache")
                else:
                    logger.info("📭 Sentiment model not found in cache - skipping to avoid download")
                    self.sentiment_tokenizer = None
                    self.sentiment_model = None

            except Exception as e:
                logger.info(f"📭 Sentiment model loading failed: {str(e)[:100]}...")
                self.sentiment_tokenizer = None
                self.sentiment_model = None

            # Check if emotion model exists in cache before trying to load
            try:
                logger.info("📦 Checking for cached emotion model...")

                # Check if model files exist in cache directory
                cache_dir = Path.home() / ".cache" / "huggingface" / "transformers"
                model_cache_exists = False

                # Look for emotion model cache
                if cache_dir.exists():
                    for item in cache_dir.iterdir():
                        if "emotion" in item.name.lower() and "distilroberta" in item.name.lower():
                            model_cache_exists = True
                            break

                if model_cache_exists:
                    logger.info("📁 Found emotion model in cache, loading...")
                    self.emotion_pipeline = pipeline(
                        "text-classification",
                        model="j-hartmann/emotion-english-distilroberta-base",
                        device=0 if self.device == "cuda" else -1,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                        local_files_only=True
                    )
                    models_loaded.append("emotion")
                    logger.info("✅ Emotion model loaded from cache")
                else:
                    logger.info("📭 Emotion model not found in cache - skipping to avoid download")
                    self.emotion_pipeline = None

            except Exception as e:
                logger.info(f"📭 Emotion model loading failed: {str(e)[:100]}...")
                self.emotion_pipeline = None

            # Skip other models that might cause hanging
            logger.info("⏭️ Skipping other models to prevent hanging")

            # Check GPU memory usage if models loaded
            if self.device == "cuda" and models_loaded:
                try:
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                    gpu_allocated = torch.cuda.memory_allocated(0) / 1024**3
                    logger.info(f"🎮 GPU Memory: {gpu_allocated:.1f}GB / {gpu_memory:.1f}GB allocated")
                except Exception:
                    pass

            # Set initialization status
            if models_loaded:
                self.is_initialized = True
                logger.info(f"✅ Advanced Mental Health Analyzer initialized with models: {models_loaded}")
            else:
                self.is_initialized = False
                logger.info("📊 No cached models found - using enhanced rule-based analysis")

        except Exception as e:
            logger.warning(f"⚠️ Model initialization failed: {e}")
            logger.info("🔄 Using enhanced rule-based analysis (offline mode)")

            # Ensure all models are None in case of failure
            self.sentiment_tokenizer = None
            self.sentiment_model = None
            self.emotion_pipeline = None
            self.mental_health_pipeline = None
            self.multilingual_pipeline = None
            self.is_initialized = False
    
    def analyze_comprehensive(self, responses: List[Dict], user_profile: Optional[Dict] = None) -> Dict:
        """
        Comprehensive analysis using multiple models
        
        Args:
            responses: List of user responses
            user_profile: Optional user profile information
            
        Returns:
            Comprehensive analysis results
        """
        try:
            # Combine all text responses
            combined_text = self._prepare_text_for_analysis(responses)
            
            if self.is_initialized:
                # Use advanced model analysis
                analysis = self._advanced_model_analysis(combined_text, responses)
            else:
                # Use enhanced rule-based analysis
                analysis = self._enhanced_rule_based_analysis(combined_text, responses)
            
            # Calculate comprehensive scores
            overall_score = self._calculate_comprehensive_score(analysis, responses)
            risk_level = self._assess_comprehensive_risk(overall_score, analysis)
            mental_state = self._determine_mental_state(analysis, overall_score)
            
            # Generate personalized recommendations
            recommendations = self._generate_personalized_recommendations(
                analysis, user_profile, overall_score, responses
            )
            
            return {
                "overall_score": overall_score,
                "risk_level": risk_level,
                "mental_state": mental_state,
                "detailed_analysis": analysis,
                "recommendations": recommendations,
                "confidence": analysis.get("confidence", 0.8),
                "processing_method": "advanced_models" if self.is_initialized else "enhanced_rules"
            }
            
        except Exception as e:
            logger.error(f"❌ Comprehensive analysis failed: {e}")
            return self._fallback_comprehensive_analysis(responses)
    
    def _prepare_text_for_analysis(self, responses: List[Dict]) -> str:
        """Prepare and clean text for analysis"""
        text_parts = []
        
        for response in responses:
            if response.get("response_text"):
                text = response["response_text"].strip()
                if len(text) > 0:
                    text_parts.append(text)
        
        combined = " ".join(text_parts)
        
        # Clean and normalize text
        combined = re.sub(r'\s+', ' ', combined)  # Multiple spaces to single
        combined = combined.strip()
        
        return combined
    
    def _advanced_model_analysis(self, text: str, responses: List[Dict]) -> Dict:
        """Advanced analysis using available AI models with fallback"""
        analysis = {}

        try:
            # Only use models that are actually loaded
            available_models = []

            # Sentiment analysis using RoBERTa (if available)
            if self.sentiment_model and self.sentiment_tokenizer:
                sentiment_result = self._analyze_sentiment_roberta(text)
                analysis["sentiment"] = sentiment_result
                available_models.append("sentiment")
            else:
                # Fallback sentiment analysis
                analysis["sentiment"] = self._fallback_sentiment_analysis(text)

            # Emotion detection (if available)
            if self.emotion_pipeline:
                emotion_result = self._analyze_emotions(text)
                analysis["emotions"] = emotion_result
                available_models.append("emotion")
            else:
                # Fallback emotion analysis
                analysis["emotions"] = self._fallback_emotion_analysis(text)

            # Mental health specific analysis (if available)
            if self.mental_health_pipeline:
                mental_health_result = self._analyze_mental_health_specific(text)
                analysis["mental_health"] = mental_health_result
                available_models.append("mental_health")
            else:
                # Use enhanced rule-based mental health analysis
                analysis["mental_health"] = self._rule_based_mental_health_analysis(text)

            # Language and cultural analysis (always available)
            language_analysis = self._analyze_language_patterns(text)
            analysis["language"] = language_analysis

            # Multilingual sentiment analysis (if available)
            if self.multilingual_pipeline:
                multilingual_result = self._analyze_multilingual_sentiment(text)
                analysis["multilingual"] = multilingual_result
                available_models.append("multilingual")

            # Calculate confidence based on available models
            analysis["confidence"] = self._calculate_model_confidence_adaptive(analysis, available_models)
            analysis["available_models"] = available_models

            logger.info(f"Analysis completed using models: {available_models}")

        except Exception as e:
            logger.error(f"❌ Advanced model analysis failed: {e}")
            return self._enhanced_rule_based_analysis(text, responses)

        return analysis
    
    def _analyze_sentiment_roberta(self, text: str) -> Dict:
        """Analyze sentiment using GPU-accelerated RoBERTa model"""
        try:
            # Tokenize input
            inputs = self.sentiment_tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )

            # Move to GPU if available
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # GPU inference with mixed precision
            with torch.no_grad():
                if self.device == "cuda":
                    with torch.cuda.amp.autocast():
                        outputs = self.sentiment_model(**inputs)
                else:
                    outputs = self.sentiment_model(**inputs)

                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # Labels: NEGATIVE, NEUTRAL, POSITIVE
            labels = ["negative", "neutral", "positive"]
            scores = predictions.cpu().numpy()[0]

            result = {
                "label": labels[np.argmax(scores)],
                "scores": {labels[i]: float(scores[i]) for i in range(len(labels))},
                "confidence": float(np.max(scores)),
                "processing_device": self.device
            }

            logger.info(f"GPU Sentiment analysis: {result['label']} (confidence: {result['confidence']:.3f}) on {self.device}")
            return result

        except Exception as e:
            logger.error(f"❌ GPU Sentiment analysis failed: {e}")
            return {"label": "neutral", "scores": {"negative": 0.33, "neutral": 0.34, "positive": 0.33}, "confidence": 0.5}
    
    def _analyze_emotions(self, text: str) -> Dict:
        """Analyze emotions using GPU-accelerated emotion detection model"""
        try:
            # Use GPU pipeline for emotion analysis
            emotion_results = self.emotion_pipeline(text, truncation=True, max_length=512)

            # Process results
            emotions = {}
            if isinstance(emotion_results, list):
                for result in emotion_results:
                    emotions[result['label']] = result['score']
            else:
                emotions[emotion_results['label']] = emotion_results['score']

            # Find dominant emotion
            dominant_emotion = max(emotions, key=emotions.get)

            result = {
                "dominant_emotion": dominant_emotion,
                "all_emotions": emotions,
                "confidence": emotions[dominant_emotion],
                "processing_device": self.device
            }

            logger.info(f"GPU Emotion analysis: {dominant_emotion} (confidence: {result['confidence']:.3f}) on {self.device}")
            return result

        except Exception as e:
            logger.error(f"❌ GPU Emotion analysis failed: {e}")
            return {"dominant_emotion": "neutral", "all_emotions": {"neutral": 1.0}, "confidence": 0.5}
    
    def _analyze_mental_health_specific(self, text: str) -> Dict:
        """Analyze using GPU-accelerated mental health specific model"""
        try:
            # Use GPU pipeline for mental health analysis
            mh_results = self.mental_health_pipeline(text, truncation=True, max_length=512)

            if isinstance(mh_results, list):
                result = {
                    "classification": mh_results[0]['label'],
                    "confidence": mh_results[0]['score'],
                    "all_scores": {r['label']: r['score'] for r in mh_results},
                    "processing_device": self.device
                }
            else:
                result = {
                    "classification": mh_results['label'],
                    "confidence": mh_results['score'],
                    "all_scores": {mh_results['label']: mh_results['score']},
                    "processing_device": self.device
                }

            logger.info(f"GPU Mental health analysis: {result['classification']} (confidence: {result['confidence']:.3f}) on {self.device}")
            return result

        except Exception as e:
            logger.error(f"❌ GPU Mental health analysis failed: {e}")
            return {"classification": "normal", "confidence": 0.5, "all_scores": {"normal": 0.5}}
    
    def _analyze_language_patterns(self, text: str) -> Dict:
        """Analyze language patterns for Hinglish and cultural context"""
        
        # Detect language mix
        hindi_words = len(re.findall(r'[\u0900-\u097F]+', text))  # Devanagari script
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        
        # Hinglish patterns
        hinglish_patterns = [
            r'\b(hai|hain|hu|hoon|kar|kya|kaise|kahan|kab|kyun)\b',
            r'\b(acha|aur|bhi|toh|woh|yeh|iska|uska)\b',
            r'\b(nahi|nahin|haan|ji|bas|abhi|phir)\b'
        ]
        
        hinglish_matches = sum(len(re.findall(pattern, text.lower())) for pattern in hinglish_patterns)
        
        # Determine language type
        if hindi_words > english_words:
            language_type = "hindi_dominant"
        elif hinglish_matches > 0:
            language_type = "hinglish"
        else:
            language_type = "english"
        
        return {
            "language_type": language_type,
            "hindi_words": hindi_words,
            "english_words": english_words,
            "hinglish_indicators": hinglish_matches,
            "cultural_context": "indian_military" if hinglish_matches > 0 or hindi_words > 0 else "general"
        }

    def _analyze_multilingual_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using multilingual model for Hinglish support"""
        try:
            if not self.multilingual_pipeline:
                return {"error": "Multilingual model not available"}

            # Use GPU pipeline for multilingual analysis
            ml_results = self.multilingual_pipeline(text, truncation=True, max_length=512)

            if isinstance(ml_results, list):
                result = {
                    "sentiment": ml_results[0]['label'],
                    "confidence": ml_results[0]['score'],
                    "all_scores": {r['label']: r['score'] for r in ml_results},
                    "processing_device": self.device
                }
            else:
                result = {
                    "sentiment": ml_results['label'],
                    "confidence": ml_results['score'],
                    "all_scores": {ml_results['label']: ml_results['score']},
                    "processing_device": self.device
                }

            logger.info(f"GPU Multilingual analysis: {result['sentiment']} (confidence: {result['confidence']:.3f}) on {self.device}")
            return result

        except Exception as e:
            logger.error(f"❌ GPU Multilingual analysis failed: {e}")
            return {"sentiment": "neutral", "confidence": 0.5, "all_scores": {"neutral": 0.5}}
    
    def _calculate_model_confidence(self, sentiment: Dict, emotion: Dict, mental_health: Dict) -> float:
        """Calculate overall confidence from multiple models"""
        confidences = [
            sentiment.get("confidence", 0.5),
            emotion.get("confidence", 0.5),
            mental_health.get("confidence", 0.5)
        ]
        
        return np.mean(confidences)

    def _fallback_sentiment_analysis(self, text: str) -> Dict:
        """Fallback sentiment analysis using rule-based approach"""
        positive_words = [
            "good", "great", "excellent", "happy", "joyful", "content", "satisfied", "peaceful",
            "calm", "relaxed", "confident", "motivated", "energetic", "optimistic", "pleased",
            "अच्छा", "बहुत अच्छा", "खुश", "संतुष्ट", "शांत", "आत्मविश्वास", "ऊर्जावान", "खुशी"
        ]

        negative_words = [
            "bad", "terrible", "awful", "sad", "depressed", "angry", "frustrated", "stressed",
            "anxious", "worried", "scared", "afraid", "hopeless", "worthless", "overwhelmed",
            "बुरा", "दुखी", "परेशान", "चिंता", "डर", "निराश", "तनाव", "गुस्सा"
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            label = "positive"
            confidence = min(0.9, 0.6 + (positive_count * 0.1))
        elif negative_count > positive_count:
            label = "negative"
            confidence = min(0.9, 0.6 + (negative_count * 0.1))
        else:
            label = "neutral"
            confidence = 0.5

        return {
            "label": label,
            "confidence": confidence,
            "scores": {
                "positive": positive_count / max(1, positive_count + negative_count),
                "negative": negative_count / max(1, positive_count + negative_count),
                "neutral": 0.5 if positive_count == negative_count else 0.1
            },
            "processing_device": "cpu_fallback"
        }

    def _fallback_emotion_analysis(self, text: str) -> Dict:
        """Fallback emotion analysis using rule-based approach"""
        emotion_keywords = {
            "joy": ["happy", "joyful", "excited", "pleased", "delighted", "खुश", "खुशी"],
            "sadness": ["sad", "depressed", "down", "unhappy", "miserable", "दुखी", "उदास"],
            "anger": ["angry", "mad", "furious", "irritated", "annoyed", "गुस्सा", "क्रोध"],
            "fear": ["scared", "afraid", "terrified", "anxious", "worried", "डर", "चिंता"],
            "surprise": ["surprised", "shocked", "amazed", "astonished", "हैरान"],
            "disgust": ["disgusted", "revolted", "sick", "नफरत"]
        }

        text_lower = text.lower()
        emotion_scores = {}

        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = count

        if sum(emotion_scores.values()) == 0:
            dominant_emotion = "neutral"
            confidence = 0.5
        else:
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = min(0.9, 0.6 + (emotion_scores[dominant_emotion] * 0.1))

        return {
            "dominant_emotion": dominant_emotion,
            "all_emotions": emotion_scores,
            "confidence": confidence,
            "processing_device": "cpu_fallback"
        }

    def _rule_based_mental_health_analysis(self, text: str) -> Dict:
        """Rule-based mental health classification"""
        severe_indicators = ["suicidal", "suicide", "kill myself", "end it all", "hopeless", "worthless"]
        moderate_indicators = ["depressed", "depression", "anxious", "anxiety", "stressed", "overwhelmed"]
        mild_indicators = ["worried", "concerned", "tired", "sad", "frustrated"]

        text_lower = text.lower()

        severe_count = sum(1 for indicator in severe_indicators if indicator in text_lower)
        moderate_count = sum(1 for indicator in moderate_indicators if indicator in text_lower)
        mild_count = sum(1 for indicator in mild_indicators if indicator in text_lower)

        if severe_count > 0:
            classification = "severe_concern"
            confidence = 0.9
        elif moderate_count >= 2:
            classification = "moderate_concern"
            confidence = 0.8
        elif moderate_count >= 1 or mild_count >= 2:
            classification = "mild_concern"
            confidence = 0.7
        else:
            classification = "stable"
            confidence = 0.6

        return {
            "classification": classification,
            "confidence": confidence,
            "all_scores": {classification: confidence},
            "processing_device": "cpu_fallback"
        }

    def _calculate_model_confidence_adaptive(self, analysis: Dict, available_models: List[str]) -> float:
        """Calculate confidence based on available models"""
        confidences = []

        if "sentiment" in available_models and "sentiment" in analysis:
            confidences.append(analysis["sentiment"].get("confidence", 0.5))

        if "emotion" in available_models and "emotions" in analysis:
            confidences.append(analysis["emotions"].get("confidence", 0.5))

        if "mental_health" in available_models and "mental_health" in analysis:
            confidences.append(analysis["mental_health"].get("confidence", 0.5))

        if not confidences:
            return 0.7  # Default confidence for rule-based analysis

        # Weight confidence based on number of models used
        base_confidence = np.mean(confidences)
        model_bonus = len(available_models) * 0.05  # Bonus for using multiple models

        return min(0.95, base_confidence + model_bonus)
    
    def _enhanced_rule_based_analysis(self, text: str, responses: List[Dict]) -> Dict:
        """Enhanced rule-based analysis as fallback"""
        
        # Comprehensive keyword analysis with severity weights
        severe_indicators = {
            "depression": ["depressed", "depression", "suicidal", "suicide", "hopeless", "worthless", "hate myself", "want to die", "end it all", "give up", "अवसाद", "आत्महत्या", "निराश", "बेकार", "मरना चाहता"],
            "anxiety": ["panic", "panic attack", "terrified", "can't breathe", "heart racing", "घबराहट", "दिल तेज़", "सांस नहीं"],
            "trauma": ["flashbacks", "nightmares", "triggered", "ptsd", "combat stress", "बुरे सपने", "डरावने सपने"],
            "substance": ["drinking", "alcohol", "drugs", "substance", "addiction", "शराब", "नशा"]
        }
        
        moderate_indicators = {
            "stress": ["stressed", "stress", "overwhelmed", "pressure", "burden", "तनाव", "दबाव", "परेशान"],
            "mood": ["sad", "angry", "frustrated", "irritated", "moody", "दुखी", "गुस्सा", "चिढ़"],
            "sleep": ["can't sleep", "insomnia", "tired", "exhausted", "fatigue", "नींद नहीं", "थका", "कमजोर"],
            "social": ["lonely", "isolated", "withdrawn", "avoid people", "अकेला", "लोगों से बचना"]
        }
        
        positive_indicators = [
            "good", "great", "excellent", "happy", "joyful", "content", "satisfied", "peaceful", 
            "calm", "relaxed", "confident", "motivated", "energetic", "optimistic",
            "अच्छा", "बहुत अच्छा", "खुश", "संतुष्ट", "शांत", "आत्मविश्वास", "ऊर्जावान", "खुशी"
        ]
        
        text_lower = text.lower()
        
        # Calculate severity scores
        severe_score = 0
        moderate_score = 0
        category_breakdown = {}
        
        for category, keywords in severe_indicators.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                severe_score += count * 3
                category_breakdown[f"severe_{category}"] = count
        
        for category, keywords in moderate_indicators.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                moderate_score += count * 2
                category_breakdown[f"moderate_{category}"] = count
        
        positive_count = sum(1 for keyword in positive_indicators if keyword in text_lower)
        
        # Determine overall assessment
        total_negative = severe_score + moderate_score
        
        if severe_score >= 6:
            mental_state = "severe_concern"
        elif severe_score >= 3 or moderate_score >= 8:
            mental_state = "moderate_concern"
        elif moderate_score >= 4:
            mental_state = "mild_concern"
        elif positive_count >= 2 and total_negative <= 2:
            mental_state = "positive"
        else:
            mental_state = "stable"
        
        return {
            "sentiment": {"label": "negative" if total_negative > positive_count else "positive" if positive_count > 0 else "neutral"},
            "emotions": {"dominant_emotion": "sadness" if total_negative > 0 else "joy" if positive_count > 0 else "neutral"},
            "mental_health": {"classification": mental_state},
            "severity_scores": {"severe": severe_score, "moderate": moderate_score, "positive": positive_count},
            "category_breakdown": category_breakdown,
            "confidence": min(0.9, 0.6 + (total_negative + positive_count) * 0.05)
        }

    def _calculate_comprehensive_score(self, analysis: Dict, responses: List[Dict]) -> float:
        """Calculate comprehensive mental health score"""
        base_score = 75.0  # Healthy baseline

        # Get analysis components
        sentiment = analysis.get("sentiment", {})
        emotions = analysis.get("emotions", {})
        mental_health = analysis.get("mental_health", {})
        severity_scores = analysis.get("severity_scores", {})

        # Reduced sentiment impact
        sentiment_label = sentiment.get("label", "neutral")
        if sentiment_label == "negative":
            base_score -= 10  # Reduced from 20 to 10
        elif sentiment_label == "positive":
            base_score += 10

        # Reduced emotion impact
        dominant_emotion = emotions.get("dominant_emotion", "neutral")
        emotion_penalties = {
            "sadness": -8, "anger": -6, "fear": -10, "disgust": -5,  # Reduced penalties
            "surprise": 0, "joy": 15, "neutral": 0
        }
        base_score += emotion_penalties.get(dominant_emotion, 0)

        # Reduced mental health classification impact
        mh_classification = mental_health.get("classification", "stable")
        classification_adjustments = {
            "severe_concern": -20,  # Reduced from -40 to -20
            "moderate_concern": -10,  # Reduced from -25 to -10
            "mild_concern": -5,  # Reduced from -15 to -5
            "stable": 0,
            "positive": 15
        }
        base_score += classification_adjustments.get(mh_classification, 0)

        # Improved severity scores impact - less harsh penalties
        severe_penalty = severity_scores.get("severe", 0) * 5  # Reduced from 8 to 5
        moderate_penalty = severity_scores.get("moderate", 0) * 2  # Reduced from 4 to 2
        positive_boost = severity_scores.get("positive", 0) * 4  # Increased from 3 to 4

        final_score = base_score - severe_penalty - moderate_penalty + positive_boost

        # Response quality adjustment
        detailed_responses = sum(1 for r in responses if r.get("response_text") and len(r.get("response_text", "")) > 20)
        if len(responses) > 0:
            quality_factor = (detailed_responses / len(responses)) * 5
            final_score += quality_factor

        # Confidence adjustment
        confidence = analysis.get("confidence", 0.7)
        if confidence < 0.6:
            final_score = final_score * 0.9  # Reduce score if low confidence

        logger.info(f"Score calculation - Base: {base_score}, Severe: -{severe_penalty}, Moderate: -{moderate_penalty}, Positive: +{positive_boost}, Final: {final_score}")

        return max(0.0, min(100.0, final_score))

    def _assess_comprehensive_risk(self, score: float, analysis: Dict) -> str:
        """Assess risk level comprehensively"""
        mental_health = analysis.get("mental_health", {})
        severity_scores = analysis.get("severity_scores", {})

        classification = mental_health.get("classification", "stable")
        severe_score = severity_scores.get("severe", 0)

        # Improved risk thresholds - less aggressive
        # High risk conditions
        if (classification == "severe_concern" or
            severe_score >= 9 or  # Increased from 6 to 9
            score < 20):  # Decreased from 25 to 20
            return "High"

        # Moderate risk conditions
        elif (classification in ["moderate_concern", "mild_concern"] or
              severe_score >= 6 or  # Increased from 3 to 6
              score < 50):  # Decreased from 55 to 50
            return "Moderate"

        # Low risk
        else:
            return "Low"

    def _determine_mental_state(self, analysis: Dict, score: float) -> str:
        """Determine overall mental state"""
        mental_health = analysis.get("mental_health", {})
        classification = mental_health.get("classification", "stable")

        if classification == "severe_concern":
            return "concerning"
        elif classification in ["moderate_concern", "mild_concern"]:
            return "concerning" if score < 40 else "stable"
        elif classification == "positive" and score >= 70:
            return "positive"
        else:
            return "stable"

    def _generate_personalized_recommendations(self, analysis: Dict, user_profile: Optional[Dict],
                                             score: float, responses: List[Dict]) -> List[str]:
        """Generate highly personalized recommendations"""
        recommendations = []

        mental_health = analysis.get("mental_health", {})
        category_breakdown = analysis.get("category_breakdown", {})
        language_info = analysis.get("language", {})

        classification = mental_health.get("classification", "stable")

        # Critical/Severe recommendations
        if classification == "severe_concern":
            recommendations.extend([
                "🚨 IMMEDIATE ACTION REQUIRED: Contact unit mental health officer NOW",
                "📞 Emergency Support: Call Army Crisis Helpline immediately",
                "⚕️ Medical Evaluation: Schedule urgent psychiatric assessment",
                "👥 Safety Network: Inform trusted battle buddy about your condition"
            ])

        # Category-specific recommendations
        if category_breakdown.get("severe_depression", 0) > 0:
            recommendations.append("💊 Depression Support: Consult unit medical officer for depression treatment options")

        if category_breakdown.get("severe_anxiety", 0) > 0:
            recommendations.append("🧘 Anxiety Management: Practice immediate breathing techniques, seek anxiety counseling")

        if category_breakdown.get("moderate_stress", 0) > 0:
            recommendations.append("⚡ Stress Reduction: Implement daily stress management routine, consider workload adjustment")

        if category_breakdown.get("moderate_sleep", 0) > 0:
            recommendations.append("😴 Sleep Hygiene: Establish regular sleep schedule, avoid screens before bed")

        if category_breakdown.get("moderate_social", 0) > 0:
            recommendations.append("🤝 Social Reconnection: Gradually increase interaction with unit members")

        # Language and cultural considerations
        language_type = language_info.get("language_type", "english")
        if language_type in ["hindi_dominant", "hinglish"]:
            recommendations.append("🇮🇳 Cultural Support: Access Hindi-speaking counselors familiar with Indian military culture")

        # Score-based recommendations
        if score >= 70:
            recommendations.extend([
                "✅ Maintain Excellence: Continue current positive mental health practices",
                "🎖️ Leadership Role: Consider mentoring fellow soldiers in wellness practices"
            ])
        elif score >= 40:
            recommendations.extend([
                "📈 Improvement Focus: Work on identified areas with unit support",
                "🏃 Physical Wellness: Increase PT activities for mental health benefits"
            ])

        # Always include army-specific guidance
        if classification in ["severe_concern", "moderate_concern"]:
            recommendations.append("🛡️ Mission Readiness: Your mental health is critical for operational effectiveness")
        else:
            recommendations.append("🎖️ Soldier Strength: Mental fitness enhances your service capabilities")

        # Ensure minimum recommendations
        if len(recommendations) < 4:
            recommendations.extend([
                "📞 Resources Available: Army mental health services are confidential and supportive",
                "💪 Strength in Seeking Help: Professional support shows military discipline",
                "🤝 Battle Buddy System: Stay connected with your support network"
            ])

        return recommendations[:8]  # Limit to 8 most relevant recommendations

    def _fallback_comprehensive_analysis(self, responses: List[Dict]) -> Dict:
        """Fallback analysis when all else fails"""
        return {
            "overall_score": 50.0,
            "risk_level": "Moderate",
            "mental_state": "stable",
            "detailed_analysis": {"confidence": 0.5},
            "recommendations": [
                "Continue regular mental health monitoring",
                "Maintain healthy lifestyle practices",
                "Seek professional guidance when needed",
                "Stay connected with unit support systems"
            ],
            "confidence": 0.5,
            "processing_method": "fallback"
        }

# Utility functions
def initialize_advanced_analyzer() -> AdvancedMentalHealthAnalyzer:
    """Initialize and return advanced analyzer"""
    return AdvancedMentalHealthAnalyzer()

if __name__ == "__main__":
    # Test the advanced analyzer
    analyzer = initialize_advanced_analyzer()

    # Test with concerning responses
    test_responses = [
        {"response_text": "I feel very depressed and hopeless. I can't sleep and have no appetite. I want to give up."},
        {"response_text": "I am constantly stressed and overwhelmed. I avoid talking to people and my work performance is terrible."}
    ]

    results = analyzer.analyze_comprehensive(test_responses)
    print("🧪 Advanced Analyzer Test Results:")
    print(f"📊 Overall Score: {results['overall_score']:.1f}")
    print(f"⚠️ Risk Level: {results['risk_level']}")
    print(f"🧠 Mental State: {results['mental_state']}")
    print(f"🔧 Processing Method: {results['processing_method']}")
    print(f"💡 Recommendations: {len(results['recommendations'])} generated")
