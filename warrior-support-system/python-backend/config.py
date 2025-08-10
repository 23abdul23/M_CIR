"""
Configuration settings for Army Mental Health Assessment System
"""
import os
from pathlib import Path
from typing import Dict, List

# Base directory
BASE_DIR = Path(__file__).parent

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/army_mental_health.db")

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Model Configuration - CPU ONLY, OFFLINE CAPABLE
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Force CPU usage - NO GPU
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TORCH_USE_CUDA"] = "0"

# Hindi Sentiment Analysis Models (CPU-only, offline-capable)
HINDI_MODELS = {
    "sentiment_primary": {
        "model_name": "ai4bharat/indic-bert",
        "local_path": MODELS_DIR / "indic_bert",
        "description": "AI4Bharat IndicBERT for Hindi sentiment analysis (CPU-only)",
        "device": "cpu",
        "offline_mode": True,
        "priority": 1
    },
    "sentiment_secondary": {
        "model_name": "l3cube-pune/hindi-bert-v2",
        "local_path": MODELS_DIR / "hindi_bert_v2",
        "description": "L3Cube Hindi BERT v2 for sentiment analysis (CPU-only)",
        "device": "cpu",
        "offline_mode": True,
        "priority": 2
    },
    "sentiment_fallback": {
        "model_name": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "local_path": MODELS_DIR / "roberta_sentiment",
        "description": "RoBERTa English sentiment (fallback only)",
        "device": "cpu",
        "offline_mode": True,
        "priority": 3
    },
    "text_classification": {
        "model_name": "ai4bharat/indic-bert",
        "local_path": MODELS_DIR / "indic_bert",
        "description": "Hindi text classification model (CPU-only)",
        "device": "cpu",
        "offline_mode": True
    }
}

# Model loading configuration
MODEL_CONFIG = {
    "device": "cpu",  # Force CPU usage
    "torch_dtype": "float32",  # Use float32 for CPU
    "low_cpu_mem_usage": True,
    "local_files_only": True,  # Offline mode after download
    "use_auth_token": False,
    "trust_remote_code": False
}

# Mental Health Assessment Configuration
MENTAL_STATE_THRESHOLDS = {
    "normal": {"min": 0, "max": 25, "label": "Normal", "color": "green"},
    "mild": {"min": 26, "max": 50, "label": "Mild", "color": "yellow"},
    "moderate": {"min": 51, "max": 75, "label": "Moderate", "color": "orange"},
    "severe": {"min": 76, "max": 100, "label": "Severe", "color": "red"}
}

# Sentiment Analysis Weights
SENTIMENT_WEIGHTS = {
    "positive": 0.2,
    "neutral": 0.5,
    "negative": 0.8
}

# Enhanced Keywords for Mental Health Assessment (Hindi)
MENTAL_HEALTH_KEYWORDS = {
    "positive": {
        "hindi": [
            # Basic positive emotions
            "खुश", "प्रसन्न", "अच्छा", "बेहतर", "सकारात्मक", "शांत", "आनंद", "हर्ष",
            # Confidence and strength
            "आत्मविश्वास", "मजबूत", "स्वस्थ", "तंदुरुस्त", "फिट", "सक्षम", "योग्य",
            # Satisfaction and contentment
            "संतुष्ट", "प्रसन्न", "राजी", "खुशी", "गर्व", "सम्मान", "उत्साह",
            # Military positive terms
            "तैयार", "सेवा", "कर्तव्य", "मिशन", "टीम", "साथी", "यूनिट", "सहयोग"
        ],
        "weight": -0.4,  # Strong negative weight for positive impact
        "severity_weight": -2.0,
        "description": "Positive mental health indicators"
    },
    "stress": {
        "hindi": [
            "तनाव", "चिंता", "परेशानी", "दबाव", "बेचैनी", "व्याकुलता", "घबराहट",
            "बोझ", "भार", "मुश्किल", "कठिनाई", "समस्या", "दिक्कत", "परेशान"
        ],
        "weight": 0.7,
        "severity_weight": 3.0,
        "description": "Stress and pressure indicators"
    },
    "depression": {
        "hindi": [
            "उदासी", "अवसाद", "निराशा", "हताशा", "दुख", "गम", "शोक", "दुखी",
            "उदास", "निराश", "हताश", "खाली", "बेकार", "व्यर्थ", "अकेला"
        ],
        "weight": 0.9,
        "severity_weight": 4.5,
        "description": "Depression and sadness indicators"
    },
    "anxiety": {
        "hindi": [
            "घबराहट", "डर", "भय", "चिंता", "बेचैनी", "व्याकुलता", "आशंका",
            "फिक्र", "सोच", "परेशानी", "डरना", "घबराना", "चिंतित", "बेचैन"
        ],
        "weight": 0.8,
        "severity_weight": 4.0,
        "description": "Anxiety and worry indicators"
    },
    "anger": {
        "hindi": [
            "गुस्सा", "क्रोध", "चिढ़", "नाराजगी", "रोष", "कोप", "आक्रोश",
            "गुस्से", "क्रोधित", "चिढ़ना", "नाराज", "रुष्ट", "खीझ", "झुंझलाहट"
        ],
        "weight": 0.6,
        "severity_weight": 3.5,
        "description": "Anger and irritation indicators"
    },
    "sleep_issues": {
        "hindi": [
            "नींद", "अनिद्रा", "जागना", "सोना", "नींद न आना", "नींद नहीं आती",
            "थकान", "थका", "सुस्त", "आलस", "कमजोर", "बेदम", "निढाल"
        ],
        "weight": 0.7,
        "severity_weight": 3.0,
        "description": "Sleep and fatigue related issues"
    },
    "physical_health": {
        "hindi": [
            "बीमार", "दर्द", "पीड़ा", "तकलीफ", "कष्ट", "बीमारी", "रोग",
            "स्वस्थ", "तंदुरुस्त", "फिट", "मजबूत", "ताकतवर", "शक्तिशाली"
        ],
        "weight": 0.5,
        "severity_weight": 2.5,
        "description": "Physical health indicators"
    },
    "social_support": {
        "hindi": [
            "साथी", "दोस्त", "मित्र", "परिवार", "सहयोग", "मदद", "सहायता",
            "टीम", "यूनिट", "समूह", "साथ", "सहारा", "सपोर्ट", "अकेला", "अकेलापन"
        ],
        "weight": -0.2,  # Mostly positive, but "अकेला" is negative
        "severity_weight": -1.0,
        "description": "Social support and isolation indicators"
    }
}

# Health Suggestions based on severity
HEALTH_SUGGESTIONS = {
    "normal": [
        "आपकी मानसिक स्थिति सामान्य है। नियमित व्यायाम और ध्यान जारी रखें।",
        "संतुलित आहार लें और पर्याप्त नींद लें।",
        "सामाजिक गतिविधियों में भाग लेते रहें।",
        "तनाव प्रबंधन तकनीकों का अभ्यास करें।"
    ],
    "mild": [
        "हल्के तनाव के लक्षण दिख रहे हैं। दैनिक ध्यान का अभ्यास करें।",
        "नियमित व्यायाम करें और पर्याप्त आराम लें।",
        "किसी विश्वसनीय व्यक्ति से बात करें।",
        "गहरी सांस लेने की तकनीक का अभ्यास करें।",
        "यदि समस्या बनी रहे तो परामर्शदाता से मिलें।"
    ],
    "moderate": [
        "मध्यम स्तर की मानसिक स्वास्थ्य समस्याएं हैं। तुरंत परामर्शदाता से मिलें।",
        "नियमित चिकित्सा जांच कराएं।",
        "तनाव कम करने वाली गतिविधियों में भाग लें।",
        "परिवार और दोस्तों का साथ लें।",
        "पेशेवर मानसिक स्वास्थ्य सेवाओं का उपयोग करें।"
    ],
    "severe": [
        "गंभीर मानसिक स्वास्थ्य समस्याएं हैं। तुरंत मानसिक स्वास्थ्य विशेषज्ञ से संपर्क करें।",
        "24/7 हेल्पलाइन नंबर: 1075 (राष्ट्रीय मानसिक स्वास्थ्य हेल्पलाइन)",
        "निकटतम अस्पताल या मानसिक स्वास्थ्य केंद्र में जाएं।",
        "परिवार के सदस्यों को तुरंत सूचित करें।",
        "अकेले न रहें, किसी के साथ रहें।"
    ]
}

# Sample questionnaires for the assessment engine
QUESTIONNAIRES = {
    "phq9": {
        "title": "PHQ-9 Depression Assessment",
        "description": "Patient Health Questionnaire-9",
        "questions": [
            {"text": "Little interest or pleasure in doing things", "type": "scale"},
            {"text": "Feeling down, depressed, or hopeless", "type": "scale"},
            {"text": "Trouble falling or staying asleep", "type": "scale"},
            {"text": "Feeling tired or having little energy", "type": "scale"},
            {"text": "Poor appetite or overeating", "type": "scale"},
            {"text": "Feeling bad about yourself", "type": "scale"},
            {"text": "Trouble concentrating", "type": "scale"},
            {"text": "Moving or speaking slowly", "type": "scale"},
            {"text": "Thoughts of self-harm", "type": "scale"}
        ]
    },
    "gad7": {
        "title": "GAD-7 Anxiety Assessment",
        "description": "Generalized Anxiety Disorder-7",
        "questions": [
            {"text": "Feeling nervous, anxious, or on edge", "type": "scale"},
            {"text": "Not being able to stop or control worrying", "type": "scale"},
            {"text": "Worrying too much about different things", "type": "scale"},
            {"text": "Trouble relaxing", "type": "scale"},
            {"text": "Being so restless that it's hard to sit still", "type": "scale"},
            {"text": "Becoming easily annoyed or irritable", "type": "scale"},
            {"text": "Feeling afraid as if something awful might happen", "type": "scale"}
        ]
    }
}

# Default Admin User
DEFAULT_ADMIN = {
    "username": "admin",
    "email": "admin@army.gov.in",
    "password": "admin123",  # Change in production
    "role": "admin"
}

# Application Settings
APP_SETTINGS = {
    "title": "Army Mental Health Assessment System",
    "description": "Mental health assessment system for army personnel using Hindi questionnaires",
    "version": "1.0.0",
    "api_port": 8002,
    "frontend_port": 8503
}

# File Upload Settings
UPLOAD_SETTINGS = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "allowed_extensions": [".txt", ".csv", ".xlsx"],
    "upload_dir": BASE_DIR / "uploads"
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    "file": BASE_DIR / "logs" / "app.log"
}

# Create necessary directories
(BASE_DIR / "logs").mkdir(exist_ok=True)
(BASE_DIR / "uploads").mkdir(exist_ok=True)
(BASE_DIR / "data" / "questionnaires").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "data" / "keywords").mkdir(parents=True, exist_ok=True)
(BASE_DIR / "data" / "suggestions").mkdir(parents=True, exist_ok=True)
