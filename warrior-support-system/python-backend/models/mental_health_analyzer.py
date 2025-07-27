"""
Mental Health Analysis using Local CPU Models
Analyzes questionnaire responses using local Hugging Face models
"""

import re
from typing import List, Dict, Any, Optional
from .hindi_sentiment import analyze_hindi_sentiment

class QWarriorMentalHealthAnalyzer:
    """
    QWarrior System - Advanced Mental Health Analysis for Army Personnel
    Robust analysis using local CPU models with military-specific indicators
    """

    def __init__(self):
        # Military-specific mental health indicators
        self.depression_keywords = {
            "hindi": [
                "उदास", "निराश", "अकेला", "दुखी", "हताश", "रोना", "मरना", "आत्महत्या",
                "बेकार", "असहाय", "थका हुआ", "खाली", "बोझ", "अंधकार", "दर्द", "पीड़ा"
            ],
            "english": [
                "sad", "depressed", "hopeless", "lonely", "worthless", "crying", "death", "suicide",
                "useless", "helpless", "exhausted", "empty", "burden", "darkness", "pain", "suffering"
            ]
        }

        self.anxiety_keywords = {
            "hindi": [
                "चिंता", "घबराहट", "डर", "तनाव", "परेशान", "बेचैन", "नर्वस", "भयभीत",
                "चौंकना", "सांस फूलना", "दिल की धड़कन", "पसीना", "कांपना", "अशांत"
            ],
            "english": [
                "anxiety", "worry", "fear", "stress", "nervous", "panic", "restless", "scared",
                "startled", "breathless", "heartbeat", "sweating", "trembling", "agitated"
            ]
        }

        self.ptsd_keywords = {
            "hindi": [
                "बुरे सपने", "यादें", "फ्लैशबैक", "बचना", "सुन्न", "गुस्सा", "चिड़चिड़ाहट",
                "नींद न आना", "एकाग्रता", "सतर्क", "डरावने विचार", "अपराधबोध"
            ],
            "english": [
                "nightmares", "memories", "flashbacks", "avoidance", "numb", "anger", "irritability",
                "insomnia", "concentration", "hypervigilant", "intrusive thoughts", "guilt"
            ]
        }

        self.military_stress_keywords = {
            "hindi": [
                "मिशन", "युद्ध", "लड़ाई", "दुश्मन", "हथियार", "बम", "गोली", "मौत का डर",
                "साथी की मौत", "कमांड", "आदेश", "ड्यूटी", "जिम्मेदारी", "दबाव"
            ],
            "english": [
                "mission", "war", "combat", "enemy", "weapons", "bomb", "bullet", "fear of death",
                "comrade death", "command", "orders", "duty", "responsibility", "pressure"
            ]
        }

        self.positive_keywords = {
            "hindi": [
                "खुश", "अच्छा", "ठीक", "सामान्य", "स्वस्थ", "प्रसन्न", "संतुष्ट", "शांत",
                "मजबूत", "आत्मविश्वास", "उम्मीद", "सकारात्मक", "खुशी", "राहत"
            ],
            "english": [
                "happy", "good", "fine", "normal", "healthy", "satisfied", "content", "calm",
                "strong", "confident", "hope", "positive", "joy", "relief"
            ]
        }

        # Military resilience indicators
        self.resilience_keywords = {
            "hindi": [
                "साहस", "वीरता", "दृढ़ता", "संघर्ष", "जीत", "सफलता", "टीम वर्क", "एकता",
                "अनुशासन", "समर्पण", "सेवा", "गर्व", "सम्मान", "कर्तव्य"
            ],
            "english": [
                "courage", "bravery", "determination", "struggle", "victory", "success", "teamwork", "unity",
                "discipline", "dedication", "service", "pride", "honor", "duty"
            ]
        }
    
    def detect_language(self, text: str) -> str:
        """Detect if text is primarily Hindi or English"""
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        total_chars = len(text.strip())
        
        if total_chars == 0:
            return "english"
        
        hindi_ratio = hindi_chars / total_chars
        return "hindi" if hindi_ratio > 0.3 else "english"
    
    def analyze_text_response(self, text: str, language: str = None) -> Dict[str, Any]:
        """
        QWarrior Advanced Text Analysis for Military Mental Health
        Comprehensive analysis including PTSD, military stress, and resilience factors
        """
        if not text or len(text.strip()) < 3:
            return {"sentiment_score": 0, "keywords": {}, "risk_level": "normal", "military_factors": {}}

        text = text.lower().strip()

        if language is None:
            language = self.detect_language(text)

        # Get sentiment analysis using local model
        sentiment_result = analyze_hindi_sentiment(text)
        sentiment_score = sentiment_result.get("sentiment_score", 0)
        confidence = sentiment_result.get("confidence", 0.5)

        # Advanced keyword analysis for military personnel
        keywords_found = {
            "depression": [],
            "anxiety": [],
            "ptsd": [],
            "military_stress": [],
            "positive": [],
            "resilience": []
        }

        # Check for depression indicators
        for keyword in self.depression_keywords.get(language, []):
            if keyword.lower() in text:
                keywords_found["depression"].append(keyword)

        # Check for anxiety indicators
        for keyword in self.anxiety_keywords.get(language, []):
            if keyword.lower() in text:
                keywords_found["anxiety"].append(keyword)

        # Check for PTSD indicators (military-specific)
        for keyword in self.ptsd_keywords.get(language, []):
            if keyword.lower() in text:
                keywords_found["ptsd"].append(keyword)

        # Check for military stress indicators
        for keyword in self.military_stress_keywords.get(language, []):
            if keyword.lower() in text:
                keywords_found["military_stress"].append(keyword)

        # Check for positive indicators
        for keyword in self.positive_keywords.get(language, []):
            if keyword.lower() in text:
                keywords_found["positive"].append(keyword)

        # Check for resilience indicators
        for keyword in self.resilience_keywords.get(language, []):
            if keyword.lower() in text:
                keywords_found["resilience"].append(keyword)

        # Advanced risk calculation for military context
        risk_score = 0

        # Sentiment contribution (weighted by confidence)
        sentiment_weight = confidence * 2
        if sentiment_score < -0.6:
            risk_score += 4 * sentiment_weight
        elif sentiment_score < -0.3:
            risk_score += 3 * sentiment_weight
        elif sentiment_score < -0.1:
            risk_score += 2 * sentiment_weight
        elif sentiment_score < 0:
            risk_score += 1 * sentiment_weight
        elif sentiment_score > 0.3:
            risk_score -= 1 * sentiment_weight

        # Military-specific keyword weights
        risk_score += len(keywords_found["depression"]) * 3.0
        risk_score += len(keywords_found["anxiety"]) * 2.0
        risk_score += len(keywords_found["ptsd"]) * 4.0  # Higher weight for PTSD
        risk_score += len(keywords_found["military_stress"]) * 2.5
        risk_score -= len(keywords_found["positive"]) * 1.5
        risk_score -= len(keywords_found["resilience"]) * 2.0  # Resilience is protective

        # Military-specific risk assessment
        military_factors = {
            "ptsd_indicators": len(keywords_found["ptsd"]),
            "combat_stress": len(keywords_found["military_stress"]),
            "resilience_level": len(keywords_found["resilience"]),
            "overall_military_risk": min(10, max(0, risk_score))
        }

        # Determine risk level with military context
        if risk_score >= 8:
            risk_level = "severe"
        elif risk_score >= 5:
            risk_level = "moderate"
        elif risk_score >= 2:
            risk_level = "mild"
        else:
            risk_level = "normal"

        # Special case: High PTSD indicators always elevate risk
        if len(keywords_found["ptsd"]) >= 3:
            risk_level = "severe" if risk_level != "severe" else risk_level
        elif len(keywords_found["ptsd"]) >= 2:
            risk_level = "moderate" if risk_level == "normal" or risk_level == "mild" else risk_level

        return {
            "sentiment_score": sentiment_score,
            "sentiment_confidence": confidence,
            "keywords": keywords_found,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "military_factors": military_factors,
            "analysis_language": language
        }
    
    def analyze_mcq_response(self, response_index: int, total_options: int, question_type: str) -> Dict[str, Any]:
        """Analyze multiple choice response"""
        if total_options == 0:
            return {"risk_score": 0, "risk_level": "normal"}
        
        # Normalize response to 0-1 scale
        normalized_score = response_index / (total_options - 1) if total_options > 1 else 0
        
        # For most mental health questions, higher index = higher risk
        risk_score = normalized_score * 4  # Scale to 0-4
        
        if risk_score >= 3:
            risk_level = "severe"
        elif risk_score >= 2:
            risk_level = "moderate"
        elif risk_score >= 1:
            risk_level = "mild"
        else:
            risk_level = "normal"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "normalized_score": normalized_score
        }
    
    def generate_military_recommendations(self, mental_state: str, military_factors: Dict, language: str = "english") -> List[str]:
        """
        Generate military-specific recommendations based on QWarrior analysis
        Includes PTSD, combat stress, and resilience-building recommendations
        """
        recommendations = []
        ptsd_indicators = military_factors.get("ptsd_indicators", 0)
        combat_stress = military_factors.get("combat_stress", 0)
        resilience_level = military_factors.get("resilience_level", 0)

        if language == "hindi":
            if mental_state == "severe":
                recommendations = [
                    "🚨 तत्काल सैन्य मानसिक स्वास्थ्य अधिकारी से संपर्क करें",
                    "📞 आपातकालीन हेल्पलाइन: 9152987821 (24/7 उपलब्ध)",
                    "👥 अपने कमांडिंग ऑफिसर को सूचित करें",
                    "🏥 मेडिकल ऑफिसर से तुरंत मिलें",
                    "❌ अकेले ड्यूटी न करें, बडी सिस्टम का उपयोग करें"
                ]

                if ptsd_indicators >= 2:
                    recommendations.extend([
                        "🧠 PTSD विशेषज्ञ से तुरंत सलाह लें",
                        "💊 दवा की आवश्यकता हो सकती है",
                        "🏠 परिवार को सूचित करें और सहायता लें"
                    ])

            elif mental_state == "moderate":
                recommendations = [
                    "🩺 सैन्य काउंसलर से नियमित सलाह लें",
                    "🏃‍♂️ दैनिक शारीरिक प्रशिक्षण जारी रखें",
                    "😴 पर्याप्त नींद (6-8 घंटे) सुनिश्चित करें",
                    "🧘‍♂️ तनाव प्रबंधन तकनीकें सीखें",
                    "👫 साथी सैनिकों से बात करें"
                ]

                if combat_stress >= 2:
                    recommendations.extend([
                        "⚔️ कॉम्बैट स्ट्रेस कंट्रोल प्रोग्राम में भाग लें",
                        "🎯 मिशन के बाद डीब्रीफिंग सेशन अटेंड करें"
                    ])

            elif mental_state == "mild":
                recommendations = [
                    "🧘 दैनिक ध्यान या प्राणायाम (15 मिनट)",
                    "📅 नियमित दिनचर्या बनाए रखें",
                    "🤝 यूनिट की सामाजिक गतिविधियों में भाग लें",
                    "🥗 संतुलित सैन्य आहार लें",
                    "📚 तनाव प्रबंधन की किताबें पढ़ें"
                ]
            else:
                recommendations = [
                    "✅ अपनी अच्छी मानसिक स्थिति बनाए रखें",
                    "💪 नियमित PT और व्यायाम जारी रखें",
                    "🎖️ अपनी सेवा पर गर्व करें",
                    "👥 साथी सैनिकों के साथ संपर्क बनाए रखें"
                ]

        else:  # English recommendations
            if mental_state == "severe":
                recommendations = [
                    "🚨 Contact Military Mental Health Officer immediately",
                    "📞 Emergency Helpline: 9152987821 (24/7 available)",
                    "👥 Inform your Commanding Officer",
                    "🏥 See Medical Officer immediately",
                    "❌ Do not perform solo duties, use buddy system"
                ]

                if ptsd_indicators >= 2:
                    recommendations.extend([
                        "🧠 Consult PTSD specialist immediately",
                        "💊 Medication may be required",
                        "🏠 Inform family and seek support"
                    ])

            elif mental_state == "moderate":
                recommendations = [
                    "🩺 Regular counseling with military counselor",
                    "🏃‍♂️ Continue daily physical training",
                    "😴 Ensure adequate sleep (6-8 hours)",
                    "🧘‍♂️ Learn stress management techniques",
                    "👫 Talk to fellow soldiers"
                ]

                if combat_stress >= 2:
                    recommendations.extend([
                        "⚔️ Participate in Combat Stress Control programs",
                        "🎯 Attend post-mission debriefing sessions"
                    ])

            elif mental_state == "mild":
                recommendations = [
                    "🧘 Daily meditation or breathing exercises (15 min)",
                    "📅 Maintain regular military routine",
                    "🤝 Participate in unit social activities",
                    "🥗 Maintain balanced military diet",
                    "📚 Read stress management resources"
                ]
            else:
                recommendations = [
                    "✅ Continue maintaining excellent mental health",
                    "💪 Keep up regular PT and exercise",
                    "🎖️ Take pride in your service",
                    "👥 Maintain connections with fellow soldiers"
                ]

        # Add resilience-building recommendations if low resilience
        if resilience_level < 2:
            if language == "hindi":
                recommendations.extend([
                    "🛡️ मानसिक मजबूती बढ़ाने के लिए रेजिलिएंस ट्रेनिंग लें",
                    "🎯 छोटे लक्ष्य निर्धारित करें और उन्हें पूरा करें"
                ])
            else:
                recommendations.extend([
                    "🛡️ Take resilience training to build mental strength",
                    "🎯 Set small goals and achieve them"
                ])

        return recommendations

def analyze_mental_health_responses(responses: List[Dict[str, Any]], language: str = "english") -> Dict[str, Any]:
    """
    QWarrior System - Advanced Military Mental Health Analysis

    Args:
        responses: List of response dictionaries with question and answer data
        language: Primary language for analysis

    Returns:
        Dictionary with comprehensive analysis results including military factors
    """
    analyzer = QWarriorMentalHealthAnalyzer()

    total_risk_score = 0
    response_count = 0
    sentiment_scores = []
    confidence_scores = []

    # Military-specific tracking
    all_keywords = {
        "depression": [], "anxiety": [], "ptsd": [],
        "military_stress": [], "positive": [], "resilience": []
    }

    military_factors_aggregate = {
        "ptsd_indicators": 0,
        "combat_stress": 0,
        "resilience_level": 0,
        "overall_military_risk": 0
    }

    detailed_analysis = []

    for response_data in responses:
        response = response_data.get("response")
        question_type = response_data.get("question_type", "text")
        question_text = response_data.get("question_text", "")

        if response is None:
            continue

        response_count += 1

        if question_type == "text" and isinstance(response, str):
            # Advanced text analysis using QWarrior system
            text_analysis = analyzer.analyze_text_response(response, language)
            total_risk_score += text_analysis["risk_score"]
            sentiment_scores.append(text_analysis["sentiment_score"])
            confidence_scores.append(text_analysis.get("sentiment_confidence", 0.5))

            # Aggregate military factors
            mil_factors = text_analysis.get("military_factors", {})
            military_factors_aggregate["ptsd_indicators"] += mil_factors.get("ptsd_indicators", 0)
            military_factors_aggregate["combat_stress"] += mil_factors.get("combat_stress", 0)
            military_factors_aggregate["resilience_level"] += mil_factors.get("resilience_level", 0)

            # Collect all keywords
            for key, keywords in text_analysis["keywords"].items():
                if key in all_keywords:
                    all_keywords[key].extend(keywords)

            # Store detailed analysis
            detailed_analysis.append({
                "question": question_text,
                "response": response,
                "analysis": text_analysis
            })

        elif question_type in ["multiple_choice", "scale"]:
            # Enhanced MCQ/scale analysis
            if isinstance(response, int):
                # Determine number of options based on question content
                num_options = 5 if "scale" in question_type.lower() else 4
                mcq_analysis = analyzer.analyze_mcq_response(response, num_options, question_type)
                total_risk_score += mcq_analysis["risk_score"]

                detailed_analysis.append({
                    "question": question_text,
                    "response": response,
                    "analysis": mcq_analysis
                })

    # Calculate comprehensive metrics
    if response_count == 0:
        return {
            "overall_score": 0,
            "percentage": 0,
            "mental_state": "normal",
            "sentiment_analysis": {},
            "military_factors": {},
            "recommendations": [],
            "qwarrior_analysis": "No responses to analyze"
        }

    average_risk_score = total_risk_score / response_count
    percentage = min(100, (average_risk_score / 8) * 100)  # Adjusted scale for enhanced scoring

    # Enhanced mental state determination with military factors
    base_mental_state = "normal"
    if average_risk_score >= 6:
        base_mental_state = "severe"
    elif average_risk_score >= 4:
        base_mental_state = "moderate"
    elif average_risk_score >= 2:
        base_mental_state = "mild"

    # Military factor adjustments
    ptsd_risk = military_factors_aggregate["ptsd_indicators"]
    combat_stress_risk = military_factors_aggregate["combat_stress"]

    # Escalate mental state based on military factors
    if ptsd_risk >= 4:
        base_mental_state = "severe"
    elif ptsd_risk >= 2 and base_mental_state in ["normal", "mild"]:
        base_mental_state = "moderate"

    if combat_stress_risk >= 3 and base_mental_state == "normal":
        base_mental_state = "mild"

    mental_state = base_mental_state

    # Enhanced sentiment analysis
    sentiment_analysis = {}
    if sentiment_scores:
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        sentiment_analysis = {
            "overall_sentiment": sum(sentiment_scores) / len(sentiment_scores),
            "sentiment_confidence": avg_confidence,
            "sentiment_count": len(sentiment_scores),
            "positive_responses": len([s for s in sentiment_scores if s > 0]),
            "negative_responses": len([s for s in sentiment_scores if s < 0]),
            "neutral_responses": len([s for s in sentiment_scores if s == 0])
        }

    # Generate military-specific recommendations
    recommendations = analyzer.generate_military_recommendations(
        mental_state, military_factors_aggregate, language
    )

    # QWarrior analysis summary
    qwarrior_summary = f"QWarrior Analysis Complete: {response_count} responses analyzed"
    if ptsd_risk > 0:
        qwarrior_summary += f", {ptsd_risk} PTSD indicators detected"
    if combat_stress_risk > 0:
        qwarrior_summary += f", {combat_stress_risk} combat stress factors identified"

    return {
        "overall_score": min(100, average_risk_score * 12.5),  # Scale to 0-100
        "percentage": percentage,
        "mental_state": mental_state,
        "sentiment_analysis": sentiment_analysis,
        "military_factors": military_factors_aggregate,
        "keywords_found": all_keywords,
        "recommendations": recommendations,
        "response_count": response_count,
        "qwarrior_analysis": qwarrior_summary,
        "detailed_analysis": detailed_analysis,
        "analysis_method": "QWarrior Military Mental Health System"
    }
