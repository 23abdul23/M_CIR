"""
Keyword Matcher for Mental Health Assessment
"""
import re
from typing import Dict, List, Tuple, Set
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import MENTAL_HEALTH_KEYWORDS

class MentalHealthKeywordMatcher:
    """
    Matches Hindi keywords related to mental health conditions
    """

    def __init__(self):
        self.keyword_categories = MENTAL_HEALTH_KEYWORDS
        self.compiled_patterns = self._compile_keyword_patterns()

    def _compile_keyword_patterns(self) -> Dict[str, List[re.Pattern]]:
        """
        Compile regex patterns for efficient keyword matching
        """
        compiled_patterns = {}

        for category, data in self.keyword_categories.items():
            patterns = []
            for keyword in data["hindi"]:
                # Create pattern that matches whole words
                pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                patterns.append(pattern)
            compiled_patterns[category] = patterns

        return compiled_patterns

    def analyze_text(self, text: str) -> Dict[str, Dict]:
        """
        Analyze text for mental health keywords

        Args:
            text: Hindi text to analyze

        Returns:
            Dictionary with analysis results for each category
        """
        results = {}

        for category, patterns in self.compiled_patterns.items():
            matches = []
            total_matches = 0

            for pattern in patterns:
                found_matches = pattern.findall(text)
                matches.extend(found_matches)
                total_matches += len(found_matches)

            # Calculate severity score based on frequency and category weight
            severity_weight = self.keyword_categories[category]["severity_weight"]
            severity_score = min(total_matches * severity_weight, 10)  # Cap at 10

            results[category] = {
                "matches": list(set(matches)),  # Remove duplicates
                "count": total_matches,
                "severity_score": severity_score,
                "description": self.keyword_categories[category]["description"]
            }

        return results

    def get_overall_assessment(self, text: str) -> Dict:
        """
        Get overall mental health assessment from text

        Args:
            text: Hindi text to analyze

        Returns:
            Overall assessment with recommendations
        """
        analysis = self.analyze_text(text)

        # Calculate overall severity
        total_severity = sum(result["severity_score"] for result in analysis.values())
        max_possible_severity = len(analysis) * 10
        overall_severity_percentage = (total_severity / max_possible_severity) * 100

        # Determine risk level
        if overall_severity_percentage >= 70:
            risk_level = "उच्च जोखिम"  # High Risk
            recommendation = "तत्काल मानसिक स्वास्थ्य विशेषज्ञ से संपर्क करें"
        elif overall_severity_percentage >= 40:
            risk_level = "मध्यम जोखिम"  # Medium Risk
            recommendation = "मानसिक स्वास्थ्य सहायता लेने पर विचार करें"
        else:
            risk_level = "कम जोखिम"  # Low Risk
            recommendation = "नियमित स्व-देखभाल और निगरानी जारी रखें"

        # Find most concerning categories
        concerning_categories = [
            category for category, result in analysis.items()
            if result["severity_score"] >= 5
        ]

        return {
            "overall_severity_percentage": overall_severity_percentage,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "concerning_categories": concerning_categories,
            "detailed_analysis": analysis
        }

    def get_category_suggestions(self, category: str) -> List[str]:
        """
        Get suggestions for specific mental health category

        Args:
            category: Mental health category

        Returns:
            List of suggestions in Hindi
        """
        suggestions = {
            "depression": [
                "नियमित व्यायाम करें",
                "पर्याप्त नींद लें (7-8 घंटे)",
                "संतुलित आहार लें",
                "दोस्तों और परिवार से जुड़े रहें",
                "ध्यान या योग का अभ्यास करें"
            ],
            "anxiety": [
                "गहरी सांस लेने का अभ्यास करें",
                "तनाव कम करने की तकनीक सीखें",
                "कैफीन का सेवन कम करें",
                "नियमित दिनचर्या बनाए रखें",
                "रिलैक्सेशन तकनीक का उपयोग करें"
            ],
            "stress": [
                "समय प्रबंधन में सुधार करें",
                "प्राथमिकताएं निर्धारित करें",
                "काम और आराम के बीच संतुलन बनाएं",
                "सामाजिक सहायता लें",
                "शौक और मनोरंजन के लिए समय निकालें"
            ],
            "ptsd": [
                "ट्रिगर्स को पहचानें और उनसे बचें",
                "सुरक्षित वातावरण बनाए रखें",
                "विश्वसनीय लोगों से बात करें",
                "पेशेवर थेरेपी लें",
                "सहायता समूहों में भाग लें"
            ],
            "sleep_disorders": [
                "नियमित सोने का समय निर्धारित करें",
                "सोने से पहले स्क्रीन का उपयोग न करें",
                "आरामदायक नींद का माहौल बनाएं",
                "दिन में कैफीन कम लें",
                "नियमित व्यायाम करें लेकिन सोने से पहले नहीं"
            ]
        }

        return suggestions.get(category, ["सामान्य स्व-देखभाल का अभ्यास करें"])
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess Hindi text for keyword matching
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Keep Hindi characters, spaces, and basic punctuation
        text = re.sub(r'[^\u0900-\u097F\s।,;:!?]', '', text)
        
        return text
    
    def find_keywords_in_text(self, text: str, category: str = None) -> Dict[str, List[str]]:
        """
        Find keywords in text for specific category or all categories
        """
        processed_text = self.preprocess_text(text)
        found_keywords = {}
        
        categories_to_check = [category] if category else self.keyword_categories.keys()
        
        for cat in categories_to_check:
            if cat not in self.compiled_patterns:
                continue
                
            found_keywords[cat] = []
            patterns = self.compiled_patterns[cat]
            
            for i, pattern in enumerate(patterns):
                matches = pattern.findall(processed_text)
                if matches:
                    keyword = self.keyword_categories[cat]["hindi"][i]
                    found_keywords[cat].extend([keyword] * len(matches))
        
        # Remove empty categories
        found_keywords = {k: v for k, v in found_keywords.items() if v}
        
        return found_keywords
    
    def calculate_keyword_scores(self, text: str) -> Dict[str, float]:
        """
        Calculate weighted scores for each mental health category
        """
        found_keywords = self.find_keywords_in_text(text)
        category_scores = {}
        
        for category, keywords in found_keywords.items():
            if category not in self.keyword_categories:
                continue
            
            # Get weight for this category
            weight = self.keyword_categories[category]["weight"]
            
            # Calculate score based on keyword frequency and weight
            keyword_count = len(keywords)
            unique_keywords = len(set(keywords))
            
            # Score considers both frequency and variety of keywords
            base_score = (keyword_count * 0.7 + unique_keywords * 0.3)
            weighted_score = base_score * abs(weight)
            
            category_scores[category] = min(weighted_score, 1.0)
        
        return category_scores
    
    def get_mental_health_indicators(self, text: str) -> Dict[str, any]:
        """
        Get comprehensive mental health indicators from text
        """
        found_keywords = self.find_keywords_in_text(text)
        category_scores = self.calculate_keyword_scores(text)
        
        # Calculate overall risk score
        total_negative_score = 0
        total_positive_score = 0
        
        for category, score in category_scores.items():
            weight = self.keyword_categories[category]["weight"]
            if weight > 0:  # Negative indicator
                total_negative_score += score * weight
            else:  # Positive indicator
                total_positive_score += score * abs(weight)
        
        # Normalize scores
        overall_risk_score = min(total_negative_score, 1.0)
        overall_positive_score = min(total_positive_score, 1.0)
        
        # Net score (considering both positive and negative)
        net_score = max(0, overall_risk_score - overall_positive_score * 0.5)
        
        return {
            "found_keywords": found_keywords,
            "category_scores": category_scores,
            "overall_risk_score": overall_risk_score,
            "overall_positive_score": overall_positive_score,
            "net_mental_health_score": net_score,
            "total_keywords_found": sum(len(keywords) for keywords in found_keywords.values())
        }
    
    def classify_mental_state(self, text: str) -> Tuple[str, float]:
        """
        Classify mental state based on keyword analysis
        """
        indicators = self.get_mental_health_indicators(text)
        net_score = indicators["net_mental_health_score"]
        
        # Convert to percentage for classification
        score_percentage = net_score * 100
        
        if score_percentage <= 25:
            return "normal", score_percentage
        elif score_percentage <= 50:
            return "mild", score_percentage
        elif score_percentage <= 75:
            return "moderate", score_percentage
        else:
            return "severe", score_percentage
    
    def get_keyword_suggestions(self, found_keywords: Dict[str, List[str]]) -> List[str]:
        """
        Get suggestions based on found keywords
        """
        suggestions = []
        
        # Priority order for suggestions
        priority_categories = ["severe", "moderate", "mild", "normal"]
        
        for category in found_keywords.keys():
            if category == "stress" and len(found_keywords[category]) > 0:
                suggestions.append("तनाव प्रबंधन तकनीकों का अभ्यास करें")
                suggestions.append("नियमित व्यायाम और ध्यान करें")
            
            elif category == "depression" and len(found_keywords[category]) > 0:
                suggestions.append("तुरंत मानसिक स्वास्थ्य विशेषज्ञ से संपर्क करें")
                suggestions.append("परिवार और दोस्तों का साथ लें")
            
            elif category == "anxiety" and len(found_keywords[category]) > 0:
                suggestions.append("गहरी सांस लेने की तकनीक का अभ्यास करें")
                suggestions.append("शांत वातावरण में समय बिताएं")
            
            elif category == "anger" and len(found_keywords[category]) > 0:
                suggestions.append("क्रोध प्रबंधन तकनीकों का अभ्यास करें")
                suggestions.append("शारीरिक गतिविधियों में भाग लें")
            
            elif category == "sleep_issues" and len(found_keywords[category]) > 0:
                suggestions.append("नियमित नींद का समय निर्धारित करें")
                suggestions.append("सोने से पहले स्क्रीन का उपयोग कम करें")
        
        # Remove duplicates while preserving order
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in unique_suggestions:
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:5]  # Return top 5 suggestions
    
    def analyze_response_keywords(self, response_text: str) -> Dict[str, any]:
        """
        Comprehensive keyword analysis for a single response
        """
        indicators = self.get_mental_health_indicators(response_text)
        mental_state, score = self.classify_mental_state(response_text)
        suggestions = self.get_keyword_suggestions(indicators["found_keywords"])
        
        return {
            "mental_state": mental_state,
            "score": score,
            "keyword_indicators": indicators,
            "suggestions": suggestions,
            "analysis_summary": {
                "total_keywords": indicators["total_keywords_found"],
                "risk_level": mental_state,
                "primary_concerns": list(indicators["category_scores"].keys())
            }
        }

# Global instance
keyword_matcher = MentalHealthKeywordMatcher()

def analyze_keywords(text: str) -> Dict[str, any]:
    """
    Convenience function to analyze keywords in text
    """
    return keyword_matcher.analyze_response_keywords(text)

def get_mental_health_score(text: str) -> float:
    """
    Get mental health risk score (0-100)
    """
    _, score = keyword_matcher.classify_mental_state(text)
    return score
