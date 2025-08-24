#!/usr/bin/env python3
"""
Voice Input Component for Streamlit
Provides microphone input functionality with real-time transcription
"""

import streamlit as st
import time
import logging
from typing import Optional, Dict

# Configure logging
logger = logging.getLogger(__name__)

def voice_input_component(
    key: str,
    placeholder: str = "Type here or use voice input...",
    language_hint: str = "hi",
    height: int = 100,
    max_chars: Optional[int] = None
) -> str:
    """
    Create a voice-enabled text input component
    
    Args:
        key: Unique key for the component
        placeholder: Placeholder text
        language_hint: Language hint for voice recognition
        height: Height of text area
        max_chars: Maximum characters allowed
        
    Returns:
        Text content (typed or transcribed)
    """
    
    # Initialize session state for this component
    if f"voice_text_{key}" not in st.session_state:
        st.session_state[f"voice_text_{key}"] = ""
    if f"voice_recording_{key}" not in st.session_state:
        st.session_state[f"voice_recording_{key}"] = False
    if f"voice_processor_{key}" not in st.session_state:
        st.session_state[f"voice_processor_{key}"] = None
    
    # Create layout
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Text area for input
        text_content = st.text_area(
            label="",
            value=st.session_state[f"voice_text_{key}"],
            placeholder=placeholder,
            height=height,
            max_chars=max_chars,
            key=f"text_area_{key}"
        )
        
        # Update session state
        st.session_state[f"voice_text_{key}"] = text_content
    
    with col2:
        # Voice input controls
        st.markdown("**🎤 Voice Input**")
        
        # Initialize voice processor if needed
        if st.session_state[f"voice_processor_{key}"] is None:
            try:
                from models.enhanced_voice_processor import EnhancedVoiceProcessor
                st.session_state[f"voice_processor_{key}"] = EnhancedVoiceProcessor()
                if st.session_state[f"voice_processor_{key}"].is_initialized:
                    st.success("🎤 Voice ready")
                else:
                    st.error("❌ Voice not available")
            except Exception as e:
                st.error(f"❌ Voice error: {e}")
                st.session_state[f"voice_processor_{key}"] = None
        
        processor = st.session_state[f"voice_processor_{key}"]
        
        if processor and processor.is_initialized:
            # Recording controls
            if not st.session_state[f"voice_recording_{key}"]:
                if st.button("🎤 Start Recording", key=f"start_rec_{key}", type="primary"):
                    if processor.start_recording():
                        st.session_state[f"voice_recording_{key}"] = True
                        st.rerun()
                    else:
                        st.error("❌ Failed to start recording")
            else:
                # Recording in progress
                st.warning("🔴 Recording...")
                
                if st.button("⏹️ Stop Recording", key=f"stop_rec_{key}", type="secondary"):
                    audio_data = processor.stop_recording()
                    st.session_state[f"voice_recording_{key}"] = False
                    
                    if audio_data is not None:
                        # Transcribe audio
                        with st.spinner("🔄 Transcribing..."):
                            result = processor.transcribe_audio(audio_data, language_hint)
                        
                        if "error" not in result:
                            # Add transcribed text to existing content
                            transcribed = result.get("transcription", "")
                            if transcribed:
                                current_text = st.session_state[f"voice_text_{key}"]
                                if current_text:
                                    new_text = current_text + " " + transcribed
                                else:
                                    new_text = transcribed
                                
                                st.session_state[f"voice_text_{key}"] = new_text
                                st.success(f"✅ Added: {transcribed[:30]}...")
                                st.rerun()
                            else:
                                st.warning("⚠️ No speech detected")
                        else:
                            st.error(f"❌ Transcription failed: {result['error']}")
                    else:
                        st.error("❌ No audio recorded")
                    
                    st.rerun()
            
            # Language selection - Indian Army application
            lang_options = {
                "hi": "🇮🇳 Hindi/Hinglish",
                "en": "🇮🇳 English",
                "auto": "🌐 Auto-detect"
            }
            
            selected_lang = st.selectbox(
                "Language",
                options=list(lang_options.keys()),
                format_func=lambda x: lang_options[x],
                index=0 if language_hint == "hi" else 1 if language_hint == "en" else 2,
                key=f"lang_select_{key}"
            )
            
            # Update language hint
            language_hint = selected_lang
            
            # Microphone test
            if st.button("🧪 Test Mic", key=f"test_mic_{key}"):
                with st.spinner("Testing microphone..."):
                    test_result = processor.test_microphone(2.0)
                
                if "error" not in test_result:
                    quality = test_result.get("quality", "unknown")
                    if quality == "good":
                        st.success("✅ Microphone working well")
                    elif quality == "low":
                        st.warning("⚠️ Low audio quality")
                    else:
                        st.error("❌ Very low audio quality")
                else:
                    st.error(f"❌ Mic test failed: {test_result['error']}")
        
        else:
            st.error("❌ Voice input not available")
            st.info("Install: pip install torch whisper sounddevice soundfile")
    
    return st.session_state[f"voice_text_{key}"]

def simple_voice_button(
    key: str,
    button_text: str = "🎤 Voice Input",
    language_hint: str = "hi"
) -> Optional[str]:
    """
    Simple voice input button that returns transcribed text
    
    Args:
        key: Unique key for the component
        button_text: Text for the button
        language_hint: Language hint for recognition
        
    Returns:
        Transcribed text or None
    """
    
    if st.button(button_text, key=f"voice_btn_{key}"):
        try:
            from models.enhanced_voice_processor import EnhancedVoiceProcessor
            
            processor = EnhancedVoiceProcessor()
            
            if not processor.is_initialized:
                st.error("❌ Voice processor not available")
                return None
            
            # Record audio
            st.info("🎤 Recording for 5 seconds... Speak now!")
            
            if processor.start_recording():
                # Show countdown
                progress_bar = st.progress(0)
                for i in range(50):  # 5 seconds = 50 * 0.1s
                    time.sleep(0.1)
                    progress_bar.progress((i + 1) / 50)
                
                audio_data = processor.stop_recording()
                progress_bar.empty()
                
                if audio_data is not None:
                    with st.spinner("🔄 Transcribing..."):
                        result = processor.transcribe_audio(audio_data, language_hint)
                    
                    if "error" not in result:
                        transcribed = result.get("transcription", "")
                        if transcribed:
                            st.success(f"✅ Transcribed: {transcribed}")
                            return transcribed
                        else:
                            st.warning("⚠️ No speech detected")
                    else:
                        st.error(f"❌ Transcription failed: {result['error']}")
                else:
                    st.error("❌ No audio recorded")
            else:
                st.error("❌ Failed to start recording")
        
        except Exception as e:
            st.error(f"❌ Voice input error: {e}")
    
    return None

def voice_file_uploader(
    key: str,
    language_hint: str = "hi",
    accepted_formats: list = None
) -> Optional[str]:
    """
    File uploader with voice transcription
    
    Args:
        key: Unique key for the component
        language_hint: Language hint for recognition
        accepted_formats: Accepted audio formats
        
    Returns:
        Transcribed text or None
    """
    
    if accepted_formats is None:
        accepted_formats = ["wav", "mp3", "m4a", "ogg"]
    
    uploaded_file = st.file_uploader(
        "Upload audio file for transcription",
        type=accepted_formats,
        key=f"voice_upload_{key}"
    )
    
    if uploaded_file is not None:
        try:
            from models.enhanced_voice_processor import EnhancedVoiceProcessor
            
            processor = EnhancedVoiceProcessor()
            
            if not processor.is_initialized:
                st.error("❌ Voice processor not available")
                return None
            
            # Save uploaded file temporarily
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            with st.spinner("🔄 Transcribing uploaded file..."):
                result = processor.transcribe_file(tmp_path, language_hint)
            
            # Clean up
            import os
            os.unlink(tmp_path)
            
            if "error" not in result:
                transcribed = result.get("transcription", "")
                if transcribed:
                    st.success("✅ File transcribed successfully!")
                    st.text_area("Transcribed text:", value=transcribed, height=150, key=f"transcribed_{key}")
                    return transcribed
                else:
                    st.warning("⚠️ No speech detected in file")
            else:
                st.error(f"❌ Transcription failed: {result['error']}")
        
        except Exception as e:
            st.error(f"❌ File transcription error: {e}")
    
    return None

# Example usage component
def voice_input_demo():
    """Demo component showing voice input capabilities"""
    st.markdown("### 🎤 Voice Input Demo")
    
    # Voice-enabled text area
    st.markdown("#### Voice-Enabled Text Area")
    text_content = voice_input_component(
        key="demo_voice",
        placeholder="Type your response or use voice input...",
        language_hint="hi",
        height=120
    )
    
    if text_content:
        st.markdown(f"**Current text:** {text_content}")
    
    # Simple voice button
    st.markdown("#### Quick Voice Input")
    voice_result = simple_voice_button(
        key="demo_quick",
        button_text="🎤 Record 5 seconds",
        language_hint="hi"
    )
    
    if voice_result:
        st.markdown(f"**Voice result:** {voice_result}")
    
    # File upload
    st.markdown("#### Audio File Transcription")
    file_result = voice_file_uploader(
        key="demo_file",
        language_hint="hi"
    )
    
    if file_result:
        st.markdown(f"**File transcription:** {file_result}")

if __name__ == "__main__":
    # Test the voice input component
    st.set_page_config(page_title="Voice Input Test", layout="wide")
    st.title("🎤 Voice Input Component Test")
    
    voice_input_demo()
