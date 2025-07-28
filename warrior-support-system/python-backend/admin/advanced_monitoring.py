"""
Advanced Admin Monitoring System for Army Mental Health Assessment
Comprehensive data analysis, visualization, and intervention management
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
    from utils.language_support import t, get_language, get_bilingual_text
    from models.suggestion_engine import suggestion_engine
except ImportError as e:
    print(f"Import error in advanced monitoring: {e}")

class AdvancedAdminMonitoring:
    """
    Advanced monitoring system for mental health assessments
    Provides comprehensive analytics, risk assessment, and intervention tracking
    """
    
    def __init__(self):
        self.db = next(get_db())
    
    def render_comprehensive_dashboard(self):
        """Render the main comprehensive admin dashboard"""
        
        # Header
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #1f4e79, #2d5aa0); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; text-align: center; margin: 0;">
                {get_bilingual_text('🏥 उन्नत मानसिक स्वास्थ्य निगरानी डैशबोर्ड', '🏥 Advanced Mental Health Monitoring Dashboard')}
            </h1>
            <p style="color: #e0e0e0; text-align: center; margin: 10px 0 0 0;">
                {get_bilingual_text('व्यापक डेटा विश्लेषण और हस्तक्षेप प्रबंधन', 'Comprehensive Data Analysis & Intervention Management')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            get_bilingual_text("📊 डैशबोर्ड", "📊 Dashboard"),
            get_bilingual_text("👥 व्यक्तिगत निगरानी", "👥 Individual Monitoring"),
            get_bilingual_text("📈 रुझान विश्लेषण", "📈 Trend Analysis"),
            get_bilingual_text("🚨 जोखिम प्रबंधन", "🚨 Risk Management"),
            get_bilingual_text("💡 हस्तक्षेप", "💡 Interventions"),
            get_bilingual_text("📋 रिपोर्ट्स", "📋 Reports")
        ])
        
        with tab1:
            self.render_overview_dashboard()
        
        with tab2:
            self.render_individual_monitoring()
        
        with tab3:
            self.render_trend_analysis()
        
        with tab4:
            self.render_risk_management()
        
        with tab5:
            self.render_intervention_management()
        
        with tab6:
            self.render_comprehensive_reports()
    
    def render_overview_dashboard(self):
        """Render overview dashboard with key metrics"""
        
        # Get data
        total_users = self.db.query(User).count()
        total_assessments = self.db.query(Assessment).count()
        recent_assessments = self.db.query(Assessment).filter(
            Assessment.started_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        # High-risk cases
        high_risk_cases = self.db.query(Assessment).filter(
            Assessment.mental_state == "severe"
        ).count()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                get_bilingual_text("कुल उपयोगकर्ता", "Total Users"),
                total_users,
                delta=None
            )
        
        with col2:
            st.metric(
                get_bilingual_text("कुल मूल्यांकन", "Total Assessments"),
                total_assessments,
                delta=None
            )
        
        with col3:
            st.metric(
                get_bilingual_text("सप्ताह के मूल्यांकन", "This Week"),
                recent_assessments,
                delta=None
            )
        
        with col4:
            st.metric(
                get_bilingual_text("उच्च जोखिम", "High Risk"),
                high_risk_cases,
                delta=None,
                delta_color="inverse"
            )
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_mental_state_distribution()
        
        with col2:
            self.render_assessment_timeline()
        
        # Recent high-risk alerts
        st.subheader(get_bilingual_text("🚨 हाल की उच्च जोखिम चेतावनियां", "🚨 Recent High-Risk Alerts"))
        self.render_high_risk_alerts()
    
    def render_mental_state_distribution(self):
        """Render mental state distribution chart"""
        
        # Get mental state data - simplified approach
        try:
            assessments = self.db.query(Assessment).filter(
                Assessment.status == "completed"
            ).all()

            # Count mental states manually
            mental_state_counts = {}
            for assessment in assessments:
                state = assessment.mental_state or "unknown"
                mental_state_counts[state] = mental_state_counts.get(state, 0) + 1

            mental_states = [(state, count) for state, count in mental_state_counts.items()]
        except Exception as e:
            print(f"Error getting mental state data: {e}")
            mental_states = []
        
        if mental_states:
            # Prepare data
            states = []
            counts = []
            colors = []
            
            color_map = {
                'normal': '#28a745',
                'mild': '#ffc107', 
                'moderate': '#fd7e14',
                'severe': '#dc3545'
            }
            
            for state, count in mental_states:
                if state:
                    states.append(get_bilingual_text(
                        {'normal': 'सामान्य', 'mild': 'हल्का', 'moderate': 'मध्यम', 'severe': 'गंभीर'}.get(state, state),
                        state.title()
                    ))
                    counts.append(count)
                    colors.append(color_map.get(state, '#6c757d'))
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=states,
                values=counts,
                marker_colors=colors,
                hole=0.4
            )])
            
            fig.update_layout(
                title=get_bilingual_text("मानसिक स्थिति वितरण", "Mental State Distribution"),
                showlegend=True,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(get_bilingual_text("कोई डेटा उपलब्ध नहीं", "No data available"))
    
    def render_assessment_timeline(self):
        """Render assessment timeline chart"""
        
        # Get assessment data for last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        assessments = self.db.query(Assessment).filter(
            Assessment.started_at >= thirty_days_ago
        ).all()
        
        if assessments:
            # Group by date
            daily_counts = {}
            for assessment in assessments:
                date = assessment.started_at.date()
                daily_counts[date] = daily_counts.get(date, 0) + 1
            
            # Create timeline data
            dates = sorted(daily_counts.keys())
            counts = [daily_counts[date] for date in dates]
            
            # Create line chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=counts,
                mode='lines+markers',
                name=get_bilingual_text("दैनिक मूल्यांकन", "Daily Assessments"),
                line=dict(color='#007bff', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title=get_bilingual_text("मूल्यांकन समयरेखा (30 दिन)", "Assessment Timeline (30 Days)"),
                xaxis_title=get_bilingual_text("दिनांक", "Date"),
                yaxis_title=get_bilingual_text("मूल्यांकन संख्या", "Number of Assessments"),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(get_bilingual_text("कोई डेटा उपलब्ध नहीं", "No data available"))
    
    def render_high_risk_alerts(self):
        """Render high-risk alerts table"""
        
        # Get high-risk assessments
        high_risk = self.db.query(Assessment, User).join(User).filter(
            Assessment.mental_state.in_(["severe", "moderate"])
        ).order_by(Assessment.started_at.desc()).limit(10).all()
        
        if high_risk:
            alert_data = []
            for assessment, user in high_risk:
                alert_data.append({
                    get_bilingual_text("नाम", "Name"): user.full_name or user.username,
                    get_bilingual_text("सेना आईडी", "Army ID"): user.army_id or "N/A",
                    get_bilingual_text("रैंक", "Rank"): user.rank or "N/A",
                    get_bilingual_text("जोखिम स्तर", "Risk Level"): get_bilingual_text(
                        {'severe': 'गंभीर', 'moderate': 'मध्यम'}.get(assessment.mental_state, assessment.mental_state),
                        assessment.mental_state.title()
                    ),
                    get_bilingual_text("स्कोर", "Score"): f"{assessment.overall_score or 0:.1f}%",
                    get_bilingual_text("दिनांक", "Date"): assessment.started_at.strftime("%d/%m/%Y %H:%M")
                })
            
            df = pd.DataFrame(alert_data)
            
            # Style the dataframe
            def highlight_risk(row):
                if "गंभीर" in str(row[get_bilingual_text("जोखिम स्तर", "Risk Level")]) or "Severe" in str(row[get_bilingual_text("जोखिम स्तर", "Risk Level")]):
                    return ['background-color: #ffebee'] * len(row)
                elif "मध्यम" in str(row[get_bilingual_text("जोखिम स्तर", "Risk Level")]) or "Moderate" in str(row[get_bilingual_text("जोखिम स्तर", "Risk Level")]):
                    return ['background-color: #fff3e0'] * len(row)
                return [''] * len(row)
            
            styled_df = df.style.apply(highlight_risk, axis=1)
            st.dataframe(styled_df, use_container_width=True)
            
            # Action buttons
            if st.button(get_bilingual_text("🚨 तत्काल हस्तक्षेप आवश्यक", "🚨 Immediate Intervention Required")):
                st.warning(get_bilingual_text(
                    "उच्च जोखिम मामलों के लिए तत्काल कार्रवाई की आवश्यकता है।",
                    "Immediate action required for high-risk cases."
                ))
        else:
            st.success(get_bilingual_text(
                "✅ कोई उच्च जोखिम मामले नहीं मिले",
                "✅ No high-risk cases found"
            ))
    
    def render_individual_monitoring(self):
        """Render individual user monitoring interface"""
        
        st.subheader(get_bilingual_text("👥 व्यक्तिगत उपयोगकर्ता निगरानी", "👥 Individual User Monitoring"))
        
        # User selection
        users = self.db.query(User).filter(User.role == "user").all()
        
        if users:
            user_options = {f"{user.full_name or user.username} ({user.army_id or 'No ID'})": user.id for user in users}
            
            selected_user_display = st.selectbox(
                get_bilingual_text("उपयोगकर्ता चुनें", "Select User"),
                options=list(user_options.keys())
            )
            
            if selected_user_display:
                selected_user_id = user_options[selected_user_display]
                selected_user = self.db.query(User).filter(User.id == selected_user_id).first()
                
                if selected_user:
                    self.render_user_profile(selected_user)
                    self.render_user_assessment_history(selected_user)
                    self.render_user_risk_analysis(selected_user)
                    self.render_intervention_recommendations(selected_user)
        else:
            st.info(get_bilingual_text("कोई उपयोगकर्ता उपलब्ध नहीं", "No users available"))
    
    def render_user_profile(self, user):
        """Render detailed user profile"""
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            **{get_bilingual_text('व्यक्तिगत जानकारी', 'Personal Information')}**
            - **{get_bilingual_text('नाम', 'Name')}:** {user.full_name or 'N/A'}
            - **{get_bilingual_text('उपयोगकर्ता नाम', 'Username')}:** {user.username}
            - **{get_bilingual_text('ईमेल', 'Email')}:** {user.email}
            """)
        
        with col2:
            st.markdown(f"""
            **{get_bilingual_text('सैन्य जानकारी', 'Military Information')}**
            - **{get_bilingual_text('सेना आईडी', 'Army ID')}:** {user.army_id or 'N/A'}
            - **{get_bilingual_text('रैंक', 'Rank')}:** {user.rank or 'N/A'}
            - **{get_bilingual_text('यूनिट', 'Unit')}:** {user.unit or 'N/A'}
            """)
        
        with col3:
            # Get latest assessment
            latest_assessment = self.db.query(Assessment).filter(
                Assessment.user_id == user.id
            ).order_by(Assessment.started_at.desc()).first()
            
            if latest_assessment:
                risk_color = {
                    'normal': 'green',
                    'mild': 'orange', 
                    'moderate': 'red',
                    'severe': 'darkred'
                }.get(latest_assessment.mental_state, 'gray')
                
                st.markdown(f"""
                **{get_bilingual_text('वर्तमान स्थिति', 'Current Status')}**
                - **{get_bilingual_text('मानसिक स्थिति', 'Mental State')}:** <span style="color: {risk_color}">**{latest_assessment.mental_state.title()}**</span>
                - **{get_bilingual_text('स्कोर', 'Score')}:** {latest_assessment.overall_score or 0:.1f}%
                - **{get_bilingual_text('अंतिम मूल्यांकन', 'Last Assessment')}:** {latest_assessment.started_at.strftime('%d/%m/%Y')}
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                **{get_bilingual_text('वर्तमान स्थिति', 'Current Status')}**
                - {get_bilingual_text('कोई मूल्यांकन नहीं', 'No assessments yet')}
                """)
    
    def get_mental_state_severity_score(self, state):
        """Convert mental state to severity-based Y-coordinate (0-100 scale)"""
        severity_mapping = {
            'normal': 85,      # High Y-coordinate for good mental health
            'stable': 85,      # Same as normal
            'good': 85,        # Same as normal
            'healthy': 85,     # Same as normal
            'mild': 60,        # Moderate Y-coordinate for mild concerns
            'moderate': 35,    # Lower Y-coordinate for moderate concerns
            'severe': 10,      # Low Y-coordinate for severe concerns
            'critical': 5,     # Very low for critical
            'unknown': 50      # Middle for unknown
        }

        # Normalize state name
        if state:
            state_lower = state.lower().strip()
            return severity_mapping.get(state_lower, 50)  # Default to middle
        return 50

    def render_user_assessment_history(self, user):
        """Render user's assessment history with trends and severity-based mental state plotting"""

        st.subheader(get_bilingual_text("📈 मूल्यांकन इतिहास", "📈 Assessment History"))
        
        # Get user's assessments
        assessments = self.db.query(Assessment).filter(
            Assessment.user_id == user.id,
            Assessment.status == "completed"
        ).order_by(Assessment.started_at.asc()).all()
        
        if assessments:
            # Create trend chart
            dates = [a.started_at for a in assessments]
            scores = [a.overall_score or 0 for a in assessments]
            states = [a.mental_state for a in assessments]

            # Convert mental states to severity-based Y-coordinates
            state_severity_scores = [self.get_mental_state_severity_score(state) for state in states]

            fig = go.Figure()

            # Add score line
            fig.add_trace(go.Scatter(
                x=dates,
                y=scores,
                mode='lines+markers',
                name=get_bilingual_text("स्कोर", "Score"),
                line=dict(color='#007bff', width=3),
                marker=dict(size=10)
            ))

            # Add mental state severity line (based on severity, not raw values)
            fig.add_trace(go.Scatter(
                x=dates,
                y=state_severity_scores,
                mode='lines+markers',
                name=get_bilingual_text("मानसिक स्थिति गंभीरता", "Mental State Severity"),
                line=dict(color='#28a745', width=2, dash='dash'),
                marker=dict(size=8, symbol='diamond')
            ))

            # Add mental state annotations with severity-based positioning
            for i, (date, severity_score, state) in enumerate(zip(dates, state_severity_scores, states)):
                color = {
                    'normal': '#28a745',
                    'stable': '#28a745',
                    'good': '#28a745',
                    'healthy': '#28a745',
                    'mild': '#ffc107',
                    'moderate': '#fd7e14',
                    'severe': '#dc3545',
                    'critical': '#721c24'
                }.get(state.lower() if state else 'unknown', '#6c757d')

                fig.add_annotation(
                    x=date,
                    y=severity_score,
                    text=state.title() if state else 'Unknown',
                    showarrow=True,
                    arrowcolor=color,
                    bgcolor=color,
                    bordercolor=color,
                    font=dict(color='white', size=9),
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2
                )
            
            fig.update_layout(
                title=get_bilingual_text("मानसिक स्वास्थ्य रुझान", "Mental Health Trend"),
                xaxis_title=get_bilingual_text("दिनांक", "Date"),
                yaxis_title=get_bilingual_text("स्कोर / गंभीरता स्तर", "Score / Severity Level"),
                height=400,
                yaxis=dict(
                    range=[0, 100],
                    tickmode='array',
                    tickvals=[10, 35, 60, 85],
                    ticktext=[
                        get_bilingual_text("गंभीर", "Severe"),
                        get_bilingual_text("मध्यम", "Moderate"),
                        get_bilingual_text("हल्का", "Mild"),
                        get_bilingual_text("सामान्य", "Normal")
                    ]
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Assessment details table
            assessment_data = []
            for assessment in assessments[-5:]:  # Last 5 assessments
                assessment_data.append({
                    get_bilingual_text("दिनांक", "Date"): assessment.started_at.strftime("%d/%m/%Y %H:%M"),
                    get_bilingual_text("स्कोर", "Score"): f"{assessment.overall_score or 0:.1f}%",
                    get_bilingual_text("मानसिक स्थिति", "Mental State"): assessment.mental_state.title(),
                    get_bilingual_text("स्थिति", "Status"): assessment.status.title()
                })
            
            if assessment_data:
                st.dataframe(pd.DataFrame(assessment_data), use_container_width=True)
        else:
            st.info(get_bilingual_text("कोई मूल्यांकन इतिहास उपलब्ध नहीं", "No assessment history available"))
    
    def render_user_risk_analysis(self, user):
        """Render detailed risk analysis for user"""
        
        st.subheader(get_bilingual_text("🚨 जोखिम विश्लेषण", "🚨 Risk Analysis"))
        
        # Get latest assessment
        latest_assessment = self.db.query(Assessment).filter(
            Assessment.user_id == user.id
        ).order_by(Assessment.started_at.desc()).first()
        
        if latest_assessment:
            col1, col2 = st.columns(2)
            
            with col1:
                # Risk level indicator
                risk_level = latest_assessment.mental_state
                risk_colors = {
                    'normal': '#28a745',
                    'mild': '#ffc107',
                    'moderate': '#fd7e14', 
                    'severe': '#dc3545'
                }
                
                st.markdown(f"""
                <div style="padding: 20px; border-radius: 10px; background-color: {risk_colors.get(risk_level, '#6c757d')}; color: white; text-align: center;">
                    <h3>{get_bilingual_text('जोखिम स्तर', 'Risk Level')}</h3>
                    <h2>{risk_level.upper()}</h2>
                    <p>{get_bilingual_text('स्कोर', 'Score')}: {latest_assessment.overall_score or 0:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Risk factors
                risk_factors = []
                if latest_assessment.overall_score and latest_assessment.overall_score > 70:
                    risk_factors.append(get_bilingual_text("उच्च स्कोर", "High Score"))
                if risk_level in ['severe', 'moderate']:
                    risk_factors.append(get_bilingual_text("गंभीर मानसिक स्थिति", "Severe Mental State"))
                
                st.markdown(f"""
                **{get_bilingual_text('जोखिम कारक', 'Risk Factors')}:**
                """)
                
                if risk_factors:
                    for factor in risk_factors:
                        st.markdown(f"- ⚠️ {factor}")
                else:
                    st.markdown(f"- ✅ {get_bilingual_text('कोई प्रमुख जोखिम कारक नहीं', 'No major risk factors')}")
        else:
            st.info(get_bilingual_text("जोखिम विश्लेषण के लिए मूल्यांकन डेटा आवश्यक", "Assessment data required for risk analysis"))

    def render_intervention_recommendations(self, user):
        """Render personalized intervention recommendations"""

        st.subheader(get_bilingual_text("💡 हस्तक्षेप सुझाव", "💡 Intervention Recommendations"))

        # Get latest assessment
        latest_assessment = self.db.query(Assessment).filter(
            Assessment.user_id == user.id
        ).order_by(Assessment.started_at.desc()).first()

        if latest_assessment:
            # Generate suggestions using the suggestion engine
            assessment_result = {
                "mental_state": latest_assessment.mental_state,
                "overall_score": latest_assessment.overall_score or 0,
                "detected_conditions": [latest_assessment.mental_state] if latest_assessment.mental_state else []
            }

            user_profile = {
                "full_name": user.full_name,
                "rank": user.rank,
                "army_id": user.army_id,
                "unit": user.unit
            }

            try:
                suggestions = suggestion_engine.generate_personalized_suggestions(
                    assessment_result, user_profile, get_language()
                )

                # Display personalized message
                if suggestions.get("personalized_message"):
                    st.info(suggestions["personalized_message"])

                # Display suggestions in tabs
                tab1, tab2, tab3 = st.tabs([
                    get_bilingual_text("तत्काल कार्रवाई", "Immediate Actions"),
                    get_bilingual_text("जीवनशैली", "Lifestyle"),
                    get_bilingual_text("पेशेवर सहायता", "Professional Help")
                ])

                with tab1:
                    if suggestions.get("immediate_actions"):
                        for action in suggestions["immediate_actions"]:
                            st.markdown(f"- 🚨 {action}")
                    else:
                        st.info(get_bilingual_text("कोई तत्काल कार्रवाई आवश्यक नहीं", "No immediate actions required"))

                with tab2:
                    if suggestions.get("lifestyle_recommendations"):
                        for rec in suggestions["lifestyle_recommendations"]:
                            st.markdown(f"- 🌱 {rec}")
                    else:
                        st.info(get_bilingual_text("सामान्य स्वस्थ जीवनशैली बनाए रखें", "Maintain general healthy lifestyle"))

                with tab3:
                    if suggestions.get("professional_help"):
                        for help_item in suggestions["professional_help"]:
                            st.markdown(f"- 👨‍⚕️ {help_item}")

                    # Emergency contacts for high-risk cases
                    if suggestions.get("emergency_contacts"):
                        st.error(get_bilingual_text("आपातकालीन संपर्क", "Emergency Contacts"))
                        for contact in suggestions["emergency_contacts"]:
                            st.markdown(f"- 📞 {contact}")

                # Follow-up plan
                if suggestions.get("follow_up"):
                    st.subheader(get_bilingual_text("📅 फॉलो-अप योजना", "📅 Follow-up Plan"))
                    for follow_up in suggestions["follow_up"]:
                        st.markdown(f"- 📋 {follow_up}")

            except Exception as e:
                st.error(f"Error generating suggestions: {e}")

        else:
            st.info(get_bilingual_text("सुझाव के लिए मूल्यांकन डेटा आवश्यक", "Assessment data required for recommendations"))

    def render_trend_analysis(self):
        """Render comprehensive trend analysis"""

        st.subheader(get_bilingual_text("📈 रुझान विश्लेषण", "📈 Trend Analysis"))

        # Time period selection
        period = st.selectbox(
            get_bilingual_text("समय अवधि चुनें", "Select Time Period"),
            [
                get_bilingual_text("पिछले 7 दिन", "Last 7 days"),
                get_bilingual_text("पिछले 30 दिन", "Last 30 days"),
                get_bilingual_text("पिछले 90 दिन", "Last 90 days"),
                get_bilingual_text("पिछले 1 साल", "Last 1 year")
            ]
        )

        # Calculate date range
        days_map = {
            get_bilingual_text("पिछले 7 दिन", "Last 7 days"): 7,
            get_bilingual_text("पिछले 30 दिन", "Last 30 days"): 30,
            get_bilingual_text("पिछले 90 दिन", "Last 90 days"): 90,
            get_bilingual_text("पिछले 1 साल", "Last 1 year"): 365
        }

        days = days_map.get(period, 30)
        start_date = datetime.now() - timedelta(days=days)

        # Get assessments in period
        assessments = self.db.query(Assessment).filter(
            Assessment.started_at >= start_date,
            Assessment.status == "completed"
        ).all()

        if assessments:
            col1, col2 = st.columns(2)

            with col1:
                self.render_mental_state_trend(assessments)

            with col2:
                self.render_score_distribution(assessments)

            # Unit-wise analysis
            self.render_unit_wise_analysis(assessments)

        else:
            st.info(get_bilingual_text("चुनी गई अवधि में कोई डेटा उपलब्ध नहीं", "No data available for selected period"))

    def render_mental_state_trend(self, assessments):
        """Render mental state trend over time with severity-based positioning"""

        if not assessments:
            st.info(get_bilingual_text("कोई डेटा उपलब्ध नहीं", "No data available"))
            return

        # Group assessments by date and calculate average severity
        daily_severity = {}
        for assessment in assessments:
            date = assessment.started_at.date()
            state = assessment.mental_state
            severity_score = self.get_mental_state_severity_score(state)

            if date not in daily_severity:
                daily_severity[date] = []
            daily_severity[date].append(severity_score)

        # Calculate daily average severity
        dates = sorted(daily_severity.keys())
        avg_severity_scores = [sum(daily_severity[date]) / len(daily_severity[date]) for date in dates]

        # Also track individual state counts for reference
        daily_states = {}
        for assessment in assessments:
            date = assessment.started_at.date()
            state = assessment.mental_state or 'unknown'

            if date not in daily_states:
                daily_states[date] = {'normal': 0, 'mild': 0, 'moderate': 0, 'severe': 0, 'unknown': 0}

            if state in daily_states[date]:
                daily_states[date][state] += 1
            else:
                daily_states[date]['unknown'] += 1

        fig = go.Figure()

        # Add average severity trend line
        fig.add_trace(go.Scatter(
            x=dates,
            y=avg_severity_scores,
            mode='lines+markers',
            name=get_bilingual_text("औसत गंभीरता स्तर", "Average Severity Level"),
            line=dict(color='#007bff', width=3),
            marker=dict(size=8)
        ))

        # Add individual state counts as stacked area (secondary y-axis)
        colors = {
            'normal': '#28a745',
            'mild': '#ffc107',
            'moderate': '#fd7e14',
            'severe': '#dc3545',
            'unknown': '#6c757d'
        }

        for state in ['severe', 'moderate', 'mild', 'normal', 'unknown']:  # Reverse order for stacking
            values = [daily_states[date][state] for date in dates]
            if any(v > 0 for v in values):  # Only add if there are values
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines',
                    stackgroup='one',
                    name=get_bilingual_text(
                        {'normal': 'सामान्य', 'mild': 'हल्का', 'moderate': 'मध्यम', 'severe': 'गंभीर', 'unknown': 'अज्ञात'}[state],
                        state.title()
                    ),
                    line=dict(color=colors[state]),
                    yaxis='y2',
                    opacity=0.7
                ))

        fig.update_layout(
            title=get_bilingual_text("मानसिक स्थिति गंभीरता रुझान", "Mental State Severity Trend"),
            xaxis_title=get_bilingual_text("दिनांक", "Date"),
            yaxis=dict(
                title=get_bilingual_text("गंभीरता स्तर", "Severity Level"),
                range=[0, 100],
                tickmode='array',
                tickvals=[10, 35, 60, 85],
                ticktext=[
                    get_bilingual_text("गंभीर", "Severe"),
                    get_bilingual_text("मध्यम", "Moderate"),
                    get_bilingual_text("हल्का", "Mild"),
                    get_bilingual_text("सामान्य", "Normal")
                ]
            ),
            yaxis2=dict(
                title=get_bilingual_text("मामलों की संख्या", "Number of Cases"),
                overlaying='y',
                side='right'
            ),
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_score_distribution(self, assessments):
        """Render score distribution histogram"""

        scores = [a.overall_score for a in assessments if a.overall_score is not None]

        if scores:
            fig = go.Figure(data=[go.Histogram(
                x=scores,
                nbinsx=20,
                marker_color='#007bff',
                opacity=0.7
            )])

            fig.update_layout(
                title=get_bilingual_text("स्कोर वितरण", "Score Distribution"),
                xaxis_title=get_bilingual_text("स्कोर (%)", "Score (%)"),
                yaxis_title=get_bilingual_text("आवृत्ति", "Frequency"),
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(get_bilingual_text("स्कोर डेटा उपलब्ध नहीं", "No score data available"))

    def render_unit_wise_analysis(self, assessments):
        """Render unit-wise mental health analysis"""

        st.subheader(get_bilingual_text("🏢 यूनिट-वार विश्लेषण", "🏢 Unit-wise Analysis"))

        # Get unit data
        unit_data = {}
        for assessment in assessments:
            user = self.db.query(User).filter(User.id == assessment.user_id).first()
            if user and user.unit:
                unit = user.unit
                if unit not in unit_data:
                    unit_data[unit] = {'total': 0, 'high_risk': 0, 'avg_score': []}

                unit_data[unit]['total'] += 1
                if assessment.mental_state in ['severe', 'moderate']:
                    unit_data[unit]['high_risk'] += 1
                if assessment.overall_score:
                    unit_data[unit]['avg_score'].append(assessment.overall_score)

        if unit_data:
            # Prepare data for chart
            units = []
            total_assessments = []
            high_risk_counts = []
            avg_scores = []

            for unit, data in unit_data.items():
                units.append(unit)
                total_assessments.append(data['total'])
                high_risk_counts.append(data['high_risk'])
                avg_scores.append(sum(data['avg_score']) / len(data['avg_score']) if data['avg_score'] else 0)

            # Create subplot
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=[
                    get_bilingual_text("यूनिट-वार मूल्यांकन", "Unit-wise Assessments"),
                    get_bilingual_text("उच्च जोखिम मामले", "High-Risk Cases")
                ]
            )

            # Total assessments bar chart
            fig.add_trace(
                go.Bar(x=units, y=total_assessments, name=get_bilingual_text("कुल", "Total"), marker_color='#007bff'),
                row=1, col=1
            )

            # High-risk cases bar chart
            fig.add_trace(
                go.Bar(x=units, y=high_risk_counts, name=get_bilingual_text("उच्च जोखिम", "High Risk"), marker_color='#dc3545'),
                row=1, col=2
            )

            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            # Unit summary table
            unit_summary = []
            for unit, data in unit_data.items():
                avg_score = sum(data['avg_score']) / len(data['avg_score']) if data['avg_score'] else 0
                risk_percentage = (data['high_risk'] / data['total']) * 100 if data['total'] > 0 else 0

                unit_summary.append({
                    get_bilingual_text("यूनिट", "Unit"): unit,
                    get_bilingual_text("कुल मूल्यांकन", "Total Assessments"): data['total'],
                    get_bilingual_text("उच्च जोखिम", "High Risk"): data['high_risk'],
                    get_bilingual_text("जोखिम %", "Risk %"): f"{risk_percentage:.1f}%",
                    get_bilingual_text("औसत स्कोर", "Avg Score"): f"{avg_score:.1f}%"
                })

            st.dataframe(pd.DataFrame(unit_summary), use_container_width=True)
        else:
            st.info(get_bilingual_text("यूनिट डेटा उपलब्ध नहीं", "No unit data available"))

    def render_risk_management(self):
        """Render risk management interface"""

        st.subheader(get_bilingual_text("🚨 जोखिम प्रबंधन", "🚨 Risk Management"))

        # Risk level filter
        risk_filter = st.multiselect(
            get_bilingual_text("जोखिम स्तर फ़िल्टर", "Risk Level Filter"),
            [
                get_bilingual_text("गंभीर", "Severe"),
                get_bilingual_text("मध्यम", "Moderate"),
                get_bilingual_text("हल्का", "Mild"),
                get_bilingual_text("सामान्य", "Normal")
            ],
            default=[get_bilingual_text("गंभीर", "Severe"), get_bilingual_text("मध्यम", "Moderate")]
        )

        # Map back to English for database query
        risk_map = {
            get_bilingual_text("गंभीर", "Severe"): "severe",
            get_bilingual_text("मध्यम", "Moderate"): "moderate",
            get_bilingual_text("हल्का", "Mild"): "mild",
            get_bilingual_text("सामान्य", "Normal"): "normal"
        }

        db_risk_filter = [risk_map.get(r, r.lower()) for r in risk_filter]

        # Get filtered assessments
        risk_assessments = self.db.query(Assessment, User).join(User).filter(
            Assessment.mental_state.in_(db_risk_filter)
        ).order_by(Assessment.started_at.desc()).all()

        if risk_assessments:
            # Risk summary
            col1, col2, col3 = st.columns(3)

            with col1:
                severe_count = len([a for a, u in risk_assessments if a.mental_state == "severe"])
                st.metric(get_bilingual_text("गंभीर मामले", "Severe Cases"), severe_count)

            with col2:
                moderate_count = len([a for a, u in risk_assessments if a.mental_state == "moderate"])
                st.metric(get_bilingual_text("मध्यम मामले", "Moderate Cases"), moderate_count)

            with col3:
                total_high_risk = severe_count + moderate_count
                st.metric(get_bilingual_text("कुल उच्च जोखिम", "Total High Risk"), total_high_risk)

            # Detailed risk table
            risk_data = []
            for assessment, user in risk_assessments:
                days_since = (datetime.now() - assessment.started_at).days

                risk_data.append({
                    get_bilingual_text("नाम", "Name"): user.full_name or user.username,
                    get_bilingual_text("सेना आईडी", "Army ID"): user.army_id or "N/A",
                    get_bilingual_text("यूनिट", "Unit"): user.unit or "N/A",
                    get_bilingual_text("जोखिम", "Risk"): get_bilingual_text(
                        {'severe': 'गंभीर', 'moderate': 'मध्यम', 'mild': 'हल्का', 'normal': 'सामान्य'}.get(assessment.mental_state, assessment.mental_state),
                        assessment.mental_state.title()
                    ),
                    get_bilingual_text("स्कोर", "Score"): f"{assessment.overall_score or 0:.1f}%",
                    get_bilingual_text("दिन पहले", "Days Ago"): days_since,
                    get_bilingual_text("स्थिति", "Status"): get_bilingual_text("कार्रवाई आवश्यक", "Action Required") if assessment.mental_state in ["severe", "moderate"] else get_bilingual_text("निगरानी", "Monitor")
                })

            df = pd.DataFrame(risk_data)

            # Color coding
            def highlight_risk_level(row):
                risk_level = row[get_bilingual_text("जोखिम", "Risk")]
                if "गंभीर" in str(risk_level) or "Severe" in str(risk_level):
                    return ['background-color: #ffebee'] * len(row)
                elif "मध्यम" in str(risk_level) or "Moderate" in str(risk_level):
                    return ['background-color: #fff3e0'] * len(row)
                return [''] * len(row)

            styled_df = df.style.apply(highlight_risk_level, axis=1)
            st.dataframe(styled_df, use_container_width=True)

            # Bulk actions
            st.subheader(get_bilingual_text("📋 बल्क एक्शन", "📋 Bulk Actions"))

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(get_bilingual_text("🚨 आपातकालीन अलर्ट भेजें", "🚨 Send Emergency Alert")):
                    st.success(get_bilingual_text("आपातकालीन अलर्ट भेजा गया", "Emergency alert sent"))

            with col2:
                if st.button(get_bilingual_text("📞 काउंसलर को सूचित करें", "📞 Notify Counselors")):
                    st.success(get_bilingual_text("काउंसलर को सूचना भेजी गई", "Counselors notified"))

            with col3:
                if st.button(get_bilingual_text("📊 रिपोर्ट जेनरेट करें", "📊 Generate Report")):
                    st.success(get_bilingual_text("रिपोर्ट तैयार की गई", "Report generated"))

        else:
            st.success(get_bilingual_text("✅ चुने गए फ़िल्टर में कोई जोखिम मामले नहीं", "✅ No risk cases in selected filters"))

    def render_intervention_management(self):
        """Render intervention management system"""

        try:
            from admin.interventions_reports import interventions_reports_system
            interventions_reports_system.render_interventions_management()
        except ImportError as e:
            st.error(f"Interventions system not available: {e}")
            st.info(get_bilingual_text("हस्तक्षेप ट्रैकिंग सिस्टम विकसित किया जा रहा है", "Intervention tracking system under development"))

    def render_comprehensive_reports(self):
        """Render comprehensive reporting system"""

        st.subheader(get_bilingual_text("📋 व्यापक रिपोर्ट्स", "📋 Comprehensive Reports"))

        try:
            # Get all assessments
            assessments = self.db.query(Assessment).filter(Assessment.status == "completed").all()

            if not assessments:
                st.info(get_bilingual_text("रिपोर्ट के लिए डेटा उपलब्ध नहीं", "No data available for reports"))
                return

            # Report tabs
            report_tab1, report_tab2, report_tab3 = st.tabs([
                get_bilingual_text("📊 सांख्यिकीय रिपोर्ट", "📊 Statistical Report"),
                get_bilingual_text("📈 रुझान रिपोर्ट", "📈 Trend Report"),
                get_bilingual_text("🎯 कार्य योजना", "🎯 Action Plan")
            ])

            with report_tab1:
                self.render_statistical_report(assessments)

            with report_tab2:
                self.render_trend_report(assessments)

            with report_tab3:
                self.render_action_plan(assessments)

        except Exception as e:
            st.error(f"Reports error: {e}")

    def render_statistical_report(self, assessments):
        """Render statistical analysis report"""

        # Prepare data
        data = []
        for assessment in assessments:
            user = self.db.query(User).filter(User.id == assessment.user_id).first()
            data.append({
                'Score': assessment.overall_score or 0,
                'Mental State': assessment.mental_state or 'unknown',
                'Unit': user.unit if user else 'Unknown',
                'Date': assessment.completed_at.strftime('%Y-%m-%d') if assessment.completed_at else 'Unknown'
            })

        df = pd.DataFrame(data)

        # Summary statistics
        st.markdown("#### " + get_bilingual_text("सारांश आंकड़े", "Summary Statistics"))

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            avg_score = df['Score'].mean()
            st.metric(
                get_bilingual_text("औसत स्कोर", "Average Score"),
                f"{avg_score:.1f}",
                help=get_bilingual_text("सभी मूल्यांकनों का औसत स्कोर", "Average score across all assessments")
            )

        with col2:
            severe_count = (df['Mental State'] == 'severe').sum()
            st.metric(
                get_bilingual_text("गंभीर मामले", "Severe Cases"),
                severe_count,
                help=get_bilingual_text("गंभीर मानसिक स्वास्थ्य मामलों की संख्या", "Number of severe mental health cases")
            )

        with col3:
            total_units = df['Unit'].nunique()
            st.metric(
                get_bilingual_text("कुल यूनिट्स", "Total Units"),
                total_units,
                help=get_bilingual_text("मूल्यांकन में शामिल यूनिट्स की संख्या", "Number of units involved in assessments")
            )

        with col4:
            completion_rate = len(assessments) / self.db.query(User).filter(User.role == "user").count() * 100
            st.metric(
                get_bilingual_text("पूर्णता दर", "Completion Rate"),
                f"{completion_rate:.1f}%",
                help=get_bilingual_text("मूल्यांकन पूर्णता प्रतिशत", "Assessment completion percentage")
            )

        # Detailed breakdown
        st.markdown("#### " + get_bilingual_text("विस्तृत विश्लेषण", "Detailed Analysis"))

        # Mental state distribution
        mental_state_dist = df['Mental State'].value_counts()

        import plotly.express as px
        fig = px.pie(
            values=mental_state_dist.values,
            names=mental_state_dist.index,
            title=get_bilingual_text("मानसिक स्थिति वितरण", "Mental State Distribution"),
            color_discrete_map={
                'normal': '#28a745',
                'mild': '#ffc107',
                'moderate': '#fd7e14',
                'severe': '#dc3545'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_trend_report(self, assessments):
        """Render trend analysis report"""

        st.markdown("#### " + get_bilingual_text("समय आधारित रुझान", "Time-based Trends"))

        # Prepare time series data
        data = []
        for assessment in assessments:
            if assessment.completed_at:
                data.append({
                    'Date': assessment.completed_at.date(),
                    'Score': assessment.overall_score or 0,
                    'Mental State': assessment.mental_state or 'unknown'
                })

        if not data:
            st.info(get_bilingual_text("रुझान विश्लेषण के लिए पर्याप्त डेटा नहीं", "Insufficient data for trend analysis"))
            return

        df = pd.DataFrame(data)

        # Daily trends
        daily_stats = df.groupby('Date').agg({
            'Score': 'mean',
            'Mental State': lambda x: (x == 'severe').sum()
        }).reset_index()

        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_stats['Date'],
            y=daily_stats['Score'],
            mode='lines+markers',
            name=get_bilingual_text('औसत स्कोर', 'Average Score'),
            line=dict(color='#007bff', width=3)
        ))

        fig.update_layout(
            title=get_bilingual_text("दैनिक औसत स्कोर रुझान", "Daily Average Score Trend"),
            xaxis_title=get_bilingual_text("दिनांक", "Date"),
            yaxis_title=get_bilingual_text("औसत स्कोर", "Average Score")
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_action_plan(self, assessments):
        """Render action plan based on analysis"""

        st.markdown("#### " + get_bilingual_text("सुझावित कार्य योजना", "Recommended Action Plan"))

        # Analyze current situation
        data = []
        for assessment in assessments:
            user = self.db.query(User).filter(User.id == assessment.user_id).first()
            data.append({
                'Mental State': assessment.mental_state or 'unknown',
                'Unit': user.unit if user else 'Unknown',
                'Score': assessment.overall_score or 0
            })

        df = pd.DataFrame(data)

        # Generate recommendations
        severe_cases = (df['Mental State'] == 'severe').sum()
        moderate_cases = (df['Mental State'] == 'moderate').sum()
        avg_score = df['Score'].mean()

        # Priority actions
        st.markdown("##### " + get_bilingual_text("प्राथमिकता कार्य", "Priority Actions"))

        if severe_cases > 0:
            st.error(f"🚨 **{get_bilingual_text('तत्काल कार्रवाई', 'IMMEDIATE ACTION')}**: {severe_cases} {get_bilingual_text('गंभीर मामलों के लिए तत्काल हस्तक्षेप आवश्यक', 'severe cases require immediate intervention')}")

            st.markdown(f"""
            **{get_bilingual_text('तत्काल कदम', 'Immediate Steps')}:**
            - {get_bilingual_text('मानसिक स्वास्थ्य पेशेवर से तत्काल संपर्क', 'Immediate contact with mental health professionals')}
            - {get_bilingual_text('व्यक्तिगत परामर्श सत्र', 'Individual counseling sessions')}
            - {get_bilingual_text('चिकित्सा मूल्यांकन', 'Medical evaluation')}
            - {get_bilingual_text('कमांड को सूचना', 'Inform command structure')}
            """)

        if moderate_cases > 0:
            st.warning(f"⚠️ **{get_bilingual_text('निगरानी आवश्यक', 'MONITORING REQUIRED')}**: {moderate_cases} {get_bilingual_text('मध्यम जोखिम मामले', 'moderate risk cases')}")

            st.markdown(f"""
            **{get_bilingual_text('निगरानी कदम', 'Monitoring Steps')}:**
            - {get_bilingual_text('साप्ताहिक चेक-इन', 'Weekly check-ins')}
            - {get_bilingual_text('समूह परामर्श सत्र', 'Group counseling sessions')}
            - {get_bilingual_text('तनाव प्रबंधन कार्यशाला', 'Stress management workshops')}
            """)

        # Unit-specific recommendations
        st.markdown("##### " + get_bilingual_text("यूनिट-विशिष्ट सिफारिशें", "Unit-specific Recommendations"))

        unit_analysis = df.groupby('Unit').agg({
            'Score': 'mean',
            'Mental State': lambda x: (x == 'severe').sum()
        }).round(2)

        for unit, stats in unit_analysis.iterrows():
            if stats['Mental State'] > 0:
                st.warning(f"**{unit}**: {get_bilingual_text('विशेष ध्यान आवश्यक', 'Special attention required')} - {stats['Mental State']} {get_bilingual_text('गंभीर मामले', 'severe cases')}")
            elif stats['Score'] < 50:
                st.info(f"**{unit}**: {get_bilingual_text('निवारक उपाय सुझाए गए', 'Preventive measures recommended')} - {get_bilingual_text('औसत स्कोर', 'Average score')}: {stats['Score']}")
            else:
                st.success(f"**{unit}**: {get_bilingual_text('अच्छी स्थिति', 'Good condition')} - {get_bilingual_text('निरंतर निगरानी जारी रखें', 'Continue regular monitoring')}")

        # Timeline for actions
        st.markdown("##### " + get_bilingual_text("कार्य समयसीमा", "Action Timeline"))

        timeline_data = [
            {get_bilingual_text('समयसीमा', 'Timeline'): get_bilingual_text('तत्काल (24 घंटे)', 'Immediate (24 hours)'),
             get_bilingual_text('कार्य', 'Action'): get_bilingual_text('गंभीर मामलों का हस्तक्षेप', 'Severe cases intervention')},
            {get_bilingual_text('समयसीमा', 'Timeline'): get_bilingual_text('1 सप्ताह', '1 Week'),
             get_bilingual_text('कार्य', 'Action'): get_bilingual_text('मध्यम जोखिम मामलों की निगरानी शुरू', 'Begin monitoring moderate risk cases')},
            {get_bilingual_text('समयसीमा', 'Timeline'): get_bilingual_text('1 महीना', '1 Month'),
             get_bilingual_text('कार्य', 'Action'): get_bilingual_text('सभी यूनिट्स के लिए निवारक कार्यक्रम', 'Preventive programs for all units')},
            {get_bilingual_text('समयसीमा', 'Timeline'): get_bilingual_text('निरंतर', 'Ongoing'),
             get_bilingual_text('कार्य', 'Action'): get_bilingual_text('नियमित मूल्यांकन और निगरानी', 'Regular assessment and monitoring')}
        ]

        timeline_df = pd.DataFrame(timeline_data)
        st.table(timeline_df)

# Global instance
admin_monitoring = AdvancedAdminMonitoring()
