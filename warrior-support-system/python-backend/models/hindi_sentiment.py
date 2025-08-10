"""
Hindi Sentiment Analysis Model for Army Mental Health Assessment
CPU-ONLY, OFFLINE-CAPABLE VERSION
"""
import os
import sys
import re
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Force CPU usage - NO GPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TORCH_USE_CUDA"] = "0"

try:
    import torch
    # Force CPU device
    torch.set_default_device('cpu')
    torch.set_default_dtype(torch.float32)

    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    print(f"Transformers not available: {e}")
    TRANSFORMERS_AVAILABLE = False

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent.parent))
try:
    from config import MODELS_DIR, HINDI_MODELS, MODEL_CONFIG
except ImportError:
    # Fallback configuration
    MODELS_DIR = Path("data/models")
    MODELS_DIR.mkdir(exist_ok=True)
    MODEL_CONFIG = {"device": "cpu", "local_files_only": True}

class HindiSentimentAnalyzer:
    """
    Hindi Sentiment Analysis using local Hugging Face models
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.sentiment_pipeline = None
        self.model_loaded = False
        
    def download_and_load_model(self) -> bool:
        """
        Download and load Hindi sentiment analysis model with priority-based selection
        """
        if not TRANSFORMERS_AVAILABLE:
            print("⚠ Transformers not available, using enhanced keyword-based sentiment analysis")
            self._setup_fallback_analyzer()
            return False

        # Try models in priority order
        model_priorities = [
            ("sentiment_primary", "AI4Bharat IndicBERT"),
            ("sentiment_secondary", "L3Cube Hindi BERT v2"),
            ("sentiment_fallback", "RoBERTa English (fallback)")
        ]

        for model_key, model_desc in model_priorities:
            try:
                model_config = HINDI_MODELS.get(model_key, {})
                if not model_config:
                    continue

                model_name = model_config.get("model_name")
                local_path = model_config.get("local_path")

                if not model_name or not local_path:
                    continue

                print(f"Attempting to load {model_desc}: {model_name} (CPU-only)")

                if self._try_load_model(model_name, local_path):
                    print(f"✓ Successfully loaded {model_desc}")
                    return True
                else:
                    print(f"✗ Failed to load {model_desc}, trying next...")

            except Exception as e:
                print(f"✗ Error loading {model_desc}: {str(e)}")
                continue

        # If all models fail, use enhanced keyword-based analysis
        print("⚠ All transformer models failed, using enhanced keyword-based sentiment analysis")
        self._setup_fallback_analyzer()
        return False

    def _try_load_model(self, model_name: str, local_path) -> bool:
        """Try to load a specific model"""
        try:

            # Create local directory if it doesn't exist
            local_path.mkdir(parents=True, exist_ok=True)

            # Try to load from local cache first (offline mode)
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    str(local_path),
                    local_files_only=True
                )

                self.model = AutoModelForSequenceClassification.from_pretrained(
                    str(local_path),
                    local_files_only=True,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
                print("✓ Loaded model from local cache (offline mode)")

            except Exception as local_error:
                print(f"Local model not found, downloading: {local_error}")

                # Download and save model locally (requires internet - one time only)
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=str(local_path)
                )

                self.model = AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    cache_dir=str(local_path),
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                )

                # Save for offline use
                self.tokenizer.save_pretrained(str(local_path))
                self.model.save_pretrained(str(local_path))
                print("✓ Model downloaded and saved for offline use")

            # Force CPU usage
            self.model.to('cpu')
            self.model.eval()  # Set to evaluation mode

            # Create sentiment analysis pipeline (CPU-only)
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1,  # Force CPU
                framework="pt"
            )

            self.model_loaded = True
            print("✓ Hindi sentiment model loaded successfully (CPU-only)")
            return True

        except Exception as e:
            print(f"✗ Error loading Hindi sentiment model: {str(e)}")
            print("⚠ Falling back to keyword-based sentiment analysis")
            # Fallback to a simpler approach if model loading fails
            self._setup_fallback_analyzer()
            return False
    
    def _setup_fallback_analyzer(self):
        """
        Setup fallback sentiment analyzer using keyword-based approach
        """
        print("Setting up fallback keyword-based sentiment analyzer...")
        
        # Enhanced Hindi sentiment keywords
        self.positive_keywords = [
            # Basic positive emotions
            "खुश", "प्रसन्न", "अच्छा", "बेहतर", "सकारात्मक", "शांत", "संतुष्ट",
            "आनंद", "हर्ष", "उत्साह", "आशा", "विश्वास", "स्वस्थ", "मजबूत",
            # Confidence and strength
            "आत्मविश्वास", "तंदुरुस्त", "फिट", "सक्षम", "योग्य", "ताकतवर",
            # Satisfaction and pride
            "गर्व", "सम्मान", "राजी", "खुशी", "प्रेम", "स्नेह",
            # Military positive terms
            "तैयार", "सेवा", "कर्तव्य", "मिशन", "टीम", "साथी", "यूनिट", "सहयोग",
            # Additional positive
            "बहुत", "बहुत अच्छा", "बहुत खुश", "बहुत बेहतर"
        ]

        self.negative_keywords = [
            # Basic negative emotions
            "उदास", "दुखी", "परेशान", "चिंतित", "तनाव", "डर", "भय", "गुस्सा",
            "क्रोध", "निराश", "हताश", "अवसाद", "बेचैन", "घबराहट", "कमजोर",
            # Additional negative terms
            "बीमार", "दर्द", "पीड़ा", "तकलीफ", "कष्ट", "समस्या", "मुश्किल",
            "अकेला", "अकेलापन", "थका", "थकान", "सुस्त", "बेदम", "निढाल",
            # Intensity markers
            "बहुत दुख", "बहुत परेशान", "बहुत तनाव", "बहुत चिंता"
        ]
        
        self.neutral_keywords = [
            "सामान्य", "ठीक", "वैसा", "कभी", "शायद", "लगता", "होता", "रहता"
        ]
        
        self.model_loaded = True
    
    def preprocess_hindi_text(self, text: str) -> str:
        """
        Preprocess Hindi text for sentiment analysis
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep Hindi characters
        text = re.sub(r'[^\u0900-\u097F\s]', '', text)

        return text
    
    def analyze_sentiment_with_model(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using the loaded model
        """
        try:
            if not self.sentiment_pipeline:
                raise Exception("Model not loaded")
            
            # Preprocess text
            processed_text = self.preprocess_hindi_text(text)
            
            if not processed_text:
                return {"label": "NEUTRAL", "score": 0.5}
            
            # Get sentiment prediction
            result = self.sentiment_pipeline(processed_text)[0]
            
            # Normalize labels
            label = result["label"].upper()
            if label in ["POSITIVE", "POS"]:
                label = "POSITIVE"
            elif label in ["NEGATIVE", "NEG"]:
                label = "NEGATIVE"
            else:
                label = "NEUTRAL"
            
            return {
                "label": label,
                "score": result["score"]
            }
            
        except Exception as e:
            print(f"Error in model-based sentiment analysis: {str(e)}")
            return self.analyze_sentiment_fallback(text)
    
    def analyze_sentiment_fallback(self, text: str) -> Dict[str, float]:
        """
        Enhanced fallback keyword-based sentiment analysis
        """
        processed_text = self.preprocess_hindi_text(text.lower())

        if not processed_text:
            return {"label": "NEUTRAL", "score": 0.5}

        # Count keyword matches with better scoring
        positive_matches = []
        negative_matches = []

        for keyword in self.positive_keywords:
            if keyword in processed_text:
                positive_matches.append(keyword)

        for keyword in self.negative_keywords:
            if keyword in processed_text:
                negative_matches.append(keyword)

        positive_count = len(positive_matches)
        negative_count = len(negative_matches)

        # Enhanced scoring logic
        if positive_count == 0 and negative_count == 0:
            return {"label": "NEUTRAL", "score": 0.5}

        # Calculate weighted scores
        positive_score = positive_count * 1.0
        negative_score = negative_count * 1.0

        # Check for intensity markers
        if any(word in processed_text for word in ["बहुत", "अत्यधिक", "काफी", "ज्यादा"]):
            if positive_count > negative_count:
                positive_score *= 1.5  # Boost positive
            elif negative_count > positive_count:
                negative_score *= 1.5  # Boost negative

        total_score = positive_score + negative_score

        if positive_score > negative_score:
            confidence = min(0.7 + (positive_score / max(total_score, 1)) * 0.3, 0.95)
            return {"label": "POSITIVE", "score": confidence}
        elif negative_score > positive_score:
            confidence = min(0.7 + (negative_score / max(total_score, 1)) * 0.3, 0.95)
            return {"label": "NEGATIVE", "score": confidence}
        else:
            return {"label": "NEUTRAL", "score": 0.5}
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Main method to analyze sentiment of Hindi text
        """
        if not self.model_loaded:
            self.download_and_load_model()
        
        # Try model-based analysis first, fallback to keyword-based
        if self.sentiment_pipeline:
            result = self.analyze_sentiment_with_model(text)
        else:
            result = self.analyze_sentiment_fallback(text)
        
        # Convert to standardized format
        sentiment_score = result["score"]
        if result["label"] == "NEGATIVE":
            sentiment_score = -sentiment_score
        elif result["label"] == "NEUTRAL":
            sentiment_score = 0.0
        
        return {
            "sentiment_label": result["label"],
            "sentiment_score": sentiment_score,  # -1 to 1 scale
            "confidence_score": abs(result["score"]),
            "raw_result": result
        }
    
    def batch_analyze_sentiment(self, texts: List[str]) -> List[Dict[str, any]]:
        """
        Analyze sentiment for multiple texts
        """
        results = []
        for text in texts:
            results.append(self.analyze_sentiment(text))
        return results
    
    def get_emotion_indicators(self, text: str) -> Dict[str, float]:
        """
        Get specific emotion indicators from Hindi text
        """
        processed_text = self.preprocess_hindi_text(text.lower())
        
        emotion_keywords = {
            "stress": ["तनाव", "दबाव", "परेशानी", "चिंता", "बेचैनी"],
            "depression": ["उदासी", "अवसाद", "निराशा", "हताशा", "दुख"],
            "anxiety": ["घबराहट", "डर", "भय", "चिंता", "बेचैनी"],
            "anger": ["गुस्सा", "क्रोध", "चिढ़", "नाराजगी", "रोष"],
            "happiness": ["खुश", "प्रसन्न", "आनंद", "हर्ष", "उत्साह"],
            "calmness": ["शांत", "आराम", "स्थिर", "संयम", "धैर्य"]
        }
        
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in processed_text)
            emotion_scores[emotion] = min(count / len(keywords), 1.0)
        
        return emotion_scores

# Global instance
hindi_sentiment_analyzer = HindiSentimentAnalyzer()

def analyze_hindi_sentiment(text: str) -> Dict[str, any]:
    """
    Convenience function to analyze Hindi sentiment
    """
    return hindi_sentiment_analyzer.analyze_sentiment(text)

def get_emotion_analysis(text: str) -> Dict[str, any]:
    """
    Get comprehensive emotion analysis for Hindi text
    """
    sentiment_result = hindi_sentiment_analyzer.analyze_sentiment(text)
    emotion_indicators = hindi_sentiment_analyzer.get_emotion_indicators(text)
    
    return {
        **sentiment_result,
        "emotion_indicators": emotion_indicators
    }
