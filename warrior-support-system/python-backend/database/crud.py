"""
CRUD operations for Army Mental Health Assessment System
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import DEFAULT_ADMIN, MENTAL_HEALTH_KEYWORDS, HEALTH_SUGGESTIONS

from .models import (
    User, Questionnaire, Question, Assessment, Response, 
    KeywordSet, HealthSuggestion, SystemLog
)

# User CRUD Operations
def create_user(db: Session, username: str, email: str, password: str, 
                full_name: str = None, role: str = "user", army_id: str = None, 
                rank: str = None, unit: str = None) -> User:
    """Create a new user"""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role,
        army_id=army_id,
        rank=rank,
        unit=unit
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user = get_user_by_username(db, username)
    if user and user.hashed_password == hashlib.sha256(password.encode()).hexdigest():
        return user
    return None

def create_default_admin(db: Session):
    """Create default admin user if not exists"""
    admin = get_user_by_username(db, DEFAULT_ADMIN["username"])
    if not admin:
        create_user(
            db=db,
            username=DEFAULT_ADMIN["username"],
            email=DEFAULT_ADMIN["email"],
            password=DEFAULT_ADMIN["password"],
            full_name="System Administrator",
            role=DEFAULT_ADMIN["role"]
        )

# Questionnaire CRUD Operations
def create_questionnaire(db: Session, title: str, description: str, 
                        instructions: str, created_by: int, 
                        time_limit_minutes: int = 30) -> Questionnaire:
    """Create a new questionnaire"""
    db_questionnaire = Questionnaire(
        title=title,
        description=description,
        instructions=instructions,
        created_by=created_by,
        time_limit_minutes=time_limit_minutes
    )
    db.add(db_questionnaire)
    db.commit()
    db.refresh(db_questionnaire)
    return db_questionnaire

def get_questionnaires(db: Session, active_only: bool = True) -> List[Questionnaire]:
    """Get all questionnaires"""
    query = db.query(Questionnaire)
    if active_only:
        query = query.filter(Questionnaire.is_active == True)
    return query.order_by(desc(Questionnaire.created_at)).all()

def get_questionnaire_by_id(db: Session, questionnaire_id: int) -> Optional[Questionnaire]:
    """Get questionnaire by ID"""
    return db.query(Questionnaire).filter(Questionnaire.id == questionnaire_id).first()

def update_questionnaire_question_count(db: Session, questionnaire_id: int):
    """Update total question count for questionnaire"""
    count = db.query(Question).filter(Question.questionnaire_id == questionnaire_id).count()
    questionnaire = get_questionnaire_by_id(db, questionnaire_id)
    if questionnaire:
        questionnaire.total_questions = count
        db.commit()

# Question CRUD Operations
def create_question(db: Session, questionnaire_id: int, question_text: str,
                   order_number: int, question_type: str = "text",
                   options: List[str] = None, positive_keywords: List[str] = None,
                   negative_keywords: List[str] = None, weight: float = 1.0) -> Question:
    """Create a new question"""
    db_question = Question(
        questionnaire_id=questionnaire_id,
        question_text=question_text,
        question_type=question_type,
        order_number=order_number,
        options=options,
        positive_keywords=positive_keywords,
        negative_keywords=negative_keywords,
        weight=weight
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    # Update questionnaire question count
    update_questionnaire_question_count(db, questionnaire_id)
    
    return db_question

def get_questions_by_questionnaire(db: Session, questionnaire_id: int) -> List[Question]:
    """Get all questions for a questionnaire"""
    return db.query(Question).filter(
        Question.questionnaire_id == questionnaire_id
    ).order_by(Question.order_number).all()

# Assessment CRUD Operations
def create_assessment(db: Session, user_id: int, questionnaire_id: int) -> Assessment:
    """Create a new assessment session"""
    db_assessment = Assessment(
        user_id=user_id,
        questionnaire_id=questionnaire_id,
        status="in_progress"
    )
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment

def get_assessment_by_id(db: Session, assessment_id: int) -> Optional[Assessment]:
    """Get assessment by ID"""
    return db.query(Assessment).filter(Assessment.id == assessment_id).first()

def complete_assessment(db: Session, assessment_id: int, overall_score: float,
                       mental_state: str, sentiment_scores: Dict,
                       ai_analysis: Dict, keyword_matches: Dict,
                       suggestions: List[str]) -> Assessment:
    """Complete an assessment with results"""
    assessment = get_assessment_by_id(db, assessment_id)
    if assessment:
        assessment.status = "completed"
        assessment.completed_at = datetime.utcnow()
        assessment.overall_score = overall_score
        assessment.mental_state = mental_state
        assessment.sentiment_scores = sentiment_scores
        assessment.ai_analysis = ai_analysis
        assessment.keyword_matches = keyword_matches
        assessment.suggestions = suggestions
        db.commit()
        db.refresh(assessment)
    return assessment

def get_user_assessments(db: Session, user_id: int, limit: int = 10) -> List[Assessment]:
    """Get user's assessment history"""
    from sqlalchemy import desc
    return db.query(Assessment).filter(
        Assessment.user_id == user_id
    ).order_by(desc(Assessment.started_at)).limit(limit).all()

# Response CRUD Operations
def create_response(db: Session, assessment_id: int, question_id: int,
                   response_text: str, response_value: str = None,
                   sentiment_score: float = None, sentiment_label: str = None,
                   confidence_score: float = None, matched_keywords: List[str] = None,
                   keyword_score: float = None, response_time_seconds: int = None) -> Response:
    """Create a new response"""
    db_response = Response(
        assessment_id=assessment_id,
        question_id=question_id,
        response_text=response_text,
        response_value=response_value,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        confidence_score=confidence_score,
        matched_keywords=matched_keywords,
        keyword_score=keyword_score,
        response_time_seconds=response_time_seconds
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response

def get_responses_by_assessment(db: Session, assessment_id: int) -> List[Response]:
    """Get all responses for an assessment"""
    return db.query(Response).filter(Response.assessment_id == assessment_id).all()

def get_assessment_responses(db: Session, assessment_id: int) -> List[Response]:
    """Get all responses for an assessment with question details"""
    return db.query(Response).join(Question).filter(
        Response.assessment_id == assessment_id
    ).order_by(Question.order_number).all()

def delete_assessment_by_id(db: Session, assessment_id: int) -> bool:
    """Delete an assessment and all its responses"""
    try:
        # Delete responses first
        db.query(Response).filter(Response.assessment_id == assessment_id).delete()

        # Delete assessment
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if assessment:
            db.delete(assessment)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting assessment: {e}")
        return False

def update_assessment_status(db: Session, assessment_id: int, status: str) -> bool:
    """Update assessment status"""
    try:
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if assessment:
            assessment.status = status
            if status == "completed":
                assessment.completed_at = datetime.utcnow()
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error updating assessment status: {e}")
        return False

# Keyword Set CRUD Operations
def create_keyword_set(db: Session, name: str, category: str, keywords: List[str],
                      weight: float = 1.0, created_by: int = None) -> KeywordSet:
    """Create a new keyword set"""
    db_keyword_set = KeywordSet(
        name=name,
        category=category,
        keywords=keywords,
        weight=weight,
        created_by=created_by
    )
    db.add(db_keyword_set)
    db.commit()
    db.refresh(db_keyword_set)
    return db_keyword_set

def get_keyword_sets(db: Session, active_only: bool = True) -> List[KeywordSet]:
    """Get all keyword sets"""
    query = db.query(KeywordSet)
    if active_only:
        query = query.filter(KeywordSet.is_active == True)
    return query.all()

def initialize_default_keywords(db: Session, admin_user_id: int):
    """Initialize default mental health keywords"""
    for category, data in MENTAL_HEALTH_KEYWORDS.items():
        existing = db.query(KeywordSet).filter(
            KeywordSet.category == category
        ).first()
        
        if not existing:
            create_keyword_set(
                db=db,
                name=f"Default {category.title()} Keywords",
                category=category,
                keywords=data["hindi"],
                weight=data["weight"],
                created_by=admin_user_id
            )

# Health Suggestion CRUD Operations
def create_health_suggestion(db: Session, mental_state: str, suggestion_text: str,
                           category: str = None, priority: int = 1,
                           created_by: int = None) -> HealthSuggestion:
    """Create a new health suggestion"""
    db_suggestion = HealthSuggestion(
        mental_state=mental_state,
        suggestion_text=suggestion_text,
        category=category,
        priority=priority,
        created_by=created_by
    )
    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion

def get_health_suggestions(db: Session, mental_state: str = None) -> List[HealthSuggestion]:
    """Get health suggestions by mental state"""
    query = db.query(HealthSuggestion).filter(HealthSuggestion.is_active == True)
    if mental_state:
        query = query.filter(HealthSuggestion.mental_state == mental_state)
    return query.order_by(HealthSuggestion.priority).all()

def initialize_default_suggestions(db: Session, admin_user_id: int):
    """Initialize default health suggestions"""
    for mental_state, suggestions in HEALTH_SUGGESTIONS.items():
        for i, suggestion in enumerate(suggestions, 1):
            existing = db.query(HealthSuggestion).filter(
                and_(
                    HealthSuggestion.mental_state == mental_state,
                    HealthSuggestion.suggestion_text == suggestion
                )
            ).first()
            
            if not existing:
                create_health_suggestion(
                    db=db,
                    mental_state=mental_state,
                    suggestion_text=suggestion,
                    priority=i,
                    created_by=admin_user_id
                )

# System Log CRUD Operations
def create_system_log(db: Session, user_id: int = None, action: str = None,
                     details: Dict = None, ip_address: str = None,
                     user_agent: str = None) -> SystemLog:
    """Create a system log entry"""
    db_log = SystemLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# Statistics and Analytics
def get_assessment_statistics(db: Session, days: int = 30) -> Dict[str, Any]:
    """Get assessment statistics for the last N days"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    total_assessments = db.query(Assessment).filter(
        Assessment.started_at >= start_date
    ).count()

    completed_assessments = db.query(Assessment).filter(
        and_(
            Assessment.started_at >= start_date,
            Assessment.status == "completed"
        )
    ).count()

    # Mental state distribution
    from sqlalchemy import func
    mental_states = db.query(Assessment.mental_state, func.count(Assessment.id)).filter(
        and_(
            Assessment.started_at >= start_date,
            Assessment.status == "completed"
        )
    ).group_by(Assessment.mental_state).all()
    
    return {
        "total_assessments": total_assessments,
        "completed_assessments": completed_assessments,
        "completion_rate": (completed_assessments / total_assessments * 100) if total_assessments > 0 else 0,
        "mental_state_distribution": dict(mental_states)
    }
