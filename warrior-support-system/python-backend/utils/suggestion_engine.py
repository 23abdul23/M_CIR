#!/usr/bin/env python3
"""
Suggestion Engine using local CPU-based analysis
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from models.suggestion_engine import MilitarySuggestionEngine
except ImportError:
    # Fallback if MilitarySuggestionEngine is not available
    MilitarySuggestionEngine = None

class SuggestionEngine:
    """
    Local CPU-based suggestion engine for mental health recommendations
    """
    
    def __init__(self):
        self.military_engine = MilitarySuggestionEngine() if MilitarySuggestionEngine else None
        
        # Base suggestions for different mental states
        self.base_suggestions = {
            "depression": {
                "mild": [
                    "Consider talking to a trusted friend or family member",
                    "Engage in regular physical exercise",
                    "Maintain a consistent sleep schedule",
                    "Practice mindfulness or meditation",
                    "Consider professional counseling if symptoms persist"
                ],
                "moderate": [
                    "Seek professional mental health support immediately",
                    "Contact your unit's mental health officer",
                    "Avoid isolation - stay connected with support network",
                    "Consider temporary duty modifications if needed",
                    "Follow up with medical personnel regularly"
                ],
                "severe": [
                    "Seek immediate professional help - contact crisis hotline",
                    "Inform your commanding officer about your mental health needs",
                    "Consider inpatient mental health treatment",
                    "Remove access to weapons if having harmful thoughts",
                    "Have someone stay with you for support and safety"
                ]
            },
            "anxiety": {
                "mild": [
                    "Practice deep breathing exercises",
                    "Use progressive muscle relaxation techniques",
                    "Limit caffeine and alcohol consumption",
                    "Maintain regular exercise routine",
                    "Consider stress management workshops"
                ],
                "moderate": [
                    "Seek counseling for anxiety management techniques",
                    "Consider cognitive behavioral therapy (CBT)",
                    "Discuss medication options with medical officer",
                    "Practice grounding techniques during panic episodes",
                    "Inform trusted colleagues about your condition"
                ],
                "severe": [
                    "Seek immediate mental health intervention",
                    "Consider temporary duty limitations",
                    "Work with mental health professionals on treatment plan",
                    "Use prescribed anxiety medications as directed",
                    "Develop comprehensive safety and coping plan"
                ]
            },
            "ptsd": {
                "mild": [
                    "Consider trauma-focused therapy",
                    "Practice grounding techniques for flashbacks",
                    "Maintain connection with fellow veterans",
                    "Engage in physical activities to manage symptoms",
                    "Learn about PTSD and its effects"
                ],
                "moderate": [
                    "Seek specialized PTSD treatment immediately",
                    "Consider EMDR or trauma-focused CBT",
                    "Work with military mental health specialists",
                    "Discuss duty modifications with command",
                    "Join veteran support groups"
                ],
                "severe": [
                    "Seek immediate specialized trauma treatment",
                    "Consider intensive outpatient or inpatient programs",
                    "Work closely with military mental health team",
                    "Implement comprehensive safety planning",
                    "Consider temporary removal from high-stress duties"
                ]
            },
            "stress": {
                "mild": [
                    "Practice time management techniques",
                    "Use stress reduction exercises",
                    "Maintain work-life balance",
                    "Get adequate sleep and nutrition",
                    "Talk to supervisor about workload concerns"
                ],
                "moderate": [
                    "Seek stress management counseling",
                    "Consider duty schedule modifications",
                    "Practice advanced stress reduction techniques",
                    "Address underlying stressors with support",
                    "Monitor for escalation of symptoms"
                ],
                "severe": [
                    "Seek immediate stress management intervention",
                    "Consider temporary duty modifications",
                    "Work with mental health professionals",
                    "Address systemic stressors in work environment",
                    "Develop comprehensive stress management plan"
                ]
            }
        }
    
    def generate_suggestions(self, mental_state: str, severity: str = "moderate", context: str = "military personnel", language: str = "english") -> list:
        """
        Generate suggestions based on mental state and severity
        
        Args:
            mental_state: Detected mental state (depression, anxiety, ptsd, stress)
            severity: Severity level (mild, moderate, severe)
            context: Context information (military personnel, combat veteran, etc.)
            language: Language preference (english, hindi)
            
        Returns:
            List of relevant suggestions
        """
        try:
            # Use military suggestion engine for comprehensive recommendations if available
            if self.military_engine:
                user_profile = {"context": context, "language": language}
                assessment_result = {
                    "mental_state": mental_state,
                    "overall_score": self._severity_to_score(severity),
                    "detected_conditions": [mental_state]
                }

                military_suggestions = self.military_engine.generate_personalized_suggestions(
                    assessment_result, user_profile, language
                )
            else:
                military_suggestions = {}
            
            # Combine with base suggestions
            base_suggestions = self._get_base_suggestions(mental_state, severity)
            
            # Merge suggestions
            all_suggestions = []
            
            if "immediate_actions" in military_suggestions:
                all_suggestions.extend(military_suggestions["immediate_actions"])
            
            all_suggestions.extend(base_suggestions)
            
            if "lifestyle_recommendations" in military_suggestions:
                all_suggestions.extend(military_suggestions["lifestyle_recommendations"])
            
            if "professional_help" in military_suggestions:
                all_suggestions.extend(military_suggestions["professional_help"])
            
            # Remove duplicates and limit to top suggestions
            unique_suggestions = list(dict.fromkeys(all_suggestions))
            return unique_suggestions[:8]  # Return top 8 suggestions
            
        except Exception as e:
            # Fallback to base suggestions
            return self._get_base_suggestions(mental_state, severity)
    
    def _get_base_suggestions(self, mental_state: str, severity: str) -> list:
        """Get base suggestions for a mental state and severity"""
        if mental_state in self.base_suggestions:
            if severity in self.base_suggestions[mental_state]:
                return self.base_suggestions[mental_state][severity]
            else:
                # Default to moderate if severity not found
                return self.base_suggestions[mental_state].get("moderate", [])
        else:
            # Generic suggestions for unknown mental states
            return [
                "Consider speaking with a mental health professional",
                "Maintain regular contact with support network",
                "Practice self-care and stress management",
                "Monitor your mental health regularly",
                "Seek help if symptoms worsen"
            ]
    
    def _severity_to_score(self, severity: str) -> int:
        """Convert severity level to numeric score"""
        severity_map = {
            "mild": 30,
            "moderate": 60,
            "severe": 90
        }
        return severity_map.get(severity, 50)
    
    def generate_emergency_suggestions(self, mental_state: str) -> dict:
        """Generate emergency suggestions for crisis situations"""
        emergency_contacts = {
            "english": [
                "National Suicide Prevention Lifeline: 988",
                "Crisis Text Line: Text HOME to 741741",
                "Military Crisis Line: 1-800-273-8255, Press 1",
                "Emergency Services: 911"
            ],
            "hindi": [
                "राष्ट्रीय आत्महत्या रोकथाम हेल्पलाइन: 988",
                "संकट टेक्स्ट लाइन: HOME को 741741 पर भेजें",
                "सैन्य संकट लाइन: 1-800-273-8255, 1 दबाएं",
                "आपातकालीन सेवाएं: 911"
            ]
        }
        
        immediate_actions = {
            "english": [
                "Stay with someone you trust",
                "Remove access to weapons or harmful objects",
                "Contact emergency services if in immediate danger",
                "Go to nearest emergency room if having thoughts of self-harm",
                "Call your commanding officer or duty officer"
            ],
            "hindi": [
                "किसी विश्वसनीय व्यक्ति के साथ रहें",
                "हथियारों या हानिकारक वस्तुओं तक पहुंच हटाएं",
                "तत्काल खतरे में होने पर आपातकालीन सेवाओं से संपर्क करें",
                "आत्म-हानि के विचार आने पर निकटतम आपातकालीन कक्ष में जाएं",
                "अपने कमांडिंग ऑफिसर या ड्यूटी ऑफिसर को कॉल करें"
            ]
        }
        
        return {
            "emergency_contacts": emergency_contacts,
            "immediate_actions": immediate_actions,
            "severity": "emergency",
            "requires_immediate_attention": True
        }
    
    def get_follow_up_plan(self, mental_state: str, severity: str) -> dict:
        """Generate follow-up plan for ongoing care"""
        follow_up_timeline = {
            "mild": "1-2 weeks",
            "moderate": "3-7 days", 
            "severe": "24-48 hours"
        }
        
        follow_up_actions = {
            "mild": [
                "Schedule check-in with mental health professional",
                "Monitor symptoms daily",
                "Continue recommended coping strategies",
                "Reassess if symptoms worsen"
            ],
            "moderate": [
                "Schedule immediate follow-up appointment",
                "Daily symptom monitoring",
                "Regular check-ins with support network",
                "Consider medication evaluation"
            ],
            "severe": [
                "Immediate professional follow-up required",
                "Continuous monitoring and support",
                "Regular medical evaluations",
                "Comprehensive treatment plan implementation"
            ]
        }
        
        return {
            "timeline": follow_up_timeline.get(severity, "1 week"),
            "actions": follow_up_actions.get(severity, follow_up_actions["moderate"]),
            "monitoring_required": True,
            "professional_oversight": severity in ["moderate", "severe"]
        }
