#!/usr/bin/env python3
"""
Enhanced Voice Input Component with Better Controls
Improved microphone management and user experience
"""

import streamlit as st
import time
import logging
from typing import Optional, Dict

# Configure logging
logger = logging.getLogger(__name__)

def enhanced_voice_text_input(
    label: str,
    key: str,
    placeholder: str = "Type here or use voice input...",
    height: int = 120,
    language_hint: str = "hi",
    max_recording_time: int = 30
) -> str:
    """
    Enhanced voice-enabled text input with better microphone controls
    
    Args:
        label: Label for the input
        key: Unique key
        placeholder: Placeholder text
        height: Height of text area
        language_hint: Language hint for voice
        max_recording_time: Maximum recording time in seconds
        
    Returns:
        Text content
    """
    
    # Initialize session state
    voice_text_key = f"enhanced_voice_text_{key}"
    voice_processor_key = f"enhanced_voice_processor_{key}"
    recording_key = f"enhanced_recording_{key}"
    recording_start_key = f"enhanced_recording_start_{key}"
    
    if voice_text_key not in st.session_state:
        st.session_state[voice_text_key] = ""
    if voice_processor_key not in st.session_state:
        st.session_state[voice_processor_key] = None
    if recording_key not in st.session_state:
        st.session_state[recording_key] = False
    if recording_start_key not in st.session_state:
        st.session_state[recording_start_key] = None
    
    # Initialize voice processor silently
    if st.session_state[voice_processor_key] is None:
        try:
            from models.enhanced_voice_processor import EnhancedVoiceProcessor
            processor = EnhancedVoiceProcessor()
            if processor.is_initialized:
                st.session_state[voice_processor_key] = processor
                logger.info(f"Enhanced voice processor initialized for {key} on {processor.device}")
            else:
                st.session_state[voice_processor_key] = None
                logger.warning(f"Enhanced voice processor failed to initialize for {key}")
        except Exception as e:
            logger.warning(f"Enhanced voice processor import failed for {key}: {e}")
            st.session_state[voice_processor_key] = None
    
    processor = st.session_state[voice_processor_key]
    
    # Main text area
    text_content = st.text_area(
        label=label,
        value=st.session_state[voice_text_key],
        placeholder=placeholder,
        height=height,
        key=f"enhanced_text_area_{key}"
    )
    
    # Update session state
    st.session_state[voice_text_key] = text_content
    
    # Voice controls (only if processor available)
    if processor and processor.is_initialized:
        
        # Voice control layout
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            if not st.session_state[recording_key]:
                # Start recording button
                if st.button(f"🎤 Start Voice Input", key=f"start_voice_{key}", type="primary"):
                    if processor.start_recording():
                        st.session_state[recording_key] = True
                        st.session_state[recording_start_key] = time.time()
                        logger.info(f"Started recording for {key}")
                        st.rerun()
                    else:
                        st.error("Failed to start recording")
            else:
                # Stop recording button
                if st.button(f"⏹️ Stop Recording", key=f"stop_voice_{key}", type="secondary"):
                    audio_data = processor.stop_recording()
                    st.session_state[recording_key] = False
                    st.session_state[recording_start_key] = None
                    
                    if audio_data is not None:
                        with st.spinner("🔄 Processing voice input..."):
                            result = processor.transcribe_audio(audio_data, language_hint)
                        
                        if "error" not in result:
                            transcribed = result.get("transcription", "")
                            if transcribed:
                                # Add to existing text
                                current_text = st.session_state[voice_text_key]
                                if current_text:
                                    new_text = current_text + " " + transcribed
                                else:
                                    new_text = transcribed
                                
                                st.session_state[voice_text_key] = new_text
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
                key=f"enhanced_lang_{key}"
            )
            
            # Update language hint
            language_hint = selected_lang
        
        with col3:
            # Recording status and timer
            if st.session_state[recording_key]:
                start_time = st.session_state[recording_start_key]
                if start_time:
                    elapsed = int(time.time() - start_time)
                    remaining = max(0, max_recording_time - elapsed)
                    
                    if remaining > 0:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; background-color: #ff4444; color: white; border-radius: 5px;">
                            <strong>🔴 REC</strong><br>
                            <small>{remaining}s left</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Auto-stop when time limit reached
                        if elapsed >= max_recording_time:
                            audio_data = processor.stop_recording()
                            st.session_state[recording_key] = False
                            st.session_state[recording_start_key] = None
                            
                            if audio_data is not None:
                                with st.spinner("🔄 Processing voice input..."):
                                    result = processor.transcribe_audio(audio_data, language_hint)
                                
                                if "error" not in result:
                                    transcribed = result.get("transcription", "")
                                    if transcribed:
                                        current_text = st.session_state[voice_text_key]
                                        if current_text:
                                            new_text = current_text + " " + transcribed
                                        else:
                                            new_text = transcribed
                                        
                                        st.session_state[voice_text_key] = new_text
                                        st.success("✅ Voice input added (auto-stopped)")
                                        st.rerun()
                            
                            st.rerun()
                    else:
                        st.markdown("""
                        <div style="text-align: center; padding: 10px; background-color: #ff8888; color: white; border-radius: 5px;">
                            <strong>⏰ TIME UP</strong>
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
        st.caption(f"💡 Click 'Start Voice Input' to begin recording. Maximum {max_recording_time} seconds per recording.")
    
    else:
        # Voice not available - show info
        st.info("🎤 Voice input not available. Please type your response.")
    
    return st.session_state[voice_text_key]

def quick_voice_input(
    key: str,
    button_text: str = "🎤 Quick Voice",
    language_hint: str = "hi",
    recording_duration: int = 10
) -> Optional[str]:
    """
    Quick voice input with fixed duration
    
    Args:
        key: Unique key
        button_text: Button text
        language_hint: Language hint
        recording_duration: Fixed recording duration
        
    Returns:
        Transcribed text or None
    """
    
    if st.button(button_text, key=f"quick_voice_{key}"):
        try:
            from models.enhanced_voice_processor import EnhancedVoiceProcessor
            
            processor = EnhancedVoiceProcessor()
            
            if not processor.is_initialized:
                st.error("❌ Voice processing not available")
                return None
            
            # Start recording with progress
            st.info(f"🎤 Recording for {recording_duration} seconds - speak now!")
            
            if processor.start_recording():
                # Progress bar with countdown
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(recording_duration * 10):  # 0.1s intervals
                    time.sleep(0.1)
                    progress = (i + 1) / (recording_duration * 10)
                    progress_bar.progress(progress)
                    remaining = recording_duration - (i // 10)
                    status_text.text(f"🔴 Recording... {remaining} seconds remaining")
                
                audio_data = processor.stop_recording()
                progress_bar.empty()
                status_text.empty()
                
                if audio_data is not None:
                    with st.spinner("🔄 Processing voice input..."):
                        result = processor.transcribe_audio(audio_data, language_hint)
                    
                    if "error" not in result:
                        transcribed = result.get("transcription", "")
                        if transcribed:
                            st.success("✅ Voice input processed successfully")
                            return transcribed
                        else:
                            st.warning("⚠️ No speech detected")
                    else:
                        st.error(f"❌ Voice processing failed: {result['error']}")
                else:
                    st.error("❌ Recording failed")
            else:
                st.error("❌ Could not start recording")
        
        except Exception as e:
            st.error("❌ Voice input error occurred")
            logger.error(f"Quick voice input error: {e}")
    
    return None

def voice_input_status():
    """Display voice input system status"""
    try:
        from models.enhanced_voice_processor import EnhancedVoiceProcessor
        
        processor = EnhancedVoiceProcessor()
        
        if processor.is_initialized:
            device_info = "GPU Accelerated" if processor.device == "cuda" else "CPU Processing"
            st.success(f"🎤 Voice System: {device_info}")
            
            # Show available microphones
            mics = processor.get_available_microphones()
            if mics:
                st.info(f"🎧 {len(mics)} microphone(s) detected")
        else:
            st.warning("🎤 Voice System: Not Available")
    
    except Exception:
        st.info("🎤 Voice System: Text Input Only")

# Example usage
if __name__ == "__main__":
    st.set_page_config(page_title="Enhanced Voice Input Test", layout="wide")
    st.title("🎤 Enhanced Voice Input Component Test")
    
    # Test enhanced voice input
    voice_response = enhanced_voice_text_input(
        label="Test Enhanced Voice Input",
        key="test_enhanced",
        placeholder="Type or speak your response...",
        height=150,
        language_hint="hi",
        max_recording_time=30
    )
    
    if voice_response:
        st.markdown("### Your Response:")
        st.text_area("Response:", value=voice_response, height=100, disabled=True)
    
    # Test quick voice input
    st.markdown("### Quick Voice Test")
    quick_result = quick_voice_input(
        key="test_quick",
        button_text="🎤 Record 10 seconds",
        language_hint="hi",
        recording_duration=10
    )
    
    if quick_result:
        st.success(f"Quick voice result: {quick_result}")
    
    # Show system status
    st.markdown("### System Status")
    voice_input_status()
