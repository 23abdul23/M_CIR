"""
Bilingual Questionnaire Management System for Admin
Allows admins to create, edit, and manage questionnaires in both Hindi and English
"""
import streamlit as st
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from database.database import get_db
    from database.crud import *
    from utils.language_support import get_bilingual_text, get_language
except ImportError as e:
    print(f"Import error in bilingual questionnaire manager: {e}")

class BilingualQuestionnaireManager:
    """
    Comprehensive bilingual questionnaire management for admins
    """
    
    def __init__(self):
        self.db = next(get_db())
    
    def render_questionnaire_management(self):
        """Render the main questionnaire management interface"""
        
        current_language = get_language()
        
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #1f4e79, #2d5aa0); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: white; text-align: center; margin: 0;">
                {get_bilingual_text('📋 प्रश्नावली प्रबंधन', '📋 Questionnaire Management')}
            </h2>
            <p style="color: #e0e0e0; text-align: center; margin: 10px 0 0 0;">
                {get_bilingual_text('द्विभाषी प्रश्नावली निर्माण और संपादन', 'Bilingual Questionnaire Creation & Editing')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            get_bilingual_text("📝 नई प्रश्नावली", "📝 Create New"),
            get_bilingual_text("✏️ संपादित करें", "✏️ Edit Existing"),
            get_bilingual_text("👀 पूर्वावलोकन", "👀 Preview"),
            get_bilingual_text("📊 प्रबंधन", "📊 Manage")
        ])
        
        with tab1:
            self.render_create_questionnaire()
        
        with tab2:
            self.render_edit_questionnaire()
        
        with tab3:
            self.render_preview_questionnaire()
        
        with tab4:
            self.render_manage_questionnaires()
    
    def render_create_questionnaire(self):
        """Render questionnaire creation interface"""
        
        st.subheader(get_bilingual_text("नई प्रश्नावली बनाएं", "Create New Questionnaire"))
        
        # Basic questionnaire information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{get_bilingual_text('हिंदी में जानकारी', 'Hindi Information')}**")
            title_hi = st.text_input(
                get_bilingual_text("शीर्षक (हिंदी)", "Title (Hindi)"),
                key="title_hi"
            )
            description_hi = st.text_area(
                get_bilingual_text("विवरण (हिंदी)", "Description (Hindi)"),
                height=100,
                key="desc_hi"
            )
            instructions_hi = st.text_area(
                get_bilingual_text("निर्देश (हिंदी)", "Instructions (Hindi)"),
                height=80,
                key="inst_hi"
            )
        
        with col2:
            st.markdown(f"**{get_bilingual_text('अंग्रेजी में जानकारी', 'English Information')}**")
            title_en = st.text_input(
                get_bilingual_text("शीर्षक (अंग्रेजी)", "Title (English)"),
                key="title_en"
            )
            description_en = st.text_area(
                get_bilingual_text("विवरण (अंग्रेजी)", "Description (English)"),
                height=100,
                key="desc_en"
            )
            instructions_en = st.text_area(
                get_bilingual_text("निर्देश (अंग्रेजी)", "Instructions (English)"),
                height=80,
                key="inst_en"
            )
        
        # Additional settings
        col1, col2, col3 = st.columns(3)
        
        with col1:
            time_limit = st.number_input(
                get_bilingual_text("समय सीमा (मिनट)", "Time Limit (minutes)"),
                min_value=1,
                max_value=60,
                value=15
            )
        
        with col2:
            category = st.selectbox(
                get_bilingual_text("श्रेणी", "Category"),
                [
                    get_bilingual_text("अवसाद", "Depression"),
                    get_bilingual_text("चिंता", "Anxiety"),
                    get_bilingual_text("तनाव", "Stress"),
                    get_bilingual_text("सामान्य", "General"),
                    get_bilingual_text("अन्य", "Other")
                ]
            )
        
        with col3:
            difficulty = st.selectbox(
                get_bilingual_text("कठिनाई स्तर", "Difficulty Level"),
                [
                    get_bilingual_text("आसान", "Easy"),
                    get_bilingual_text("मध्यम", "Medium"),
                    get_bilingual_text("कठिन", "Hard")
                ]
            )
        
        # Questions section
        st.markdown("---")
        st.subheader(get_bilingual_text("प्रश्न जोड़ें", "Add Questions"))
        
        # Initialize questions in session state
        if "questionnaire_questions" not in st.session_state:
            st.session_state.questionnaire_questions = []
        
        # Add question interface
        with st.expander(get_bilingual_text("नया प्रश्न जोड़ें", "Add New Question"), expanded=True):
            self.render_add_question_interface()
        
        # Display existing questions
        if st.session_state.questionnaire_questions:
            st.subheader(get_bilingual_text("जोड़े गए प्रश्न", "Added Questions"))
            self.display_questions_list()
        
        # Save questionnaire
        st.markdown("---")
        if st.button(get_bilingual_text("प्रश्नावली सहेजें", "Save Questionnaire"), type="primary"):
            if self.validate_questionnaire_data(title_hi, title_en, description_hi, description_en):
                questionnaire_data = {
                    "title": {"hindi": title_hi, "english": title_en},
                    "description": {"hindi": description_hi, "english": description_en},
                    "instructions": {"hindi": instructions_hi, "english": instructions_en},
                    "time_limit": time_limit,
                    "category": category,
                    "difficulty": difficulty,
                    "questions": st.session_state.questionnaire_questions
                }
                
                if self.save_questionnaire(questionnaire_data):
                    st.success(get_bilingual_text("प्रश्नावली सफलतापूर्वक सहेजी गई", "Questionnaire saved successfully"))
                    # Clear the form
                    st.session_state.questionnaire_questions = []
                    st.rerun()
    
    def render_add_question_interface(self):
        """Render interface to add a new question"""
        
        col1, col2 = st.columns(2)
        
        with col1:
            question_hi = st.text_area(
                get_bilingual_text("प्रश्न (हिंदी)", "Question (Hindi)"),
                key="new_question_hi"
            )
        
        with col2:
            question_en = st.text_area(
                get_bilingual_text("प्रश्न (अंग्रेजी)", "Question (English)"),
                key="new_question_en"
            )
        
        # Question type
        question_type = st.selectbox(
            get_bilingual_text("प्रश्न प्रकार", "Question Type"),
            [
                get_bilingual_text("स्केल (0-3)", "Scale (0-3)"),
                get_bilingual_text("हाँ/नहीं", "Yes/No"),
                get_bilingual_text("बहुविकल्पीय", "Multiple Choice"),
                get_bilingual_text("टेक्स्ट", "Text")
            ]
        )
        
        # Options based on question type
        options_hi = []
        options_en = []
        
        if "स्केल" in question_type or "Scale" in question_type:
            # Default scale options
            options_hi = ["बिल्कुल नहीं", "कई दिन", "आधे से अधिक दिन", "लगभग हर दिन"]
            options_en = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
            
        elif "हाँ/नहीं" in question_type or "Yes/No" in question_type:
            options_hi = ["हाँ", "नहीं"]
            options_en = ["Yes", "No"]
            
        elif "बहुविकल्पीय" in question_type or "Multiple Choice" in question_type:
            st.markdown(f"**{get_bilingual_text('विकल्प जोड़ें', 'Add Options')}**")
            
            num_options = st.number_input(
                get_bilingual_text("विकल्पों की संख्या", "Number of Options"),
                min_value=2,
                max_value=6,
                value=4
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**{get_bilingual_text('हिंदी विकल्प', 'Hindi Options')}**")
                for i in range(num_options):
                    option = st.text_input(f"विकल्प {i+1}", key=f"option_hi_{i}")
                    if option:
                        if len(options_hi) <= i:
                            options_hi.append(option)
                        else:
                            options_hi[i] = option
            
            with col2:
                st.markdown(f"**{get_bilingual_text('अंग्रेजी विकल्प', 'English Options')}**")
                for i in range(num_options):
                    option = st.text_input(f"Option {i+1}", key=f"option_en_{i}")
                    if option:
                        if len(options_en) <= i:
                            options_en.append(option)
                        else:
                            options_en[i] = option
        
        # Scoring (for scale questions)
        scores = []
        if "स्केल" in question_type or "Scale" in question_type:
            scores = [0, 1, 2, 3]
        elif "हाँ/नहीं" in question_type or "Yes/No" in question_type:
            scores = [1, 0]  # Yes=1, No=0
        else:
            # Custom scoring
            st.markdown(f"**{get_bilingual_text('स्कोरिंग', 'Scoring')}**")
            score_input = st.text_input(
                get_bilingual_text("स्कोर (कॉमा से अलग करें)", "Scores (comma separated)"),
                placeholder="0,1,2,3"
            )
            if score_input:
                try:
                    scores = [int(x.strip()) for x in score_input.split(",")]
                except:
                    st.error(get_bilingual_text("अवैध स्कोर प्रारूप", "Invalid score format"))
        
        # Add question button
        if st.button(get_bilingual_text("प्रश्न जोड़ें", "Add Question")):
            if question_hi and question_en and options_hi and options_en:
                new_question = {
                    "id": len(st.session_state.questionnaire_questions) + 1,
                    "text": {"hindi": question_hi, "english": question_en},
                    "type": "scale" if "स्केल" in question_type or "Scale" in question_type else "multiple_choice",
                    "options": {"hindi": options_hi, "english": options_en},
                    "scores": scores if scores else list(range(len(options_hi)))
                }
                
                st.session_state.questionnaire_questions.append(new_question)
                st.success(get_bilingual_text("प्रश्न जोड़ा गया", "Question added"))
                st.rerun()
            else:
                st.error(get_bilingual_text("कृपया सभी फ़ील्ड भरें", "Please fill all fields"))
    
    def display_questions_list(self):
        """Display list of added questions"""
        
        for i, question in enumerate(st.session_state.questionnaire_questions):
            with st.expander(f"{get_bilingual_text('प्रश्न', 'Question')} {i+1}: {question['text']['hindi'][:50]}..."):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**{get_bilingual_text('हिंदी', 'Hindi')}:** {question['text']['hindi']}")
                    st.markdown(f"**{get_bilingual_text('विकल्प', 'Options')}:** {', '.join(question['options']['hindi'])}")
                
                with col2:
                    st.markdown(f"**{get_bilingual_text('अंग्रेजी', 'English')}:** {question['text']['english']}")
                    st.markdown(f"**{get_bilingual_text('विकल्प', 'Options')}:** {', '.join(question['options']['english'])}")
                
                st.markdown(f"**{get_bilingual_text('स्कोर', 'Scores')}:** {question['scores']}")
                
                if st.button(get_bilingual_text("हटाएं", "Remove"), key=f"remove_{i}"):
                    st.session_state.questionnaire_questions.pop(i)
                    st.rerun()
    
    def validate_questionnaire_data(self, title_hi, title_en, desc_hi, desc_en):
        """Validate questionnaire data"""
        if not title_hi or not title_en:
            st.error(get_bilingual_text("शीर्षक आवश्यक है", "Title is required"))
            return False
        
        if not desc_hi or not desc_en:
            st.error(get_bilingual_text("विवरण आवश्यक है", "Description is required"))
            return False
        
        if not st.session_state.questionnaire_questions:
            st.error(get_bilingual_text("कम से कम एक प्रश्न जोड़ें", "Add at least one question"))
            return False
        
        return True
    
    def save_questionnaire(self, questionnaire_data):
        """Save questionnaire to database"""
        try:
            # Create questionnaire record
            questionnaire = create_questionnaire(
                db=self.db,
                title=questionnaire_data["title"]["english"],  # Use English as primary
                description=questionnaire_data["description"]["english"],
                instructions=questionnaire_data["instructions"]["english"],
                time_limit_minutes=questionnaire_data["time_limit"],
                created_by=1  # Admin user ID
            )
            
            # Save questions
            for question_data in questionnaire_data["questions"]:
                create_question(
                    db=self.db,
                    questionnaire_id=questionnaire.id,
                    text=question_data["text"]["english"],  # Use English as primary
                    question_type=question_data["type"],
                    options=json.dumps(question_data["options"]),  # Store both languages
                    correct_answer=None,
                    points=max(question_data["scores"]) if question_data["scores"] else 1
                )
            
            # Save bilingual data as JSON (for future use)
            # This could be stored in a separate table or as metadata
            
            return True
            
        except Exception as e:
            st.error(f"{get_bilingual_text('सहेजने में त्रुटि', 'Error saving')}: {str(e)}")
            return False
    
    def render_edit_questionnaire(self):
        """Render questionnaire editing interface"""

        st.subheader(get_bilingual_text("प्रश्नावली संपादित करें", "Edit Questionnaire"))

        # Get list of existing questionnaires
        questionnaires = self.get_questionnaire_list()

        if not questionnaires:
            st.warning(get_bilingual_text(
                "कोई प्रश्नावली उपलब्ध नहीं है। पहले एक प्रश्नावली बनाएं।",
                "No questionnaires available. Please create a questionnaire first."
            ))
            return

        # Select questionnaire to edit
        selected_questionnaire = st.selectbox(
            get_bilingual_text("संपादित करने के लिए प्रश्नावली चुनें:", "Select questionnaire to edit:"),
            options=questionnaires,
            format_func=lambda x: x["title"]
        )

        if selected_questionnaire:
            # Get full questionnaire details
            questionnaire_details = self.get_questionnaire(selected_questionnaire["id"])

            if questionnaire_details:
                # Edit basic information
                st.markdown("### " + get_bilingual_text("बुनियादी जानकारी", "Basic Information"))

                col1, col2 = st.columns(2)

                with col1:
                    new_title = st.text_input(
                        get_bilingual_text("शीर्षक", "Title"),
                        value=questionnaire_details["title"]
                    )

                with col2:
                    new_description = st.text_area(
                        get_bilingual_text("विवरण", "Description"),
                        value=questionnaire_details["description"]
                    )

                new_instructions = st.text_area(
                    get_bilingual_text("निर्देश", "Instructions"),
                    value=questionnaire_details.get("instructions", "")
                )

                new_time_limit = st.number_input(
                    get_bilingual_text("समय सीमा (मिनट)", "Time Limit (minutes)"),
                    min_value=1,
                    max_value=120,
                    value=questionnaire_details.get("time_limit", 30)
                )

                # Display existing questions
                st.markdown("### " + get_bilingual_text("प्रश्न", "Questions"))

                if questionnaire_details.get("questions"):
                    for i, question in enumerate(questionnaire_details["questions"]):
                        with st.expander(f"{get_bilingual_text('प्रश्न', 'Question')} {i+1}: {question['text'][:50]}..."):
                            st.text(f"{get_bilingual_text('प्रकार', 'Type')}: {question['type']}")
                            st.text(f"{get_bilingual_text('विकल्प', 'Options')}: {', '.join(question['options'])}")

                # Update button
                if st.button(get_bilingual_text("अपडेट करें", "Update Questionnaire")):
                    if self.update_questionnaire(
                        selected_questionnaire["id"],
                        new_title,
                        new_description,
                        new_instructions,
                        new_time_limit
                    ):
                        st.success(get_bilingual_text(
                            "प्रश्नावली सफलतापूर्वक अपडेट की गई",
                            "Questionnaire updated successfully"
                        ))
                        st.rerun()
            else:
                st.error(get_bilingual_text(
                    "प्रश्नावली विवरण लोड नहीं हो सका",
                    "Could not load questionnaire details"
                ))
    
    def render_preview_questionnaire(self):
        """Render questionnaire preview"""

        st.subheader(get_bilingual_text("प्रश्नावली पूर्वावलोकन", "Questionnaire Preview"))

        # Get list of questionnaires
        questionnaires = self.get_questionnaire_list()

        if not questionnaires:
            st.warning(get_bilingual_text(
                "कोई प्रश्नावली उपलब्ध नहीं है।",
                "No questionnaires available."
            ))
            return

        # Select questionnaire to preview
        selected_questionnaire = st.selectbox(
            get_bilingual_text("पूर्वावलोकन के लिए प्रश्नावली चुनें:", "Select questionnaire to preview:"),
            options=questionnaires,
            format_func=lambda x: x["title"]
        )

        if selected_questionnaire:
            questionnaire_details = self.get_questionnaire(selected_questionnaire["id"])

            if questionnaire_details:
                # Display questionnaire header
                st.markdown(f"""
                <div style="background: linear-gradient(90deg, #28a745, #20c997); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    <h3 style="color: white; margin: 0;">{questionnaire_details['title']}</h3>
                    <p style="color: #e0e0e0; margin: 10px 0 0 0;">{questionnaire_details['description']}</p>
                </div>
                """, unsafe_allow_html=True)

                # Instructions
                if questionnaire_details.get('instructions'):
                    st.info(f"**{get_bilingual_text('निर्देश', 'Instructions')}:** {questionnaire_details['instructions']}")

                # Time limit
                st.info(f"**{get_bilingual_text('समय सीमा', 'Time Limit')}:** {questionnaire_details.get('time_limit', 30)} {get_bilingual_text('मिनट', 'minutes')}")

                # Display questions
                st.markdown("### " + get_bilingual_text("प्रश्न", "Questions"))

                for i, question in enumerate(questionnaire_details.get("questions", [])):
                    st.markdown(f"**{i+1}. {question['text']}**")

                    if question['options']:
                        for j, option in enumerate(question['options']):
                            st.markdown(f"   {chr(97+j)}) {option}")

                    st.markdown("---")
    
    def render_manage_questionnaires(self):
        """Render questionnaire management interface"""

        st.subheader(get_bilingual_text("प्रश्नावली प्रबंधन", "Manage Questionnaires"))

        # Get list of questionnaires
        questionnaires = self.get_questionnaire_list()

        if not questionnaires:
            st.warning(get_bilingual_text(
                "कोई प्रश्नावली उपलब्ध नहीं है।",
                "No questionnaires available."
            ))
            return

        # Display questionnaires in a table format
        st.markdown("### " + get_bilingual_text("सभी प्रश्नावली", "All Questionnaires"))

        for questionnaire in questionnaires:
            with st.expander(f"📋 {questionnaire['title']}"):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"**{get_bilingual_text('विवरण', 'Description')}:** {questionnaire['description']}")

                    # Get full details
                    details = self.get_questionnaire(questionnaire['id'])
                    if details:
                        st.markdown(f"**{get_bilingual_text('प्रश्नों की संख्या', 'Number of Questions')}:** {len(details.get('questions', []))}")
                        st.markdown(f"**{get_bilingual_text('समय सीमा', 'Time Limit')}:** {details.get('time_limit', 30)} {get_bilingual_text('मिनट', 'minutes')}")

                with col2:
                    if st.button(get_bilingual_text("सक्रिय/निष्क्रिय", "Toggle Active"), key=f"toggle_{questionnaire['id']}"):
                        self.toggle_questionnaire_status(questionnaire['id'])
                        st.rerun()

                with col3:
                    if st.button(get_bilingual_text("हटाएं", "Delete"), key=f"delete_{questionnaire['id']}", type="secondary"):
                        if st.session_state.get(f"confirm_delete_{questionnaire['id']}", False):
                            if self.delete_questionnaire(questionnaire['id']):
                                st.success(get_bilingual_text("प्रश्नावली हटा दी गई", "Questionnaire deleted"))
                                st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{questionnaire['id']}"] = True
                            st.warning(get_bilingual_text("फिर से क्लिक करें पुष्टि के लिए", "Click again to confirm"))

        # Statistics
        st.markdown("---")
        st.markdown("### " + get_bilingual_text("आंकड़े", "Statistics"))

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                get_bilingual_text("कुल प्रश्नावली", "Total Questionnaires"),
                len(questionnaires)
            )

        with col2:
            active_count = len([q for q in questionnaires if self.is_questionnaire_active(q['id'])])
            st.metric(
                get_bilingual_text("सक्रिय प्रश्नावली", "Active Questionnaires"),
                active_count
            )

        with col3:
            total_questions = 0
            for q in questionnaires:
                details = self.get_questionnaire(q['id'])
                if details and details.get('questions'):
                    total_questions += len(details['questions'])
            st.metric(
                get_bilingual_text("कुल प्रश्न", "Total Questions"),
                total_questions
            )

    def get_questionnaire_list(self, language=None):
        """Get list of available questionnaires"""
        try:
            questionnaires = self.db.query(Questionnaire).filter(
                Questionnaire.is_active == True
            ).all()
            # Convert to dictionary format expected by the UI
            questionnaire_list = []
            for q in questionnaires:
                questionnaire_list.append({
                    "id": q.id,
                    "title": q.title,
                    "description": q.description
                })
            return questionnaire_list
        except Exception as e:
            st.error(f"Error loading questionnaires: {e}")
            return []

    def get_questionnaire(self, questionnaire_id, language=None):
        """Get questionnaire details by ID"""
        try:
            questionnaire = self.db.query(Questionnaire).filter(
                Questionnaire.id == questionnaire_id
            ).first()

            if not questionnaire:
                return None

            # Get questions for this questionnaire
            questions = self.db.query(Question).filter(
                Question.questionnaire_id == questionnaire_id
            ).all()

            return {
                "id": questionnaire.id,
                "title": questionnaire.title,
                "description": questionnaire.description,
                "instructions": getattr(questionnaire, 'instructions', ''),
                "time_limit": getattr(questionnaire, 'time_limit', 30),
                "questions": [
                    {
                        "id": q.id,
                        "text": q.question_text,
                        "type": q.question_type,
                        "options": q.options if isinstance(q.options, list) else (q.options.split(',') if q.options else [])
                    } for q in questions
                ]
            }
        except Exception as e:
            st.error(f"Error loading questionnaire details: {e}")
            return None

    def update_questionnaire(self, questionnaire_id, title, description, instructions, time_limit):
        """Update questionnaire details"""
        try:
            questionnaire = self.db.query(Questionnaire).filter(
                Questionnaire.id == questionnaire_id
            ).first()

            if questionnaire:
                questionnaire.title = title
                questionnaire.description = description
                questionnaire.instructions = instructions
                questionnaire.time_limit_minutes = time_limit
                self.db.commit()
                return True
            return False
        except Exception as e:
            st.error(f"Error updating questionnaire: {e}")
            return False

    def toggle_questionnaire_status(self, questionnaire_id):
        """Toggle questionnaire active status"""
        try:
            questionnaire = self.db.query(Questionnaire).filter(
                Questionnaire.id == questionnaire_id
            ).first()

            if questionnaire:
                questionnaire.is_active = not questionnaire.is_active
                self.db.commit()
                return True
            return False
        except Exception as e:
            st.error(f"Error toggling questionnaire status: {e}")
            return False

    def delete_questionnaire(self, questionnaire_id):
        """Delete questionnaire and its questions"""
        try:
            # Delete questions first
            self.db.query(Question).filter(
                Question.questionnaire_id == questionnaire_id
            ).delete()

            # Delete questionnaire
            self.db.query(Questionnaire).filter(
                Questionnaire.id == questionnaire_id
            ).delete()

            self.db.commit()
            return True
        except Exception as e:
            st.error(f"Error deleting questionnaire: {e}")
            return False

    def is_questionnaire_active(self, questionnaire_id):
        """Check if questionnaire is active"""
        try:
            questionnaire = self.db.query(Questionnaire).filter(
                Questionnaire.id == questionnaire_id
            ).first()
            return questionnaire.is_active if questionnaire else False
        except:
            return False

# Global instance
bilingual_questionnaire_manager = BilingualQuestionnaireManager()
