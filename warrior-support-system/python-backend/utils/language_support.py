"""
Bilingual Language Support for Army Mental Health Assessment System
"""
import streamlit as st
from typing import Dict, Any

# Language translations
TRANSLATIONS = {
    "en": {
        # Main headers
        "app_title": "Army Mental Health Assessment System",
        "login_header": "Login",
        "admin_dashboard": "Admin Dashboard",
        "user_dashboard": "User Dashboard",
        
        # Login page
        "username": "Username",
        "password": "Password",
        "login_button": "Login",
        "welcome_message": "Welcome, {}!",
        "invalid_credentials": "Invalid username or password",
        "fill_all_fields": "Please fill all fields",
        "default_admin_info": "Default Admin Login:",
        
        # Navigation
        "questionnaire_management": "Questionnaire Management",
        "user_management": "User Management",
        "reports": "Reports",
        "system_settings": "System Settings",
        "take_assessment": "Take Assessment",
        "voice_assessment": "Voice Assessment",
        "facial_analysis": "Facial Analysis",
        "my_results": "My Results",
        "logout": "Logout",
        
        # Questionnaire Management
        "load_sample_questionnaires": "Load Sample Questionnaires",
        "refresh_questionnaire_list": "Refresh Questionnaire List",
        "questionnaires_loaded": "{} questionnaires loaded successfully",
        "questionnaires_failed": "{} questionnaires failed to load",
        "no_questionnaires": "No questionnaires available. Please load sample questionnaires.",
        "select_questionnaire_details": "Select questionnaire to view details:",
        "description": "Description",
        "assessment_instructions": "Instructions",
        "time_limit": "Time Limit",
        "minutes": "minutes",
        "start_assessment": "Start Assessment",
        "question": "Question",
        "select_answer": "Select your answer:",
        "previous_question": "Previous Question",
        "next_question": "Next Question",
        "assessment_complete": "Assessment Complete!",
        "view_results": "View Results",
        "assessment_results": "Assessment Results",
        "total_score": "Total Score",
        "percentage": "Percentage",
        "risk_level": "Risk Level",
        "assessment": "Assessment",
        "status": "Status",
        "score": "Score",
        "mental_state": "Mental State",
        "completed": "Completed",
        "suggestions": "Suggestions",
        "results_saved": "Results saved successfully",
        "error_saving_results": "Error saving results",
        "please_try_again": "Please try again",
        "error_loading_results": "Error loading results",
        "no_assessment_results": "No assessment results available",
        "complete_assessment_first": "Please complete an assessment first",
        "suggestions_not_available": "Suggestions not available",
        "voice_assessment": "Voice Assessment",
        "record_voice": "Record your voice",
        "analyze": "Analyze",
        "analysis_result": "Analysis Result",
        "sentiment": "Sentiment",
        
        # User Management
        "create_new_user": "Create New User",
        "full_name": "Full Name",
        "email": "Email",
        "role": "Role",
        "army_id": "Army ID",
        "rank": "Rank",
        "unit": "Unit",
        "create_user": "Create User",
        "user_created": "User '{}' created successfully",
        "user_creation_error": "Error creating user: {}",
        "required_fields": "Please fill required fields",
        
        # Reports
        "reports_analysis": "Reports and Analysis",
        "total_assessments": "Total Assessments",
        "completed_assessments": "Completed Assessments",
        "completion_rate": "Completion Rate",
        "mental_state_distribution": "Mental State Distribution",
        
        # Assessment
        "assessment_instructions": "Instructions",
        "time_limit": "Time Limit",
        "minutes": "minutes",
        "start_assessment": "Start Assessment",
        "question": "Question",
        "select_answer": "Select your answer:",
        "previous_question": "Previous Question",
        "next_question": "Next Question",
        "assessment_complete": "Assessment Complete!",
        "view_results": "View Results",
        "assessment_results": "Assessment Results",
        "total_score": "Total Score",
        "percentage": "Percentage",
        "risk_level": "Risk Level",
        "results_saved": "Results saved",
        "result_save_error": "Error saving results: {}",
        "start_new_assessment": "Start New Assessment",
        
        # Voice Assessment
        "voice_instructions": "Instructions:",
        "voice_instruction_1": "1. Answer the question below in Hindi",
        "voice_instruction_2": "2. Press record button to record your answer",
        "voice_instruction_3": "3. Or type in the text box",
        "select_question": "Select Question:",
        "type_response": "Type your response here:",
        "or_voice_input": "Or provide voice input:",
        "upload_audio": "Upload Audio File",
        "analyze_response": "Analyze Response",
        "audio_processing": "Processing audio...",
        "audio_processed": "Audio processed successfully!",
        "transcribed_text": "Transcribed Text:",
        "audio_processing_error": "Audio processing error: {}",
        
        # Analysis Results
        "sentiment_analysis": "Sentiment Analysis",
        "sentiment": "Sentiment",
        "score": "Score",
        "confidence": "Confidence",
        "keyword_analysis": "Keyword Analysis",
        "mental_state": "Mental State",
        "risk_score": "Risk Score",
        "suggestions": "Suggestions",
        "positive": "Positive",
        "negative": "Negative",
        "neutral": "Neutral",
        "normal": "Normal",
        "mild": "Mild",
        "moderate": "Moderate",
        "severe": "Severe",
        
        # Results
        "no_results": "No assessment results available",
        "status": "Status",
        "completed": "Completed",
        
        # System Settings
        "database_management": "Database Management",
        "load_default_keywords": "Load Default Keywords",
        "load_default_suggestions": "Load Default Suggestions",
        "keywords_loaded": "Default keywords loaded",
        "suggestions_loaded": "Default suggestions loaded",
        "keyword_load_error": "Error loading keywords: {}",
        "suggestion_load_error": "Error loading suggestions: {}",
        
        # Language
        "language": "Language",
        "select_language": "Select Language:",
        "english": "English",
        "hindi": "हिंदी",

        # Facial Analysis
        "facial_behavior_analysis": "Facial Behavior Analysis",
        "analysis_settings": "Analysis Settings",
        "analysis_duration": "Analysis Duration (seconds)",
        "analysis_type": "Analysis Type",
        "general_assessment": "General Assessment",
        "stress_analysis": "Stress Analysis",
        "anxiety_indicators": "Anxiety Indicators",
        "engagement_level": "Engagement Level",
        "camera_preview": "Camera Preview",
        "test_camera": "Test Camera",
        "camera_available": "✅ Camera available",
        "camera_not_available": "❌ Camera not available",
        "start_analysis": "🎥 Start Analysis",
        "analysis_in_progress": "Analysis in progress...",
        "analysis_complete": "✅ Analysis Complete",
        "analysis_summary": "Analysis Summary",
        "frames_analyzed": "Frames Analyzed",
        "average_score": "Average Score",
        "face_detection_percent": "Face Detection %",
        "duration": "Duration",
        "mental_health_indicators": "Mental Health Indicators",
        "stress_detection_rate": "Stress Detection Rate",
        "anxiety_indicators_rate": "Anxiety Indicators Rate",
        "overall_wellbeing": "Overall Wellbeing",
        "recommendations": "Recommendations",
        "results_saved": "✅ Results saved",
        "privacy_notice": "🔒 Privacy Notice: All video data is processed locally and not stored.",
        "facial_analysis_not_available": "Facial analysis not available. Please install required packages.",
        "camera_test_error": "Camera test error",
        "analysis_failed": "Analysis failed",
        "ensure_camera_connected": "Please ensure your camera is connected and working.",

        # Common
        "description": "Description",
        "save": "Save",
        "cancel": "Cancel",
        "edit": "Edit",
        "delete": "Delete",
        "confirm": "Confirm",
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "info": "Info"
    },
    
    "hi": {
        # Main headers
        "app_title": "सेना मानसिक स्वास्थ्य मूल्यांकन प्रणाली",
        "login_header": "लॉगिन",
        "admin_dashboard": "एडमिन डैशबोर्ड",
        "user_dashboard": "उपयोगकर्ता डैशबोर्ड",
        
        # Login page
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "login_button": "लॉगिन करें",
        "welcome_message": "स्वागत है, {}!",
        "invalid_credentials": "गलत उपयोगकर्ता नाम या पासवर्ड",
        "fill_all_fields": "कृपया सभी फ़ील्ड भरें",
        "default_admin_info": "डिफ़ॉल्ट एडमिन लॉगिन:",
        
        # Navigation
        "questionnaire_management": "प्रश्नावली प्रबंधन",
        "user_management": "उपयोगकर्ता प्रबंधन",
        "reports": "रिपोर्ट्स",
        "system_settings": "सिस्टम सेटिंग्स",
        "take_assessment": "मूल्यांकन करें",
        "voice_assessment": "आवाज़ से मूल्यांकन",
        "facial_analysis": "चेहरे का विश्लेषण",
        "my_results": "मेरे परिणाम",
        "logout": "लॉग आउट",
        
        # Questionnaire Management
        "load_sample_questionnaires": "नमूना प्रश्नावली लोड करें",
        "refresh_questionnaire_list": "प्रश्नावली सूची रीफ्रेश करें",
        "questionnaires_loaded": "{} प्रश्नावली सफलतापूर्वक लोड की गईं",
        "questionnaires_failed": "{} प्रश्नावली लोड नहीं हो सकीं",
        "no_questionnaires": "कोई प्रश्नावली उपलब्ध नहीं है। कृपया नमूना प्रश्नावली लोड करें।",
        "select_questionnaire_details": "विस्तार देखने के लिए प्रश्नावली चुनें:",
        "description": "विवरण",
        "assessment_instructions": "निर्देश",
        "time_limit": "समय सीमा",
        "minutes": "मिनट",
        "start_assessment": "मूल्यांकन शुरू करें",
        "question": "प्रश्न",
        "select_answer": "अपना उत्तर चुनें:",
        "previous_question": "पिछला प्रश्न",
        "next_question": "अगला प्रश्न",
        "assessment_complete": "मूल्यांकन पूर्ण!",
        "view_results": "परिणाम देखें",
        "assessment_results": "मूल्यांकन परिणाम",
        "total_score": "कुल स्कोर",
        "percentage": "प्रतिशत",
        "risk_level": "जोखिम स्तर",
        "assessment": "मूल्यांकन",
        "status": "स्थिति",
        "score": "स्कोर",
        "mental_state": "मानसिक स्थिति",
        "completed": "पूर्ण",
        "suggestions": "सुझाव",
        "results_saved": "परिणाम सहेजे गए",
        "error_saving_results": "परिणाम सहेजने में त्रुटि",
        "please_try_again": "कृपया फिर से प्रयास करें",
        "error_loading_results": "परिणाम लोड करने में त्रुटि",
        "no_assessment_results": "कोई मूल्यांकन परिणाम उपलब्ध नहीं है",
        "complete_assessment_first": "कृपया पहले एक मूल्यांकन पूरा करें",
        "suggestions_not_available": "सुझाव उपलब्ध नहीं",
        "voice_assessment": "आवाज़ से मूल्यांकन",
        "record_voice": "अपनी आवाज़ रिकॉर्ड करें",
        "analyze": "विश्लेषण करें",
        "analysis_result": "विश्लेषण परिणाम",
        "sentiment": "भावना",
        
        # User Management
        "create_new_user": "नया उपयोगकर्ता बनाएं",
        "full_name": "पूरा नाम",
        "email": "ईमेल",
        "role": "भूमिका",
        "army_id": "सेना आईडी",
        "rank": "रैंक",
        "unit": "यूनिट",
        "create_user": "उपयोगकर्ता बनाएं",
        "user_created": "उपयोगकर्ता '{}' सफलतापूर्वक बनाया गया",
        "user_creation_error": "उपयोगकर्ता बनाने में त्रुटि: {}",
        "required_fields": "कृपया आवश्यक फ़ील्ड भरें",
        
        # Reports
        "reports_analysis": "रिपोर्ट्स और विश्लेषण",
        "total_assessments": "कुल मूल्यांकन",
        "completed_assessments": "पूर्ण मूल्यांकन",
        "completion_rate": "पूर्णता दर",
        "mental_state_distribution": "मानसिक स्थिति वितरण",
        
        # Assessment
        "assessment_instructions": "निर्देश",
        "time_limit": "समय सीमा",
        "minutes": "मिनट",
        "start_assessment": "मूल्यांकन शुरू करें",
        "question": "प्रश्न",
        "select_answer": "अपना उत्तर चुनें:",
        "previous_question": "पिछला प्रश्न",
        "next_question": "अगला प्रश्न",
        "assessment_complete": "मूल्यांकन पूर्ण!",
        "view_results": "परिणाम देखें",
        "assessment_results": "मूल्यांकन परिणाम",
        "total_score": "कुल स्कोर",
        "percentage": "प्रतिशत",
        "risk_level": "जोखिम स्तर",
        "results_saved": "परिणाम सहेजे गए",
        "result_save_error": "परिणाम सहेजने में त्रुटि: {}",
        "start_new_assessment": "नया मूल्यांकन शुरू करें",
        
        # Voice Assessment
        "voice_instructions": "निर्देश:",
        "voice_instruction_1": "1. नीचे दिए गए प्रश्न का उत्तर हिंदी में दें",
        "voice_instruction_2": "2. रिकॉर्ड बटन दबाकर अपना उत्तर रिकॉर्ड करें",
        "voice_instruction_3": "3. या फिर टेक्स्ट बॉक्स में टाइप करें",
        "select_question": "प्रश्न चुनें:",
        "type_response": "यहाँ अपना उत्तर लिखें:",
        "or_voice_input": "या आवाज़ से उत्तर दें:",
        "upload_audio": "ऑडियो फ़ाइल अपलोड करें",
        "analyze_response": "उत्तर का विश्लेषण करें",
        "audio_processing": "ऑडियो प्रोसेस हो रहा है...",
        "audio_processed": "ऑडियो सफलतापूर्वक प्रोसेस हुआ!",
        "transcribed_text": "ट्रांसक्राइब किया गया टेक्स्ट:",
        "audio_processing_error": "ऑडियो प्रोसेसिंग में त्रुटि: {}",
        
        # Analysis Results
        "sentiment_analysis": "भावना विश्लेषण",
        "sentiment": "भावना",
        "score": "स्कोर",
        "confidence": "विश्वास",
        "keyword_analysis": "कीवर्ड विश्लेषण",
        "mental_state": "मानसिक स्थिति",
        "risk_score": "जोखिम स्कोर",
        "suggestions": "सुझाव",
        "positive": "सकारात्मक",
        "negative": "नकारात्मक",
        "neutral": "तटस्थ",
        "normal": "सामान्य",
        "mild": "हल्का",
        "moderate": "मध्यम",
        "severe": "गंभीर",
        
        # Results
        "no_results": "कोई मूल्यांकन परिणाम उपलब्ध नहीं है",
        "status": "स्थिति",
        "completed": "पूर्ण",
        
        # System Settings
        "database_management": "डेटाबेस प्रबंधन",
        "load_default_keywords": "डिफ़ॉल्ट कीवर्ड सेट लोड करें",
        "load_default_suggestions": "डिफ़ॉल्ट सुझाव लोड करें",
        "keywords_loaded": "डिफ़ॉल्ट कीवर्ड सेट लोड किए गए",
        "suggestions_loaded": "डिफ़ॉल्ट सुझाव लोड किए गए",
        "keyword_load_error": "कीवर्ड लोड करने में त्रुटि: {}",
        "suggestion_load_error": "सुझाव लोड करने में त्रुटि: {}",
        
        # Language
        "language": "भाषा",
        "select_language": "भाषा चुनें:",
        "english": "English",
        "hindi": "हिंदी",

        # Facial Analysis
        "facial_behavior_analysis": "चेहरे का व्यवहार विश्लेषण",
        "analysis_settings": "विश्लेषण सेटिंग्स",
        "analysis_duration": "विश्लेषण अवधि (सेकंड)",
        "analysis_type": "विश्लेषण प्रकार",
        "general_assessment": "सामान्य मूल्यांकन",
        "stress_analysis": "तनाव विश्लेषण",
        "anxiety_indicators": "चिंता संकेतक",
        "engagement_level": "जुड़ाव स्तर",
        "camera_preview": "कैमरा पूर्वावलोकन",
        "test_camera": "कैमरा परीक्षण",
        "camera_available": "✅ कैमरा उपलब्ध है",
        "camera_not_available": "❌ कैमरा उपलब्ध नहीं",
        "start_analysis": "🎥 विश्लेषण शुरू करें",
        "analysis_in_progress": "विश्लेषण चल रहा है...",
        "analysis_complete": "✅ विश्लेषण पूर्ण",
        "analysis_summary": "विश्लेषण सारांश",
        "frames_analyzed": "फ्रेम विश्लेषित",
        "average_score": "औसत स्कोर",
        "face_detection_percent": "चेहरा पहचान %",
        "duration": "अवधि",
        "mental_health_indicators": "मानसिक स्वास्थ्य संकेतक",
        "stress_detection_rate": "तनाव संकेतक दर",
        "anxiety_indicators_rate": "चिंता संकेतक दर",
        "overall_wellbeing": "समग्र कल्याण",
        "recommendations": "सुझाव",
        "results_saved": "✅ परिणाम सहेजे गए",
        "privacy_notice": "🔒 गोपनीयता सूचना: सभी वीडियो डेटा स्थानीय रूप से प्रोसेस किया जाता है और संग्रहीत नहीं किया जाता।",
        "facial_analysis_not_available": "चेहरे का विश्लेषण उपलब्ध नहीं है। कृपया आवश्यक पैकेज इंस्टॉल करें।",
        "camera_test_error": "कैमरा परीक्षण त्रुटि",
        "analysis_failed": "विश्लेषण असफल",
        "ensure_camera_connected": "कृपया सुनिश्चित करें कि आपका कैमरा कनेक्ट है और काम कर रहा है।",

        # Common
        "description": "विवरण",
        "save": "सहेजें",
        "cancel": "रद्द करें",
        "edit": "संपादित करें",
        "delete": "हटाएं",
        "confirm": "पुष्टि करें",
        "error": "त्रुटि",
        "success": "सफलता",
        "warning": "चेतावनी",
        "info": "जानकारी"
    }
}

def get_language():
    """Get current language from session state"""
    if "language" not in st.session_state:
        st.session_state.language = "hi"  # Default to Hindi
    return st.session_state.language

def set_language(lang_code: str):
    """Set current language in session state"""
    if lang_code in TRANSLATIONS:
        st.session_state.language = lang_code

def t(key: str, *args) -> str:
    """
    Translate a key to current language
    
    Args:
        key: Translation key
        *args: Arguments for string formatting
        
    Returns:
        Translated string
    """
    lang = get_language()
    translation = TRANSLATIONS.get(lang, {}).get(key, key)
    
    if args:
        try:
            return translation.format(*args)
        except:
            return translation
    
    return translation

def language_selector():
    """Display language selector in sidebar"""
    with st.sidebar:
        st.markdown("---")
        current_lang = get_language()
        
        # Language selection - Using Indian flag for both languages (Indian Army application)
        lang_options = {
            "hi": "🇮🇳 हिंदी",
            "en": "🇮🇳 English"
        }
        
        selected_lang = st.selectbox(
            t("select_language"),
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=0 if current_lang == "hi" else 1,
            key="language_selector"
        )
        
        if selected_lang != current_lang:
            set_language(selected_lang)
            st.rerun()

def get_bilingual_text(hindi_text: str, english_text: str) -> str:
    """
    Return text based on current language
    
    Args:
        hindi_text: Hindi text
        english_text: English text
        
    Returns:
        Text in current language
    """
    lang = get_language()
    if lang == "hi":
        return hindi_text
    else:
        return english_text

def display_bilingual_header(hindi_text: str, english_text: str, level: int = 1):
    """
    Display bilingual header
    
    Args:
        hindi_text: Hindi header text
        english_text: English header text
        level: Header level (1-6)
    """
    lang = get_language()
    
    if lang == "hi":
        primary_text = hindi_text
        secondary_text = english_text
    else:
        primary_text = english_text
        secondary_text = hindi_text
    
    # Display primary text
    if level == 1:
        st.markdown(f'<h1 class="main-header">{primary_text}</h1>', unsafe_allow_html=True)
    elif level == 2:
        st.markdown(f'<h2 class="section-header">{primary_text}</h2>', unsafe_allow_html=True)
    elif level == 3:
        st.markdown(f'<h3 class="section-header">{primary_text}</h3>', unsafe_allow_html=True)
    else:
        st.markdown(f'<h{level}>{primary_text}</h{level}>', unsafe_allow_html=True)
    
    # Display secondary text in smaller font
    if st.session_state.get("show_bilingual", True):
        st.markdown(f'<p style="font-size: 0.8em; color: #666; margin-top: -10px;"><em>{secondary_text}</em></p>', unsafe_allow_html=True)

def bilingual_info_box(hindi_text: str, english_text: str, box_type: str = "info"):
    """
    Display bilingual info box
    
    Args:
        hindi_text: Hindi text
        english_text: English text
        box_type: Type of box (info, warning, error, success)
    """
    lang = get_language()
    
    if lang == "hi":
        primary_text = hindi_text
        secondary_text = english_text
    else:
        primary_text = english_text
        secondary_text = hindi_text
    
    box_class = f"{box_type}-box"
    
    st.markdown(f"""
    <div class="{box_class}">
    <strong>{primary_text}</strong><br>
    <em style="font-size: 0.9em; color: #666;">{secondary_text}</em>
    </div>
    """, unsafe_allow_html=True)
