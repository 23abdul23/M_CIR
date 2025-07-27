#!/usr/bin/env python3
"""
Comprehensive Assessment Controller for Army Mental Health System
Manages step-wise assessment flow: Questionnaire -> Voice -> Facial -> Final Report
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveAssessmentController:
    """
    Controls the complete assessment workflow with step-wise progression
    """
    
    def __init__(self):
        """Initialize the assessment controller"""
        self.assessment_steps = [
            "questionnaire",
            "language_analysis",
            "voice_analysis",
            "facial_analysis",
            "final_report"
        ]

        self.step_names = {
            "questionnaire": {"en": "Questionnaire Assessment", "hi": "प्रश्नावली मूल्यांकन"},
            "language_analysis": {"en": "Language Analysis", "hi": "भाषा विश्लेषण"},
            "voice_analysis": {"en": "Voice Analysis", "hi": "आवाज़ विश्लेषण"},
            "facial_analysis": {"en": "Facial Behavior Analysis", "hi": "चेहरे का व्यवहार विश्लेषण"},
            "final_report": {"en": "Comprehensive Report", "hi": "व्यापक रिपोर्ट"}
        }

        # Step weights for final scoring
        self.step_weights = {
            "questionnaire": 0.35,      # 35%
            "language_analysis": 0.15,  # 15%
            "voice_analysis": 0.25,     # 25%
            "facial_analysis": 0.25     # 25%
        }
        
        # Initialize session state for assessment flow
        if 'assessment_flow' not in st.session_state:
            st.session_state.assessment_flow = {
                'current_step': 0,
                'completed_steps': [],
                'results': {},
                'started_at': None,
                'completed_at': None
            }
    
    def get_current_step(self) -> str:
        """Get current assessment step"""
        current_index = st.session_state.assessment_flow['current_step']
        if current_index < len(self.assessment_steps):
            return self.assessment_steps[current_index]
        return "completed"
    
    def get_step_name(self, step: str, language: str = "en") -> str:
        """Get localized step name"""
        return self.step_names.get(step, {}).get(language, step)
    
    def is_step_completed(self, step: str) -> bool:
        """Check if a step is completed"""
        return step in st.session_state.assessment_flow['completed_steps']
    
    def complete_step(self, step: str, results: Dict):
        """Mark a step as completed and store results"""
        if step not in st.session_state.assessment_flow['completed_steps']:
            st.session_state.assessment_flow['completed_steps'].append(step)
        
        st.session_state.assessment_flow['results'][step] = {
            'data': results,
            'completed_at': datetime.now().isoformat(),
            'timestamp': time.time()
        }
        
        # Move to next step
        current_index = st.session_state.assessment_flow['current_step']
        if current_index < len(self.assessment_steps) - 1:
            st.session_state.assessment_flow['current_step'] = current_index + 1
        
        logger.info(f"Step '{step}' completed successfully")
    
    def start_assessment(self):
        """Start the assessment flow"""
        st.session_state.assessment_flow['started_at'] = datetime.now().isoformat()
        st.session_state.assessment_flow['current_step'] = 0
        st.session_state.assessment_flow['completed_steps'] = []
        st.session_state.assessment_flow['results'] = {}
        logger.info("Assessment flow started")
    
    def reset_assessment(self):
        """Reset the assessment flow"""
        st.session_state.assessment_flow = {
            'current_step': 0,
            'completed_steps': [],
            'results': {},
            'started_at': None,
            'completed_at': None
        }
        logger.info("Assessment flow reset")
    
    def get_progress_percentage(self) -> float:
        """Get assessment progress as percentage"""
        completed_count = len(st.session_state.assessment_flow['completed_steps'])
        total_steps = len(self.assessment_steps)
        return (completed_count / total_steps) * 100
    
    def display_progress_bar(self, language: str = "en"):
        """Display assessment progress bar with fraction"""
        completed_count = len(st.session_state.assessment_flow['completed_steps'])
        # Only count the main assessment steps (exclude final_report)
        main_steps = [s for s in self.assessment_steps if s != 'final_report']
        total_main_steps = len(main_steps)

        # Calculate completed main steps
        completed_main_steps = sum(1 for step in main_steps if self.is_step_completed(step))

        progress_percentage = (completed_main_steps / total_main_steps) * 100

        st.subheader("Assessment Progress" if language == "en" else "मूल्यांकन प्रगति")

        # Progress bar with fraction display
        col1, col2 = st.columns([3, 1])

        with col1:
            st.progress(progress_percentage / 100)

        with col2:
            st.markdown(f"**{completed_main_steps}/{total_main_steps}** " +
                       ("completed" if language == "en" else "पूर्ण"))

        # Step indicators for main steps only
        cols = st.columns(len(main_steps))
        current_step = self.get_current_step()

        for i, step in enumerate(main_steps):
            with cols[i]:
                step_name = self.get_step_name(step, language)

                if self.is_step_completed(step):
                    st.success(f"✓ {step_name}")
                elif step == current_step:
                    st.info(f"→ {step_name}")
                else:
                    st.write(f"○ {step_name}")

        st.write(f"Progress: {progress_percentage:.0f}% Complete")
    
    def can_proceed_to_step(self, target_step: str) -> bool:
        """Check if user can proceed to a specific step"""
        target_index = self.assessment_steps.index(target_step)
        current_index = st.session_state.assessment_flow['current_step']
        
        # Can only proceed to current step or completed steps
        return target_index <= current_index or target_step in st.session_state.assessment_flow['completed_steps']
    
    def get_assessment_results(self) -> Dict:
        """Get all assessment results"""
        return st.session_state.assessment_flow['results']
    
    def is_assessment_complete(self) -> bool:
        """Check if all assessment steps are completed"""
        required_steps = self.assessment_steps[:-1]  # Exclude final_report
        return all(step in st.session_state.assessment_flow['completed_steps'] for step in required_steps)
    
    def calculate_overall_score(self) -> Dict:
        """Calculate overall assessment score from all components"""
        results = self.get_assessment_results()
        
        if not results:
            return {"error": "No assessment results available"}
        
        scores = {}
        weights = {
            'questionnaire': 0.4,  # 40% weight
            'voice_analysis': 0.3,  # 30% weight
            'facial_analysis': 0.3  # 30% weight
        }
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        # Extract scores from each assessment
        for step, weight in weights.items():
            if step in results:
                step_data = results[step]['data']
                
                if step == 'questionnaire':
                    # Extract questionnaire score (0-100)
                    score = step_data.get('score', 0) / 100.0  # Normalize to 0-1
                elif step == 'voice_analysis':
                    # Extract voice analysis score
                    score = step_data.get('overall_score', 0.5)  # Default to neutral
                elif step == 'facial_analysis':
                    # Extract facial analysis score (convert stress to wellness)
                    stress_score = step_data.get('analysis_summary', {}).get('average_stress_score', 0.5)
                    score = 1.0 - stress_score  # Convert stress to wellness score
                
                scores[step] = score
                total_weighted_score += score * weight
                total_weight += weight
        
        # Calculate final score
        if total_weight > 0:
            final_score = total_weighted_score / total_weight
        else:
            final_score = 0.5  # Default neutral score
        
        # Determine overall stress level
        if final_score >= 0.8:
            stress_level = "Low"
            risk_category = "Minimal Risk"
        elif final_score >= 0.6:
            stress_level = "Moderate"
            risk_category = "Low Risk"
        elif final_score >= 0.4:
            stress_level = "High"
            risk_category = "Moderate Risk"
        else:
            stress_level = "Severe"
            risk_category = "High Risk"
        
        return {
            'overall_score': final_score,
            'overall_percentage': final_score * 100,
            'stress_level': stress_level,
            'risk_category': risk_category,
            'component_scores': scores,
            'weights_used': weights,
            'assessment_date': datetime.now().isoformat()
        }
    
    def extract_key_findings(self) -> Dict:
        """Extract key findings from all assessments for AI recommendation generation"""
        results = self.get_assessment_results()
        findings = {
            'questionnaire_responses': {},
            'voice_indicators': {},
            'facial_indicators': {},
            'risk_factors': [],
            'positive_factors': []
        }
        
        # Extract questionnaire findings
        if 'questionnaire' in results:
            q_data = results['questionnaire']['data']
            findings['questionnaire_responses'] = q_data.get('responses', {})
            
            # Identify high-risk responses
            for question, response in findings['questionnaire_responses'].items():
                if isinstance(response, (int, float)) and response >= 3:  # High stress indicators
                    findings['risk_factors'].append(f"High stress in: {question}")
                elif isinstance(response, (int, float)) and response <= 1:  # Positive indicators
                    findings['positive_factors'].append(f"Good coping in: {question}")
        
        # Extract voice findings
        if 'voice_analysis' in results:
            v_data = results['voice_analysis']['data']
            findings['voice_indicators'] = {
                'stress_level': v_data.get('stress_level', 'unknown'),
                'confidence': v_data.get('confidence', 0),
                'emotional_state': v_data.get('emotional_state', 'neutral')
            }
            
            if v_data.get('stress_level') in ['high', 'severe']:
                findings['risk_factors'].append("Voice analysis indicates high stress")
        
        # Extract facial findings
        if 'facial_analysis' in results:
            f_data = results['facial_analysis']['data']
            analysis_summary = f_data.get('analysis_summary', {})
            
            findings['facial_indicators'] = {
                'stress_level': analysis_summary.get('final_stress_level', 'unknown'),
                'dominant_emotions': analysis_summary.get('emotion_distribution', {}),
                'stress_score': analysis_summary.get('average_stress_score', 0.5)
            }
            
            if analysis_summary.get('average_stress_score', 0) > 0.7:
                findings['risk_factors'].append("Facial analysis shows elevated stress")
        
        return findings
    
    def generate_assessment_summary(self) -> str:
        """Generate a comprehensive assessment summary for AI processing"""
        overall_score = self.calculate_overall_score()
        findings = self.extract_key_findings()
        
        summary = f"""
COMPREHENSIVE MENTAL HEALTH ASSESSMENT SUMMARY

Overall Assessment:
- Overall Score: {overall_score.get('overall_percentage', 0):.1f}%
- Stress Level: {overall_score.get('stress_level', 'Unknown')}
- Risk Category: {overall_score.get('risk_category', 'Unknown')}

Component Scores:
"""
        
        for component, score in overall_score.get('component_scores', {}).items():
            summary += f"- {component.replace('_', ' ').title()}: {score*100:.1f}%\n"
        
        summary += f"""
Key Findings:
Risk Factors Identified:
"""
        for risk in findings['risk_factors']:
            summary += f"- {risk}\n"
        
        summary += f"""
Positive Factors:
"""
        for positive in findings['positive_factors']:
            summary += f"- {positive}\n"
        
        summary += f"""
Voice Analysis: {findings['voice_indicators'].get('stress_level', 'Not available')}
Facial Analysis: {findings['facial_indicators'].get('stress_level', 'Not available')}

Assessment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return summary.strip()
