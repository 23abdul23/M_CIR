import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import '../styles/CombinedAssessment.css';

const CombinedAssessment = () => {
  const navigate = useNavigate();
  
  // Facial Analysis States
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [facialSessionId, setFacialSessionId] = useState(null);
  const [facialFrameCount, setFacialFrameCount] = useState(0);
  const [facialProgress, setFacialProgress] = useState(0);
  const [facialResults, setFacialResults] = useState(null);
  const [cameraStarted, setCameraStarted] = useState(false);
  const [facialImgData, setFacialImgData] = useState('');
  const facialIntervalRef = useRef(null);
  
  // Voice Analysis States
  const [audioDevices, setAudioDevices] = useState([]);
  const [selectedAudioDevice, setSelectedAudioDevice] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [voiceTranscript, setVoiceTranscript] = useState('');
  const [voiceLoading, setVoiceLoading] = useState(false);
  const [manualInput, setManualInput] = useState('');
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioStreamRef = useRef(null);
  const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition();
  
  // Questionnaire States
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [questionsLoading, setQuestionsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [assessmentComplete, setAssessmentComplete] = useState(false);
  
  // Permission States
  const [cameraPermission, setCameraPermission] = useState(false);
  const [audioPermission, setAudioPermission] = useState(false);
  const [availableCameras, setAvailableCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState('');
  

  // Constants
  const FACIAL_FRAME_INTERVAL = 1000; // 24 FPS

  // Track assessment start time for duration calculation
  const assessmentStartTimeRef = useRef(null);
  
  // Initialize component
  useEffect(() => {
    initializeAssessment();
    return () => {
      cleanup();
    };
  }, []);
  
  const initializeAssessment = async () => {
    await Promise.all([
      requestPermissions(),
      fetchQuestions()
    ]);
  };
  
  const requestPermissions = async () => {
    try {
      // Request camera permission
      const videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoStream.getTracks().forEach(track => track.stop());
      setCameraPermission(true);
      
      // Request audio permission
      const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStream.getTracks().forEach(track => track.stop());
      setAudioPermission(true);
      
      // Get available devices
      const devices = await navigator.mediaDevices.enumerateDevices();
      
      const videoInputs = devices.filter(device => device.kind === 'videoinput');
      setAvailableCameras(videoInputs);
      
      const audioInputs = devices.filter(device => device.kind === 'audioinput');
      setAudioDevices(audioInputs);
      
      // Set default devices and start camera
      if (videoInputs.length > 0) {
        const defaultCamera = videoInputs[0].deviceId;
        setSelectedCamera(defaultCamera);
        
        // Start camera immediately after setting the device
        setTimeout(() => {
          startCameraWithDevice(defaultCamera);
        }, 500);
      }
      
      if (audioInputs.length > 0) {
        setSelectedAudioDevice(audioInputs[0].deviceId);
      }
      
    } catch (error) {
      console.error('Permission error:', error);
    }
  };
  
  const fetchQuestions = async () => {
    try {
      setQuestionsLoading(true);
      const response = await axios.get('/api/questions', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });

      const Q = response.data.slice(0, response.data.length-1);
      console.log(Q)
      setQuestions(Q);
    } catch (error) {
      console.error('Error loading questions:', error);
    } finally {
      setQuestionsLoading(false);
    }
  };
  
  const startCamera = async () => {
    try {
      if (!selectedCamera) {
        console.log('No camera selected, cannot start camera');
        return;
      }
      
      const constraints = {
        video: {
          deviceId: { exact: selectedCamera },
          width: { ideal: 640 },
          height: { ideal: 480 }
        }
      };
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      
      setCameraStarted(true);
      
      // Auto-start facial analysis
      setTimeout(() => {
        startFacialAnalysis();
      }, 2000);
      
    } catch (error) {
      console.error('Camera error:', error);
    }
  };
  
  const startCameraWithDevice = async (deviceId) => {
    try {
      if (!deviceId) {
        console.log('No device ID provided, cannot start camera');
        return;
      }
      
      console.log('Starting camera with device:', deviceId);
      
      const constraints = {
        video: {
          deviceId: { exact: deviceId },
          width: { ideal: 640 },
          height: { ideal: 480 }
        }
      };
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        console.log('Camera started successfully');
      }
      
      setCameraStarted(true);
      
      // Auto-start facial analysis
      setTimeout(() => {
        startFacialAnalysis();
      }, 2000);
      
    } catch (error) {
      console.error('Camera error:', error);
      // Try with default constraints if exact device fails
      try {
        console.log('Trying with default constraints...');
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        streamRef.current = stream;
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
          console.log('Camera started with default settings');
        }
        
        setCameraStarted(true);
        
        setTimeout(() => {
          startFacialAnalysis();
        }, 2000);
        
      } catch (fallbackError) {
        console.error('Failed to start camera with fallback:', fallbackError);
      }
    }
  };
  
  const stopFacialAnalysis = async () => {
    if (facialIntervalRef.current) {
      clearInterval(facialIntervalRef.current);
      facialIntervalRef.current = null;
      
      // Get final results when stopping
      if (facialSessionId) {
        try {
          const result = await axios.get(`http://localhost:8000/api/final_score?session_id=${facialSessionId}`);
          setFacialResults(result.data);
          setFacialImgData(result.data.image_base64);
          console.log('Facial analysis stopped and results retrieved');
        } catch (error) {
          console.error('Error getting facial results on stop:', error);
        }
      }
    }
  };
  
  const handleCameraChange = async (deviceId) => {
    setSelectedCamera(deviceId);
    
    // Stop current camera if running
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    
    setCameraStarted(false);
    
    // Start camera with new device
    setTimeout(() => {
      startCameraWithDevice(deviceId);
    }, 300);
  };
  
  const startFacialAnalysis = () => {
    if (!videoRef.current || !canvasRef.current || facialIntervalRef.current) return;

    const sessionId = Date.now().toString();
    setFacialSessionId(sessionId);
    setFacialFrameCount(0);
    setFacialProgress(0);

    // Set assessment start time (only once)
    if (!assessmentStartTimeRef.current) {
      assessmentStartTimeRef.current = Date.now();
    }

    facialIntervalRef.current = setInterval(async () => {
      // Calculate elapsed time since assessment started
      const elapsed = Date.now() - assessmentStartTimeRef.current;
      // Update progress based on questions answered instead of time
      const questionsProgress = questions.length > 0 ? (Object.keys(answers).length / questions.length) * 100 : 0;
      setFacialProgress(Math.round(questionsProgress));

      // Continue capturing frames until assessment is submitted
      // No time-based stopping condition

      // Capture and send frame
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;

      context.drawImage(videoRef.current, 0, 0);
      canvas.toBlob(blob => {
        if (blob) sendFacialFrame(blob, sessionId, elapsed);
      }, 'image/jpeg', 0.8);
    }, FACIAL_FRAME_INTERVAL);
  };
  
  const sendFacialFrame = async (blob, sessionId, durationMs) => {
    const file = new File([blob], `frame-${Date.now()}.jpg`, { type: 'image/jpeg' });
    const formData = new FormData();
    formData.append('frame', file);
    formData.append('session_id', sessionId);
    // Send duration in milliseconds (as required by backend)
    formData.append('duration', durationMs || 0);

    try {
      const response = await axios.post('http://localhost:8000/api/stream_frame', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (response.data.frame_count) {
        setFacialFrameCount(response.data.frame_count);
      }
    } catch (error) {
      console.error('Error sending facial frame:', error);
    }
  };
  
  const startVoiceRecording = async () => {
    try {
      setVoiceLoading(false);
      resetTranscript();
      
      if (!selectedAudioDevice) return;
      
      const constraints = {
        audio: {
          deviceId: { exact: selectedAudioDevice },
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false,
        },
      };
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      audioStreamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        if (audioChunksRef.current.length > 0) {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          const formData = new FormData();
          formData.append('audio', audioBlob);

          console.log("Recorded ASuidio Data", audioBlob)
          
          try {
            setVoiceLoading(true);
            const response = await axios.post('http://localhost:8000/api/translate', formData, {
              headers: { 'Content-Type': 'multipart/form-data' },
            });
            
            const transcript = response.data.transcript;
            setVoiceTranscript(transcript);
            
            // Update answer
            updateAnswer(transcript);
          } catch (error) {
            console.error('Voice transcription error:', error);
          } finally {
            setVoiceLoading(false);
          }
        }
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      
      // Start browser speech recognition as backup
      if (browserSupportsSpeechRecognition) {
        SpeechRecognition.startListening({ continuous: true });
      }
      
    } catch (error) {
      console.error('Recording error:', error);
    }
  };
  
  const stopVoiceRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    
    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach(track => track.stop());
    }
    
    SpeechRecognition.stopListening();
    setIsRecording(false);
  };
  
  const updateAnswer = (answerText) => {
    const currentQuestion = questions[currentQuestionIndex];
    if (currentQuestion) {
      setAnswers(prev => ({
        ...prev,
        [currentQuestion.questionId]: answerText
      }));
    }
  };
  
  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setVoiceTranscript('');
      setManualInput('');
      resetTranscript();
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
      setVoiceTranscript('');
      setManualInput('');
      resetTranscript();
    }
  };
  
  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Stop facial analysis and get final results
      await stopFacialAnalysis();
      
      // Submit questionnaire answers
      const armyNo = localStorage.getItem('currentArmyNo');
      const submissionData = {
        armyNo,
        answers,
        completedAt: new Date().toISOString(),
        voiceAnalysis: {
          transcripts: Object.values(answers),
          completed: true
        },
        facialAnalysis: {
          sessionId: facialSessionId,
          frameCount: facialFrameCount,
          results: facialResults,
          completed: !!facialResults
        }
      };
      
      // You can submit to your backend here
      console.log('Submitting combined assessment:', submissionData);
      
      setAssessmentComplete(true);
      
      

    } catch (error) {
      console.error('Submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const cleanup = () => {
    if (facialIntervalRef.current) {
      clearInterval(facialIntervalRef.current);
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    
    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach(track => track.stop());
    }
    
    stopVoiceRecording();
  };
  
  if (questionsLoading) {
    return (
      <div className="combined-assessment-container">
        <div className="loading-screen">
          <div className="loading-spinner"></div>
          <p>Loading assessment...</p>
        </div>
      </div>
    );
  }
  
  if (assessmentComplete) {
    return (
      <div className="combined-assessment-container">
        <div className="completion-screen">
          <div className="completion-message">
            <h2>✅ Assessment Complete!</h2>
            <p>Your responses have been recorded successfully.</p>
            
            {/* Show processing status */}
            {!facialResults && facialSessionId && (
              <div className="processing-status">
                <div className="loading-spinner"></div>
                <p>Processing facial analysis results...</p>
              </div>
            )}
            
            <div className="completion-summary">
              <div>Questions Answered: {Object.keys(answers).length}</div>
              <div>Facial Analysis: {facialResults ? 'Complete' : facialSessionId ? 'Processing...' : 'Not Started'}</div>
              <div>Voice Analysis: Complete</div>
              {facialFrameCount > 0 && <div>Facial Frames Captured: {facialFrameCount}</div>}
            </div>
            <button onClick={() => navigate('/examination-complete')}>Proceed</button>
          </div>
          
        </div>
      </div>
    );
  }
  
  const currentQuestion = questions[currentQuestionIndex];
  // Always prefer the answer from answers state for the current question
  const currentAnswer = answers[currentQuestion?.questionId] || '';
  // For MCQ, use currentAnswer; for others, prefer manualInput, then voice, then transcript, then currentAnswer
  const displayAnswer = currentQuestion?.questionType === 'MCQ'
    ? currentAnswer
    : (manualInput || voiceTranscript || transcript || currentAnswer);
  
  return (
    <div className="combined-assessment-container">
      <div className="assessment-header">
        <h1>🧠 AI-Powered Comprehensive Assessment</h1>
        <div className="progress-indicator">
          Question {currentQuestionIndex + 1} of {questions.length}
        </div>
      </div>
      
      <div className="assessment-layout">
        {/* Camera Section */}
        <div className="camera-section">
          {/* Device Selection Controls */}
          <div className="device-selection">
            {/* Permission Status */}
            <div className="permission-status">
              <div className={`permission-indicator ${cameraPermission ? 'granted' : 'denied'}`}>
                📹 Camera: {cameraPermission ? 'Granted' : 'Requesting...'}
              </div>
              <div className={`permission-indicator ${audioPermission ? 'granted' : 'denied'}`}>
                🎤 Audio: {audioPermission ? 'Granted' : 'Requesting...'}
              </div>
            </div>
            
            {availableCameras.length > 0 && (
              <div className="device-selector">
                <label htmlFor="cameraSelect" className="device-label">
                  📹 Select Camera:
                </label>
                <select
                  id="cameraSelect"
                  className="device-select"
                  value={selectedCamera}
                  onChange={(e) => handleCameraChange(e.target.value)}
                  disabled={cameraStarted}
                >
                  {availableCameras.map((device) => (
                    <option key={device.deviceId} value={device.deviceId}>
                      {device.label || `Camera ${device.deviceId.substring(0, 8)}`}
                    </option>
                  ))}
                </select>
              </div>
            )}
            
            {audioDevices.length > 0 && (
              <div className="device-selector">
                <label htmlFor="micSelect" className="device-label">
                  🎤 Select Microphone:
                </label>
                <select
                  id="micSelect"
                  className="device-select"
                  value={selectedAudioDevice}
                  onChange={(e) => setSelectedAudioDevice(e.target.value)}
                  disabled={isRecording}
                >
                  {audioDevices.map((device) => (
                    <option key={device.deviceId} value={device.deviceId}>
                      {device.label || `Microphone ${device.deviceId.substring(0, 8)}`}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
          
          <div className="camera-container">
            <video
              ref={videoRef}
              className="video-preview"
              autoPlay
              muted
              playsInline
              onLoadedMetadata={() => {
                console.log('Video metadata loaded - Camera is working');
              }}
              onError={(e) => {
                console.error('Video error:', e);
              }}
            />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            
            {/* Facial Analysis Status Overlay */}
            {cameraStarted && (
              <div className="facial-status-overlay">
                {facialIntervalRef.current ? (
                  <div className="analysis-active">
                    <div className="status-indicator recording"></div>
                    <span>Facial Analysis: Active (Frames: {facialFrameCount})</span>
                  </div>
                ) : facialResults ? (
                  <div className="analysis-complete">
                    <div className="status-indicator complete"></div>
                    <span>Facial Analysis: Complete</span>
                  </div>
                ) : (
                  <div className="analysis-ready">
                    <div className="status-indicator ready"></div>
                    <span>Camera Ready</span>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Camera Controls */}
          <div className="camera-controls">
            {!cameraStarted ? (
              <button
                onClick={() => startCamera()}
                className="camera-control-btn start"
                disabled={!selectedCamera}
              >
                📹 Start Camera
              </button>
            ) : (
              <button
                onClick={() => {
                  if (streamRef.current) {
                    streamRef.current.getTracks().forEach(track => track.stop());
                  }
                  setCameraStarted(false);
                }}
                className="camera-control-btn stop"
              >
                ⏹️ Stop Camera
              </button>
            )}
          </div>
        </div>
        
        {/* Questionnaire Section */}
        <div className="questionnaire-section">
          {currentQuestion && (
            <div className="question-container">
              <div className="question-header">
                <h3>Question {currentQuestion.questionId}</h3>
                <div className="question-type">{currentQuestion.questionType}</div>
              </div>
              
              <div className="question-text">
                {currentQuestion.questionText}
              </div>
              
              {/* {currentQuestion.questionType === 'MCQ' && currentQuestion.options && (
                <div className="options-container">
                  {currentQuestion.options.map((option, index) => (
                    <button
                      key={index}
                      className={`option-button ${currentAnswer === option.optionText ? 'selected' : ''}`}
                      onClick={() => {
                        setManualInput(''); // Clear manual input for MCQ
                        setVoiceTranscript(''); // Clear voice transcript for MCQ
                        setAnswers(prev => ({
                          ...prev,
                          [currentQuestion.questionId]: option.optionText
                        }));
                      }}
                    >
                      {option.optionId}. {option.optionText}
                    </button>
                  ))}
                </div>
              )} */}
              
              {/* Voice Recording Section */}
              <div className="voice-section">
                <div className="voice-controls">
                  {!isRecording ? (
                    <button
                      onClick={startVoiceRecording}
                      className="voice-btn start-recording"
                      disabled={voiceLoading}
                    >
                      🎤 Start Recording
                    </button>
                  ) : (
                    <button
                      onClick={stopVoiceRecording}
                      className="voice-btn stop-recording"
                    >
                      ⏹️ Stop Recording
                    </button>
                  )}
                  
                  {voiceLoading && (
                    <div className="voice-loading">
                      <div className="loading-spinner small"></div>
                      Processing audio...
                    </div>
                  )}
                </div>
                
                {/* Answer Display */}
                <div className="answer-section">
                  <label>Your Answer:</label>
                  <textarea
                    value={displayAnswer}
                    onChange={(e) => {
                      setManualInput(e.target.value);
                      setAnswers(prev => ({
                        ...prev,
                        [currentQuestion.questionId]: e.target.value
                      }));
                    }}
                    placeholder="Speak your answer or type here..."
                    className="answer-textarea"
                    rows={4}
                  />
                </div>
                
                {/* Real-time transcript */}
                {(listening || transcript) && (
                  <div className="real-time-transcript">
                    <strong>Live Transcript:</strong> {transcript}
                  </div>
                )}
              </div>
              
              {/* Navigation */}
              <div className="question-navigation">
                
                
                <button
                  onClick={handleNext}
                  disabled={
                    currentQuestion.questionType === 'MCQ'
                      ? !currentAnswer.trim()
                      : !displayAnswer.trim()
                  }
                  className="nav-btn next"
                >
                  {currentQuestionIndex === questions.length - 1 ? 'Complete Assessment' : 'Next →'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Results Section */}
      {facialResults && (
        <div className="results-section">
          <h3>Facial Analysis Results</h3>
          <div className="facial-results">
            <div className="result-item">
              <strong>Primary Emotion:</strong> {facialResults.results?.frame_analysis?.emotions?.[0] || 'Processing...'}
            </div>
            
            {facialResults.results?.recommendations && (
              <div className="recommendations">
                <strong>Recommendations:</strong>
                <ul>
                  {facialResults.results.recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {facialImgData && (
              <div className="analysis-chart">
                <img src={`data:image/png;base64,${facialImgData}`} alt="Analysis Chart" />
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Progress Summary */}
      <div className="progress-summary">
        <div className="progress-item">
          <span>Questions: {Object.keys(answers).length}/{questions.length}</span>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${(Object.keys(answers).length / questions.length) * 100}%` }}
            />
          </div>
        </div>
        
        
      </div>
    </div>
  );
};

export default CombinedAssessment;
