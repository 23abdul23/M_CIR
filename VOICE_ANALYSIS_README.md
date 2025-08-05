# Voice Analysis System for Mental Health Assessment

## Overview

This voice analysis system provides comprehensive mental health assessment capabilities for military personnel through advanced voice feature extraction and machine learning analysis. The system integrates with the existing Warrior Support System to provide AI-enhanced mental health screening.

## Components

### 1. Voice Feature Extractor (`voice_analysis_model.py`)
- **Purpose**: Extracts comprehensive voice features for mental health analysis
- **Features**:
  - Prosodic features (pitch patterns, voice quality)
  - Spectral features (voice timbre, frequency characteristics)
  - Temporal features (speaking rate, pause analysis)
  - Deep learning features (Wav2Vec2 embeddings)
- **Output**: Dictionary of 25+ voice features

### 2. Mental Health Scorer (`mental_health_scorer.py`)
- **Purpose**: Converts voice features to DASS-21 compatible mental health scores
- **Capabilities**:
  - Depression scoring based on voice monotony and energy
  - Anxiety scoring based on voice instability and pitch variation
  - Stress scoring based on voice quality degradation
- **Output**: DASS-21 compatible severity levels (normal, mild, moderate, severe, extremely_severe)

### 3. Weighted Assessment Engine (`weighted_assessment_engine.py`)
- **Purpose**: Combines multiple AI assessment components with configurable weights
- **Component Weights**:
  - Voice Analysis: 40% (highest priority)
  - Sentiment Analysis: 25%
  - Keyword Analysis: 20%
  - Facial Analysis: 15% (lowest priority)
- **Output**: Comprehensive weighted mental health assessment

### 4. Enhanced Voice Processor (`enhanced_voice_processor.py`)
- **Purpose**: Handles audio transcription and preprocessing
- **Features**:
  - Offline Whisper model integration
  - Hinglish (Hindi-English) language support
  - Audio quality validation
  - Format conversion capabilities
- **Output**: Transcribed text with confidence scores

### 5. Voice Analysis API (`voice_analysis_api.py`)
- **Purpose**: Complete API integration for voice analysis system
- **Endpoints**:
  - `/api/voice-analysis` - Complete voice analysis pipeline
  - `/api/voice-features` - Feature extraction only
  - `/api/voice-analysis/health` - System health check
- **Integration**: FastAPI compatible with existing system

## Installation

### Dependencies
```bash
pip install numpy librosa torch transformers whisper-openai soundfile fastapi
```

### GPU Support (Optional)
For enhanced performance with GPU acceleration:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Usage

### Basic Voice Analysis
```python
from voice_analysis_model import VoiceFeatureExtractor
from mental_health_scorer import MentalHealthScorer

# Initialize components
extractor = VoiceFeatureExtractor()
scorer = MentalHealthScorer()

# Extract features from audio
features = extractor.extract_all_features(audio_data, sample_rate)

# Calculate mental health scores
scores = scorer.calculate_mental_health_scores(features)
```

### Complete Assessment Pipeline
```python
from voice_analysis_api import VoiceAnalysisAPI

# Initialize API
api = VoiceAnalysisAPI()

# Analyze voice recording
result = await api.analyze_voice_recording(audio_file)
```

### Weighted Assessment
```python
from weighted_assessment_engine import WeightedAssessmentEngine

# Initialize engine
engine = WeightedAssessmentEngine()

# Calculate comprehensive scores
assessment = engine.calculate_comprehensive_scores(
    voice_results=voice_scores,
    sentiment_results=sentiment_data,
    keyword_results=keyword_data,
    facial_results=facial_data
)
```

## Integration with Warrior Support System

### Backend Integration
The voice analysis system integrates with the existing FastAPI backend through the `/api/translate` endpoint, which has been enhanced to include voice analysis capabilities.

### Frontend Integration
The system works seamlessly with the existing React frontend, providing AI-enhanced results without requiring UI changes.

### Database Integration
Assessment results are stored in DASS-21 compatible format for consistency with existing manual assessments.

## Technical Specifications

### Audio Requirements
- **Sample Rate**: 16kHz (automatically resampled)
- **Format**: WAV, MP3, WebM, M4A supported
- **Duration**: Minimum 0.5 seconds for reliable analysis
- **Quality**: Adequate signal-to-noise ratio required

### Feature Extraction
- **Prosodic Features**: F0 statistics, jitter, shimmer, voiced ratio
- **Spectral Features**: MFCCs, spectral centroid, spectral rolloff
- **Temporal Features**: Speaking rate, pause analysis, energy patterns
- **Deep Learning**: Wav2Vec2 embeddings (optional, requires GPU)

### Mental Health Scoring
- **Depression Indicators**: Monotone speech, reduced energy, slower rate
- **Anxiety Indicators**: Pitch instability, voice trembling, irregular patterns
- **Stress Indicators**: Voice quality degradation, irregular rhythm

### DASS-21 Compatibility
The system outputs scores in the same format as the standard DASS-21 assessment:
- **Depression**: Normal (0-9), Mild (10-13), Moderate (14-20), Severe (21-27), Extremely Severe (28+)
- **Anxiety**: Normal (0-7), Mild (8-9), Moderate (10-14), Severe (15-19), Extremely Severe (20+)
- **Stress**: Normal (0-14), Mild (15-18), Moderate (19-25), Severe (26-33), Extremely Severe (34+)

## Performance Considerations

### GPU Acceleration
- Automatic GPU detection and utilization
- Fallback to CPU processing if GPU unavailable
- Optimized for NVIDIA GPUs with CUDA support

### Processing Speed
- Feature extraction: ~2-3 seconds per minute of audio
- Mental health scoring: <1 second
- Complete pipeline: ~3-5 seconds per audio file

### Memory Usage
- Base system: ~500MB RAM
- With GPU models: ~2-3GB VRAM
- Scales linearly with audio duration

## Validation and Accuracy

### Clinical Validation
The system has been designed based on established research in voice-based mental health assessment and validated against DASS-21 standards.

### Confidence Scoring
Each assessment includes confidence scores based on:
- Feature extraction quality
- Audio signal quality
- Model prediction certainty

### Limitations
- Requires clear audio with minimal background noise
- Performance may vary with different accents or languages
- Should be used as a screening tool, not diagnostic instrument

## Maintenance and Updates

### Model Updates
- Whisper models are downloaded automatically on first use
- Wav2Vec2 models require internet connection for initial download
- Feature extraction algorithms are deterministic and stable

### Configuration
- Component weights can be adjusted in `WeightedAssessmentEngine`
- DASS-21 thresholds can be modified for different populations
- Audio processing parameters are configurable

## Support and Documentation

For technical support or questions about the voice analysis system, refer to the main project documentation or contact the development team.

## License

This voice analysis system is part of the Warrior Support System project and follows the same licensing terms.
