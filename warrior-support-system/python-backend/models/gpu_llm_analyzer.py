#!/usr/bin/env python3
"""
GPU-Powered Local LLM Analyzer for Army Mental Health Assessment
Provides intelligent analysis and recommendations using local models
"""

import logging
import torch
from typing import Dict, List, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPULLMAnalyzer:
    """
    GPU-powered local LLM analyzer for mental health assessment
    """
    
    def __init__(self):
        """Initialize the GPU LLM analyzer"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.is_initialized = False
        
        logger.info(f"🎮 GPU LLM Analyzer initializing on {self.device}")
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the local LLM model"""
        try:
            # Try to load transformers for advanced analysis
            from transformers import AutoTokenizer, AutoModelForCausalLM

            # Use a smaller, efficient model for local processing
            model_name = "distilgpt2"  # Lighter model for better compatibility

            logger.info(f"📦 Loading model: {model_name}")

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )

            if self.device == "cuda":
                self.model = self.model.to(self.device)

            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.is_initialized = True
            logger.info("✅ GPU LLM Analyzer initialized successfully")

        except ImportError as e:
            logger.warning(f"⚠️ Transformers library not available: {e}")
            logger.info("🔄 Using rule-based analysis as fallback")
            self.is_initialized = False
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize advanced LLM: {e}")
            logger.info("🔄 Using rule-based analysis as fallback")
            self.is_initialized = False
    
    def analyze_responses(self, responses: List[Dict], user_profile: Optional[Dict] = None) -> Dict:
        """
        Analyze user responses and generate comprehensive assessment
        
        Args:
            responses: List of user responses
            user_profile: Optional user profile information
            
        Returns:
            Comprehensive analysis results
        """
        try:
            # Combine all responses into analysis text
            combined_text = self._prepare_analysis_text(responses)
            
            # Perform analysis
            if self.is_initialized:
                analysis = self._llm_analysis(combined_text, user_profile)
            else:
                analysis = self._rule_based_analysis(combined_text, responses)
            
            # Calculate overall metrics
            overall_score = self._calculate_overall_score(responses, analysis)
            risk_level = self._assess_risk_level(overall_score, analysis)
            
            # Generate personalized recommendations
            recommendations = self._generate_recommendations(analysis, user_profile, overall_score)
            
            return {
                "overall_score": overall_score,
                "risk_level": risk_level,
                "mental_state": analysis.get("mental_state", "stable"),
                "key_insights": analysis.get("insights", []),
                "recommendations": recommendations,
                "analysis_confidence": analysis.get("confidence", 0.8),
                "processing_method": "llm" if self.is_initialized else "rule_based"
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return self._fallback_analysis(responses)
    
    def _prepare_analysis_text(self, responses: List[Dict]) -> str:
        """Prepare text for analysis from responses"""
        text_parts = []
        
        for response in responses:
            if response.get("response_text"):
                text_parts.append(response["response_text"])
            elif response.get("response_value"):
                text_parts.append(str(response["response_value"]))
        
        return " ".join(text_parts)
    
    def _llm_analysis(self, text: str, user_profile: Optional[Dict] = None) -> Dict:
        """Perform LLM-based analysis"""
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(text, user_profile)
            
            # Tokenize and generate
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            if self.device == "cuda":
                inputs = inputs.to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 100,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            analysis_part = generated_text[len(prompt):].strip()
            
            # Parse analysis (simplified for this implementation)
            return {
                "mental_state": self._extract_mental_state(text),
                "insights": self._extract_insights(text, analysis_part),
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"❌ LLM analysis failed: {e}")
            return self._rule_based_analysis(text, [])
    
    def _rule_based_analysis(self, text: str, responses: List[Dict]) -> Dict:
        """Enhanced rule-based analysis with comprehensive evaluation"""

        # Comprehensive keyword analysis
        severe_negative = [
            "depressed", "suicidal", "hopeless", "worthless", "hate myself", "want to die",
            "can't cope", "breaking down", "falling apart", "desperate", "trapped",
            "अवसाद", "आत्महत्या", "निराश", "बेकार", "मरना चाहता", "टूट गया", "हार गया"
        ]

        moderate_negative = [
            "stressed", "anxious", "worried", "sad", "angry", "frustrated", "overwhelmed",
            "tired", "exhausted", "lonely", "isolated", "confused", "scared", "afraid",
            "तनाव", "चिंता", "परेशान", "दुखी", "गुस्सा", "थका", "अकेला", "डरा", "घबराया"
        ]

        mild_negative = [
            "concerned", "uneasy", "uncomfortable", "bothered", "annoyed", "restless",
            "बेचैन", "परेशानी", "असहज", "चिंतित"
        ]

        positive_indicators = [
            "good", "great", "excellent", "happy", "joyful", "content", "satisfied",
            "peaceful", "calm", "relaxed", "confident", "motivated", "energetic",
            "अच्छा", "बहुत अच्छा", "खुश", "संतुष्ट", "शांत", "आत्मविश्वास", "ऊर्जावान"
        ]

        # Sleep and appetite indicators
        sleep_issues = [
            "can't sleep", "insomnia", "nightmares", "restless sleep", "wake up tired",
            "नींद नहीं आती", "बुरे सपने", "नींद में परेशानी"
        ]

        appetite_issues = [
            "no appetite", "not eating", "lost weight", "can't eat", "food tastes bad",
            "भूख नहीं", "खाना नहीं खाया", "वजन कम"
        ]

        # Social withdrawal indicators
        social_issues = [
            "avoiding people", "don't want to talk", "isolated", "withdrawn", "alone",
            "लोगों से बचना", "बात नहीं करना", "अकेले रहना"
        ]

        # Work/duty performance indicators
        performance_issues = [
            "can't concentrate", "making mistakes", "poor performance", "distracted",
            "ध्यान नहीं", "गलतियां", "काम में मन नहीं"
        ]

        text_lower = text.lower()

        # Count different severity levels
        severe_count = sum(1 for phrase in severe_negative if phrase in text_lower)
        moderate_count = sum(1 for phrase in moderate_negative if phrase in text_lower)
        mild_count = sum(1 for phrase in mild_negative if phrase in text_lower)
        positive_count = sum(1 for phrase in positive_indicators if phrase in text_lower)

        # Specific issue counts
        sleep_count = sum(1 for phrase in sleep_issues if phrase in text_lower)
        appetite_count = sum(1 for phrase in appetite_issues if phrase in text_lower)
        social_count = sum(1 for phrase in social_issues if phrase in text_lower)
        performance_count = sum(1 for phrase in performance_issues if phrase in text_lower)

        # Determine mental state based on comprehensive analysis
        total_negative = severe_count * 3 + moderate_count * 2 + mild_count * 1
        total_positive = positive_count

        # Additional weight for specific issues
        issue_weight = (sleep_count + appetite_count + social_count + performance_count) * 1.5

        final_score = total_negative + issue_weight - total_positive

        logger.info(f"Analysis scores - Severe: {severe_count}, Moderate: {moderate_count}, Mild: {mild_count}, Positive: {positive_count}")
        logger.info(f"Issue indicators - Sleep: {sleep_count}, Appetite: {appetite_count}, Social: {social_count}, Performance: {performance_count}")
        logger.info(f"Final negative score: {final_score}")

        if severe_count > 0 or final_score >= 6:
            mental_state = "concerning"
        elif moderate_count >= 2 or final_score >= 3:
            mental_state = "concerning"
        elif final_score >= 1:
            mental_state = "stable"
        elif positive_count > 0 and final_score <= 0:
            mental_state = "positive"
        else:
            mental_state = "stable"

        # Generate detailed insights
        insights = []

        if severe_count > 0:
            insights.append("Severe mental health concerns detected - immediate attention needed")
        if moderate_count >= 2:
            insights.append("Multiple stress indicators present")
        if sleep_count > 0:
            insights.append("Sleep disturbances reported")
        if appetite_count > 0:
            insights.append("Appetite/eating concerns noted")
        if social_count > 0:
            insights.append("Social withdrawal patterns detected")
        if performance_count > 0:
            insights.append("Work/duty performance issues indicated")
        if positive_count > 0 and final_score <= 0:
            insights.append("Positive mental health indicators present")

        if not insights:
            insights.append("Standard response patterns - monitoring recommended")

        # Calculate confidence based on keyword matches
        total_matches = severe_count + moderate_count + mild_count + positive_count
        confidence = min(0.9, 0.5 + (total_matches * 0.1))

        return {
            "mental_state": mental_state,
            "insights": insights,
            "confidence": confidence,
            "severity_breakdown": {
                "severe": severe_count,
                "moderate": moderate_count,
                "mild": mild_count,
                "positive": positive_count
            },
            "issue_indicators": {
                "sleep": sleep_count,
                "appetite": appetite_count,
                "social": social_count,
                "performance": performance_count
            }
        }
    
    def _create_analysis_prompt(self, text: str, user_profile: Optional[Dict] = None) -> str:
        """Create analysis prompt for LLM"""
        prompt = f"""Analyze the following mental health response from an army personnel:

Response: "{text}"

Provide insights about their mental state and well-being."""
        
        return prompt
    
    def _extract_mental_state(self, text: str) -> str:
        """Extract mental state from text"""
        # Simple keyword-based extraction
        if any(word in text.lower() for word in ["good", "fine", "well", "अच्छा", "ठीक"]):
            return "positive"
        elif any(word in text.lower() for word in ["bad", "stressed", "worried", "बुरा", "परेशान"]):
            return "concerning"
        else:
            return "stable"
    
    def _extract_insights(self, text: str, analysis: str) -> List[str]:
        """Extract key insights"""
        insights = []
        
        # Language detection
        has_hindi = any(hindi in text for hindi in ["मैं", "हूं", "है", "का"])
        has_english = any(eng in text.lower() for eng in ["i", "am", "is", "the"])
        
        if has_hindi and has_english:
            insights.append("Comfortable with bilingual communication")
        
        # Response length analysis
        if len(text.split()) > 20:
            insights.append("Detailed and expressive responses")
        elif len(text.split()) < 5:
            insights.append("Brief responses - may need encouragement to elaborate")
        
        return insights
    
    def _calculate_overall_score(self, responses: List[Dict], analysis: Dict) -> float:
        """Calculate comprehensive mental health score based on detailed analysis"""
        base_score = 70.0  # Start with healthy baseline

        # Get severity breakdown from analysis
        severity = analysis.get("severity_breakdown", {})
        issues = analysis.get("issue_indicators", {})
        mental_state = analysis.get("mental_state", "stable")

        # Severe penalties for concerning indicators
        severe_penalty = severity.get("severe", 0) * 25  # -25 per severe indicator
        moderate_penalty = severity.get("moderate", 0) * 15  # -15 per moderate indicator
        mild_penalty = severity.get("mild", 0) * 8  # -8 per mild indicator

        # Additional penalties for specific issues
        sleep_penalty = issues.get("sleep", 0) * 10
        appetite_penalty = issues.get("appetite", 0) * 10
        social_penalty = issues.get("social", 0) * 12
        performance_penalty = issues.get("performance", 0) * 12

        # Positive adjustments
        positive_boost = severity.get("positive", 0) * 5  # +5 per positive indicator

        # Calculate total adjustments
        total_penalty = (severe_penalty + moderate_penalty + mild_penalty +
                        sleep_penalty + appetite_penalty + social_penalty + performance_penalty)

        final_score = base_score - total_penalty + positive_boost

        # Additional adjustment based on mental state
        if mental_state == "concerning":
            final_score = min(final_score, 40)  # Cap at 40 for concerning state
        elif mental_state == "positive":
            final_score = max(final_score, 60)  # Minimum 60 for positive state

        # Response quality factor
        total_responses = len(responses)
        if total_responses > 0:
            detailed_responses = sum(1 for r in responses if r.get("response_text") and len(r.get("response_text", "")) > 10)
            response_quality_factor = (detailed_responses / total_responses) * 5
            final_score += response_quality_factor

        logger.info(f"Score calculation - Base: {base_score}, Penalties: {total_penalty}, Positive: {positive_boost}, Final: {final_score}")

        return min(100.0, max(0.0, final_score))
    
    def _assess_risk_level(self, score: float, analysis: Dict) -> str:
        """Assess risk level based on score and detailed analysis"""
        mental_state = analysis.get("mental_state", "stable")
        severity = analysis.get("severity_breakdown", {})

        # High risk conditions
        if (severity.get("severe", 0) > 0 or
            mental_state == "concerning" or
            score < 30):
            return "High"

        # Moderate risk conditions
        elif (severity.get("moderate", 0) >= 2 or
              score < 60 or
              (severity.get("moderate", 0) >= 1 and score < 70)):
            return "Moderate"

        # Low risk
        else:
            return "Low"
    
    def _generate_recommendations(self, analysis: Dict, user_profile: Optional[Dict], score: float) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        mental_state = analysis.get("mental_state", "stable")
        severity = analysis.get("severity_breakdown", {})
        issues = analysis.get("issue_indicators", {})

        # High priority recommendations for severe cases
        if severity.get("severe", 0) > 0 or mental_state == "concerning":
            recommendations.extend([
                "🚨 URGENT: Contact unit mental health officer immediately",
                "📞 Call army crisis helpline: Available 24/7",
                "⚕️ Schedule emergency mental health evaluation",
                "👥 Inform trusted battle buddy about your situation"
            ])

        # Specific issue-based recommendations
        if issues.get("sleep", 0) > 0:
            recommendations.append("😴 Address sleep issues: Establish regular sleep schedule")

        if issues.get("appetite", 0) > 0:
            recommendations.append("🍽️ Nutrition support: Consult unit medic about eating concerns")

        if issues.get("social", 0) > 0:
            recommendations.append("🤝 Social reconnection: Re-engage with unit activities")

        if issues.get("performance", 0) > 0:
            recommendations.append("🎯 Performance support: Discuss workload with commanding officer")

        # Moderate concern recommendations
        if severity.get("moderate", 0) >= 1 and mental_state != "concerning":
            recommendations.extend([
                "🧘 Daily stress management: Practice breathing exercises",
                "💪 Physical wellness: Maintain regular PT activities",
                "📝 Keep a daily mood journal to track patterns"
            ])

        # Positive reinforcement for good mental health
        if mental_state == "positive" and score >= 70:
            recommendations.extend([
                "✅ Excellent mental health - continue current practices",
                "🎖️ Consider peer mentoring role within your unit"
            ])

        # General army-specific recommendations
        if mental_state == "concerning":
            recommendations.append("🛡️ Your mental health directly impacts mission readiness")
        else:
            recommendations.append("🎖️ Mental fitness is as important as physical fitness")

        # Ensure we have enough recommendations
        if len(recommendations) < 4:
            recommendations.extend([
                "🤝 Stay connected with your support network",
                "💪 Your strength includes knowing when to seek support"
            ])
        
        return recommendations[:6]  # Limit to 6 recommendations
    
    def _fallback_analysis(self, responses: List[Dict]) -> Dict:
        """Fallback analysis when everything fails"""
        return {
            "overall_score": 50.0,
            "risk_level": "Moderate",
            "mental_state": "stable",
            "key_insights": ["Assessment completed with basic analysis"],
            "recommendations": [
                "Continue regular mental health check-ins",
                "Maintain healthy lifestyle practices",
                "Seek professional guidance when needed"
            ],
            "analysis_confidence": 0.5,
            "processing_method": "fallback"
        }

# Utility functions
def initialize_gpu_llm_analyzer() -> GPULLMAnalyzer:
    """Initialize and return GPU LLM analyzer"""
    return GPULLMAnalyzer()

def install_llm_dependencies():
    """Install required dependencies for LLM analysis"""
    import subprocess
    import sys
    
    dependencies = [
        "transformers",
        "torch",
        "accelerate"
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            logger.info(f"✅ Installed {dep}")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install {dep}: {e}")

if __name__ == "__main__":
    # Test the GPU LLM analyzer
    analyzer = initialize_gpu_llm_analyzer()
    
    # Test analysis
    test_responses = [
        {"response_text": "I am feeling good today and ready for duty"},
        {"response_text": "Sometimes I feel stressed but I manage it well"}
    ]
    
    results = analyzer.analyze_responses(test_responses)
    print("✅ GPU LLM Analyzer test completed")
    print(f"📊 Results: {results}")
