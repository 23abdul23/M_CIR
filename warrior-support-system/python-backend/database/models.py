"""
Database models for Army Mental Health Assessment System
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict

Base = declarative_base()

class User(Base):
    """User model for authentication and user management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="user")  # "admin" or "user"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Army specific fields
    army_id = Column(String(20), unique=True)
    rank = Column(String(50))
    unit = Column(String(100))
    
    # Relationships
    assessments = relationship("Assessment", back_populates="user")

class Questionnaire(Base):
    """Questionnaire model for storing Hindi questionnaires"""
    __tablename__ = "questionnaires"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    instructions = Column(Text)  # Instructions in Hindi
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Assessment configuration
    total_questions = Column(Integer, default=0)
    time_limit_minutes = Column(Integer, default=30)
    
    # Relationships
    questions = relationship("Question", back_populates="questionnaire", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="questionnaire")
    creator = relationship("User")

class Question(Base):
    """Question model for individual questions in questionnaires"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    questionnaire_id = Column(Integer, ForeignKey("questionnaires.id"))
    question_text = Column(Text, nullable=False)  # Question in Hindi
    question_type = Column(String(20), default="text")  # "text", "multiple_choice", "scale"
    order_number = Column(Integer, nullable=False)
    is_required = Column(Boolean, default=True)
    
    # For multiple choice questions
    options = Column(JSON)  # Store options as JSON array
    
    # Keywords for sentiment analysis
    positive_keywords = Column(JSON)  # Hindi keywords indicating positive response
    negative_keywords = Column(JSON)  # Hindi keywords indicating negative response
    weight = Column(Float, default=1.0)  # Weight for this question in overall assessment
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    questionnaire = relationship("Questionnaire", back_populates="questions")
    responses = relationship("Response", back_populates="question")

class Assessment(Base):
    """Assessment model for user test sessions"""
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    questionnaire_id = Column(Integer, ForeignKey("questionnaires.id"))
    
    # Assessment status
    status = Column(String(20), default="in_progress")  # "in_progress", "completed", "abandoned"
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Results
    overall_score = Column(Float)  # 0-100 scale
    mental_state = Column(String(20))  # "normal", "mild", "moderate", "severe"
    sentiment_scores = Column(JSON)  # Detailed sentiment analysis results
    
    # AI Analysis Results
    ai_analysis = Column(JSON)  # Store AI analysis results
    keyword_matches = Column(JSON)  # Matched keywords and their weights
    
    # Recommendations
    suggestions = Column(JSON)  # Health suggestions based on assessment
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    questionnaire = relationship("Questionnaire", back_populates="assessments")
    responses = relationship("Response", back_populates="assessment")

class Response(Base):
    """Response model for individual question responses"""
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    
    # Response data
    response_text = Column(Text)  # User's response in Hindi
    response_value = Column(String(100))  # For multiple choice or scale responses
    
    # AI Analysis for this response
    sentiment_score = Column(Float)  # -1 to 1 (negative to positive)
    sentiment_label = Column(String(20))  # "positive", "neutral", "negative"
    confidence_score = Column(Float)  # 0 to 1
    
    # Keyword analysis
    matched_keywords = Column(JSON)  # Keywords found in this response
    keyword_score = Column(Float)  # Score based on matched keywords
    
    # Timing
    response_time_seconds = Column(Integer)  # Time taken to answer
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    assessment = relationship("Assessment", back_populates="responses")
    question = relationship("Question", back_populates="responses")

class KeywordSet(Base):
    """Keyword sets for mental health assessment"""
    __tablename__ = "keyword_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # "stress", "depression", "anxiety", etc.
    keywords = Column(JSON, nullable=False)  # List of Hindi keywords
    weight = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User")

class HealthSuggestion(Base):
    """Health suggestions based on assessment results"""
    __tablename__ = "health_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    mental_state = Column(String(20), nullable=False)  # "normal", "mild", "moderate", "severe"
    suggestion_text = Column(Text, nullable=False)  # Suggestion in Hindi
    category = Column(String(50))  # "exercise", "meditation", "professional_help", etc.
    priority = Column(Integer, default=1)  # 1 = highest priority
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    creator = relationship("User")

class SystemLog(Base):
    """System logs for monitoring and debugging"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
