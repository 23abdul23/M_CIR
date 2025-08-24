"""
Army Mental Health Advisor
Specialized recommendation system for military personnel based on army lifestyle, 
operational requirements, and military mental health best practices.
"""

import logging
from typing import Dict, List, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ArmyMentalHealthAdvisor:
    """
    Specialized mental health advisor for army personnel
    Based on military mental health research and army lifestyle requirements
    """
    
    def __init__(self):
        self.military_ranks = {
            'enlisted': ['private', 'lance corporal', 'corporal', 'sergeant', 'staff sergeant'],
            'nco': ['sergeant first class', 'master sergeant', 'first sergeant', 'sergeant major'],
            'officer': ['second lieutenant', 'first lieutenant', 'captain', 'major', 'colonel']
        }
        
        self.operational_contexts = {
            'combat': ['frontline', 'combat zone', 'active duty', 'deployment'],
            'training': ['basic training', 'advanced training', 'exercises', 'simulation'],
            'garrison': ['base duty', 'administrative', 'maintenance', 'support'],
            'transition': ['returning', 'reintegration', 'leave', 'discharge preparation']
        }
        
        # Army-specific stress factors and interventions
        self.army_stress_factors = {
            'operational_stress': {
                'indicators': ['combat exposure', 'deployment stress', 'mission pressure'],
                'interventions': ['tactical breathing', 'unit cohesion activities', 'mission debriefing']
            },
            'leadership_stress': {
                'indicators': ['command responsibility', 'decision fatigue', 'subordinate welfare'],
                'interventions': ['leadership counseling', 'peer support groups', 'command consultation']
            },
            'separation_stress': {
                'indicators': ['family separation', 'homesickness', 'relationship strain'],
                'interventions': ['family communication programs', 'chaplain services', 'support groups']
            },
            'transition_stress': {
                'indicators': ['role changes', 'civilian adjustment', 'career uncertainty'],
                'interventions': ['transition counseling', 'career guidance', 'skill translation programs']
            }
        }

    def generate_army_recommendations(self, assessment_data: Dict) -> List[str]:
        """
        Generate army-specific mental health recommendations
        
        Args:
            assessment_data: Combined assessment results including:
                - overall_score: float (0-100)
                - mental_state: str (normal, mild, moderate, severe)
                - user_profile: dict (rank, unit, role, deployment_status)
                - assessment_results: dict (questionnaire, voice, facial)
                
        Returns:
            List of army-specific recommendations
        """
        try:
            recommendations = []
            
            # Extract key information
            overall_score = assessment_data.get('overall_score', 50)
            mental_state = assessment_data.get('mental_state', 'normal')
            user_profile = assessment_data.get('user_profile', {})
            
            # Determine rank category
            rank_category = self._determine_rank_category(user_profile.get('rank', ''))
            
            # Determine operational context
            operational_context = self._determine_operational_context(user_profile)
            
            # Generate recommendations based on severity
            if mental_state == 'severe' or overall_score < 30:
                recommendations.extend(self._get_critical_army_recommendations(rank_category, operational_context))
            elif mental_state == 'moderate' or overall_score < 50:
                recommendations.extend(self._get_moderate_army_recommendations(rank_category, operational_context))
            elif mental_state == 'mild' or overall_score < 70:
                recommendations.extend(self._get_mild_army_recommendations(rank_category, operational_context))
            else:
                recommendations.extend(self._get_maintenance_army_recommendations(rank_category, operational_context))
            
            # Add specific recommendations based on assessment components
            recommendations.extend(self._get_component_specific_recommendations(assessment_data))
            
            # Add rank-specific leadership recommendations
            if rank_category in ['nco', 'officer']:
                recommendations.extend(self._get_leadership_recommendations(mental_state, rank_category))
            
            return recommendations[:8]  # Return top 8 recommendations
            
        except Exception as e:
            logger.error(f"Error generating army recommendations: {e}")
            return self._get_default_army_recommendations()

    def _determine_rank_category(self, rank: str) -> str:
        """Determine rank category from rank string"""
        rank_lower = rank.lower()
        for category, ranks in self.military_ranks.items():
            if any(r in rank_lower for r in ranks):
                return category
        return 'enlisted'  # Default

    def _determine_operational_context(self, user_profile: Dict) -> str:
        """Determine operational context from user profile"""
        deployment_status = user_profile.get('deployment_status', '').lower()
        unit_type = user_profile.get('unit', '').lower()
        role = user_profile.get('role', '').lower()
        
        # Check for combat context
        if any(term in deployment_status for term in ['deployed', 'combat', 'frontline']):
            return 'combat'
        
        # Check for training context
        if any(term in role for term in ['training', 'instructor', 'student']):
            return 'training'
        
        # Check for transition context
        if any(term in deployment_status for term in ['returning', 'leave', 'discharge']):
            return 'transition'
        
        return 'garrison'  # Default

    def _get_critical_army_recommendations(self, rank_category: str, context: str) -> List[str]:
        """Critical intervention recommendations for severe cases"""
        recommendations = [
            "🚨 Immediate consultation with unit mental health officer or chaplain required",
            "📞 Contact Military Family Life Counselor (MFLC) for immediate support",
            "🏥 Schedule appointment with behavioral health specialist within 24-48 hours",
            "👥 Inform trusted NCO or officer about current mental health concerns",
            "🛡️ Utilize Army's Comprehensive Soldier Fitness (CSF) resources immediately"
        ]
        
        if context == 'combat':
            recommendations.extend([
                "⚡ Request temporary duty modification if operationally feasible",
                "🤝 Engage battle buddy system for continuous peer support"
            ])
        
        return recommendations

    def _get_moderate_army_recommendations(self, rank_category: str, context: str) -> List[str]:
        """Moderate intervention recommendations"""
        recommendations = [
            "📋 Schedule regular check-ins with unit mental health personnel",
            "🧘 Practice Army's tactical breathing techniques during high-stress situations",
            "💪 Maintain physical fitness routine as mental health foundation",
            "👨‍⚕️ Consider counseling through Military Family Life Counselor (MFLC)",
            "📚 Utilize Master Resilience Training (MRT) techniques learned in unit training"
        ]
        
        if rank_category in ['nco', 'officer']:
            recommendations.extend([
                "👥 Delegate responsibilities appropriately to reduce command stress",
                "🎯 Focus on unit morale and welfare programs to build collective resilience"
            ])
        
        if context == 'garrison':
            recommendations.extend([
                "🏃‍♂️ Participate in unit physical training and morale events",
                "📱 Use Army's mobile mental health apps for daily wellness tracking"
            ])
        
        return recommendations

    def _get_mild_army_recommendations(self, rank_category: str, context: str) -> List[str]:
        """Mild intervention recommendations for early prevention"""
        recommendations = [
            "🎯 Maintain regular sleep schedule aligned with military duties",
            "🤝 Strengthen battle buddy relationships and peer support networks",
            "📖 Continue professional military education to build confidence",
            "🏋️ Use unit gym facilities for stress relief and physical wellness",
            "📞 Stay connected with family through available communication channels"
        ]
        
        if context == 'training':
            recommendations.extend([
                "📚 Focus on skill development to build competence and confidence",
                "👨‍🏫 Seek mentorship from experienced NCOs or officers"
            ])
        
        return recommendations

    def _get_maintenance_army_recommendations(self, rank_category: str, context: str) -> List[str]:
        """Maintenance recommendations for good mental health"""
        recommendations = [
            "✅ Continue current positive mental health practices",
            "🎖️ Share successful coping strategies with fellow soldiers",
            "📈 Set professional development goals within military career path",
            "🏆 Participate in unit recognition and award programs",
            "🌟 Consider mentoring junior soldiers to build unit cohesion"
        ]
        
        if rank_category in ['nco', 'officer']:
            recommendations.extend([
                "👑 Model positive mental health behaviors for subordinates",
                "📊 Implement unit-level mental health awareness programs"
            ])
        
        return recommendations

    def _get_component_specific_recommendations(self, assessment_data: Dict) -> List[str]:
        """Generate recommendations based on specific assessment components"""
        recommendations = []
        assessment_results = assessment_data.get('assessment_results', {})
        
        # Voice assessment specific
        voice_results = assessment_results.get('voice', {})
        if voice_results.get('stress_level') == 'high':
            recommendations.append("🗣️ Practice clear military communication techniques to reduce verbal stress indicators")
        
        # Facial assessment specific
        facial_results = assessment_results.get('facial', {})
        if facial_results.get('primary_emotion') in ['angry', 'sad']:
            recommendations.append("😌 Use tactical breathing and mindfulness during duty hours to manage emotional responses")
        
        # Questionnaire specific
        questionnaire_results = assessment_results.get('questionnaire', {})
        if questionnaire_results.get('sleep_issues', False):
            recommendations.append("😴 Maintain military sleep hygiene standards: 7-8 hours, consistent schedule")
        
        return recommendations

    def _get_leadership_recommendations(self, mental_state: str, rank_category: str) -> List[str]:
        """Specific recommendations for military leaders"""
        recommendations = []
        
        if rank_category == 'nco':
            recommendations.extend([
                "👨‍💼 Utilize NCO support channels and professional development programs",
                "⚖️ Balance soldier welfare responsibilities with personal mental health needs"
            ])
        
        elif rank_category == 'officer':
            recommendations.extend([
                "🎖️ Access officer-specific mental health resources and command consultation",
                "📋 Implement unit-level mental health initiatives while managing personal wellness"
            ])
        
        return recommendations

    def _get_default_army_recommendations(self) -> List[str]:
        """Default recommendations when system fails"""
        return [
            "🏥 Contact unit mental health officer for professional assessment",
            "📞 Call Military Crisis Line: 1-800-273-8255",
            "👥 Reach out to trusted battle buddy or NCO for support",
            "🛡️ Utilize Army Comprehensive Soldier Fitness resources",
            "📚 Review Army mental health policies and available resources"
        ]

    def get_army_mental_health_resources(self) -> Dict[str, List[str]]:
        """Get comprehensive list of army mental health resources"""
        return {
            'immediate_help': [
                "Military Crisis Line: 1-800-273-8255",
                "Unit Mental Health Officer",
                "Chaplain Services",
                "Military Family Life Counselor (MFLC)"
            ],
            'ongoing_support': [
                "Behavioral Health Specialist",
                "Master Resilience Training (MRT)",
                "Comprehensive Soldier Fitness (CSF)",
                "Army Community Service Center"
            ],
            'peer_support': [
                "Battle Buddy System",
                "Unit Support Groups",
                "Veteran Support Networks",
                "NCO/Officer Mentorship Programs"
            ],
            'family_support': [
                "Family Readiness Groups",
                "Military Family Life Counselor",
                "Chaplain Family Programs",
                "Base Family Support Services"
            ]
        }
