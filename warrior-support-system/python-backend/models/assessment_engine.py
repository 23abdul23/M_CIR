"""
Mental Health Assessment Engine
"""
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import QUESTIONNAIRES
from .keyword_matcher import MentalHealthKeywordMatcher

class MentalHealthAssessmentEngine:
    """
    Main engine for conducting mental health assessments
    """
    
    def __init__(self):
        self.questionnaires = QUESTIONNAIRES
        self.keyword_matcher = MentalHealthKeywordMatcher()
        self.assessment_history = []
    
    def get_questionnaire(self, questionnaire_type: str) -> Optional[Dict]:
        """
        Get a specific questionnaire
        
        Args:
            questionnaire_type: Type of questionnaire (e.g., 'phq9', 'gad7')
            
        Returns:
            Questionnaire data or None if not found
        """
        return self.questionnaires.get(questionnaire_type)
    
    def calculate_questionnaire_score(self, questionnaire_type: str, responses: List[int]) -> Dict:
        """
        Calculate score for a completed questionnaire
        
        Args:
            questionnaire_type: Type of questionnaire
            responses: List of response values (0-3 for most questionnaires)
            
        Returns:
            Score analysis with interpretation
        """
        questionnaire = self.get_questionnaire(questionnaire_type)
        if not questionnaire:
            raise ValueError(f"Questionnaire type '{questionnaire_type}' not found")
        
        if len(responses) != len(questionnaire["questions"]):
            raise ValueError("Number of responses doesn't match number of questions")
        
        # Calculate total score
        total_score = sum(responses)
        
        # Get interpretation based on scoring ranges
        interpretation = self._get_score_interpretation(questionnaire_type, total_score)
        
        return {
            "questionnaire_type": questionnaire_type,
            "total_score": total_score,
            "max_possible_score": len(questionnaire["questions"]) * 3,  # Assuming 0-3 scale
            "interpretation": interpretation,
            "responses": responses,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_score_interpretation(self, questionnaire_type: str, score: int) -> Dict:
        """
        Get interpretation for questionnaire score
        
        Args:
            questionnaire_type: Type of questionnaire
            score: Total score
            
        Returns:
            Interpretation with severity level and recommendations
        """
        interpretations = {
            "phq9": {
                "ranges": [
                    (0, 4, "न्यूनतम अवसाद", "कोई महत्वपूर्ण अवसादग्रस्त लक्षण नहीं"),
                    (5, 9, "हल्का अवसाद", "हल्के अवसादग्रस्त लक्षण, निगरानी की आवश्यकता"),
                    (10, 14, "मध्यम अवसाद", "मध्यम अवसादग्रस्त लक्षण, उपचार पर विचार करें"),
                    (15, 19, "मध्यम-गंभीर अवसाद", "सक्रिय उपचार की आवश्यकता"),
                    (20, 27, "गंभीर अवसाद", "तत्काल पेशेवर सहायता आवश्यक")
                ]
            },
            "gad7": {
                "ranges": [
                    (0, 4, "न्यूनतम चिंता", "कोई महत्वपूर्ण चिंता के लक्षण नहीं"),
                    (5, 9, "हल्की चिंता", "हल्के चिंता के लक्षण"),
                    (10, 14, "मध्यम चिंता", "मध्यम चिंता के लक्षण, उपचार पर विचार करें"),
                    (15, 21, "गंभीर चिंता", "गंभीर चिंता, तत्काल उपचार आवश्यक")
                ]
            },
            "pss": {
                "ranges": [
                    (0, 13, "कम तनाव", "तनाव का स्तर सामान्य है"),
                    (14, 26, "मध्यम तनाव", "मध्यम तनाव, तनाव प्रबंधन तकनीक सीखें"),
                    (27, 40, "उच्च तनाव", "उच्च तनाव, पेशेवर सहायता लें")
                ]
            }
        }
        
        questionnaire_interp = interpretations.get(questionnaire_type, {})
        ranges = questionnaire_interp.get("ranges", [])
        
        for min_score, max_score, severity, description in ranges:
            if min_score <= score <= max_score:
                return {
                    "severity": severity,
                    "description": description,
                    "score_range": f"{min_score}-{max_score}",
                    "recommendations": self._get_recommendations(severity)
                }
        
        return {
            "severity": "अज्ञात",
            "description": "स्कोर की व्याख्या उपलब्ध नहीं",
            "score_range": "N/A",
            "recommendations": []
        }
    
    def _get_recommendations(self, severity: str) -> List[str]:
        """
        Get recommendations based on severity level
        
        Args:
            severity: Severity level in Hindi
            
        Returns:
            List of recommendations
        """
        recommendations = {
            "न्यूनतम अवसाद": [
                "नियमित स्व-देखभाल जारी रखें",
                "स्वस्थ जीवनशैली बनाए रखें",
                "तनाव प्रबंधन तकनीक सीखें"
            ],
            "हल्का अवसाद": [
                "नियमित व्यायाम करें",
                "सामाजिक गतिविधियों में भाग लें",
                "पर्याप्त नींद लें",
                "यदि लक्षण बने रहें तो परामर्श लें"
            ],
            "मध्यम अवसाद": [
                "मानसिक स्वास्थ्य पेशेवर से मिलें",
                "थेरेपी या परामर्श लें",
                "दवा के बारे में डॉक्टर से बात करें",
                "सहायता समूह में शामिल हों"
            ],
            "मध्यम-गंभीर अवसाद": [
                "तत्काल मानसिक स्वास्थ्य विशेषज्ञ से मिलें",
                "नियमित चिकित्सा निगरानी",
                "दवा उपचार पर विचार करें",
                "परिवार और दोस्तों का सहारा लें"
            ],
            "गंभीर अवसाद": [
                "आपातकालीन मानसिक स्वास्थ्य सेवा से संपर्क करें",
                "24/7 निगरानी की आवश्यकता हो सकती है",
                "तत्काल दवा उपचार",
                "अस्पताल में भर्ती पर विचार करें"
            ]
        }
        
        return recommendations.get(severity, ["पेशेवर सहायता लें"])
    
    def conduct_text_analysis(self, text: str) -> Dict:
        """
        Conduct keyword-based analysis of free text
        
        Args:
            text: Hindi text to analyze
            
        Returns:
            Analysis results with recommendations
        """
        return self.keyword_matcher.get_overall_assessment(text)
    
    def generate_comprehensive_report(self, 
                                    questionnaire_results: List[Dict] = None,
                                    text_analysis: Dict = None,
                                    patient_info: Dict = None) -> Dict:
        """
        Generate comprehensive mental health report
        
        Args:
            questionnaire_results: List of completed questionnaire results
            text_analysis: Results from text analysis
            patient_info: Patient demographic information
            
        Returns:
            Comprehensive report
        """
        report = {
            "report_id": f"MH_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "patient_info": patient_info or {},
            "assessment_summary": {},
            "recommendations": [],
            "follow_up_required": False
        }
        
        # Process questionnaire results
        if questionnaire_results:
            report["questionnaire_results"] = questionnaire_results
            
            # Determine overall severity from questionnaires
            high_risk_found = False
            for result in questionnaire_results:
                severity = result["interpretation"]["severity"]
                if any(keyword in severity for keyword in ["गंभीर", "मध्यम-गंभीर"]):
                    high_risk_found = True
                    report["follow_up_required"] = True
        
        # Process text analysis
        if text_analysis:
            report["text_analysis"] = text_analysis
            if text_analysis["overall_severity_percentage"] >= 70:
                report["follow_up_required"] = True
        
        # Generate overall recommendations
        report["recommendations"] = self._generate_overall_recommendations(
            questionnaire_results, text_analysis
        )
        
        # Store in history
        self.assessment_history.append(report)
        
        return report
    
    def _generate_overall_recommendations(self, 
                                        questionnaire_results: List[Dict] = None,
                                        text_analysis: Dict = None) -> List[str]:
        """
        Generate overall recommendations based on all assessments
        """
        recommendations = set()
        
        # Add questionnaire-based recommendations
        if questionnaire_results:
            for result in questionnaire_results:
                recommendations.update(result["interpretation"]["recommendations"])
        
        # Add text analysis recommendations
        if text_analysis:
            recommendations.add(text_analysis["recommendation"])
            
            # Add category-specific suggestions
            for category in text_analysis["concerning_categories"]:
                category_suggestions = self.keyword_matcher.get_category_suggestions(category)
                recommendations.update(category_suggestions)
        
        return list(recommendations)
    
    def get_assessment_history(self) -> List[Dict]:
        """
        Get history of all assessments
        """
        return self.assessment_history
    
    def save_assessment_to_file(self, assessment: Dict, filename: str):
        """
        Save assessment to JSON file
        
        Args:
            assessment: Assessment data
            filename: Output filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(assessment, f, ensure_ascii=False, indent=2)
