"""
Enhanced Suggestion Engine for Army Mental Health Assessment System
Provides personalized mental health suggestions based on assessment results
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class MentalHealthSuggestionEngine:
    """
    Advanced suggestion engine that provides personalized mental health recommendations
    based on assessment results, user profile, and severity levels
    """
    
    def __init__(self):
        self.suggestions_db = self._load_suggestions_database()
        self.emergency_contacts = self._load_emergency_contacts()
    
    def _load_suggestions_database(self) -> Dict[str, Any]:
        """Load comprehensive suggestions database"""
        return {
            "depression": {
                "mild": {
                    "hindi": [
                        "नियमित व्यायाम करें - दिन में कम से कम 30 मिनट टहलें",
                        "पर्याप्त नींद लें - रोज 7-8 घंटे की नींद जरूरी है",
                        "परिवार और दोस्तों से बात करें - अकेले न रहें",
                        "योग और ध्यान का अभ्यास करें",
                        "संतुलित आहार लें - फल और सब्जियों को शामिल करें",
                        "सूर्य की रोशनी में समय बिताएं",
                        "अपनी पसंदीदा गतिविधियों में भाग लें",
                        "दैनिक दिनचर्या बनाए रखें"
                    ],
                    "english": [
                        "Exercise regularly - walk for at least 30 minutes daily",
                        "Get adequate sleep - 7-8 hours of sleep is essential",
                        "Talk to family and friends - don't stay alone",
                        "Practice yoga and meditation",
                        "Eat a balanced diet - include fruits and vegetables",
                        "Spend time in sunlight",
                        "Engage in your favorite activities",
                        "Maintain a daily routine"
                    ]
                },
                "moderate": {
                    "hindi": [
                        "तुरंत मानसिक स्वास्थ्य विशेषज्ञ से मिलें",
                        "परिवार के सदस्यों को अपनी स्थिति के बारे में बताएं",
                        "नियमित काउंसलिंग सेशन लें",
                        "दवाई के लिए डॉक्टर से सलाह लें",
                        "तनावपूर्ण स्थितियों से बचें",
                        "सामाजिक गतिविधियों में भाग लें",
                        "नकारात्मक विचारों को चुनौती दें",
                        "आत्म-देखभाल को प्राथमिकता दें"
                    ],
                    "english": [
                        "Consult a mental health specialist immediately",
                        "Inform family members about your condition",
                        "Take regular counseling sessions",
                        "Consult a doctor for medication",
                        "Avoid stressful situations",
                        "Participate in social activities",
                        "Challenge negative thoughts",
                        "Prioritize self-care"
                    ]
                },
                "severe": {
                    "hindi": [
                        "तत्काल चिकित्सा सहायता लें - यह आपातकालीन स्थिति है",
                        "किसी भरोसेमंद व्यक्ति के साथ रहें",
                        "मानसिक स्वास्थ्य हेल्पलाइन पर कॉल करें",
                        "अस्पताल में भर्ती होने पर विचार करें",
                        "सभी दवाइयां डॉक्टर की सलाह के अनुसार लें",
                        "आत्महत्या के विचार आने पर तुरंत मदद मांगें",
                        "24/7 निगरानी की व्यवस्था करें",
                        "पेशेवर मानसिक स्वास्थ्य टीम से संपर्क करें"
                    ],
                    "english": [
                        "Seek immediate medical help - this is an emergency",
                        "Stay with a trusted person",
                        "Call mental health helpline",
                        "Consider hospitalization",
                        "Take all medications as prescribed by doctor",
                        "Seek immediate help if having suicidal thoughts",
                        "Arrange for 24/7 monitoring",
                        "Contact professional mental health team"
                    ]
                }
            },
            "anxiety": {
                "mild": {
                    "hindi": [
                        "गहरी सांस लेने का अभ्यास करें",
                        "कैफीन और अल्कोहल से बचें",
                        "नियमित व्यायाम करें",
                        "तनाव प्रबंधन तकनीक सीखें",
                        "पर्याप्त आराम करें",
                        "चिंता के कारणों को पहचानें",
                        "सकारात्मक सोच विकसित करें",
                        "समय प्रबंधन में सुधार करें"
                    ],
                    "english": [
                        "Practice deep breathing exercises",
                        "Avoid caffeine and alcohol",
                        "Exercise regularly",
                        "Learn stress management techniques",
                        "Get adequate rest",
                        "Identify anxiety triggers",
                        "Develop positive thinking",
                        "Improve time management"
                    ]
                },
                "moderate": {
                    "hindi": [
                        "संज्ञानात्मक व्यवहार चिकित्सा (CBT) लें",
                        "चिंता विकार विशेषज्ञ से मिलें",
                        "रिलैक्सेशन तकनीक सीखें",
                        "सामाजिक समर्थन प्राप्त करें",
                        "चिंता डायरी बनाए रखें",
                        "माइंडफुलनेस का अभ्यास करें",
                        "नियमित फॉलो-अप करें",
                        "जीवनशैली में बदलाव करें"
                    ],
                    "english": [
                        "Take Cognitive Behavioral Therapy (CBT)",
                        "Consult an anxiety disorder specialist",
                        "Learn relaxation techniques",
                        "Get social support",
                        "Maintain an anxiety diary",
                        "Practice mindfulness",
                        "Regular follow-ups",
                        "Make lifestyle changes"
                    ]
                },
                "severe": {
                    "hindi": [
                        "तुरंत मानसिक स्वास्थ्य आपातकाल सेवा से संपर्क करें",
                        "पैनिक अटैक के लिए तत्काल उपचार लें",
                        "एंटी-एंग्जायटी दवाओं पर विचार करें",
                        "गहन चिकित्सा की आवश्यकता हो सकती है",
                        "दैनिक गतिविधियों में सहायता लें",
                        "24/7 सहायता उपलब्ध रखें",
                        "तनावपूर्ण स्थितियों से पूरी तरह बचें",
                        "विशेषज्ञ मानसिक स्वास्थ्य टीम से मिलें"
                    ],
                    "english": [
                        "Contact mental health emergency services immediately",
                        "Get immediate treatment for panic attacks",
                        "Consider anti-anxiety medications",
                        "Intensive therapy may be needed",
                        "Get help with daily activities",
                        "Keep 24/7 support available",
                        "Completely avoid stressful situations",
                        "Meet with specialist mental health team"
                    ]
                }
            },
            "stress": {
                "mild": {
                    "hindi": [
                        "काम और जीवन में संतुलन बनाएं",
                        "समय प्रबंधन में सुधार करें",
                        "नियमित ब्रेक लें",
                        "शौक और मनोरंजन के लिए समय निकालें",
                        "सामाजिक संपर्क बनाए रखें",
                        "स्वस्थ भोजन करें",
                        "पर्याप्त नींद लें",
                        "तनाव के स्रोतों को कम करें"
                    ],
                    "english": [
                        "Maintain work-life balance",
                        "Improve time management",
                        "Take regular breaks",
                        "Make time for hobbies and recreation",
                        "Maintain social connections",
                        "Eat healthy food",
                        "Get adequate sleep",
                        "Reduce sources of stress"
                    ]
                }
            },
            "ptsd": {
                "mild": {
                    "hindi": [
                        "ट्रामा-फोकस्ड थेरेपी लें",
                        "सुरक्षित वातावरण बनाए रखें",
                        "ट्रिगर्स को पहचानें और उनसे बचें",
                        "सामाजिक समर्थन प्राप्त करें",
                        "नियमित व्यायाम करें",
                        "रिलैक्सेशन तकनीक सीखें",
                        "स्वस्थ दिनचर्या बनाए रखें",
                        "पेशेवर सहायता लें"
                    ],
                    "english": [
                        "Take trauma-focused therapy",
                        "Maintain a safe environment",
                        "Identify and avoid triggers",
                        "Get social support",
                        "Exercise regularly",
                        "Learn relaxation techniques",
                        "Maintain healthy routine",
                        "Seek professional help"
                    ]
                }
            }
        }
    
    def _load_emergency_contacts(self) -> Dict[str, Any]:
        """Load emergency contact information"""
        return {
            "hindi": {
                "suicide_prevention": "आत्महत्या रोकथाम हेल्पलाइन: 9152987821",
                "mental_health_helpline": "मानसिक स्वास्थ्य हेल्पलाइन: 08046110007",
                "emergency": "आपातकाल: 112",
                "army_counseling": "सेना काउंसलिंग सेवा: 1800-XXX-XXXX"
            },
            "english": {
                "suicide_prevention": "Suicide Prevention Helpline: 9152987821",
                "mental_health_helpline": "Mental Health Helpline: 08046110007",
                "emergency": "Emergency: 112",
                "army_counseling": "Army Counseling Service: 1800-XXX-XXXX"
            }
        }
    
    def generate_personalized_suggestions(
        self, 
        assessment_result: Dict[str, Any], 
        user_profile: Dict[str, Any],
        language: str = "hindi"
    ) -> Dict[str, Any]:
        """
        Generate personalized suggestions based on assessment results and user profile
        
        Args:
            assessment_result: Results from mental health assessment
            user_profile: User's profile information
            language: Language preference (hindi/english)
            
        Returns:
            Comprehensive suggestions with emergency contacts and follow-up recommendations
        """
        
        mental_state = assessment_result.get("mental_state", "normal")
        overall_score = assessment_result.get("overall_score", 0)
        detected_conditions = assessment_result.get("detected_conditions", [])
        
        suggestions = {
            "immediate_actions": [],
            "lifestyle_recommendations": [],
            "professional_help": [],
            "emergency_contacts": [],
            "follow_up": [],
            "severity_level": mental_state,
            "risk_assessment": self._assess_risk_level(overall_score, detected_conditions),
            "personalized_message": ""
        }
        
        # Generate condition-specific suggestions
        for condition in detected_conditions:
            if condition in self.suggestions_db:
                severity = self._map_score_to_severity(overall_score)
                if severity in self.suggestions_db[condition]:
                    condition_suggestions = self.suggestions_db[condition][severity][language]
                    suggestions["immediate_actions"].extend(condition_suggestions[:3])
                    suggestions["lifestyle_recommendations"].extend(condition_suggestions[3:6])
                    suggestions["professional_help"].extend(condition_suggestions[6:])
        
        # Add emergency contacts if needed
        if mental_state in ["severe", "moderate"]:
            suggestions["emergency_contacts"] = list(self.emergency_contacts[language].values())
        
        # Generate personalized message
        suggestions["personalized_message"] = self._generate_personalized_message(
            user_profile, mental_state, language
        )
        
        # Add follow-up recommendations
        suggestions["follow_up"] = self._generate_follow_up_plan(mental_state, language)
        
        # Remove duplicates
        for key in ["immediate_actions", "lifestyle_recommendations", "professional_help"]:
            suggestions[key] = list(set(suggestions[key]))
        
        return suggestions
    
    def _assess_risk_level(self, score: float, conditions: List[str]) -> str:
        """Assess overall risk level based on score and conditions"""
        if score >= 75 or "severe_depression" in conditions or "severe_anxiety" in conditions:
            return "high"
        elif score >= 50 or "moderate_depression" in conditions or "moderate_anxiety" in conditions:
            return "medium"
        elif score >= 25:
            return "low"
        else:
            return "minimal"
    
    def _map_score_to_severity(self, score: float) -> str:
        """Map numerical score to severity level"""
        if score >= 75:
            return "severe"
        elif score >= 50:
            return "moderate"
        else:
            return "mild"
    
    def _generate_personalized_message(
        self, 
        user_profile: Dict[str, Any], 
        mental_state: str, 
        language: str
    ) -> str:
        """Generate personalized message based on user profile"""
        
        name = user_profile.get("full_name", "")
        rank = user_profile.get("rank", "")
        
        if language == "hindi":
            if mental_state == "severe":
                return f"{rank} {name}, आपकी मानसिक स्थिति गंभीर है। कृपया तुरंत चिकित्सा सहायता लें। आप अकेले नहीं हैं, हम आपकी मदद के लिए यहाँ हैं।"
            elif mental_state == "moderate":
                return f"{rank} {name}, आपको मानसिक स्वास्थ्य सहायता की आवश्यकता है। कृपया जल्द से जल्द विशेषज्ञ से मिलें।"
            elif mental_state == "mild":
                return f"{rank} {name}, आपकी मानसिक स्थिति में सुधार की गुंजाइश है। नीचे दिए गए सुझावों का पालन करें।"
            else:
                return f"{rank} {name}, आपकी मानसिक स्थिति सामान्य है। स्वस्थ जीवनशैली बनाए रखें।"
        else:
            if mental_state == "severe":
                return f"{rank} {name}, your mental health condition is severe. Please seek immediate medical help. You are not alone, we are here to help you."
            elif mental_state == "moderate":
                return f"{rank} {name}, you need mental health support. Please consult a specialist as soon as possible."
            elif mental_state == "mild":
                return f"{rank} {name}, there is room for improvement in your mental state. Please follow the suggestions below."
            else:
                return f"{rank} {name}, your mental state is normal. Maintain a healthy lifestyle."
    
    def _generate_follow_up_plan(self, mental_state: str, language: str) -> List[str]:
        """Generate follow-up plan based on mental state"""
        
        if language == "hindi":
            if mental_state == "severe":
                return [
                    "24 घंटे के भीतर मानसिक स्वास्थ्य विशेषज्ञ से मिलें",
                    "1 सप्ताह बाद फॉलो-अप असेसमेंट करें",
                    "दैनिक मूड ट्रैकिंग शुरू करें",
                    "परिवार को स्थिति की जानकारी दें"
                ]
            elif mental_state == "moderate":
                return [
                    "3 दिन के भीतर काउंसलर से मिलें",
                    "2 सप्ताह बाद री-असेसमेंट करें",
                    "साप्ताहिक थेरेपी सेशन शुरू करें",
                    "तनाव प्रबंधन तकनीक सीखें"
                ]
            else:
                return [
                    "1 महीने बाद फॉलो-अप असेसमेंट करें",
                    "स्वस्थ जीवनशैली बनाए रखें",
                    "नियमित व्यायाम करें",
                    "सामाजिक संपर्क बनाए रखें"
                ]
        else:
            if mental_state == "severe":
                return [
                    "Meet mental health specialist within 24 hours",
                    "Follow-up assessment after 1 week",
                    "Start daily mood tracking",
                    "Inform family about the situation"
                ]
            elif mental_state == "moderate":
                return [
                    "Meet counselor within 3 days",
                    "Re-assessment after 2 weeks",
                    "Start weekly therapy sessions",
                    "Learn stress management techniques"
                ]
            else:
                return [
                    "Follow-up assessment after 1 month",
                    "Maintain healthy lifestyle",
                    "Exercise regularly",
                    "Maintain social connections"
                ]

# Global instance
suggestion_engine = MentalHealthSuggestionEngine()
