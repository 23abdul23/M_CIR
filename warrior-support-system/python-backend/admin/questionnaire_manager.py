"""
Admin Interface for Managing Hindi Questionnaires
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.database.crud import *
from src.database.database import get_db

class QuestionnaireManager:
    """
    Admin interface for managing mental health questionnaires
    """
    
    def __init__(self):
        self.sample_questionnaires = self._load_sample_questionnaires()
    
    def _load_sample_questionnaires(self) -> Dict[str, Dict]:
        """
        Load sample Hindi questionnaires for army mental health assessment
        """
        return {
            "army_depression_hindi": {
                "title": "सेना अवसाद मूल्यांकन प्रश्नावली",
                "description": "सैनिकों के लिए अवसाद के लक्षणों का मूल्यांकन",
                "instructions": "पिछले 2 सप्ताह में, आपको निम्नलिखित समस्याओं से कितनी परेशानी हुई है?",
                "time_limit_minutes": 15,
                "questions": [
                    {
                        "text": "काम या अन्य गतिविधियों में रुचि या आनंद की कमी",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "उदास, निराश या हताश महसूस करना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "सोने में परेशानी, नींद न आना या बहुत अधिक सोना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "थकान महसूस करना या ऊर्जा की कमी",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "भूख में कमी या अधिक खाना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "अपने बारे में बुरा महसूस करना - या यह कि आप असफल हैं या अपने परिवार को निराश किया है",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "ध्यान केंद्रित करने में परेशानी, जैसे अखबार पढ़ना या टेलीविजन देखना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "धीमी गति से चलना या बोलना जो दूसरे लोग नोटिस कर सकें, या इसके विपरीत - सामान्य से अधिक बेचैन या हिलना-डुलना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "मरने के बारे में सोचना या किसी तरह से खुद को नुकसान पहुंचाने के बारे में सोचना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    }
                ]
            },
            "army_anxiety_hindi": {
                "title": "सेना चिंता मूल्यांकन प्रश्नावली",
                "description": "सैनिकों के लिए चिंता के लक्षणों का मूल्यांकन",
                "instructions": "पिछले 2 सप्ताह में, आपको निम्नलिखित समस्याओं से कितनी परेशानी हुई है?",
                "time_limit_minutes": 10,
                "questions": [
                    {
                        "text": "घबराहट, चिंता या किनारे पर महसूस करना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "चिंता को रोकने या नियंत्रित करने में असमर्थ होना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "विभिन्न चीजों के बारे में बहुत अधिक चिंता करना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "आराम करने में परेशानी",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "इतनी बेचैनी कि स्थिर बैठना कठिन हो",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "आसानी से परेशान या चिड़चिड़ाहट होना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    },
                    {
                        "text": "डर लगना जैसे कि कुछ भयानक होने वाला है",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
                        "values": [0, 1, 2, 3]
                    }
                ]
            },
            "army_stress_hindi": {
                "title": "सेना तनाव मूल्यांकन प्रश्नावली",
                "description": "सैनिकों के लिए तनाव के स्तर का मूल्यांकन",
                "instructions": "पिछले महीने में, आपने कितनी बार निम्नलिखित महसूस किया है?",
                "time_limit_minutes": 10,
                "questions": [
                    {
                        "text": "अप्रत्याशित घटना के कारण परेशान हुए हैं?",
                        "type": "scale",
                        "options": ["कभी नहीं", "लगभग कभी नहीं", "कभी-कभी", "काफी बार", "बहुत बार"],
                        "values": [0, 1, 2, 3, 4]
                    },
                    {
                        "text": "अपने जीवन की महत्वपूर्ण चीजों को नियंत्रित करने में असमर्थ महसूस किया है?",
                        "type": "scale",
                        "options": ["कभी नहीं", "लगभग कभी नहीं", "कभी-कभी", "काफी बार", "बहुत बार"],
                        "values": [0, 1, 2, 3, 4]
                    },
                    {
                        "text": "घबराहट और तनाव महसूस किया है?",
                        "type": "scale",
                        "options": ["कभी नहीं", "लगभग कभी नहीं", "कभी-कभी", "काफी बार", "बहुत बार"],
                        "values": [0, 1, 2, 3, 4]
                    },
                    {
                        "text": "व्यक्तिगत समस्याओं से सफलतापूर्वक निपटा है?",
                        "type": "scale",
                        "options": ["कभी नहीं", "लगभग कभी नहीं", "कभी-कभी", "काफी बार", "बहुत बार"],
                        "values": [4, 3, 2, 1, 0]  # Reverse scored
                    },
                    {
                        "text": "महसूस किया है कि चीजें आपके अनुकूल चल रही हैं?",
                        "type": "scale",
                        "options": ["कभी नहीं", "लगभग कभी नहीं", "कभी-कभी", "काफी बार", "बहुत बार"],
                        "values": [4, 3, 2, 1, 0]  # Reverse scored
                    }
                ]
            },
            "army_ptsd_hindi": {
                "title": "सेना PTSD मूल्यांकन प्रश्नावली",
                "description": "सैनिकों के लिए PTSD के लक्षणों का मूल्यांकन",
                "instructions": "पिछले महीने में, आपको निम्नलिखित समस्याओं से कितनी परेशानी हुई है?",
                "time_limit_minutes": 15,
                "questions": [
                    {
                        "text": "दर्दनाक घटना की बार-बार यादें आना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "थोड़ा सा", "मध्यम", "काफी", "बहुत अधिक"],
                        "values": [0, 1, 2, 3, 4]
                    },
                    {
                        "text": "दर्दनाक घटना के बारे में बुरे सपने आना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "थोड़ा सा", "मध्यम", "काफी", "बहुत अधिक"],
                        "values": [0, 1, 2, 3, 4]
                    },
                    {
                        "text": "उन चीजों से बचना जो घटना की याद दिलाती हैं",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "थोड़ा सा", "मध्यम", "काफी", "बहुत अधिक"],
                        "values": [0, 1, 2, 3, 4]
                    },
                    {
                        "text": "लगातार सतर्क या सावधान रहना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "थोड़ा सा", "मध्यम", "काफी", "बहुत अधिक"],
                        "values": [0, 1, 2, 3, 4]
                    },
                    {
                        "text": "आसानी से चौंक जाना",
                        "type": "scale",
                        "options": ["बिल्कुल नहीं", "थोड़ा सा", "मध्यम", "काफी", "बहुत अधिक"],
                        "values": [0, 1, 2, 3, 4]
                    }
                ]
            }
        }
    
    def create_questionnaire(self, db, title: str, description: str, 
                           instructions: str, questions: List[Dict],
                           created_by: int, time_limit_minutes: int = 30) -> Dict:
        """
        Create a new questionnaire
        
        Args:
            db: Database session
            title: Questionnaire title
            description: Description
            instructions: Instructions for users
            questions: List of question dictionaries
            created_by: User ID of creator
            time_limit_minutes: Time limit in minutes
            
        Returns:
            Created questionnaire data
        """
        try:
            # Create questionnaire
            questionnaire = create_questionnaire(
                db=db,
                title=title,
                description=description,
                instructions=instructions,
                created_by=created_by,
                time_limit_minutes=time_limit_minutes
            )
            
            # Add questions
            for i, question_data in enumerate(questions):
                create_question(
                    db=db,
                    questionnaire_id=questionnaire.id,
                    question_text=question_data["text"],
                    order_number=i + 1,
                    question_type=question_data.get("type", "scale"),
                    options=question_data.get("options", []),
                    positive_keywords=question_data.get("positive_keywords", []),
                    negative_keywords=question_data.get("negative_keywords", []),
                    weight=question_data.get("weight", 1.0)
                )
            
            return {
                "success": True,
                "questionnaire_id": questionnaire.id,
                "message": f"प्रश्नावली '{title}' सफलतापूर्वक बनाई गई"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "प्रश्नावली बनाने में त्रुटि"
            }
    
    def load_sample_questionnaires(self, db, admin_user_id: int) -> Dict:
        """
        Load all sample questionnaires into database
        
        Args:
            db: Database session
            admin_user_id: Admin user ID
            
        Returns:
            Results of loading operation
        """
        results = []
        
        for questionnaire_key, questionnaire_data in self.sample_questionnaires.items():
            result = self.create_questionnaire(
                db=db,
                title=questionnaire_data["title"],
                description=questionnaire_data["description"],
                instructions=questionnaire_data["instructions"],
                questions=questionnaire_data["questions"],
                created_by=admin_user_id,
                time_limit_minutes=questionnaire_data["time_limit_minutes"]
            )
            
            results.append({
                "questionnaire_key": questionnaire_key,
                "result": result
            })
        
        successful = sum(1 for r in results if r["result"]["success"])
        
        return {
            "total_questionnaires": len(self.sample_questionnaires),
            "successful": successful,
            "failed": len(results) - successful,
            "details": results
        }
    
    def get_questionnaire_list(self, db) -> List[Dict]:
        """
        Get list of all questionnaires
        
        Args:
            db: Database session
            
        Returns:
            List of questionnaires
        """
        questionnaires = get_questionnaires(db)
        
        return [
            {
                "id": q.id,
                "title": q.title,
                "description": q.description,
                "total_questions": q.total_questions,
                "time_limit_minutes": q.time_limit_minutes,
                "is_active": q.is_active,
                "created_at": q.created_at.isoformat() if q.created_at else None
            }
            for q in questionnaires
        ]
    
    def get_questionnaire_details(self, db, questionnaire_id: int) -> Optional[Dict]:
        """
        Get detailed questionnaire information
        
        Args:
            db: Database session
            questionnaire_id: Questionnaire ID
            
        Returns:
            Detailed questionnaire data or None
        """
        questionnaire = get_questionnaire_by_id(db, questionnaire_id)
        if not questionnaire:
            return None
        
        questions = get_questions_by_questionnaire(db, questionnaire_id)
        
        return {
            "id": questionnaire.id,
            "title": questionnaire.title,
            "description": questionnaire.description,
            "instructions": questionnaire.instructions,
            "time_limit_minutes": questionnaire.time_limit_minutes,
            "total_questions": questionnaire.total_questions,
            "is_active": questionnaire.is_active,
            "created_at": questionnaire.created_at.isoformat() if questionnaire.created_at else None,
            "questions": [
                {
                    "id": q.id,
                    "text": self._parse_question_text(q.question_text),
                    "type": q.question_type,
                    "order": q.order_number,
                    "options": self._parse_question_options(q.options),
                    "weight": q.weight
                }
                for q in questions
            ]
        }

    def _parse_question_text(self, question_text):
        """Parse question text - handle both JSON and plain text"""
        try:
            # Try to parse as JSON (bilingual format)
            import json
            parsed = json.loads(question_text)
            if isinstance(parsed, dict):
                return parsed
            else:
                return {"english": str(parsed), "hindi": str(parsed)}
        except (json.JSONDecodeError, TypeError):
            # Fallback to plain text
            return {"english": str(question_text), "hindi": str(question_text)}

    def _parse_question_options(self, options):
        """Parse question options - handle both JSON and plain text"""
        try:
            # Try to parse as JSON
            import json
            if isinstance(options, str):
                parsed = json.loads(options)
            else:
                parsed = options

            if isinstance(parsed, dict):
                return parsed
            elif isinstance(parsed, list):
                # Convert list to bilingual format
                return {"english": parsed, "hindi": parsed}
            else:
                return {"english": [], "hindi": []}
        except (json.JSONDecodeError, TypeError):
            # Fallback to empty options
            return {"english": [], "hindi": []}

    def update_questionnaire(self, db, questionnaire_id: int,
                           updates: Dict) -> Dict:
        """
        Update questionnaire details
        
        Args:
            db: Database session
            questionnaire_id: Questionnaire ID
            updates: Dictionary of fields to update
            
        Returns:
            Update result
        """
        try:
            questionnaire = get_questionnaire_by_id(db, questionnaire_id)
            if not questionnaire:
                return {
                    "success": False,
                    "message": "प्रश्नावली नहीं मिली"
                }
            
            # Update fields
            for field, value in updates.items():
                if hasattr(questionnaire, field):
                    setattr(questionnaire, field, value)
            
            db.commit()
            
            return {
                "success": True,
                "message": "प्रश्नावली सफलतापूर्वक अपडेट की गई"
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": str(e),
                "message": "प्रश्नावली अपडेट करने में त्रुटि"
            }
    
    def delete_questionnaire(self, db, questionnaire_id: int) -> Dict:
        """
        Delete questionnaire (soft delete by setting is_active=False)
        
        Args:
            db: Database session
            questionnaire_id: Questionnaire ID
            
        Returns:
            Delete result
        """
        return self.update_questionnaire(
            db, questionnaire_id, {"is_active": False}
        )
    
    def export_questionnaire(self, db, questionnaire_id: int) -> Optional[Dict]:
        """
        Export questionnaire to JSON format
        
        Args:
            db: Database session
            questionnaire_id: Questionnaire ID
            
        Returns:
            Questionnaire data in JSON format
        """
        questionnaire_data = self.get_questionnaire_details(db, questionnaire_id)
        if questionnaire_data:
            questionnaire_data["exported_at"] = datetime.now().isoformat()
        
        return questionnaire_data
    
    def import_questionnaire(self, db, questionnaire_data: Dict, 
                           admin_user_id: int) -> Dict:
        """
        Import questionnaire from JSON data
        
        Args:
            db: Database session
            questionnaire_data: Questionnaire data
            admin_user_id: Admin user ID
            
        Returns:
            Import result
        """
        try:
            return self.create_questionnaire(
                db=db,
                title=questionnaire_data["title"],
                description=questionnaire_data["description"],
                instructions=questionnaire_data["instructions"],
                questions=questionnaire_data["questions"],
                created_by=admin_user_id,
                time_limit_minutes=questionnaire_data.get("time_limit_minutes", 30)
            )
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "प्रश्नावली इम्पोर्ट करने में त्रुटि"
            }

# Global instance
questionnaire_manager = QuestionnaireManager()
