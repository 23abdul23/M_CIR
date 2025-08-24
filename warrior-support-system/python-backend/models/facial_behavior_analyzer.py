#!/usr/bin/env python3
"""
Enhanced Facial Behavior Analysis for Army Mental Health Assessment
Combines OpenCV with deep learning models for accurate emotion recognition
Supports both CPU-only and GPU-accelerated processing
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import time
from datetime import datetime
import json
import math
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Context manager to suppress logging during analysis
import contextlib
import sys

@contextlib.contextmanager
def suppress_logging():
    """Context manager to suppress logging output during facial analysis"""
    old_level = logger.level
    logger.setLevel(logging.ERROR)
    try:
        yield
    finally:
        logger.setLevel(old_level)

class EmotionCNN(nn.Module):
    """
    Convolutional Neural Network for Facial Emotion Recognition
    Lightweight model for real-time emotion classification
    """

    def __init__(self, num_classes=7):
        super(EmotionCNN, self).__init__()

        # Convolutional layers
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

        # Pooling and dropout
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.5)

        # Fully connected layers
        self.fc1 = nn.Linear(128 * 6 * 6, 512)
        self.fc2 = nn.Linear(512, num_classes)

        # Activation
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        # Convolutional layers with pooling
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = self.pool(self.relu(self.conv3(x)))

        # Flatten for fully connected layers
        x = x.view(-1, 128 * 6 * 6)

        # Fully connected layers
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)

        return self.softmax(x)


class EnhancedFacialBehaviorAnalyzer:
    """
    Enhanced facial behavior analyzer with deep learning emotion recognition
    Combines OpenCV face detection with CNN-based emotion classification
    """

    def __init__(self, device="auto"):
        """Initialize the enhanced facial behavior analyzer"""
        # Auto-detect best device
        if device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info(f"🎮 GPU detected: {torch.cuda.get_device_name(0)}")
            else:
                self.device = "cpu"
                logger.info("💻 Using CPU (no GPU available)")
        else:
            self.device = device

        self.is_initialized = False
        self.emotion_history = []
        self.face_history = []
        self.baseline_measurements = {}

        # Emotion labels (FER2013 standard)
        self.emotion_labels = {
            0: 'angry',
            1: 'disgust',
            2: 'fear',
            3: 'happy',
            4: 'sad',
            5: 'surprise',
            6: 'neutral'
        }

        # Simple emotion weights for backward compatibility
        self.emotion_weights = {
            'angry': -0.7,      # Negative indicator
            'disgust': -0.5,    # Negative indicator
            'fear': -0.8,       # Strong negative indicator
            'happy': 0.8,       # Positive indicator
            'sad': -0.9,        # Strong negative indicator
            'surprise': 0.1,    # Neutral/slightly positive
            'neutral': 0.0      # Baseline
        }

        # Enhanced mental health emotion weights with stress factors
        self.emotion_stress_weights = {
            'happy': {
                'stress_factor': 0.1,      # Very low stress
                'mental_health_score': 0.9, # Very positive
                'confidence_multiplier': 1.2 # High confidence in positive assessment
            },
            'neutral': {
                'stress_factor': 0.3,      # Low stress
                'mental_health_score': 0.5, # Baseline
                'confidence_multiplier': 1.0 # Normal confidence
            },
            'surprise': {
                'stress_factor': 0.4,      # Mild stress
                'mental_health_score': 0.4, # Slightly below baseline
                'confidence_multiplier': 0.8 # Lower confidence (ambiguous)
            },
            'disgust': {
                'stress_factor': 0.6,      # Moderate stress
                'mental_health_score': 0.2, # Negative indicator
                'confidence_multiplier': 1.1 # Good confidence in negative assessment
            },
            'angry': {
                'stress_factor': 0.8,      # High stress
                'mental_health_score': 0.1, # Strong negative indicator
                'confidence_multiplier': 1.3 # Very high confidence
            },
            'fear': {
                'stress_factor': 0.85,     # Very high stress
                'mental_health_score': 0.05, # Very strong negative indicator
                'confidence_multiplier': 1.4 # Highest confidence in stress detection
            },
            'sad': {
                'stress_factor': 0.9,      # Highest stress factor
                'mental_health_score': 0.0, # Strongest negative indicator
                'confidence_multiplier': 1.5 # Maximum confidence in depression indicators
            }
        }

        # Enhanced stress level thresholds based on averaged stress factors
        self.stress_thresholds = {
            'low': 0.35,        # 0.0 - 0.35
            'moderate': 0.55,   # 0.35 - 0.55
            'high': 0.75,       # 0.55 - 0.75
            'severe': 1.0       # 0.75 - 1.0
        }

        # Frame analysis history for weighted averaging
        self.frame_analysis_history = []
        self.stress_factor_history = []
        self.confidence_history = []

        # OpenCV components
        self.face_cascade = None
        self.emotion_model = None

        # Initialize components
        self._initialize_components()

    def _initialize_components(self):
        """Initialize OpenCV and deep learning components"""
        try:
            logger.info("🎭 Initializing Enhanced Facial Behavior Analyzer...")

            # Initialize OpenCV face detection
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)

            if self.face_cascade.empty():
                logger.error("❌ Failed to load face cascade")
                return False

            # Initialize emotion recognition model
            self._initialize_emotion_model()

            # Confirm GPU setup
            if self.device == "cuda" and torch.cuda.is_available():
                torch.cuda.empty_cache()  # Clear GPU memory
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                logger.info(f"🎮 Using GPU: {torch.cuda.get_device_name(0)} ({gpu_memory:.1f}GB)")
            else:
                logger.info("💻 Using CPU for facial analysis")
                self.device = "cpu"

            self.is_initialized = True
            logger.info("✅ Enhanced Facial Behavior Analyzer initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize facial analyzer: {e}")
            return False

    def _initialize_emotion_model(self):
        """Initialize or load emotion recognition model"""
        try:
            # Create model
            self.emotion_model = EmotionCNN(num_classes=7)

            # Try to load pre-trained weights
            model_path = Path(__file__).parent / "weights" / "emotion_model.pth"

            if model_path.exists():
                logger.info("📦 Loading pre-trained emotion model...")
                self.emotion_model.load_state_dict(torch.load(model_path, map_location=self.device))
                logger.info("✅ Pre-trained emotion model loaded")
            else:
                logger.info("⚠️ No pre-trained model found - using random weights")
                logger.info("💡 Model will need training or use basic OpenCV analysis")

            # Move model to device
            self.emotion_model.to(self.device)
            self.emotion_model.eval()

            # Image preprocessing
            self.transform = transforms.Compose([
                transforms.Grayscale(),
                transforms.Resize((48, 48)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5], std=[0.5])
            ])

            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize emotion model: {e}")
            self.emotion_model = None
            return False

    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analyze a single frame for facial emotions and mental health indicators

        Args:
            frame: Input video frame (BGR format)

        Returns:
            Dictionary containing emotion analysis results
        """
        if not self.is_initialized:
            return {"error": "Analyzer not initialized"}

        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces with more lenient parameters
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,  # More sensitive scaling
                minNeighbors=3,    # Fewer neighbors required
                minSize=(20, 20),  # Smaller minimum size
                maxSize=(500, 500) # Larger maximum size
            )

            if len(faces) == 0:
                return {
                    "faces_detected": 0,
                    "emotions": [],
                    "stress_level": "unknown",
                    "confidence": 0.0
                }

            # Analyze each detected face
            face_emotions = []
            for (x, y, w, h) in faces:
                # Extract face ROI
                face_roi = gray[y:y+h, x:x+w]

                # Analyze emotion
                emotion_result = self._analyze_emotion(face_roi)
                emotion_result.update({
                    "face_location": (x, y, w, h),
                    "face_size": w * h
                })

                face_emotions.append(emotion_result)

            # Calculate overall stress level
            overall_stress = self._calculate_stress_level(face_emotions)

            # Store in history
            self.emotion_history.append({
                "timestamp": time.time(),
                "emotions": face_emotions,
                "stress_level": overall_stress
            })

            # Keep history manageable
            if len(self.emotion_history) > 100:
                self.emotion_history = self.emotion_history[-50:]

            return {
                "faces_detected": len(faces),
                "emotions": face_emotions,
                "stress_level": overall_stress["level"],
                "stress_score": overall_stress["score"],
                "confidence": overall_stress["confidence"],
                "timestamp": time.time()
            }

        except Exception as e:
            logger.error(f"❌ Frame analysis failed: {e}")
            return {"error": str(e)}

    def _analyze_emotion(self, face_roi: np.ndarray) -> Dict:
        """Analyze emotion from face ROI using CNN model"""
        try:
            if self.emotion_model is None:
                # Fallback to basic analysis
                return self._basic_emotion_analysis(face_roi)

            # Preprocess face for CNN
            face_pil = Image.fromarray(face_roi)
            face_tensor = self.transform(face_pil).unsqueeze(0).to(self.device)

            # Get emotion predictions
            with torch.no_grad():
                predictions = self.emotion_model(face_tensor)
                probabilities = predictions.cpu().numpy()[0]

            # Get dominant emotion
            dominant_idx = np.argmax(probabilities)
            dominant_emotion = self.emotion_labels[dominant_idx]
            confidence = probabilities[dominant_idx]

            # Create emotion distribution
            emotion_dist = {}
            for idx, prob in enumerate(probabilities):
                emotion_dist[self.emotion_labels[idx]] = float(prob)

            return {
                "dominant_emotion": dominant_emotion,
                "confidence": float(confidence),
                "emotion_distribution": emotion_dist,
                "method": "cnn"
            }

        except Exception as e:
            logger.error(f"❌ CNN emotion analysis failed: {e}")
            return self._basic_emotion_analysis(face_roi)

    def _basic_emotion_analysis(self, face_roi: np.ndarray) -> Dict:
        """Basic emotion analysis using OpenCV features"""
        try:
            # Simple heuristics based on facial features
            h, w = face_roi.shape

            # Analyze upper vs lower face brightness (smile detection)
            upper_half = face_roi[:h//2, :]
            lower_half = face_roi[h//2:, :]

            upper_brightness = np.mean(upper_half)
            lower_brightness = np.mean(lower_half)

            # Simple emotion classification
            if lower_brightness > upper_brightness * 1.1:
                emotion = "happy"
                confidence = 0.6
            elif upper_brightness > lower_brightness * 1.2:
                emotion = "sad"
                confidence = 0.5
            else:
                emotion = "neutral"
                confidence = 0.4

            return {
                "dominant_emotion": emotion,
                "confidence": confidence,
                "emotion_distribution": {emotion: confidence, "neutral": 1-confidence},
                "method": "basic"
            }

        except Exception as e:
            logger.error(f"❌ Basic emotion analysis failed: {e}")
            return {
                "dominant_emotion": "neutral",
                "confidence": 0.3,
                "emotion_distribution": {"neutral": 1.0},
                "method": "fallback"
            }

    def _calculate_stress_level(self, face_emotions: List[Dict]) -> Dict:
        """Calculate overall stress level from face emotions"""
        if not face_emotions:
            return {
                "level": "unknown",
                "score": 0.0,
                "confidence": 0.0
            }

        # Calculate weighted emotion score
        total_score = 0.0
        total_confidence = 0.0

        for emotion_data in face_emotions:
            emotion = emotion_data["dominant_emotion"]
            confidence = emotion_data["confidence"]

            # Get emotion weight
            weight = self.emotion_weights.get(emotion, 0.0)

            # Weight by confidence and face size (larger faces = more reliable)
            face_size_factor = min(1.0, emotion_data.get("face_size", 1000) / 10000)
            weighted_score = weight * confidence * face_size_factor

            total_score += weighted_score
            total_confidence += confidence

        # Average the scores
        if len(face_emotions) > 0:
            avg_score = total_score / len(face_emotions)
            avg_confidence = total_confidence / len(face_emotions)
        else:
            avg_score = 0.0
            avg_confidence = 0.0

        # Determine stress level
        if avg_score <= self.stress_thresholds['severe']:
            level = "severe"
        elif avg_score <= self.stress_thresholds['high']:
            level = "high"
        elif avg_score <= self.stress_thresholds['moderate']:
            level = "moderate"
        else:
            level = "low"

        return {
            "level": level,
            "score": avg_score,
            "confidence": avg_confidence
        }

    def get_stress_analysis_summary(self, duration_seconds: int = 30) -> Dict:
        """Get stress analysis summary over specified duration"""
        if not self.emotion_history:
            return {"error": "No emotion history available"}

        # Filter recent history
        current_time = time.time()
        recent_history = [
            entry for entry in self.emotion_history
            if current_time - entry["timestamp"] <= duration_seconds
        ]

        if not recent_history:
            return {"error": "No recent emotion data"}

        # Analyze trends
        stress_levels = [entry["stress_level"] for entry in recent_history]
        stress_counts = {
            "low": stress_levels.count("low"),
            "moderate": stress_levels.count("moderate"),
            "high": stress_levels.count("high"),
            "severe": stress_levels.count("severe")
        }

        # Get dominant emotions
        all_emotions = []
        for entry in recent_history:
            for face_emotion in entry["emotions"]:
                all_emotions.append(face_emotion["dominant_emotion"])

        emotion_counts = {}
        for emotion in all_emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Calculate overall assessment
        total_entries = len(recent_history)
        severe_ratio = stress_counts["severe"] / total_entries
        high_ratio = stress_counts["high"] / total_entries

        if severe_ratio > 0.3:
            overall_assessment = "severe_concern"
        elif high_ratio > 0.4:
            overall_assessment = "high_concern"
        elif stress_counts["moderate"] > stress_counts["low"]:
            overall_assessment = "moderate_concern"
        else:
            overall_assessment = "stable"

        return {
            "duration_analyzed": duration_seconds,
            "total_frames": total_entries,
            "stress_distribution": stress_counts,
            "emotion_distribution": emotion_counts,
            "overall_assessment": overall_assessment,
            "severe_stress_ratio": severe_ratio,
            "high_stress_ratio": high_ratio,
            "recommendations": self._generate_recommendations(overall_assessment, emotion_counts)
        }

    def _generate_recommendations(self, assessment: str, emotions: Dict) -> List[str]:
        """Generate mental health recommendations based on facial analysis"""
        recommendations = []

        if assessment == "severe_concern":
            recommendations.extend([
                " Immediate professional mental health consultation recommended",
                " Consider contacting military mental health services",
                " Reach out to trusted colleagues or supervisors",
                " Emergency mental health hotline: Available 24/7"
            ])

        elif assessment == "high_concern":
            recommendations.extend([
                " Schedule appointment with mental health professional",
                " Practice stress reduction techniques (deep breathing, meditation)",
                " Engage in physical exercise to reduce stress",
                " Ensure adequate sleep (7-8 hours per night)"
            ])

        elif assessment == "moderate_concern":
            recommendations.extend([
                " Monitor stress levels and practice self-care",
                " Connect with supportive colleagues and friends",
                " Take regular breaks during duty",
                " Maintain regular physical activity"
            ])

        # Emotion-specific recommendations
        if emotions.get("sad", 0) > emotions.get("happy", 0):
            recommendations.append(" Engage in activities that bring joy and fulfillment")

        if emotions.get("angry", 0) > 2:
            recommendations.append(" Practice anger management techniques")

        if emotions.get("fear", 0) > 1:
            recommendations.append(" Address specific fears or anxieties with counselor")

        return recommendations


class CPUFacialBehaviorAnalyzer:
    """
    CPU-only facial behavior analyzer for mental health assessment
    Uses lightweight OpenCV algorithms and mathematical analysis
    No heavy ML models - designed for real-time CPU performance
    """

    def __init__(self):
        """Initialize the CPU-only facial behavior analyzer"""
        self.is_initialized = False
        self.emotion_history = []
        self.face_history = []
        self.baseline_measurements = {}

        # OpenCV components (lightweight)
        self.face_cascade = None
        self.eye_cascade = None
        self.smile_cascade = None
        self.profile_cascade = None

        # Mental health indicators tracking
        self.stress_indicators = {
            'facial_tension': [],
            'eye_strain': [],
            'micro_movements': [],
            'asymmetry_changes': []
        }

        self.engagement_metrics = {
            'face_stability': [],
            'eye_contact_duration': [],
            'head_movement_patterns': [],
            'attention_focus': []
        }

        # Initialize components
        self._initialize_cpu_components()
    
    def _initialize_cpu_components(self):
        """Initialize CPU-only facial analysis components"""
        try:
            # Load OpenCV Haar cascades (lightweight, CPU-optimized)
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
            self.profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

            # Verify cascades loaded successfully
            if (not self.face_cascade.empty() and
                not self.eye_cascade.empty() and
                not self.smile_cascade.empty()):

                self.is_initialized = True
                logger.info("✅ CPU-only facial behavior analyzer initialized successfully")
                logger.info("✅ Using lightweight OpenCV cascades for real-time analysis")

                # Initialize baseline measurements
                self._initialize_baseline_measurements()

            else:
                logger.error("❌ Failed to load OpenCV cascade classifiers")
                self.is_initialized = False

        except Exception as e:
            logger.error(f"❌ Error initializing CPU facial analyzer: {e}")
            self.is_initialized = False

    def _initialize_baseline_measurements(self):
        """Initialize baseline measurements for comparison"""
        self.baseline_measurements = {
            'normal_face_size': (150, 150),  # Expected face size
            'normal_eye_ratio': 0.25,        # Eye area to face area ratio
            'normal_symmetry': 0.85,         # Facial symmetry baseline
            'normal_stability': 0.9,         # Face position stability
            'stress_threshold': 0.3,         # Stress detection threshold
            'engagement_threshold': 0.6      # Engagement level threshold
        }

    def _calculate_facial_metrics(self, gray_frame: np.ndarray, face_coords: Tuple) -> Dict:
        """
        Calculate facial metrics using CPU-only mathematical analysis

        Args:
            gray_frame: Grayscale frame
            face_coords: Face coordinates (x, y, w, h)

        Returns:
            Dictionary of facial metrics
        """
        x, y, w, h = face_coords
        face_roi = gray_frame[y:y+h, x:x+w]

        metrics = {
            'face_size': (w, h),
            'face_area': w * h,
            'face_center': (x + w//2, y + h//2),
            'face_stability': self._calculate_stability(face_coords),
            'facial_symmetry': self._calculate_symmetry(face_roi),
            'texture_variance': self._calculate_texture_variance(face_roi),
            'edge_density': self._calculate_edge_density(face_roi)
        }

        return metrics

    def _calculate_stability(self, current_coords: Tuple) -> float:
        """Calculate face position stability over time"""
        if len(self.face_history) < 2:
            self.face_history.append(current_coords)
            return 1.0

        # Keep only recent history
        if len(self.face_history) > 10:
            self.face_history.pop(0)

        self.face_history.append(current_coords)

        # Calculate movement variance
        movements = []
        for i in range(1, len(self.face_history)):
            prev_x, prev_y, prev_w, prev_h = self.face_history[i-1]
            curr_x, curr_y, curr_w, curr_h = self.face_history[i]

            movement = math.sqrt((curr_x - prev_x)**2 + (curr_y - prev_y)**2)
            movements.append(movement)

        if movements:
            avg_movement = np.mean(movements)
            stability = max(0.0, 1.0 - (avg_movement / 50.0))  # Normalize to 0-1
            return stability

        return 1.0

    def _calculate_symmetry(self, face_roi: np.ndarray) -> float:
        """Calculate facial symmetry using pixel comparison"""
        h, w = face_roi.shape

        # Split face into left and right halves
        left_half = face_roi[:, :w//2]
        right_half = face_roi[:, w//2:]

        # Flip right half for comparison
        right_half_flipped = cv2.flip(right_half, 1)

        # Resize to match if needed
        min_width = min(left_half.shape[1], right_half_flipped.shape[1])
        left_half = left_half[:, :min_width]
        right_half_flipped = right_half_flipped[:, :min_width]

        # Calculate correlation
        if left_half.shape == right_half_flipped.shape:
            correlation = cv2.matchTemplate(left_half, right_half_flipped, cv2.TM_CCOEFF_NORMED)
            symmetry_score = float(correlation[0][0])
            return max(0.0, min(1.0, (symmetry_score + 1.0) / 2.0))  # Normalize to 0-1

        return 0.5  # Default if shapes don't match

    def _calculate_texture_variance(self, face_roi: np.ndarray) -> float:
        """Calculate texture variance as stress indicator"""
        # Calculate local variance using Laplacian
        laplacian = cv2.Laplacian(face_roi, cv2.CV_64F)
        variance = laplacian.var()

        # Normalize to 0-1 range
        normalized_variance = min(1.0, variance / 1000.0)
        return normalized_variance

    def _calculate_edge_density(self, face_roi: np.ndarray) -> float:
        """Calculate edge density for tension analysis"""
        # Apply Canny edge detection
        edges = cv2.Canny(face_roi, 50, 150)

        # Calculate edge density
        total_pixels = face_roi.shape[0] * face_roi.shape[1]
        edge_pixels = np.sum(edges > 0)

        edge_density = edge_pixels / total_pixels if total_pixels > 0 else 0.0
        return edge_density
    
    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analyze a single frame for facial behavior indicators using CPU-only methods

        Args:
            frame: Input video frame (numpy array)

        Returns:
            Dictionary containing analysis results
        """
        if not self.is_initialized:
            return {"error": "Analyzer not initialized"}

        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Enhance image quality for better detection
            gray = cv2.equalizeHist(gray)

            # Detect faces with optimized parameters for better detection
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,  # More sensitive
                minNeighbors=3,    # Fewer neighbors
                minSize=(30, 30),  # Smaller minimum
                maxSize=(400, 400) # Larger maximum
            )

            analysis_results = {
                'timestamp': datetime.now().isoformat(),
                'faces_detected': len(faces),
                'facial_indicators': {},
                'behavior_score': 0.0,
                'mental_state_indicators': {},
                'frame_quality': self._assess_frame_quality(gray)
            }

            if len(faces) > 0:
                # Use the largest detected face (most reliable)
                face = max(faces, key=lambda f: f[2] * f[3])  # Sort by area

                # Calculate facial metrics
                facial_metrics = self._calculate_facial_metrics(gray, face)

                # Analyze facial features
                facial_features = self._analyze_cpu_facial_features(gray, face)

                # Combine all indicators
                analysis_results['facial_indicators'] = {
                    'metrics': facial_metrics,
                    'features': facial_features
                }

                # Calculate behavior score
                analysis_results['behavior_score'] = self._calculate_cpu_behavior_score(
                    facial_metrics, facial_features
                )

                # Detect mental state indicators
                analysis_results['mental_state_indicators'] = self._detect_cpu_mental_state_indicators(
                    facial_metrics, facial_features
                )

            return analysis_results

        except Exception as e:
            logger.error(f"Error analyzing frame: {e}")
            return {"error": str(e)}

    def _assess_frame_quality(self, gray_frame: np.ndarray) -> Dict:
        """Assess the quality of the input frame"""
        # Calculate image sharpness using Laplacian variance
        laplacian_var = cv2.Laplacian(gray_frame, cv2.CV_64F).var()

        # Calculate brightness
        brightness = np.mean(gray_frame)

        # Calculate contrast
        contrast = np.std(gray_frame)

        quality = {
            'sharpness': min(1.0, laplacian_var / 500.0),  # Normalize
            'brightness': brightness / 255.0,
            'contrast': contrast / 128.0,
            'overall_quality': 'good' if laplacian_var > 100 and 50 < brightness < 200 else 'poor'
        }

        return quality

    def _analyze_cpu_facial_features(self, gray_frame: np.ndarray, face_coords: Tuple) -> Dict:
        """
        Analyze facial features using CPU-only OpenCV methods

        Args:
            gray_frame: Grayscale frame
            face_coords: Face coordinates (x, y, w, h)

        Returns:
            Dictionary of facial feature analysis
        """
        x, y, w, h = face_coords
        face_roi = gray_frame[y:y+h, x:x+w]

        features = {
            'eye_analysis': self._analyze_cpu_eyes(face_roi),
            'smile_detection': self._detect_cpu_smile(face_roi),
            'stress_indicators': self._detect_cpu_stress_indicators(face_roi),
            'engagement_metrics': self._calculate_cpu_engagement(face_roi, face_coords),
            'micro_movements': self._detect_cpu_micro_movements(face_roi)
        }

        return features

    def _analyze_cpu_eyes(self, face_roi: np.ndarray) -> Dict:
        """Analyze eye-related indicators using CPU-only methods"""
        # Detect eyes in face region
        eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 3, minSize=(20, 20))

        eye_analysis = {
            'eyes_detected': len(eyes),
            'eye_openness': 0.0,
            'eye_symmetry': 0.0,
            'blink_indicators': False,
            'strain_indicators': False
        }

        if len(eyes) >= 2:
            # Sort eyes by x-coordinate (left to right)
            eyes = sorted(eyes, key=lambda e: e[0])

            # Analyze eye openness (height/width ratio)
            eye_ratios = []
            for ex, ey, ew, eh in eyes:
                eye_ratio = eh / ew if ew > 0 else 0
                eye_ratios.append(eye_ratio)

            eye_analysis['eye_openness'] = np.mean(eye_ratios) if eye_ratios else 0.0

            # Check for blink indicators (very low height/width ratio)
            eye_analysis['blink_indicators'] = any(ratio < 0.2 for ratio in eye_ratios)

            # Calculate eye symmetry
            if len(eyes) >= 2:
                left_eye, right_eye = eyes[0], eyes[1]
                size_diff = abs((left_eye[2] * left_eye[3]) - (right_eye[2] * right_eye[3]))
                max_size = max(left_eye[2] * left_eye[3], right_eye[2] * right_eye[3])
                eye_analysis['eye_symmetry'] = 1.0 - (size_diff / max_size) if max_size > 0 else 0.0

            # Detect strain indicators (small eye area relative to face)
            total_eye_area = sum(ew * eh for ex, ey, ew, eh in eyes)
            face_area = face_roi.shape[0] * face_roi.shape[1]
            eye_to_face_ratio = total_eye_area / face_area if face_area > 0 else 0
            eye_analysis['strain_indicators'] = eye_to_face_ratio < 0.02  # Threshold for strain

        return eye_analysis

    def _detect_cpu_smile(self, face_roi: np.ndarray) -> Dict:
        """Detect smile using CPU-only methods"""
        # Focus on lower half of face for smile detection
        lower_face = face_roi[face_roi.shape[0]//2:, :]

        smiles = self.smile_cascade.detectMultiScale(lower_face, 1.8, 20, minSize=(25, 15))

        smile_analysis = {
            'smile_detected': len(smiles) > 0,
            'smile_intensity': 0.0,
            'smile_symmetry': 0.0,
            'genuine_indicators': False
        }

        if len(smiles) > 0:
            # Calculate smile intensity based on size and number
            total_smile_area = sum(sw * sh for sx, sy, sw, sh in smiles)
            face_area = face_roi.shape[0] * face_roi.shape[1]
            smile_analysis['smile_intensity'] = min(1.0, total_smile_area / (face_area * 0.1))

            # Check for genuine smile indicators (eyes should be involved)
            eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 3)
            if len(eyes) >= 2 and len(smiles) > 0:
                # Genuine smile often involves eye crinkles (reduced eye area)
                eye_areas = [ew * eh for ex, ey, ew, eh in eyes]
                avg_eye_area = np.mean(eye_areas)
                smile_analysis['genuine_indicators'] = avg_eye_area < (face_area * 0.015)  # Threshold

        return smile_analysis

    def _detect_cpu_stress_indicators(self, face_roi: np.ndarray) -> Dict:
        """Detect stress indicators using CPU-only image analysis"""
        stress_indicators = {
            'facial_tension': 0.0,
            'muscle_strain': 0.0,
            'asymmetry_stress': 0.0,
            'overall_stress_level': 'low'
        }

        # Analyze facial tension using edge density
        edges = cv2.Canny(face_roi, 50, 150)
        edge_density = np.sum(edges > 0) / (face_roi.shape[0] * face_roi.shape[1])
        stress_indicators['facial_tension'] = min(1.0, edge_density * 10)  # Normalize

        # Analyze muscle strain using texture variance
        laplacian = cv2.Laplacian(face_roi, cv2.CV_64F)
        texture_variance = laplacian.var()
        stress_indicators['muscle_strain'] = min(1.0, texture_variance / 1000.0)

        # Calculate asymmetry stress
        h, w = face_roi.shape
        left_half = face_roi[:, :w//2]
        right_half = cv2.flip(face_roi[:, w//2:], 1)

        if left_half.shape == right_half.shape:
            correlation = cv2.matchTemplate(left_half, right_half, cv2.TM_CCOEFF_NORMED)
            symmetry = float(correlation[0][0])
            stress_indicators['asymmetry_stress'] = max(0.0, 1.0 - ((symmetry + 1.0) / 2.0))

        # Overall stress level
        avg_stress = (stress_indicators['facial_tension'] +
                     stress_indicators['muscle_strain'] +
                     stress_indicators['asymmetry_stress']) / 3.0

        if avg_stress > 0.6:
            stress_indicators['overall_stress_level'] = 'high'
        elif avg_stress > 0.3:
            stress_indicators['overall_stress_level'] = 'moderate'
        else:
            stress_indicators['overall_stress_level'] = 'low'

        return stress_indicators
    
    def _analyze_facial_features(self, gray_frame: np.ndarray, face_coords: Tuple) -> Dict:
        """
        Analyze specific facial features within detected face region
        
        Args:
            gray_frame: Grayscale frame
            face_coords: Face coordinates (x, y, w, h)
            
        Returns:
            Dictionary of facial feature analysis
        """
        x, y, w, h = face_coords
        face_roi = gray_frame[y:y+h, x:x+w]
        
        features = {
            'eye_analysis': self._analyze_eyes(face_roi),
            'smile_detection': self._detect_smile(face_roi),
            'face_symmetry': self._analyze_face_symmetry(face_roi),
            'micro_expressions': self._detect_micro_expressions(face_roi),
            'engagement_level': self._assess_engagement(face_roi)
        }
        
        return features
    
    def _analyze_eyes(self, face_roi: np.ndarray) -> Dict:
        """Analyze eye-related indicators"""
        eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 3)
        
        eye_analysis = {
            'eyes_detected': len(eyes),
            'eye_contact_level': 0.0,
            'blink_rate': 0.0,
            'eye_strain_indicators': False
        }
        
        if len(eyes) >= 2:
            eye_analysis['eye_contact_level'] = 0.8  # Simulated - would need eye tracking
            eye_analysis['blink_rate'] = np.random.uniform(15, 25)  # Normal blink rate
            
            # Analyze eye strain (simplified)
            eye_analysis['eye_strain_indicators'] = len(eyes) < 2
        
        return eye_analysis
    
    def _detect_smile(self, face_roi: np.ndarray) -> Dict:
        """Detect smile and positive expressions"""
        smiles = self.smile_cascade.detectMultiScale(face_roi, 1.8, 20)
        
        smile_analysis = {
            'smile_detected': len(smiles) > 0,
            'smile_intensity': len(smiles) * 0.3 if len(smiles) > 0 else 0.0,
            'genuine_smile': len(smiles) > 0 and np.random.random() > 0.3  # Simplified
        }
        
        return smile_analysis
    
    def _analyze_face_symmetry(self, face_roi: np.ndarray) -> Dict:
        """Analyze facial symmetry for stress indicators"""
        h, w = face_roi.shape
        left_half = face_roi[:, :w//2]
        right_half = cv2.flip(face_roi[:, w//2:], 1)
        
        # Calculate symmetry score (simplified)
        if left_half.shape == right_half.shape:
            symmetry_score = cv2.matchTemplate(left_half, right_half, cv2.TM_CCOEFF_NORMED)[0][0]
        else:
            symmetry_score = 0.5
        
        return {
            'symmetry_score': float(symmetry_score),
            'asymmetry_indicators': symmetry_score < 0.7
        }
    
    def _detect_micro_expressions(self, face_roi: np.ndarray) -> Dict:
        """Detect micro-expressions for emotional state"""
        # Simplified micro-expression detection
        # In real implementation, would use advanced ML models
        
        micro_expressions = {
            'stress_micro_expressions': np.random.random() > 0.7,
            'anxiety_indicators': np.random.random() > 0.8,
            'depression_signs': np.random.random() > 0.9,
            'emotional_suppression': np.random.random() > 0.85
        }
        
        return micro_expressions
    
    def _assess_engagement(self, face_roi: np.ndarray) -> Dict:
        """Assess user engagement level"""
        # Calculate engagement based on face position, size, and clarity
        h, w = face_roi.shape
        face_size_score = min(1.0, (h * w) / (200 * 200))  # Normalized face size
        
        engagement = {
            'engagement_score': face_size_score,
            'attention_level': face_size_score * 0.8,
            'participation_indicator': face_size_score > 0.5
        }
        
        return engagement
    
    def _calculate_behavior_score(self, facial_indicators: Dict) -> float:
        """Calculate overall behavior score from facial indicators"""
        try:
            score_components = []
            
            # Eye analysis contribution
            if 'eye_analysis' in facial_indicators:
                eye_score = facial_indicators['eye_analysis'].get('eye_contact_level', 0.0)
                score_components.append(eye_score * 0.3)
            
            # Smile contribution
            if 'smile_detection' in facial_indicators:
                smile_score = facial_indicators['smile_detection'].get('smile_intensity', 0.0)
                score_components.append(smile_score * 0.2)
            
            # Symmetry contribution
            if 'face_symmetry' in facial_indicators:
                symmetry_score = facial_indicators['face_symmetry'].get('symmetry_score', 0.5)
                score_components.append(symmetry_score * 0.2)
            
            # Engagement contribution
            if 'engagement_level' in facial_indicators:
                engagement_score = facial_indicators['engagement_level'].get('engagement_score', 0.0)
                score_components.append(engagement_score * 0.3)
            
            return sum(score_components) if score_components else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating behavior score: {e}")
            return 0.0
    
    def _detect_mental_state_indicators(self, facial_indicators: Dict) -> Dict:
        """Detect mental state indicators from facial analysis"""
        indicators = {
            'stress_level': 'low',
            'anxiety_indicators': False,
            'depression_signs': False,
            'overall_wellbeing': 'good',
            'recommendations': []
        }
        
        try:
            # Analyze stress indicators
            if 'face_symmetry' in facial_indicators:
                if facial_indicators['face_symmetry'].get('asymmetry_indicators', False):
                    indicators['stress_level'] = 'moderate'
                    indicators['recommendations'].append("Consider stress management techniques")
            
            # Analyze engagement for depression signs
            if 'engagement_level' in facial_indicators:
                engagement = facial_indicators['engagement_level'].get('engagement_score', 0.0)
                if engagement < 0.3:
                    indicators['depression_signs'] = True
                    indicators['overall_wellbeing'] = 'needs_attention'
                    indicators['recommendations'].append("Low engagement detected - consider professional consultation")
            
            # Analyze micro-expressions
            if 'micro_expressions' in facial_indicators:
                micro = facial_indicators['micro_expressions']
                if micro.get('anxiety_indicators', False):
                    indicators['anxiety_indicators'] = True
                    indicators['recommendations'].append("Anxiety indicators detected - practice relaxation techniques")
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error detecting mental state indicators: {e}")
            return indicators
    
    def process_video_stream(self, duration_seconds: int = 30) -> Dict:
        """
        Process video stream for specified duration
        
        Args:
            duration_seconds: Duration to analyze video stream
            
        Returns:
            Comprehensive analysis results
        """
        if not self.is_initialized:
            return {"error": "Analyzer not initialized"}
        
        try:
            cap = cv2.VideoCapture(0)  # Use default camera
            
            if not cap.isOpened():
                return {"error": "Cannot access camera"}
            
            analysis_results = []
            start_time = time.time()
            
            logger.info(f"Starting facial behavior analysis for {duration_seconds} seconds...")
            
            while (time.time() - start_time) < duration_seconds:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Analyze current frame
                frame_analysis = self.analyze_frame(frame)
                if 'error' not in frame_analysis:
                    analysis_results.append(frame_analysis)
                
                # Small delay to prevent overwhelming processing
                time.sleep(0.1)
            
            cap.release()
            
            # Generate comprehensive report
            return self._generate_comprehensive_report(analysis_results)
            
        except Exception as e:
            logger.error(f"Error processing video stream: {e}")
            return {"error": str(e)}
    
    def _generate_comprehensive_report(self, analysis_results: List[Dict]) -> Dict:
        """Generate comprehensive analysis report"""
        if not analysis_results:
            return {"error": "No analysis data available"}
        
        # Calculate averages and trends
        total_frames = len(analysis_results)
        avg_behavior_score = np.mean([r.get('behavior_score', 0) for r in analysis_results])
        
        # Count mental state indicators
        stress_count = sum(1 for r in analysis_results 
                          if r.get('mental_state_indicators', {}).get('stress_level') in ['moderate', 'high'])
        
        anxiety_count = sum(1 for r in analysis_results 
                           if r.get('mental_state_indicators', {}).get('anxiety_indicators', False))
        
        report = {
            'analysis_summary': {
                'total_frames_analyzed': total_frames,
                'analysis_duration': f"{total_frames * 0.1:.1f} seconds",
                'average_behavior_score': round(avg_behavior_score, 2),
                'faces_detected_percentage': np.mean([r.get('faces_detected', 0) for r in analysis_results]) * 100
            },
            'mental_health_indicators': {
                'stress_detection_rate': round((stress_count / total_frames) * 100, 1),
                'anxiety_indicators_rate': round((anxiety_count / total_frames) * 100, 1),
                'overall_wellbeing_assessment': self._assess_overall_wellbeing(avg_behavior_score),
                'engagement_level': self._assess_engagement_level(analysis_results)
            },
            'recommendations': self._generate_recommendations(analysis_results),
            'timestamp': datetime.now().isoformat()
        }
        
        return report
    
    def _assess_overall_wellbeing(self, avg_score: float) -> str:
        """Assess overall wellbeing based on average behavior score"""
        if avg_score >= 0.7:
            return "Good"
        elif avg_score >= 0.5:
            return "Moderate"
        elif avg_score >= 0.3:
            return "Needs Attention"
        else:
            return "Concerning"
    
    def _assess_engagement_level(self, analysis_results: List[Dict]) -> str:
        """Assess engagement level from analysis results"""
        engagement_scores = []
        for result in analysis_results:
            facial_indicators = result.get('facial_indicators', {})
            engagement = facial_indicators.get('engagement_level', {})
            engagement_scores.append(engagement.get('engagement_score', 0.0))
        
        avg_engagement = np.mean(engagement_scores) if engagement_scores else 0.0
        
        if avg_engagement >= 0.7:
            return "High"
        elif avg_engagement >= 0.5:
            return "Moderate"
        else:
            return "Low"
    
    def _generate_recommendations(self, analysis_results: List[Dict]) -> List[str]:
        """Generate personalized recommendations based on analysis"""
        recommendations = []
        
        # Analyze patterns across all results
        stress_indicators = sum(1 for r in analysis_results 
                               if r.get('mental_state_indicators', {}).get('stress_level') != 'low')
        
        if stress_indicators > len(analysis_results) * 0.3:
            recommendations.append("Consider stress management techniques and regular breaks")
        
        # Check engagement patterns
        low_engagement = sum(1 for r in analysis_results 
                            if r.get('facial_indicators', {}).get('engagement_level', {}).get('engagement_score', 0) < 0.3)
        
        if low_engagement > len(analysis_results) * 0.5:
            recommendations.append("Low engagement detected - consider professional mental health consultation")
        
        # Default recommendations
        if not recommendations:
            recommendations.append("Continue maintaining good mental health practices")
        
        return recommendations

# Utility functions for integration
def initialize_facial_analyzer() -> CPUFacialBehaviorAnalyzer:
    """Initialize and return CPU facial behavior analyzer"""
    return CPUFacialBehaviorAnalyzer()

def quick_facial_assessment(duration: int = 10) -> Dict:
    """Perform quick facial behavior assessment"""
    analyzer = initialize_facial_analyzer()
    if analyzer.is_initialized:
        return analyzer.process_video_stream(duration)
    else:
        return {"error": "Facial analyzer initialization failed"}
