import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from "./Header"
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import '../styles/CombinedAssessment.css';

const CombinedAssessment = () => {
  const navigate = useNavigate();
  const [personnelInfo, setPersonnelInfo] = useState(null)

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
  const [isProcessingAudio, setIsProcessingAudio] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioStreamRef = useRef(null);
  const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition();
  
  //Voice Scores
  const [voiceScores, setVoiceScores] = useState({'depression' : [], 'anxiety' : [], 'stress' : []});
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

    // Prevent accidental page reload during audio processing
    const handleBeforeUnload = (e) => {
      if (isProcessingAudio) {
        e.preventDefault();
        e.returnValue = 'Audio is being processed. Are you sure you want to leave?';
        return 'Audio is being processed. Are you sure you want to leave?';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      cleanup();
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isProcessingAudio]);
  
  const initializeAssessment = async () => {
    await Promise.all([
      requestPermissions(),
      fetchQuestions(),
      fetchPersonnelInfo()
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

  const fetchPersonnelInfo = async () => {
    const armyNo = localStorage.getItem("currentArmyNo")
    if (!armyNo) {
      setError("No Army Number found. Please start from the beginning.")
      navigate("/army-number-entry")
      return
    }
    try {
      const response = await axios.get(`/api/personnel/army-no/${armyNo}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      })
      setPersonnelInfo(response.data)
    } catch (error) {
      setError("Error fetching personnel information")
    }
  }
  
  const fetchQuestions = async () => {
    try {
      setQuestionsLoading(true);
      const response = await axios.get('/api/questions/ai', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });

      const Q = response.data.slice(0, response.data.length-1);
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
  
  // Determine severity levels (DASS-21 compatible)
  const getSeverity = (score, type) => {
    if (type === 'depression') {
      if (score <= 9) return 'Normal';
      if (score <= 13) return 'Mild';
      if (score <= 20) return 'Moderate';
      if (score <= 27) return 'Severe';
      return 'Extremely Severe';
    } else if (type === 'anxiety') {
      if (score <= 7) return 'Normal';
      if (score <= 9) return 'Mild';
      if (score <= 14) return 'Moderate';
      if (score <= 19) return 'Severe';
      return 'Extremely Severe';
    } else { // stress
      if (score <= 14) return 'Normal';
      if (score <= 18) return 'Mild';
      if (score <= 25) return 'Moderate';
      if (score <= 33) return 'Severe';
      return 'Extremely Severe';
    }
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
      console.log('🎙️ Starting voice recording...');
      setVoiceLoading(false);
      resetTranscript();
      setVoiceTranscript(''); // Clear previous transcript

      if (!selectedAudioDevice) {
        console.warn('⚠️ No audio device selected');
        alert('Please select an audio device first.');
        return;
      }

      console.log(`🎤 Using audio device: ${selectedAudioDevice}`);

      const constraints = {
        audio: {
          deviceId: { exact: selectedAudioDevice },
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false,
          sampleRate: 16000, // Optimal for Whisper
        },
      };

      console.log('🔊 Requesting microphone access...');
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      audioStreamRef.current = stream;

      // Check if WebM is supported, fallback to other formats
      let mimeType = 'audio/webm';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/mp4';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
          mimeType = 'audio/wav';
        }
      }

      console.log(`📹 Using MIME type: ${mimeType}`);

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        console.log('🎙️ Recording stopped, processing audio...');

        if (audioChunksRef.current.length > 0) {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          console.log(`📊 Audio blob created: ${audioBlob.size} bytes, type: ${audioBlob.type}`);

          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.webm');

          try {
            setVoiceLoading(true);
            setIsProcessingAudio(true);
            console.log('📤 Sending audio to backend for transcription...');

            const response = await axios.post('http://localhost:8000/api/translate', formData, {
              headers: { 'Content-Type': 'multipart/form-data' },
              
            });

            console.log('✅ Transcription response received:', response.data);

            const transcript = response.data.transcript;
            const voiceAnalysis = response.data.voice_analysis;
            const aiEnhanced = response.data.ai_enhanced;
            
            const scores = response.data.weighted_assessment.final_scores

            setVoiceScores((prevScores) => ({
              depression: [...prevScores.depression, scores.depression],
              anxiety: [...prevScores.anxiety, scores.anxiety],
              stress: [...prevScores.stress, scores.stress],
            }));



            if (transcript) {
              setVoiceTranscript(transcript)
              // Create enhanced answer object if AI analysis is available
              const answerData = aiEnhanced && voiceAnalysis ? {
                transcript: transcript,
                voice_analysis: voiceAnalysis,
                ai_enhanced: true,
                timestamp: new Date().toISOString()
              } : transcript;

              console.log('💾 Saving answer data:', answerData);

              // Update answer
              updateAnswer(answerData.transcript);

              if (aiEnhanced) {
                console.log('🤖 AI analysis included in response');
              }
            } else {
              console.error('❌ No transcript received from backend');
              alert('Transcription failed. Please try recording again.');
            }

          } catch (error) {
            console.error('❌ Voice transcription error:', error);

            if (error.code === 'ECONNABORTED') {
              alert('Transcription timed out. Please try with a shorter recording.');
            } else if (error.response) {
              console.error('Backend error response:', error.response.data);
              alert(`Transcription failed: ${error.response.data.error || 'Unknown error'}`);
            } else {
              alert('Network error. Please check your connection and try again.');
            }
          } finally {
            setVoiceLoading(false);
            setIsProcessingAudio(false);
            console.log('🏁 Transcription process completed');
          }
        } else {
          console.warn('⚠️ No audio data recorded');
          alert('No audio was recorded. Please try again.');
        }
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      console.log('✅ Recording started successfully');

      // Start browser speech recognition as backup
      if (browserSupportsSpeechRecognition) {
        SpeechRecognition.startListening({ continuous: true });
        console.log('🎤 Browser speech recognition started as backup');
      }

    } catch (error) {
      console.error('❌ Recording error:', error);

      if (error.name === 'NotAllowedError') {
        alert('Microphone access denied. Please allow microphone access and try again.');
      } else if (error.name === 'NotFoundError') {
        alert('No microphone found. Please connect a microphone and try again.');
      } else if (error.name === 'NotReadableError') {
        alert('Microphone is being used by another application. Please close other applications and try again.');
      } else {
        alert(`Recording failed: ${error.message}`);
      }

      setIsRecording(false);
    }
  };
  
  const stopVoiceRecording = () => {
    console.log('🛑 Stopping voice recording...');

    try {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
        console.log('📹 MediaRecorder stopped');
      }

      if (audioStreamRef.current) {
        audioStreamRef.current.getTracks().forEach(track => track.stop());
        console.log('🔇 Audio stream tracks stopped');
      }

      SpeechRecognition.stopListening();
      setIsRecording(false);
      console.log('✅ Recording stopped successfully');

    } catch (error) {
      console.error('❌ Error stopping recording:', error);
      setIsRecording(false);
    }
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
  
  const handleNext = async () => {
    // Prevent navigation during audio processing
    if (isProcessingAudio) {
      console.log('⚠️ Cannot navigate while processing audio');
      return;
    }

    // If manualInput is present (user typed answer), send to hindi_sentiment API and wait for response
    if (manualInput && manualInput.trim()) {
      setIsSubmitting(true);
      try {
        const response = await axios.post(
          'http://localhost:8000/api/get_sentiment',
          { text: manualInput },
          { headers: { 'Content-Type': 'application/json' } }
        );

        console.log(response.data)
        // Optionally, you can use response.data here (e.g., save sentiment)
        // For now, just proceed to next question after response
      } catch (error) {
        console.error('Error sending manual input to sentiment API:', error);
        alert('Failed to analyze your answer. Please try again.');
        setIsSubmitting(false);
        return;
      }
      setIsSubmitting(false);
    }

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      setVoiceTranscript('');
      setManualInput('');
      resetTranscript();
    } else {
      handleSubmit();
    }
  };

  
  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Stop facial analysis and get final results
      await stopFacialAnalysis();
      
      // Submit questionnaire answers
      const armyNo = localStorage.getItem('currentArmyNo');

      
      // Calculate average AI scores if we have voice analysis data
      let aiAssessmentData = null;
      const avgScores = {
          depression: 0,
          anxiety: 0,
          stress: 0,
          confidence: 0
        };

      const count = voiceScores.depression.length; // all arrays should have the same length if updated together
      if (count > 0) {
        avgScores.depression = voiceScores.depression.reduce((sum, val) => sum + val, 0) / count;
        avgScores.anxiety = voiceScores.anxiety.reduce((sum, val) => sum + val, 0) / count;
        avgScores.stress = voiceScores.stress.reduce((sum, val) => sum + val, 0) / count;
      }

      aiAssessmentData = {
          depression: avgScores.depression,
          depressionSeverity: getSeverity(avgScores.depression, 'depression'),
          anxiety: avgScores.anxiety,
          anxietySeverity: getSeverity(avgScores.anxiety, 'anxiety'),
          stress: avgScores.stress,
          stressSeverity: getSeverity(avgScores.stress, 'stress'),
        };

        console.log("this was the data", aiAssessmentData)
        

        // Prepare examination data with scores
      const examinationData = {
        armyNo: armyNo,
        answers: Object.keys(answers).map((questionId) => ({
          questionId,
          answer: answers[questionId],
        })),
        dassScores: aiAssessmentData,
        battalion : localStorage.getItem('selectedBattalion'),
        completedAt: new Date(),
        mode : "AI",
        // examAI_taken : True
      }

      console.log("I am here: " , examinationData)
        // Save AI assessment to backend
        try {
          const response = await axios.post(`/api/examination/submit/${localStorage.getItem('examModes')}`, examinationData, {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
          })
          
          console.log('Examination submitted successfully:', response.data)
          
          setAssessmentComplete(true);

          // Don't auto-navigate - let user stay on the page to see results
          // User can manually navigate when ready
          console.log('Assessment completed successfully - staying on current page');
        } catch (error) {
          console.error('⚠️ Failed to save AI assessment:', error);
        }
    
      
      setAssessmentComplete(true);

      // Don't auto-navigate - let user stay on the page to see results
      // User can manually navigate when ready
      console.log('Assessment completed successfully - staying on current page');
      

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

      <div className = "inner-container">
        <Header/>
      <div className="questionnaire-content">
        <div className="personnel-info">
          <div className="info-item">
            <span>ARMY NO</span>
            <span>{personnelInfo.armyNo}</span>
          </div>
          <div className="info-item">
            <span>RANK</span>
            <span>{personnelInfo.rank}</span>
          </div>
          <div className="info-item">
            <span>NAME</span>
            <span>{personnelInfo.name}</span>
          </div>
          <div className="info-item">
            <span>COY/SQN/BTY</span>
            <span>{personnelInfo.subBty}</span>
          </div>
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
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  startCamera();
                }}
                className="camera-control-btn start"
                disabled={!selectedCamera}
              >
                📹 Start Camera
              </button>
            ) : (
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
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
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        startVoiceRecording();
                      }}
                      className="voice-btn start-recording"
                      disabled={voiceLoading}
                    >
                      🎤 Start Recording
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        stopVoiceRecording();
                      }}
                      className="voice-btn stop-recording"
                    >
                      ⏹️ Stop Recording
                    </button>
                  )}
                  
                  {/* {voiceLoading && (
                    <div className="voice-loading">
                      <div className="loading-spinner small"></div>
                      Processing audio... (Please wait, do not navigate)
                    </div>
                  )} */}

                  {isProcessingAudio && (
                    <div className="processing-warning" style={{
                      backgroundColor: '#fff3cd',
                      border: '1px solid #ffeaa7',
                      borderRadius: '4px',
                      padding: '8px',
                      marginTop: '8px',
                      fontSize: '12px',
                      color: '#856404'
                    }}>
                      ⚠️ Audio processing in progress. Please wait before navigating.
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
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleNext();
                  }}
                  disabled={
                    isProcessingAudio ||
                    (currentQuestion.questionType === 'MCQ'
                      ? !(typeof currentAnswer === 'string' ? currentAnswer.trim() : currentAnswer)
                      : !(typeof displayAnswer === 'string' ? displayAnswer.trim() : displayAnswer))
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
    </div>
  );
};

export default CombinedAssessment;
