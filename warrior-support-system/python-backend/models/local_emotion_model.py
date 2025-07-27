#!/usr/bin/env python3
"""
Local Emotion Recognition Model for Army Mental Health Assessment
Downloads and runs a lightweight emotion model locally without internet dependency
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple
import json
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalEmotionModel:
    """
    Local emotion recognition model that can be downloaded once and run offline
    Uses lightweight models optimized for CPU performance
    """
    
    def __init__(self):
        """Initialize the local emotion model"""
        self.model_dir = Path("data/models/emotion")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Model files
        self.model_files = {
            'face_detection': 'opencv_face_detector_uint8.pb',
            'face_detection_config': 'opencv_face_detector.pbtxt',
            'emotion_model': 'emotion_model.onnx',
            'emotion_labels': 'emotion_labels.json'
        }
        
        # No external URLs - using completely local approach
        self.model_urls = {}  # Removed external dependencies
        
        # Emotion labels
        self.emotion_labels = [
            'Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral'
        ]
        
        # Model components
        self.face_net = None
        self.emotion_net = None
        self.is_initialized = False
        
        # Initialize model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the local emotion recognition model using only OpenCV built-ins"""
        try:
            # Use only OpenCV built-in cascades - no external downloads needed
            self._initialize_opencv_cascades()

            # Create enhanced face detection
            self._create_enhanced_face_detection()

            # Create rule-based emotion model
            self._create_simple_emotion_model()

            self.is_initialized = True
            logger.info("✅ Local emotion model initialized successfully (OpenCV only)")

        except Exception as e:
            logger.error(f"❌ Failed to initialize local emotion model: {e}")
            self.is_initialized = False
    
    def _initialize_opencv_cascades(self):
        """Initialize OpenCV cascade classifiers (no downloads needed)"""
        try:
            # Use OpenCV's built-in cascade classifiers
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
            self.profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

            # Verify cascades loaded
            if (self.face_cascade.empty() or self.eye_cascade.empty() or
                self.smile_cascade.empty() or self.profile_cascade.empty()):
                raise Exception("Failed to load OpenCV cascade classifiers")

            logger.info("✅ OpenCV cascades initialized successfully")

            # Create emotion labels file for reference
            labels_path = self.model_dir / self.model_files['emotion_labels']
            if not labels_path.exists():
                with open(labels_path, 'w') as f:
                    json.dump(self.emotion_labels, f)

        except Exception as e:
            logger.error(f"Failed to initialize OpenCV cascades: {e}")
            raise
    
    def _create_enhanced_face_detection(self):
        """Create enhanced face detection using multiple cascade approaches"""
        try:
            # Initialize multiple cascade classifiers for better detection
            self.detection_methods = {
                'frontal': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'),
                'alt': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'),
                'profile': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml'),
                'alt2': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
            }

            # Remove any empty classifiers
            self.detection_methods = {
                name: classifier for name, classifier in self.detection_methods.items()
                if not classifier.empty()
            }

            logger.info(f"✅ Enhanced face detection initialized with {len(self.detection_methods)} methods")

        except Exception as e:
            logger.warning(f"⚠️ Enhanced face detection setup failed: {e}")
            # Fallback to basic detection
            self.detection_methods = {
                'frontal': self.face_cascade
            }
    
    def _create_simple_emotion_model(self):
        """Create a simple rule-based emotion model"""
        # This is a simplified emotion recognition based on facial features
        # In a real implementation, you would use a pre-trained model
        
        self.emotion_rules = {
            'happy': {
                'smile_threshold': 0.6,
                'eye_crinkle': True,
                'mouth_curve': 'up'
            },
            'sad': {
                'smile_threshold': 0.1,
                'eye_droop': True,
                'mouth_curve': 'down'
            },
            'angry': {
                'eyebrow_furrow': True,
                'mouth_tension': True,
                'eye_narrow': True
            },
            'neutral': {
                'default': True
            }
        }
        
        logger.info("✅ Simple emotion model created")
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in the frame using enhanced cascade detection

        Args:
            frame: Input frame

        Returns:
            List of face coordinates (x, y, w, h)
        """
        return self._detect_faces_enhanced_cascade(frame)
    
    def _detect_faces_enhanced_cascade(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Enhanced face detection using multiple cascade methods"""
        try:
            # Convert to grayscale if needed
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame

            # Enhance image quality for better detection
            gray = cv2.equalizeHist(gray)

            all_faces = []

            # Try multiple detection methods
            for method_name, classifier in getattr(self, 'detection_methods', {'frontal': self.face_cascade}).items():
                try:
                    # Use very relaxed parameters for better detection
                    if method_name == 'profile':
                        scale_factor = 1.03
                        min_neighbors = 2
                        min_size = (20, 20)
                    else:
                        scale_factor = 1.05
                        min_neighbors = 3
                        min_size = (25, 25)

                    faces = classifier.detectMultiScale(
                        gray,
                        scaleFactor=scale_factor,
                        minNeighbors=min_neighbors,
                        minSize=min_size,
                        maxSize=(400, 400),
                        flags=cv2.CASCADE_SCALE_IMAGE
                    )

                    # Add detected faces with method info
                    for (x, y, w, h) in faces:
                        all_faces.append({
                            'coords': (x, y, w, h),
                            'method': method_name,
                            'area': w * h
                        })

                except Exception as e:
                    logger.warning(f"Detection method {method_name} failed: {e}")
                    continue

            # Remove duplicate detections (faces detected by multiple methods)
            unique_faces = self._remove_duplicate_faces(all_faces)

            # If no faces found, try ultra-relaxed detection
            if not unique_faces:
                logger.info("No faces found with standard parameters, trying ultra-relaxed detection...")
                ultra_faces = self._ultra_relaxed_detection(gray)
                unique_faces.extend(ultra_faces)

            # Return just the coordinates
            return [face['coords'] for face in unique_faces]

        except Exception as e:
            logger.error(f"Enhanced cascade detection failed: {e}")
            return self._detect_faces_basic_fallback(frame)

    def _remove_duplicate_faces(self, faces: List[Dict]) -> List[Dict]:
        """Remove duplicate face detections"""
        if not faces:
            return []

        # Sort by area (largest first)
        faces.sort(key=lambda f: f['area'], reverse=True)

        unique_faces = []
        for face in faces:
            x, y, w, h = face['coords']
            is_duplicate = False

            # Check if this face overlaps significantly with any existing face
            for existing in unique_faces:
                ex, ey, ew, eh = existing['coords']

                # Calculate overlap
                overlap_x = max(0, min(x + w, ex + ew) - max(x, ex))
                overlap_y = max(0, min(y + h, ey + eh) - max(y, ey))
                overlap_area = overlap_x * overlap_y

                # If overlap is more than 50% of smaller face, consider it duplicate
                min_area = min(w * h, ew * eh)
                if overlap_area > 0.5 * min_area:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_faces.append(face)

        return unique_faces

    def _ultra_relaxed_detection(self, gray: np.ndarray) -> List[Dict]:
        """Ultra-relaxed face detection as last resort"""
        ultra_faces = []

        try:
            # Try with very aggressive parameters
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.02,  # Very small scale factor
                minNeighbors=1,    # Minimum neighbors
                minSize=(15, 15),  # Very small minimum size
                maxSize=(500, 500), # Large maximum size
                flags=cv2.CASCADE_DO_CANNY_PRUNING
            )

            for (x, y, w, h) in faces:
                ultra_faces.append({
                    'coords': (x, y, w, h),
                    'method': 'ultra_relaxed',
                    'area': w * h
                })

            if ultra_faces:
                logger.info(f"Ultra-relaxed detection found {len(ultra_faces)} faces")

        except Exception as e:
            logger.warning(f"Ultra-relaxed detection failed: {e}")

        return ultra_faces

    def _detect_faces_basic_fallback(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Basic fallback face detection"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame

            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 50)
            )

            return [(x, y, w, h) for x, y, w, h in faces]

        except Exception as e:
            logger.error(f"Basic fallback detection failed: {e}")
            return []
    

    
    def predict_emotion(self, face_roi: np.ndarray) -> Dict[str, float]:
        """
        Predict emotion from face ROI
        
        Args:
            face_roi: Face region of interest
            
        Returns:
            Dictionary of emotion probabilities
        """
        try:
            # Simple rule-based emotion recognition
            emotions = self._analyze_facial_features_for_emotion(face_roi)
            return emotions
            
        except Exception as e:
            logger.error(f"Emotion prediction failed: {e}")
            return {emotion: 0.0 for emotion in self.emotion_labels}
    
    def _analyze_facial_features_for_emotion(self, face_roi: np.ndarray) -> Dict[str, float]:
        """Analyze facial features for emotion using simple rules"""
        # Initialize emotion scores
        emotion_scores = {emotion.lower(): 0.0 for emotion in self.emotion_labels}
        
        try:
            # Convert to grayscale if needed
            if len(face_roi.shape) == 3:
                gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            else:
                gray_face = face_roi
            
            # Detect smile
            smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
            smiles = smile_cascade.detectMultiScale(gray_face, 1.8, 20)
            
            # Detect eyes
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            eyes = eye_cascade.detectMultiScale(gray_face, 1.1, 3)
            
            # Simple emotion rules
            if len(smiles) > 0:
                emotion_scores['happy'] = 0.7
                emotion_scores['neutral'] = 0.2
            elif len(eyes) < 2:
                emotion_scores['sad'] = 0.5
                emotion_scores['neutral'] = 0.3
            else:
                emotion_scores['neutral'] = 0.8
            
            # Calculate texture variance for stress/anger
            laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
            if laplacian_var > 500:
                emotion_scores['angry'] = min(0.6, laplacian_var / 1000)
                emotion_scores['neutral'] = max(0.1, emotion_scores['neutral'] - 0.3)
            
            # Normalize scores
            total_score = sum(emotion_scores.values())
            if total_score > 0:
                emotion_scores = {k: v / total_score for k, v in emotion_scores.items()}
            
            return emotion_scores
            
        except Exception as e:
            logger.error(f"Feature analysis failed: {e}")
            return {'neutral': 1.0}
    
    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analyze frame for emotions and mental health indicators
        
        Args:
            frame: Input frame
            
        Returns:
            Analysis results
        """
        if not self.is_initialized:
            return {"error": "Model not initialized"}
        
        try:
            # Detect faces
            faces = self.detect_faces(frame)
            
            results = {
                'faces_detected': len(faces),
                'emotions': [],
                'mental_health_indicators': {
                    'stress_level': 'low',
                    'engagement': 'moderate',
                    'overall_mood': 'neutral'
                }
            }
            
            # Analyze each face
            for face_coords in faces:
                x, y, w, h = face_coords
                face_roi = frame[y:y+h, x:x+w]
                
                # Predict emotions
                emotions = self.predict_emotion(face_roi)
                
                results['emotions'].append({
                    'face_coords': face_coords,
                    'emotions': emotions,
                    'dominant_emotion': max(emotions.items(), key=lambda x: x[1])
                })
            
            # Calculate mental health indicators
            if results['emotions']:
                results['mental_health_indicators'] = self._calculate_mental_health_indicators(
                    results['emotions']
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Frame analysis failed: {e}")
            return {"error": str(e)}
    
    def _calculate_mental_health_indicators(self, emotions_data: List[Dict]) -> Dict:
        """Calculate mental health indicators from emotion data"""
        indicators = {
            'stress_level': 'low',
            'engagement': 'moderate',
            'overall_mood': 'neutral',
            'recommendations': []
        }
        
        try:
            # Aggregate emotions across all faces
            all_emotions = {}
            for face_data in emotions_data:
                for emotion, score in face_data['emotions'].items():
                    if emotion not in all_emotions:
                        all_emotions[emotion] = []
                    all_emotions[emotion].append(score)
            
            # Calculate averages
            avg_emotions = {
                emotion: np.mean(scores) 
                for emotion, scores in all_emotions.items()
            }
            
            # Determine stress level
            stress_emotions = ['angry', 'fear', 'disgust']
            stress_score = sum(avg_emotions.get(emotion, 0) for emotion in stress_emotions)
            
            if stress_score > 0.4:
                indicators['stress_level'] = 'high'
                indicators['recommendations'].append("High stress detected - consider relaxation techniques")
            elif stress_score > 0.2:
                indicators['stress_level'] = 'moderate'
                indicators['recommendations'].append("Moderate stress detected - take regular breaks")
            
            # Determine engagement
            positive_emotions = ['happy', 'surprise']
            engagement_score = sum(avg_emotions.get(emotion, 0) for emotion in positive_emotions)
            
            if engagement_score > 0.3:
                indicators['engagement'] = 'high'
            elif engagement_score < 0.1:
                indicators['engagement'] = 'low'
                indicators['recommendations'].append("Low engagement detected - consider professional consultation")
            
            # Overall mood
            if avg_emotions.get('happy', 0) > 0.4:
                indicators['overall_mood'] = 'positive'
            elif avg_emotions.get('sad', 0) > 0.4:
                indicators['overall_mood'] = 'negative'
                indicators['recommendations'].append("Negative mood detected - consider mental health support")
            
            return indicators
            
        except Exception as e:
            logger.error(f"Mental health indicator calculation failed: {e}")
            return indicators

# Utility functions
def initialize_local_emotion_model() -> LocalEmotionModel:
    """Initialize and return local emotion model"""
    return LocalEmotionModel()

def download_models_if_needed():
    """Download models if they don't exist"""
    model = LocalEmotionModel()
    return model.is_initialized
