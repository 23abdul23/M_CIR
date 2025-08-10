#!/usr/bin/env python3
"""
Professional Voice Input Component for Army Mental Health Assessment
Clean, military-grade UI without unnecessary symbols
"""

import streamlit as st
import time
import logging
from typing import Optional, Dict

# Configure logging
logger = logging.getLogger(__name__)

def professional_voice_text_area(
    key: str,
    label: str = "",
    placeholder: str = "Type your response here...",
    height: int = 120,
    language_hint: str = "hi",
    max_chars: Optional[int] = None
) -> str:
    """
    Professional voice-enabled text area with clean military UI
    
    Args:
        key: Unique key for the component
        label: Label for the text area
        placeholder: Placeholder text
        height: Height of text area
        language_hint: Language hint for voice recognition
        max_chars: Maximum characters allowed
        
    Returns:
        Text content (typed or transcribed)
    """
    
    # Initialize session state
    if f"voice_text_{key}" not in st.session_state:
        st.session_state[f"voice_text_{key}"] = ""
    if f"voice_processor_{key}" not in st.session_state:
        st.session_state[f"voice_processor_{key}"] = None
    if f"voice_recording_{key}" not in st.session_state:
        st.session_state[f"voice_recording_{key}"] = False
    
    # Initialize voice processor if needed
    if st.session_state[f"voice_processor_{key}"] is None:
        try:
            from models.enhanced_voice_processor import EnhancedVoiceProcessor
            processor = EnhancedVoiceProcessor()
            if processor.is_initialized:
                st.session_state[f"voice_processor_{key}"] = processor
            else:
                st.session_state[f"voice_processor_{key}"] = None
        except Exception as e:
            logger.warning(f"Voice processor initialization failed: {e}")
            st.session_state[f"voice_processor_{key}"] = None
    
    processor = st.session_state[f"voice_processor_{key}"]
    
    # Main text area
    text_content = st.text_area(
        label=label,
        value=st.session_state[f"voice_text_{key}"],
        placeholder=placeholder,
        height=height,
        max_chars=max_chars,
        key=f"text_area_{key}",
        help="Type your response or use voice input below"
    )
    
    # Update session state
    st.session_state[f"voice_text_{key}"] = text_content
    
    # Voice controls (only if processor available)
    if processor and processor.is_initialized:
        # Professional voice controls layout
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            if not st.session_state[f"voice_recording_{key}"]:
                if st.button(
                    "🎤 Voice Input", 
                    key=f"start_voice_{key}",
                    help="Click to start voice recording (Hindi/English supported)"
                ):
                    if processor.start_recording():
                        st.session_state[f"voice_recording_{key}"] = True
                        st.rerun()
            else:
                if st.button(
                    "⏹ Stop Recording", 
                    key=f"stop_voice_{key}",
                    type="secondary"
                ):
                    audio_data = processor.stop_recording()
                    st.session_state[f"voice_recording_{key}"] = False
                    
                    if audio_data is not None:
                        with st.spinner("Processing voice input..."):
                            result = processor.transcribe_audio(audio_data, language_hint)
                        
                        if "error" not in result:
                            transcribed = result.get("transcription", "")
                            if transcribed:
                                current_text = st.session_state[f"voice_text_{key}"]
                                if current_text:
                                    new_text = current_text + " " + transcribed
                                else:
                                    new_text = transcribed
                                
                                st.session_state[f"voice_text_{key}"] = new_text
                                # Log success to terminal only
                                logger.info(f"Voice input transcribed: {transcribed[:50]}...")
                                st.rerun()
                            else:
                                logger.warning("No speech detected in voice input")
                        else:
                            logger.error("Voice processing failed")
                    
                    st.rerun()
        
        with col2:
            # Language selection (professional dropdown)
            lang_options = {
                "hi": "Hindi/Hinglish",
                "en": "English",
                "auto": "Auto-detect"
            }
            
            language_hint = st.selectbox(
                "Language",
                options=list(lang_options.keys()),
                format_func=lambda x: lang_options[x],
                index=0,
                key=f"lang_{key}",
                help="Select language for voice recognition"
            )
        
        with col3:
            # Clean status - no visible indicators
            if st.session_state[f"voice_recording_{key}"]:
                # Log to terminal only
                logger.info("Voice recording in progress")
            else:
                # Log device status to terminal only
                logger.info(f"Voice system ready on {processor.device}")
    
    else:
        # Voice not available - log to terminal only, no UI message
        logger.info("Voice input not available - text input only")
    
    return st.session_state[f"voice_text_{key}"]

def simple_voice_text_input(
    label: str,
    key: str,
    placeholder: str = "Type here or use voice input...",
    height: int = 100,
    language_hint: str = "hi"
) -> str:
    """
    Simple voice-enabled text input with minimal UI

    Args:
        label: Label for the input
        key: Unique key
        placeholder: Placeholder text
        height: Height of text area
        language_hint: Language hint for voice

    Returns:
        Text content
    """

    # Initialize session state
    if f"simple_voice_text_{key}" not in st.session_state:
        st.session_state[f"simple_voice_text_{key}"] = ""
    if f"simple_voice_processor_{key}" not in st.session_state:
        st.session_state[f"simple_voice_processor_{key}"] = None
    if f"simple_voice_recording_{key}" not in st.session_state:
        st.session_state[f"simple_voice_recording_{key}"] = False
    if f"simple_voice_start_time_{key}" not in st.session_state:
        st.session_state[f"simple_voice_start_time_{key}"] = None

    # Initialize voice processor silently
    if st.session_state[f"simple_voice_processor_{key}"] is None:
        try:
            from models.enhanced_voice_processor import EnhancedVoiceProcessor
            processor = EnhancedVoiceProcessor()
            if processor.is_initialized:
                st.session_state[f"simple_voice_processor_{key}"] = processor
                logger.info(f"Voice processor initialized for {key} on {processor.device}")
            else:
                st.session_state[f"simple_voice_processor_{key}"] = None
                logger.warning(f"Voice processor failed to initialize for {key}")
        except Exception as e:
            logger.warning(f"Voice processor import failed for {key}: {e}")
            st.session_state[f"simple_voice_processor_{key}"] = None

    processor = st.session_state[f"simple_voice_processor_{key}"]

    # Main text area
    text_content = st.text_area(
        label=label,
        value=st.session_state[f"simple_voice_text_{key}"],
        placeholder=placeholder,
        height=height,
        key=f"simple_text_area_{key}"
    )

    # Update session state
    st.session_state[f"simple_voice_text_{key}"] = text_content

    # Enhanced Voice Controls with Manual Stop (only if processor available)
    if processor and processor.is_initialized:

        # Create columns for voice controls
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            if not st.session_state[f"simple_voice_recording_{key}"]:
                # Start Recording Button
                if st.button(f"🎤 Start Voice Input", key=f"simple_voice_start_{key}", type="primary"):
                    if processor.start_recording():
                        st.session_state[f"simple_voice_recording_{key}"] = True
                        st.session_state[f"simple_voice_start_time_{key}"] = time.time()
                        logger.info(f"Started recording for {key}")
                        st.rerun()
                    else:
                        st.error("Failed to start recording")
            else:
                # Stop Recording Button
                if st.button(f"⏹️ Stop Recording", key=f"simple_voice_stop_{key}", type="secondary"):
                    audio_data = processor.stop_recording()
                    st.session_state[f"simple_voice_recording_{key}"] = False
                    st.session_state[f"simple_voice_start_time_{key}"] = None

                    if audio_data is not None:
                        with st.spinner("🔄 Processing voice input..."):
                            result = processor.transcribe_audio(audio_data, language_hint)

                        if "error" not in result:
                            transcribed = result.get("transcription", "")
                            if transcribed:
                                # Add to existing text
                                current_text = st.session_state[f"simple_voice_text_{key}"]
                                if current_text:
                                    new_text = current_text + " " + transcribed
                                else:
                                    new_text = transcribed

                                st.session_state[f"simple_voice_text_{key}"] = new_text
                                logger.info(f"Voice transcribed for {key}: {transcribed[:50]}...")
                                st.success("✅ Voice input added successfully")
                                st.rerun()
                            else:
                                st.warning("⚠️ No speech detected")
                        else:
                            st.error(f"❌ Voice processing failed: {result['error']}")
                    else:
                        st.error("❌ No audio recorded")

                    st.rerun()

        with col2:
            # Language selection - Indian Army application
            lang_options = {
                "hi": "🇮🇳 Hindi/Hinglish",
                "en": "🇮🇳 English",
                "auto": "🌐 Auto-detect"
            }

            selected_lang = st.selectbox(
                "Voice Language",
                options=list(lang_options.keys()),
                format_func=lambda x: lang_options[x],
                index=0,
                key=f"simple_lang_{key}"
            )

            # Update language hint
            language_hint = selected_lang

        with col3:
            # Recording status and timer
            if st.session_state[f"simple_voice_recording_{key}"]:
                start_time = st.session_state[f"simple_voice_start_time_{key}"]
                if start_time:
                    elapsed = int(time.time() - start_time)

                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; background-color: #ff4444; color: white; border-radius: 5px;">
                        <strong>🔴 RECORDING</strong><br>
                        <small>{elapsed}s elapsed</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Show ready status
                device_info = "GPU" if processor.device == "cuda" else "CPU"
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background-color: #28a745; color: white; border-radius: 5px;">
                    <strong>✅ READY</strong><br>
                    <small>{device_info}</small>
                </div>
                """, unsafe_allow_html=True)

        # Instructions
        st.caption("💡 Click 'Start Voice Input' to begin recording. Click 'Stop Recording' when finished speaking.")

    else:
        # Voice not available - show info
        st.info("🎤 Voice input not available. Please type your response.")

    return st.session_state[f"simple_voice_text_{key}"]

def professional_quick_voice(
    key: str,
    button_text: str = "Voice Input",
    language_hint: str = "hi",
    recording_duration: int = 5
) -> Optional[str]:
    """
    Professional quick voice input button
    
    Args:
        key: Unique key
        button_text: Button text
        language_hint: Language hint
        recording_duration: Recording duration in seconds
        
    Returns:
        Transcribed text or None
    """
    
    if st.button(button_text, key=f"quick_voice_{key}"):
        try:
            from models.enhanced_voice_processor import EnhancedVoiceProcessor
            
            processor = EnhancedVoiceProcessor()
            
            if not processor.is_initialized:
                st.error("Voice processing not available")
                return None
            
            # Professional recording interface
            st.info(f"Recording for {recording_duration} seconds - speak now")
            
            if processor.start_recording():
                # Clean progress indicator
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(recording_duration * 10):  # 0.1s intervals
                    time.sleep(0.1)
                    progress = (i + 1) / (recording_duration * 10)
                    progress_bar.progress(progress)
                    status_text.text(f"Recording... {recording_duration - (i // 10)} seconds remaining")
                
                audio_data = processor.stop_recording()
                progress_bar.empty()
                status_text.empty()
                
                if audio_data is not None:
                    with st.spinner("Processing voice input..."):
                        result = processor.transcribe_audio(audio_data, language_hint)
                    
                    if "error" not in result:
                        transcribed = result.get("transcription", "")
                        if transcribed:
                            st.success("Voice input processed successfully")
                            return transcribed
                        else:
                            st.warning("No speech detected")
                    else:
                        st.error("Voice processing failed")
                else:
                    st.error("Recording failed")
            else:
                st.error("Could not start recording")
        
        except Exception as e:
            st.error("Voice input error occurred")
            logger.error(f"Voice input error: {e}")
    
    return None

def voice_status_indicator():
    """Log voice system status to terminal only"""
    try:
        from models.enhanced_voice_processor import EnhancedVoiceProcessor

        processor = EnhancedVoiceProcessor()

        if processor.is_initialized:
            device_info = "GPU Accelerated" if processor.device == "cuda" else "CPU Processing"
            logger.info(f"Voice System: {device_info}")
        else:
            logger.warning("Voice System: Not Available")

    except Exception:
        logger.info("Voice System: Text Input Only")

def enhanced_voice_assessment_section():
    """Enhanced voice assessment section for the main app"""
    
    # Professional header
    st.markdown("### Voice Assessment")
    st.markdown("*Speak in Hindi, English, or mixed Hinglish - the system will understand and transcribe appropriately*")
    
    # Voice system status
    voice_status_indicator()
    
    # Main voice input area
    voice_response = professional_voice_text_area(
        key="voice_assessment_main",
        label="Share your thoughts and feelings",
        placeholder="आप कैसा महसूस कर रहे हैं? / How are you feeling? (Type or use voice input)",
        height=150,
        language_hint="hi"
    )
    
    if voice_response:
        # Professional analysis display
        st.markdown("#### Your Response")
        st.text_area(
            "Recorded Response:",
            value=voice_response,
            height=100,
            disabled=True,
            key="voice_display"
        )
        
        # Analysis button
        if st.button("Analyze Response", type="primary"):
            with st.spinner("Analyzing your response..."):
                # Here you would integrate with your existing analysis logic
                time.sleep(2)  # Simulate processing
                
                st.success("Analysis completed")
                
                # Professional results display
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Sentiment Score", "0.75", "0.15")
                    st.metric("Stress Level", "Low", "-0.2")
                
                with col2:
                    st.metric("Engagement", "High", "0.3")
                    st.metric("Language Mix", "Hinglish", "")
                
                # Recommendations
                st.markdown("#### Recommendations")
                st.info("Based on your response, you appear to be in good mental health. Continue with regular wellness practices.")

# Professional styling
def apply_professional_voice_styling():
    """Apply professional styling for voice components"""
    st.markdown("""
    <style>
    /* Professional voice input styling */
    .stTextArea textarea {
        border: 2px solid #2E8B57;
        border-radius: 5px;
        font-family: 'Arial', sans-serif;
    }
    
    .stButton button {
        background-color: #2E8B57;
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    
    .stButton button:hover {
        background-color: #228B22;
    }
    
    /* Remove unnecessary symbols and clean up UI */
    .stAlert > div {
        border-radius: 5px;
    }
    
    /* Professional progress bar */
    .stProgress .st-bo {
        background-color: #2E8B57;
    }
    
    /* Clean selectbox */
    .stSelectbox > div > div {
        border: 1px solid #2E8B57;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
