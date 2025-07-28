"""
Voice Input System for Army Mental Health Assessment
Supports Hindi and English voice recognition with microphone integration
"""
import streamlit as st
import tempfile
import os
from typing import Optional, Dict, Any
import json

# Try to import speech recognition libraries
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("speech_recognition not available")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("whisper not available")

try:
    import pydub
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("pydub not available")

class VoiceInputSystem:
    """
    Comprehensive voice input system with microphone support
    """
    
    def __init__(self):
        self.recognizer = None
        self.whisper_model = None
        self.setup_recognizers()
    
    def setup_recognizers(self):
        """Setup speech recognition systems"""
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            print("✓ Speech recognition initialized")
        
        if WHISPER_AVAILABLE:
            try:
                # Load small model for CPU efficiency
                self.whisper_model = whisper.load_model("base")
                print("✓ Whisper model loaded")
            except Exception as e:
                print(f"Error loading Whisper: {e}")
                self.whisper_model = None
    
    def render_voice_input_interface(self, language: str = "hi") -> Optional[str]:
        """
        Render voice input interface with microphone
        Returns transcribed text or None
        """
        st.subheader("🎤 Voice Input" if language == "en" else "🎤 आवाज़ इनपुट")
        
        # Language selection for voice
        voice_lang = st.selectbox(
            "Voice Language" if language == "en" else "आवाज़ की भाषा",
            ["Hindi (हिंदी)", "English"],
            key="voice_language"
        )
        
        # Audio recording interface
        audio_data = st.audio_input(
            "Record your voice" if language == "en" else "अपनी आवाज़ रिकॉर्ड करें",
            key="voice_recorder"
        )
        
        transcribed_text = None
        
        if audio_data is not None:
            # Process the audio
            with st.spinner("Processing audio..." if language == "en" else "ऑडियो प्रोसेस कर रहे हैं..."):
                transcribed_text = self.process_audio(audio_data, voice_lang, language)
        
        # Manual text input as fallback
        st.markdown("---")
        st.subheader("✍️ Text Input" if language == "en" else "✍️ टेक्स्ट इनपुट")
        
        manual_text = st.text_area(
            "Or type your response here" if language == "en" else "या यहाँ अपना जवाब टाइप करें",
            height=100,
            key="manual_text_input"
        )
        
        # Return transcribed text or manual text
        return transcribed_text or manual_text
    
    def process_audio(self, audio_data, voice_lang: str, ui_language: str) -> Optional[str]:
        """
        Process audio data and return transcribed text
        """
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_data.read())
                audio_path = tmp_file.name
            
            # Try different transcription methods
            transcribed_text = None
            
            # Method 1: Whisper (best for multilingual)
            if self.whisper_model:
                transcribed_text = self.transcribe_with_whisper(audio_path, voice_lang)
            
            # Method 2: Google Speech Recognition (fallback)
            if not transcribed_text and SPEECH_RECOGNITION_AVAILABLE:
                transcribed_text = self.transcribe_with_google(audio_path, voice_lang)
            
            # Method 3: Simple audio analysis (final fallback)
            if not transcribed_text:
                transcribed_text = self.analyze_audio_simple(audio_path)
            
            # Clean up temporary file
            try:
                os.unlink(audio_path)
            except:
                pass
            
            if transcribed_text:
                st.success(f"Transcribed: {transcribed_text}")
                return transcribed_text
            else:
                st.error("Could not transcribe audio" if ui_language == "en" else "ऑडियो ट्रांसक्राइब नहीं हो सका")
                return None
                
        except Exception as e:
            st.error(f"Error processing audio: {e}")
            return None
    
    def transcribe_with_whisper(self, audio_path: str, voice_lang: str) -> Optional[str]:
        """Transcribe audio using Whisper"""
        try:
            # Set language for Whisper
            lang_code = "hi" if "Hindi" in voice_lang else "en"
            
            result = self.whisper_model.transcribe(
                audio_path,
                language=lang_code,
                fp16=False  # CPU compatibility
            )
            
            return result["text"].strip()
            
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            return None
    
    def transcribe_with_google(self, audio_path: str, voice_lang: str) -> Optional[str]:
        """Transcribe audio using Google Speech Recognition"""
        try:
            # Convert audio format if needed
            if PYDUB_AVAILABLE:
                audio = AudioSegment.from_file(audio_path)
                audio = audio.set_frame_rate(16000).set_channels(1)
                
                # Save as WAV
                wav_path = audio_path.replace('.wav', '_converted.wav')
                audio.export(wav_path, format="wav")
                audio_path = wav_path
            
            # Use speech recognition
            with sr.AudioFile(audio_path) as source:
                audio_data = self.recognizer.record(source)
            
            # Set language
            lang_code = "hi-IN" if "Hindi" in voice_lang else "en-US"
            
            text = self.recognizer.recognize_google(audio_data, language=lang_code)
            return text
            
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Google Speech Recognition error: {e}")
            return None
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return None
    
    def analyze_audio_simple(self, audio_path: str) -> Optional[str]:
        """Simple audio analysis fallback"""
        try:
            # Basic audio file validation
            file_size = os.path.getsize(audio_path)
            if file_size > 1000:  # At least 1KB
                return "[Audio recorded - please type your response]"
            else:
                return None
        except:
            return None
    
    def render_voice_assessment_interface(self, language: str = "hi") -> Dict[str, Any]:
        """
        Render complete voice assessment interface
        """
        st.markdown("### 🎤 Voice-Based Mental Health Assessment" if language == "en" else "### 🎤 आवाज़-आधारित मानसिक स्वास्थ्य मूल्यांकन")
        
        # Instructions
        instructions = {
            "en": """
            **Instructions:**
            1. Click the microphone button below
            2. Speak clearly about how you're feeling
            3. You can speak in Hindi or English
            4. The system will analyze your speech for emotional indicators
            """,
            "hi": """
            **निर्देश:**
            1. नीचे माइक्रोफोन बटन पर क्लिक करें
            2. अपनी भावनाओं के बारे में स्पष्ट रूप से बोलें
            3. आप हिंदी या अंग्रेजी में बोल सकते हैं
            4. सिस्टम आपकी आवाज़ में भावनात्मक संकेतकों का विश्लेषण करेगा
            """
        }
        
        st.markdown(instructions[language])
        
        # Voice input
        voice_text = self.render_voice_input_interface(language)
        
        results = {}
        
        if voice_text and len(voice_text.strip()) > 10:
            st.markdown("---")
            st.subheader("Analysis Results" if language == "en" else "विश्लेषण परिणाम")
            
            # Analyze the voice text
            results = self.analyze_voice_text(voice_text, language)
            
            # Display results
            self.display_voice_analysis_results(results, language)
        
        return results
    
    def analyze_voice_text(self, text: str, language: str) -> Dict[str, Any]:
        """
        Analyze voice text for mental health indicators
        """
        # Simple keyword-based analysis
        hindi_negative_keywords = [
            "दुखी", "परेशान", "चिंता", "डर", "गुस्सा", "थका", "अकेला",
            "निराश", "बेचैन", "तनाव", "समस्या", "मुश्किल", "बुरा"
        ]
        
        english_negative_keywords = [
            "sad", "worried", "anxious", "scared", "angry", "tired", "lonely",
            "depressed", "stressed", "problem", "difficult", "bad", "upset"
        ]
        
        hindi_positive_keywords = [
            "खुश", "अच्छा", "ठीक", "बेहतर", "शांत", "आराम", "संतुष्ट", "प्रसन्न"
        ]
        
        english_positive_keywords = [
            "happy", "good", "fine", "better", "calm", "relaxed", "satisfied", "pleased"
        ]
        
        text_lower = text.lower()
        
        # Count keywords
        negative_count = 0
        positive_count = 0
        
        for keyword in hindi_negative_keywords + english_negative_keywords:
            negative_count += text_lower.count(keyword)
        
        for keyword in hindi_positive_keywords + english_positive_keywords:
            positive_count += text_lower.count(keyword)
        
        # Determine sentiment
        if negative_count > positive_count:
            sentiment = "negative"
            mental_state = "moderate" if negative_count > 2 else "mild"
        elif positive_count > negative_count:
            sentiment = "positive"
            mental_state = "normal"
        else:
            sentiment = "neutral"
            mental_state = "mild"
        
        # Calculate score
        total_words = len(text.split())
        sentiment_score = max(0, min(100, 50 + (positive_count - negative_count) * 10))
        
        return {
            "text": text,
            "sentiment": sentiment,
            "mental_state": mental_state,
            "sentiment_score": sentiment_score,
            "word_count": total_words,
            "negative_indicators": negative_count,
            "positive_indicators": positive_count,
            "analysis_method": "voice_keyword_analysis"
        }
    
    def display_voice_analysis_results(self, results: Dict[str, Any], language: str):
        """Display voice analysis results"""
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Sentiment Score" if language == "en" else "भावना स्कोर",
                f"{results['sentiment_score']:.1f}%"
            )
        
        with col2:
            st.metric(
                "Mental State" if language == "en" else "मानसिक स्थिति",
                results['mental_state'].title()
            )
        
        with col3:
            st.metric(
                "Word Count" if language == "en" else "शब्द संख्या",
                results['word_count']
            )
        
        # Sentiment indicator
        sentiment_colors = {
            "positive": "green",
            "neutral": "orange", 
            "negative": "red"
        }
        
        color = sentiment_colors.get(results['sentiment'], 'gray')
        
        st.markdown(f"""
        <div style="padding: 10px; border-radius: 5px; background-color: {color}20; border-left: 4px solid {color};">
            <strong>{'Overall Sentiment' if language == 'en' else 'समग्र भावना'}:</strong> {results['sentiment'].title()}
        </div>
        """, unsafe_allow_html=True)
        
        # Recommendations
        if results['sentiment'] == 'negative' or results['mental_state'] in ['moderate', 'severe']:
            st.warning(
                "Consider speaking with a counselor or mental health professional." if language == "en" 
                else "किसी काउंसलर या मानसिक स्वास्थ्य पेशेवर से बात करने पर विचार करें।"
            )

# Global instance
voice_input_system = VoiceInputSystem()
