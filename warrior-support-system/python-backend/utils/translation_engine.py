"""
Enhanced Hindi-English Translation Engine
Provides better translation capabilities for the Army Mental Health Assessment System
"""
import re
from typing import Dict, List, Optional, Tuple
import unicodedata

class HindiEnglishTranslator:
    """
    Enhanced translation engine for Hindi-English conversion
    Uses multiple approaches for better accuracy
    """
    
    def __init__(self):
        self.hindi_to_english_dict = self._load_hindi_english_dictionary()
        self.english_to_hindi_dict = self._load_english_hindi_dictionary()
        self.transliteration_map = self._load_transliteration_map()
        self.mental_health_terms = self._load_mental_health_terms()
    
    def _load_hindi_english_dictionary(self) -> Dict[str, str]:
        """Load Hindi to English dictionary"""
        return {
            # Basic words
            "मैं": "I", "आप": "you", "हम": "we", "वे": "they",
            "है": "is", "हैं": "are", "था": "was", "थे": "were",
            "और": "and", "या": "or", "लेकिन": "but", "क्योंकि": "because",
            
            # Mental health terms
            "अवसाद": "depression", "चिंता": "anxiety", "तनाव": "stress",
            "डर": "fear", "घबराहट": "nervousness", "परेशानी": "trouble",
            "दुख": "sadness", "खुशी": "happiness", "गुस्सा": "anger",
            "चिड़चिड़ाहट": "irritability", "बेचैनी": "restlessness",
            
            # Feelings and emotions
            "खुश": "happy", "दुखी": "sad", "परेशान": "worried",
            "डरा हुआ": "scared", "गुस्से में": "angry", "शांत": "calm",
            "थका हुआ": "tired", "ऊर्जावान": "energetic",
            
            # Physical symptoms
            "सिरदर्द": "headache", "पेट दर्द": "stomach ache", "सांस लेने में तकलीफ": "breathing difficulty",
            "दिल की धड़कन": "heartbeat", "पसीना": "sweating", "कांपना": "trembling",
            
            # Sleep and appetite
            "नींद": "sleep", "भूख": "appetite", "खाना": "food",
            "सोना": "to sleep", "जागना": "to wake up", "सपने": "dreams",
            "बुरे सपने": "nightmares",
            
            # Social and work
            "काम": "work", "परिवार": "family", "दोस्त": "friend",
            "रिश्ते": "relationships", "समाज": "society", "अकेलापन": "loneliness",
            
            # Time expressions
            "आज": "today", "कल": "yesterday/tomorrow", "रोज": "daily",
            "हमेशा": "always", "कभी": "sometimes", "कभी नहीं": "never",
            
            # Intensity words
            "बहुत": "very", "थोड़ा": "little", "ज्यादा": "more",
            "कम": "less", "अधिक": "much", "बिल्कुल": "completely",
            
            # Army specific terms
            "सेना": "army", "सैनिक": "soldier", "अधिकारी": "officer",
            "ड्यूटी": "duty", "मिशन": "mission", "युद्ध": "war",
            "प्रशिक्षण": "training", "कमांडर": "commander",
            
            # Medical terms
            "डॉक्टर": "doctor", "दवाई": "medicine", "इलाज": "treatment",
            "अस्पताल": "hospital", "जांच": "examination", "रिपोर्ट": "report",
            
            # Common phrases
            "मुझे लगता है": "I feel", "मैं सोचता हूं": "I think",
            "मुझे डर लगता है": "I am afraid", "मैं परेशान हूं": "I am worried",
            "मैं खुश हूं": "I am happy", "मैं दुखी हूं": "I am sad",
            
            # Question words
            "क्या": "what", "कैसे": "how", "कब": "when",
            "कहां": "where", "क्यों": "why", "कौन": "who",
            
            # Negation
            "नहीं": "no/not", "ना": "no", "बिल्कुल नहीं": "not at all",
            
            # Frequency
            "रोज": "daily", "हफ्ते में": "weekly", "महीने में": "monthly",
            "साल में": "yearly", "कभी कभी": "sometimes"
        }
    
    def _load_english_hindi_dictionary(self) -> Dict[str, str]:
        """Load English to Hindi dictionary"""
        # Reverse the Hindi-English dictionary
        return {v: k for k, v in self.hindi_to_english_dict.items()}
    
    def _load_transliteration_map(self) -> Dict[str, str]:
        """Load Devanagari to Roman transliteration map"""
        return {
            'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ii', 'उ': 'u', 'ऊ': 'uu',
            'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
            'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'nga',
            'च': 'cha', 'छ': 'chha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'nya',
            'ट': 'ta', 'ठ': 'tha', 'ड': 'da', 'ढ': 'dha', 'ण': 'na',
            'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
            'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
            'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va',
            'श': 'sha', 'ष': 'sha', 'स': 'sa', 'ह': 'ha',
            'ा': 'aa', 'ि': 'i', 'ी': 'ii', 'ु': 'u', 'ू': 'uu',
            'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', '्': ''
        }
    
    def _load_mental_health_terms(self) -> Dict[str, Dict[str, str]]:
        """Load specialized mental health terminology"""
        return {
            "conditions": {
                "depression": "अवसाद", "anxiety": "चिंता", "stress": "तनाव",
                "ptsd": "पीटीएसडी", "panic": "घबराहट", "phobia": "फोबिया"
            },
            "symptoms": {
                "sadness": "उदासी", "worry": "चिंता", "fear": "डर",
                "anger": "गुस्सा", "irritability": "चिड़चिड़ाहट",
                "fatigue": "थकान", "insomnia": "अनिद्रा"
            },
            "treatments": {
                "therapy": "चिकित्सा", "counseling": "परामर्श",
                "medication": "दवाई", "exercise": "व्यायाम",
                "meditation": "ध्यान", "yoga": "योग"
            }
        }
    
    def translate_hindi_to_english(self, hindi_text: str) -> str:
        """
        Translate Hindi text to English
        
        Args:
            hindi_text: Hindi text to translate
            
        Returns:
            English translation
        """
        if not hindi_text or not hindi_text.strip():
            return ""
        
        # Clean and normalize text
        cleaned_text = self._clean_text(hindi_text)
        
        # Try word-by-word translation first
        words = cleaned_text.split()
        translated_words = []
        
        for word in words:
            # Remove punctuation for lookup
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            # Direct dictionary lookup
            if clean_word in self.hindi_to_english_dict:
                translated_words.append(self.hindi_to_english_dict[clean_word])
            # Try partial matches
            elif self._find_partial_match(clean_word, self.hindi_to_english_dict):
                match = self._find_partial_match(clean_word, self.hindi_to_english_dict)
                translated_words.append(match)
            # Transliterate if no translation found
            else:
                transliterated = self._transliterate_word(clean_word)
                translated_words.append(transliterated if transliterated else word)
        
        # Join and clean up the result
        result = " ".join(translated_words)
        return self._post_process_translation(result)
    
    def translate_english_to_hindi(self, english_text: str) -> str:
        """
        Translate English text to Hindi
        
        Args:
            english_text: English text to translate
            
        Returns:
            Hindi translation
        """
        if not english_text or not english_text.strip():
            return ""
        
        # Clean and normalize text
        cleaned_text = english_text.lower().strip()
        
        # Try word-by-word translation
        words = cleaned_text.split()
        translated_words = []
        
        for word in words:
            # Remove punctuation for lookup
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            # Direct dictionary lookup
            if clean_word in self.english_to_hindi_dict:
                translated_words.append(self.english_to_hindi_dict[clean_word])
            # Try partial matches
            elif self._find_partial_match(clean_word, self.english_to_hindi_dict):
                match = self._find_partial_match(clean_word, self.english_to_hindi_dict)
                translated_words.append(match)
            # Keep original if no translation found
            else:
                translated_words.append(word)
        
        return " ".join(translated_words)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Normalize Unicode characters
        text = unicodedata.normalize('NFKC', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _find_partial_match(self, word: str, dictionary: Dict[str, str]) -> Optional[str]:
        """Find partial matches in dictionary"""
        for key, value in dictionary.items():
            if word in key or key in word:
                return value
        return None
    
    def _transliterate_word(self, hindi_word: str) -> str:
        """Transliterate Hindi word to Roman script"""
        result = ""
        for char in hindi_word:
            if char in self.transliteration_map:
                result += self.transliteration_map[char]
            else:
                result += char
        return result
    
    def _post_process_translation(self, text: str) -> str:
        """Post-process translated text for better readability"""
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Fix common grammar issues
        text = re.sub(r'\bi am\b', 'I am', text, flags=re.IGNORECASE)
        text = re.sub(r'\bi\b', 'I', text)
        
        return text
    
    def detect_language(self, text: str) -> str:
        """
        Detect if text is primarily Hindi or English
        
        Args:
            text: Text to analyze
            
        Returns:
            'hindi' or 'english'
        """
        if not text:
            return 'english'
        
        # Count Devanagari characters
        hindi_chars = 0
        total_chars = 0
        
        for char in text:
            if char.isalpha():
                total_chars += 1
                if '\u0900' <= char <= '\u097F':  # Devanagari Unicode range
                    hindi_chars += 1
        
        if total_chars == 0:
            return 'english'
        
        hindi_ratio = hindi_chars / total_chars
        return 'hindi' if hindi_ratio > 0.5 else 'english'
    
    def smart_translate(self, text: str, target_language: str = None) -> Dict[str, str]:
        """
        Smart translation that detects source language and translates accordingly
        
        Args:
            text: Text to translate
            target_language: Target language ('hindi' or 'english'), auto-detect if None
            
        Returns:
            Dictionary with original text, detected language, and translation
        """
        if not text:
            return {
                "original": "",
                "detected_language": "english",
                "translation": "",
                "target_language": target_language or "english"
            }
        
        detected_lang = self.detect_language(text)
        
        if target_language is None:
            # Auto-translate to opposite language
            target_language = 'english' if detected_lang == 'hindi' else 'hindi'
        
        if detected_lang == 'hindi' and target_language == 'english':
            translation = self.translate_hindi_to_english(text)
        elif detected_lang == 'english' and target_language == 'hindi':
            translation = self.translate_english_to_hindi(text)
        else:
            # Same language or no translation needed
            translation = text
        
        return {
            "original": text,
            "detected_language": detected_lang,
            "translation": translation,
            "target_language": target_language
        }

# Global translator instance
translator = HindiEnglishTranslator()
