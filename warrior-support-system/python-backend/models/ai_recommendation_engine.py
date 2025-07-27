#!/usr/bin/env python3
"""
AI-Powered Recommendation Engine for Army Mental Health System
Generates personalized recommendations based on comprehensive assessment results
"""

import json
import logging
import re
from typing import Dict, List, Optional
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIRecommendationEngine:
    """
    AI-powered recommendation engine using local language models
    Similar to CultureGuardian approach but focused on mental health
    """
    
    def __init__(self, device="auto"):
        """Initialize the AI recommendation engine"""
        # Auto-detect best device
        if device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info(f"🎮 AI Engine using GPU: {torch.cuda.get_device_name(0)}")
            else:
                self.device = "cpu"
                logger.info("💻 AI Engine using CPU")
        else:
            self.device = device
        self.is_initialized = False
        self.model = None
        self.tokenizer = None
        
        # Mental health recommendation templates
        self.recommendation_templates = {
            "severe": {
                "immediate_actions": [
                    "Seek immediate professional mental health support",
                    "Contact military mental health services",
                    "Reach out to trusted supervisors or colleagues",
                    "Consider emergency mental health resources"
                ],
                "follow_up": [
                    "Schedule regular counseling sessions",
                    "Develop crisis management plan",
                    "Monitor symptoms daily",
                    "Engage family support system"
                ]
            },
            "high": {
                "immediate_actions": [
                    "Schedule mental health consultation within 48 hours",
                    "Implement stress reduction techniques",
                    "Increase physical activity",
                    "Improve sleep hygiene"
                ],
                "follow_up": [
                    "Weekly stress monitoring",
                    "Join stress management programs",
                    "Practice mindfulness techniques",
                    "Maintain social connections"
                ]
            },
            "moderate": {
                "immediate_actions": [
                    "Practice regular self-care routines",
                    "Engage in stress-reducing activities",
                    "Maintain work-life balance",
                    "Connect with support network"
                ],
                "follow_up": [
                    "Monitor stress levels weekly",
                    "Continue healthy lifestyle habits",
                    "Participate in wellness programs",
                    "Regular check-ins with peers"
                ]
            },
            "low": {
                "immediate_actions": [
                    "Continue current wellness practices",
                    "Maintain healthy routines",
                    "Stay connected with support systems",
                    "Practice preventive self-care"
                ],
                "follow_up": [
                    "Regular wellness check-ins",
                    "Maintain physical fitness",
                    "Continue stress management practices",
                    "Support colleagues when needed"
                ]
            }
        }
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the local language model for recommendations"""
        try:
            logger.info("🤖 Initializing AI recommendation engine...")
            
            # Try to use a lightweight local model for CPU inference
            model_name = "microsoft/DialoGPT-small"  # Lightweight conversational model
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Move to specified device
            self.model.to(self.device)
            self.model.eval()
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.is_initialized = True
            logger.info("✅ AI recommendation engine initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI model: {e}")
            logger.info("💡 Falling back to rule-based recommendations")
            self.is_initialized = False
    
    def generate_personalized_recommendations(self, assessment_summary: str, stress_level: str, findings: Dict) -> Dict:
        """
        Generate personalized recommendations based on comprehensive assessment
        
        Args:
            assessment_summary: Complete assessment summary text
            stress_level: Overall stress level (low, moderate, high, severe)
            findings: Key findings from all assessments
            
        Returns:
            Dictionary containing personalized recommendations
        """
        try:
            # Get base recommendations from templates
            base_recommendations = self.recommendation_templates.get(stress_level.lower(), 
                                                                   self.recommendation_templates["moderate"])
            
            # Generate AI-enhanced recommendations if model is available
            if self.is_initialized:
                ai_recommendations = self._generate_ai_recommendations(assessment_summary, findings)
            else:
                ai_recommendations = self._generate_rule_based_recommendations(findings)
            
            # Combine and personalize recommendations
            personalized_recommendations = self._combine_recommendations(
                base_recommendations, ai_recommendations, findings
            )
            
            return {
                "stress_level": stress_level,
                "immediate_actions": personalized_recommendations["immediate"],
                "short_term_goals": personalized_recommendations["short_term"],
                "long_term_strategies": personalized_recommendations["long_term"],
                "specific_interventions": personalized_recommendations["specific"],
                "resources": personalized_recommendations["resources"],
                "generated_by": "AI" if self.is_initialized else "Rule-based",
                "confidence": personalized_recommendations.get("confidence", 0.8)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate recommendations: {e}")
            return self._fallback_recommendations(stress_level)
    
    def _generate_ai_recommendations(self, assessment_summary: str, findings: Dict) -> Dict:
        """Generate AI-powered recommendations using local model"""
        try:
            # Create a focused prompt for mental health recommendations
            prompt = f"""Based on this mental health assessment, provide specific recommendations:

Assessment Summary: {assessment_summary[:500]}

Key Issues: {', '.join(findings.get('risk_factors', [])[:3])}

Provide practical recommendations for:"""
            
            # Tokenize and generate
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
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
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            generated_text = response[len(prompt):].strip()
            
            # Parse AI response into structured recommendations
            return self._parse_ai_response(generated_text, findings)
            
        except Exception as e:
            logger.error(f"❌ AI recommendation generation failed: {e}")
            return self._generate_rule_based_recommendations(findings)
    
    def _generate_rule_based_recommendations(self, findings: Dict) -> Dict:
        """Generate rule-based recommendations when AI is not available"""
        recommendations = {
            "immediate": [],
            "short_term": [],
            "long_term": [],
            "specific": []
        }
        
        # Analyze questionnaire responses
        q_responses = findings.get('questionnaire_responses', {})
        
        # Check for specific issues and add targeted recommendations
        for question, response in q_responses.items():
            if isinstance(response, (int, float)):
                if "sleep" in question.lower() and response >= 3:
                    recommendations["immediate"].append("Implement sleep hygiene practices")
                    recommendations["specific"].append("Establish consistent bedtime routine")
                
                if "anxiety" in question.lower() and response >= 3:
                    recommendations["immediate"].append("Practice breathing exercises")
                    recommendations["specific"].append("Learn progressive muscle relaxation")
                
                if "work" in question.lower() and response >= 3:
                    recommendations["short_term"].append("Discuss workload with supervisor")
                    recommendations["specific"].append("Implement time management strategies")
        
        # Voice analysis recommendations
        voice_indicators = findings.get('voice_indicators', {})
        if voice_indicators.get('stress_level') in ['high', 'severe']:
            recommendations["immediate"].append("Practice vocal stress reduction techniques")
            recommendations["specific"].append("Engage in regular verbal expression exercises")
        
        # Facial analysis recommendations
        facial_indicators = findings.get('facial_indicators', {})
        dominant_emotions = facial_indicators.get('dominant_emotions', {})
        
        if dominant_emotions.get('sad', 0) > dominant_emotions.get('happy', 0):
            recommendations["short_term"].append("Engage in mood-lifting activities")
            recommendations["specific"].append("Schedule enjoyable social activities")
        
        if dominant_emotions.get('angry', 0) > 2:
            recommendations["immediate"].append("Practice anger management techniques")
            recommendations["specific"].append("Learn conflict resolution skills")
        
        return recommendations
    
    def _parse_ai_response(self, ai_text: str, findings: Dict) -> Dict:
        """Parse AI-generated text into structured recommendations"""
        recommendations = {
            "immediate": [],
            "short_term": [],
            "long_term": [],
            "specific": []
        }
        
        # Simple parsing logic - can be enhanced
        sentences = ai_text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short fragments
                if any(word in sentence.lower() for word in ['immediately', 'urgent', 'now', 'today']):
                    recommendations["immediate"].append(sentence)
                elif any(word in sentence.lower() for word in ['week', 'short', 'soon']):
                    recommendations["short_term"].append(sentence)
                elif any(word in sentence.lower() for word in ['long', 'future', 'ongoing']):
                    recommendations["long_term"].append(sentence)
                else:
                    recommendations["specific"].append(sentence)
        
        return recommendations
    
    def _combine_recommendations(self, base_recs: Dict, ai_recs: Dict, findings: Dict) -> Dict:
        """Combine base template recommendations with AI-generated ones"""
        combined = {
            "immediate": base_recs.get("immediate_actions", []),
            "short_term": ai_recs.get("short_term", []),
            "long_term": ai_recs.get("long_term", []),
            "specific": ai_recs.get("specific", []),
            "resources": [
                "Military Mental Health Services",
                "Employee Assistance Program",
                "Stress Management Workshops",
                "Peer Support Groups"
            ],
            "confidence": 0.85 if self.is_initialized else 0.75
        }
        
        # Add AI immediate recommendations if available
        if ai_recs.get("immediate"):
            combined["immediate"].extend(ai_recs["immediate"])
        
        # Add follow-up recommendations as short-term goals
        if base_recs.get("follow_up"):
            combined["short_term"].extend(base_recs["follow_up"])
        
        # Remove duplicates and limit recommendations
        for key in ["immediate", "short_term", "long_term", "specific"]:
            combined[key] = list(dict.fromkeys(combined[key]))[:5]  # Remove duplicates and limit to 5
        
        return combined
    
    def _fallback_recommendations(self, stress_level: str) -> Dict:
        """Fallback recommendations when all else fails"""
        base = self.recommendation_templates.get(stress_level.lower(), 
                                                self.recommendation_templates["moderate"])
        
        return {
            "stress_level": stress_level,
            "immediate_actions": base.get("immediate_actions", []),
            "short_term_goals": base.get("follow_up", []),
            "long_term_strategies": [
                "Develop resilience skills",
                "Maintain healthy lifestyle",
                "Build strong support network",
                "Practice stress prevention"
            ],
            "specific_interventions": [
                "Regular exercise routine",
                "Mindfulness practice",
                "Social connection activities",
                "Professional development"
            ],
            "resources": [
                "Military Mental Health Services",
                "Employee Assistance Program"
            ],
            "generated_by": "Fallback",
            "confidence": 0.6
        }
    
    def format_recommendations_for_display(self, recommendations: Dict, language: str = "en") -> str:
        """Format recommendations for display in the app"""
        if language == "hi":
            headers = {
                "immediate_actions": "तत्काल कार्य",
                "short_term_goals": "अल्पकालिक लक्ष्य", 
                "long_term_strategies": "दीर्घकालिक रणनीति",
                "specific_interventions": "विशिष्ट हस्तक्षेप",
                "resources": "संसाधन"
            }
        else:
            headers = {
                "immediate_actions": "Immediate Actions",
                "short_term_goals": "Short-term Goals",
                "long_term_strategies": "Long-term Strategies", 
                "specific_interventions": "Specific Interventions",
                "resources": "Available Resources"
            }
        
        formatted = f"**Stress Level: {recommendations.get('stress_level', 'Unknown')}**\n\n"
        
        for key, header in headers.items():
            items = recommendations.get(key, [])
            if items:
                formatted += f"**{header}:**\n"
                for i, item in enumerate(items, 1):
                    formatted += f"{i}. {item}\n"
                formatted += "\n"
        
        formatted += f"*Generated by: {recommendations.get('generated_by', 'System')}*\n"
        formatted += f"*Confidence: {recommendations.get('confidence', 0.8):.1%}*"
        
        return formatted
