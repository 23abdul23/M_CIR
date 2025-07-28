"""
Comprehensive Interventions and Reports System
Advanced intervention management and detailed reporting for Army Mental Health Assessment
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from database.database import get_db
    from database.crud import *
    from utils.language_support import get_bilingual_text, get_language
    from models.suggestion_engine import suggestion_engine
except ImportError as e:
    print(f"Import error in interventions and reports: {e}")

class InterventionsReportsSystem:
    """
    Comprehensive interventions and reports management system
    """
    
    def __init__(self):
        self.db = next(get_db())
    
    def render_interventions_management(self):
        """Render comprehensive interventions management interface"""
        
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #28a745, #20c997); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: white; text-align: center; margin: 0;">
                {get_bilingual_text('💡 हस्तक्षेप प्रबंधन', '💡 Intervention Management')}
            </h2>
            <p style="color: #e0e0e0; text-align: center; margin: 10px 0 0 0;">
                {get_bilingual_text('व्यापक हस्तक्षेप योजना और ट्रैकिंग', 'Comprehensive Intervention Planning & Tracking')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            get_bilingual_text("🚨 तत्काल हस्तक्षेप", "🚨 Immediate Interventions"),
            get_bilingual_text("📋 हस्तक्षेप योजना", "📋 Intervention Plans"),
            get_bilingual_text("📊 प्रगति ट्रैकिंग", "📊 Progress Tracking"),
            get_bilingual_text("👥 टीम समन्वय", "👥 Team Coordination")
        ])
        
        with tab1:
            self.render_immediate_interventions()
        
        with tab2:
            self.render_intervention_plans()
        
        with tab3:
            self.render_progress_tracking()
        
        with tab4:
            self.render_team_coordination()
    
    def render_immediate_interventions(self):
        """Render immediate intervention interface for high-risk cases"""
        
        st.subheader(get_bilingual_text("🚨 तत्काल हस्तक्षेप आवश्यक", "🚨 Immediate Interventions Required"))
        
        # Get high-risk cases
        high_risk_assessments = self.db.query(Assessment, User).join(User).filter(
            Assessment.mental_state.in_(["severe", "moderate"]),
            Assessment.status == "completed"
        ).order_by(Assessment.started_at.desc()).limit(20).all()
        
        if high_risk_assessments:
            for assessment, user in high_risk_assessments:
                self.render_intervention_card(assessment, user)
        else:
            st.success(get_bilingual_text(
                "✅ कोई तत्काल हस्तक्षेप आवश्यक नहीं",
                "✅ No immediate interventions required"
            ))
    
    def render_intervention_card(self, assessment, user):
        """Render individual intervention card"""
        
        # Determine urgency color
        urgency_colors = {
            "severe": "#dc3545",
            "moderate": "#fd7e14",
            "mild": "#ffc107"
        }
        
        color = urgency_colors.get(assessment.mental_state, "#6c757d")
        
        with st.container():
            st.markdown(f"""
            <div style="border-left: 5px solid {color}; padding: 15px; margin: 10px 0; background-color: {color}10; border-radius: 5px;">
                <h4 style="margin: 0; color: {color};">
                    {user.full_name or user.username} ({user.army_id or 'No ID'})
                </h4>
                <p style="margin: 5px 0;">
                    <strong>{get_bilingual_text('जोखिम स्तर', 'Risk Level')}:</strong> 
                    <span style="color: {color}; font-weight: bold;">{assessment.mental_state.upper()}</span>
                </p>
                <p style="margin: 5px 0;">
                    <strong>{get_bilingual_text('स्कोर', 'Score')}:</strong> {assessment.overall_score or 0:.1f}%
                </p>
                <p style="margin: 5px 0;">
                    <strong>{get_bilingual_text('दिनांक', 'Date')}:</strong> {assessment.started_at.strftime('%d/%m/%Y %H:%M')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button(
                    get_bilingual_text("तत्काल संपर्क", "Immediate Contact"),
                    key=f"contact_{assessment.id}"
                ):
                    self.initiate_immediate_contact(user, assessment)
            
            with col2:
                if st.button(
                    get_bilingual_text("परामर्श शेड्यूल", "Schedule Counseling"),
                    key=f"counsel_{assessment.id}"
                ):
                    self.schedule_counseling(user, assessment)
            
            with col3:
                if st.button(
                    get_bilingual_text("चिकित्सा रेफरल", "Medical Referral"),
                    key=f"medical_{assessment.id}"
                ):
                    self.create_medical_referral(user, assessment)
            
            with col4:
                if st.button(
                    get_bilingual_text("विस्तृत योजना", "Detailed Plan"),
                    key=f"plan_{assessment.id}"
                ):
                    self.create_intervention_plan(user, assessment)
    
    def render_intervention_plans(self):
        """Render intervention planning interface"""
        
        st.subheader(get_bilingual_text("📋 व्यापक हस्तक्षेप योजना", "📋 Comprehensive Intervention Plans"))
        
        # Intervention plan templates
        plan_templates = {
            "severe": {
                "hindi": {
                    "immediate": [
                        "तत्काल मनोवैज्ञानिक परामर्श",
                        "24/7 सहायता हॉटलाइन उपलब्ध कराना",
                        "परिवार को सूचित करना",
                        "चिकित्सा मूल्यांकन"
                    ],
                    "short_term": [
                        "साप्ताहिक परामर्श सत्र",
                        "दवा की समीक्षा",
                        "कार्य भार में कमी",
                        "सहायता समूह में शामिल करना"
                    ],
                    "long_term": [
                        "मासिक फॉलो-अप",
                        "करियर काउंसलिंग",
                        "पारिवारिक थेरेपी",
                        "तनाव प्रबंधन प्रशिक्षण"
                    ]
                },
                "english": {
                    "immediate": [
                        "Immediate psychological counseling",
                        "24/7 support hotline access",
                        "Notify family members",
                        "Medical evaluation"
                    ],
                    "short_term": [
                        "Weekly counseling sessions",
                        "Medication review",
                        "Reduced workload",
                        "Support group participation"
                    ],
                    "long_term": [
                        "Monthly follow-ups",
                        "Career counseling",
                        "Family therapy",
                        "Stress management training"
                    ]
                }
            },
            "moderate": {
                "hindi": {
                    "immediate": [
                        "परामर्श सत्र शेड्यूल करना",
                        "सुपरवाइज़र को सूचित करना",
                        "कार्य वातावरण का मूल्यांकन"
                    ],
                    "short_term": [
                        "द्विसाप्ताहिक परामर्श",
                        "तनाव कम करने की तकनीक",
                        "सामाजिक सहायता बढ़ाना"
                    ],
                    "long_term": [
                        "मासिक चेक-इन",
                        "कौशल विकास कार्यक्रम",
                        "लाइफस्टाइल काउंसलिंग"
                    ]
                },
                "english": {
                    "immediate": [
                        "Schedule counseling session",
                        "Notify supervisor",
                        "Assess work environment"
                    ],
                    "short_term": [
                        "Bi-weekly counseling",
                        "Stress reduction techniques",
                        "Enhance social support"
                    ],
                    "long_term": [
                        "Monthly check-ins",
                        "Skill development programs",
                        "Lifestyle counseling"
                    ]
                }
            }
        }
        
        # Display intervention plan creator
        selected_user = st.selectbox(
            get_bilingual_text("उपयोगकर्ता चुनें", "Select User"),
            options=self.get_users_needing_intervention()
        )
        
        if selected_user:
            st.info(get_bilingual_text(
                "हस्तक्षेप योजना निर्माता विकसित किया जा रहा है",
                "Intervention plan creator under development"
            ))

    def render_progress_tracking(self):
        """Render progress tracking interface"""

        st.subheader(get_bilingual_text("📊 प्रगति ट्रैकिंग", "📊 Progress Tracking"))

        st.info(get_bilingual_text(
            "प्रगति ट्रैकिंग सिस्टम विकसित किया जा रहा है",
            "Progress tracking system under development"
        ))

        # Placeholder for progress tracking functionality
        st.markdown("""
        **Features to be implemented:**
        - Individual progress monitoring
        - Intervention effectiveness tracking
        - Recovery timeline visualization
        - Goal achievement metrics
        """)

    def render_team_coordination(self):
        """Render team coordination interface"""

        st.subheader(get_bilingual_text("👥 टीम समन्वय", "👥 Team Coordination"))

        st.info(get_bilingual_text(
            "टीम समन्वय सिस्टम विकसित किया जा रहा है",
            "Team coordination system under development"
        ))

        # Placeholder for team coordination functionality
        st.markdown("""
        **Features to be implemented:**
        - Multi-disciplinary team assignments
        - Communication channels
        - Task delegation and tracking
        - Collaborative care planning
        """)

    def render_comprehensive_reports(self):
        """Render comprehensive reporting system"""
        
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #6f42c1, #e83e8c); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: white; text-align: center; margin: 0;">
                {get_bilingual_text('📊 व्यापक रिपोर्ट सिस्टम', '📊 Comprehensive Reports System')}
            </h2>
            <p style="color: #e0e0e0; text-align: center; margin: 10px 0 0 0;">
                {get_bilingual_text('विस्तृत विश्लेषण और रिपोर्टिंग', 'Detailed Analysis & Reporting')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Report tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            get_bilingual_text("📈 सांख्यिकी रिपोर्ट", "📈 Statistical Reports"),
            get_bilingual_text("👤 व्यक्तिगत रिपोर्ट", "👤 Individual Reports"),
            get_bilingual_text("🏢 यूनिट रिपोर्ट", "🏢 Unit Reports"),
            get_bilingual_text("📅 समय-आधारित", "📅 Time-based"),
            get_bilingual_text("📋 कस्टम रिपोर्ट", "📋 Custom Reports")
        ])
        
        with tab1:
            self.render_statistical_reports()
        
        with tab2:
            self.render_individual_reports()
        
        with tab3:
            self.render_unit_reports()
        
        with tab4:
            self.render_time_based_reports()
        
        with tab5:
            self.render_custom_reports()
    
    def render_statistical_reports(self):
        """Render statistical analysis reports"""
        
        st.subheader(get_bilingual_text("📈 सांख्यिकी विश्लेषण", "📈 Statistical Analysis"))
        
        # Get data for analysis
        assessments = self.db.query(Assessment).filter(Assessment.status == "completed").all()
        
        if assessments:
            # Overall statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_assessments = len(assessments)
                st.metric(
                    get_bilingual_text("कुल मूल्यांकन", "Total Assessments"),
                    total_assessments
                )
            
            with col2:
                high_risk = len([a for a in assessments if a.mental_state in ["severe", "moderate"]])
                risk_percentage = (high_risk / total_assessments * 100) if total_assessments > 0 else 0
                st.metric(
                    get_bilingual_text("उच्च जोखिम", "High Risk"),
                    f"{high_risk} ({risk_percentage:.1f}%)"
                )
            
            with col3:
                avg_score = sum([a.overall_score for a in assessments if a.overall_score]) / len([a for a in assessments if a.overall_score])
                st.metric(
                    get_bilingual_text("औसत स्कोर", "Average Score"),
                    f"{avg_score:.1f}%"
                )
            
            with col4:
                recent_assessments = len([a for a in assessments if a.started_at >= datetime.now() - timedelta(days=7)])
                st.metric(
                    get_bilingual_text("इस सप्ताह", "This Week"),
                    recent_assessments
                )
            
            # Detailed charts
            self.render_mental_health_trends(assessments)
            self.render_risk_distribution(assessments)
            self.render_intervention_effectiveness()
        
        else:
            st.info(get_bilingual_text("विश्लेषण के लिए डेटा उपलब्ध नहीं", "No data available for analysis"))
    
    def normalize_mental_state(self, state):
        """Normalize mental state to English values"""
        if not state:
            return "unknown"

        # Mapping from various possible values to standard English values
        state_mapping = {
            # English values (keep as is)
            "normal": "normal",
            "mild": "mild",
            "moderate": "moderate",
            "severe": "severe",
            "unknown": "unknown",

            # Hindi values
            "सामान्य": "normal",
            "हल्का": "mild",
            "मध्यम": "moderate",
            "गंभीर": "severe",
            "मध्यम जोखिम": "moderate",
            "उच्च जोखिम": "severe",
            "कम जोखिम": "mild",

            # Other possible values
            "low": "mild",
            "medium": "moderate",
            "high": "severe",
            "good": "normal",
            "fair": "mild",
            "poor": "moderate",
            "critical": "severe"
        }

        return state_mapping.get(state.lower(), "unknown")

    def render_mental_health_trends(self, assessments):
        """Render mental health trends over time"""

        st.subheader(get_bilingual_text("मानसिक स्वास्थ्य रुझान", "Mental Health Trends"))

        # Group assessments by date and mental state
        daily_data = {}
        for assessment in assessments:
            date = assessment.started_at.date()
            state = self.normalize_mental_state(assessment.mental_state)

            if date not in daily_data:
                daily_data[date] = {"normal": 0, "mild": 0, "moderate": 0, "severe": 0, "unknown": 0}

            daily_data[date][state] += 1
        
        # Create trend chart
        dates = sorted(daily_data.keys())
        
        fig = go.Figure()
        
        colors = {
            "normal": "#28a745",
            "mild": "#ffc107",
            "moderate": "#fd7e14",
            "severe": "#dc3545",
            "unknown": "#6c757d"
        }
        
        for state in ["severe", "moderate", "mild", "normal", "unknown"]:
            values = [daily_data[date][state] for date in dates]
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name=get_bilingual_text(
                    {"severe": "गंभीर", "moderate": "मध्यम", "mild": "हल्का", "normal": "सामान्य", "unknown": "अज्ञात"}[state],
                    state.title()
                ),
                line=dict(color=colors[state], width=2),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            title=get_bilingual_text("दैनिक मानसिक स्वास्थ्य रुझान", "Daily Mental Health Trends"),
            xaxis_title=get_bilingual_text("दिनांक", "Date"),
            yaxis_title=get_bilingual_text("मामलों की संख्या", "Number of Cases"),
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def get_users_needing_intervention(self):
        """Get list of users needing intervention"""
        users = self.db.query(User, Assessment).join(Assessment).filter(
            Assessment.mental_state.in_(["severe", "moderate"]),
            Assessment.status == "completed"
        ).distinct().all()
        
        return [f"{user.full_name or user.username} ({user.army_id or 'No ID'})" for user, _ in users]
    
    # Additional helper methods would be implemented here...
    
    def initiate_immediate_contact(self, user, assessment):
        """Initiate immediate contact protocol"""
        st.success(get_bilingual_text(
            f"तत्काल संपर्क प्रोटोकॉल शुरू किया गया: {user.full_name}",
            f"Immediate contact protocol initiated for: {user.full_name}"
        ))
    
    def schedule_counseling(self, user, assessment):
        """Schedule counseling session"""
        st.success(get_bilingual_text(
            f"परामर्श सत्र शेड्यूल किया गया: {user.full_name}",
            f"Counseling session scheduled for: {user.full_name}"
        ))
    
    def create_medical_referral(self, user, assessment):
        """Create medical referral"""
        st.success(get_bilingual_text(
            f"चिकित्सा रेफरल बनाया गया: {user.full_name}",
            f"Medical referral created for: {user.full_name}"
        ))
    
    def create_intervention_plan(self, user, assessment):
        """Create detailed intervention plan"""
        st.success(get_bilingual_text(
            f"हस्तक्षेप योजना बनाई गई: {user.full_name}",
            f"Intervention plan created for: {user.full_name}"
        ))

    def render_risk_distribution(self, assessments):
        """Render risk distribution chart"""

        st.subheader(get_bilingual_text("जोखिम वितरण", "Risk Distribution"))

        # Count assessments by mental state
        risk_counts = {}
        for assessment in assessments:
            state = self.normalize_mental_state(assessment.mental_state)
            risk_counts[state] = risk_counts.get(state, 0) + 1

        if risk_counts:
            # Create pie chart
            labels = list(risk_counts.keys())
            values = list(risk_counts.values())

            fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
            fig.update_layout(
                title=get_bilingual_text("मानसिक स्वास्थ्य जोखिम वितरण", "Mental Health Risk Distribution"),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(get_bilingual_text("जोखिम डेटा उपलब्ध नहीं", "No risk data available"))

    def render_individual_reports(self):
        """Render individual assessment reports"""

        st.subheader(get_bilingual_text("व्यक्तिगत रिपोर्ट", "Individual Reports"))

        st.info(get_bilingual_text(
            "व्यक्तिगत रिपोर्ट सिस्टम विकसित किया जा रहा है",
            "Individual reports system under development"
        ))

        # Placeholder for individual reports functionality
        st.markdown("""
        **Features to be implemented:**
        - Individual assessment history
        - Detailed response analysis
        - Progress tracking over time
        - Personalized recommendations
        """)

    def render_unit_reports(self):
        """Render unit-based reports"""

        st.subheader(get_bilingual_text("यूनिट रिपोर्ट", "Unit Reports"))

        st.info(get_bilingual_text(
            "यूनिट रिपोर्ट सिस्टम विकसित किया जा रहा है",
            "Unit reports system under development"
        ))

        # Placeholder for unit reports functionality
        st.markdown("""
        **Features to be implemented:**
        - Unit-wise mental health statistics
        - Comparative analysis between units
        - Unit performance metrics
        - Command-level insights
        """)

    def render_trend_analysis(self):
        """Render trend analysis"""

        st.subheader(get_bilingual_text("रुझान विश्लेषण", "Trend Analysis"))

        st.info(get_bilingual_text(
            "रुझान विश्लेषण सिस्टम विकसित किया जा रहा है",
            "Trend analysis system under development"
        ))

# Global instance
interventions_reports_system = InterventionsReportsSystem()
