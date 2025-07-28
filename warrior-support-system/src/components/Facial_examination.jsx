import '../styles/Facial_examination.css';
import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Facial_examination = () => {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  
  const [isCapturing, setIsCapturing] = useState(false);
  const [capturedImages, setCapturedImages] = useState([]);
  const [permissionGranted, setPermissionGranted] = useState(false);
  const [availableDevices, setAvailableDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isStreamingFrames, setIsStreamingFrames] = useState(false);
  const [frameCount, setFrameCount] = useState(0);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  
  const FRAME_INTERVAL = 1000 / 24; // 1 frame per second
  const CAPTURE_DURATION = 8000; // 30 seconds
  const sessionIdRef = useRef(null);
  const streamingIntervalRef = useRef(null);

  const sendFrameToBackend = async (blob) => {
    const file = new File([blob], `frame-${Date.now()}.jpg`, { type: 'image/jpeg' });
    const formData = new FormData();
    formData.append('frame', file);
    formData.append('session_id', sessionIdRef.current);
    formData.append('duration', CAPTURE_DURATION/ 1000)

    try {
      const response = await axios.post('http://localhost:8000/api/stream_frame', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (response.data.frame_count) {
        setFrameCount(response.data.frame_count);
      }
      
     
    } catch (err) {
      console.error('Error sending frame:', err);
    }
  };

  const startRealTimeCapture = async () => {
    if (!videoRef.current || !canvasRef.current) {
      alert('Camera must be started before analyzing');
      return;
    }

    sessionIdRef.current = Date.now().toString(); // Unique ID for 30s session
    setIsStreamingFrames(true);
    setIsAnalyzing(true);
    setAnalysisResults(null);
    setFrameCount(0);
    setAnalysisProgress(0);
    const startTime = Date.now();

    console.log(`Starting analysis session: ${sessionIdRef.current}`);

    streamingIntervalRef.current = setInterval(async () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(100, (elapsed / CAPTURE_DURATION) * 100);
      setAnalysisProgress(Math.round(progress));
      
      if (elapsed >= CAPTURE_DURATION) {
        clearInterval(streamingIntervalRef.current);
        console.log("Capture complete, fetching final results...");
        
        try {
          const result = await axios.get(`http://localhost:8000/api/final_score?session_id=${sessionIdRef.current}`);
          setAnalysisResults(result.data);
          console.log('Analysis results:', result.data);
        } catch (err) {
          console.error('Error getting final results:', err);
          setAnalysisResults({
            overallMood: 'Error',
            confidence: 0,
            emotions: { error: 100 },
            recommendations: ['Unable to analyze due to server error']
          });
        }
        
        setIsStreamingFrames(false);
        setIsAnalyzing(false);
        return;
      }

      // Capture and send frame
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;

      context.drawImage(videoRef.current, 0, 0);
      canvas.toBlob(blob => {
        if (blob) sendFrameToBackend(blob);
      }, 'image/jpeg', 0.8);
    }, FRAME_INTERVAL);
  };

  const stopAnalysis = () => {
    if (streamingIntervalRef.current) {
      clearInterval(streamingIntervalRef.current);
      streamingIntervalRef.current = null;
    }
    setIsStreamingFrames(false);
    setIsAnalyzing(false);
    setFrameCount(0);
    setAnalysisProgress(0);
    console.log('Analysis stopped manually');
  };


  // Get video devices
  const getVideoDevices = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      stream.getTracks().forEach(track => track.stop());
      setPermissionGranted(true);

      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoInputs = devices.filter(device => device.kind === 'videoinput');
      setAvailableDevices(videoInputs);

      if (videoInputs.length > 0 && !selectedDeviceId) {
        setSelectedDeviceId(videoInputs[0].deviceId);
      }
    } catch (err) {
      console.error('Error getting video devices:', err);
      setPermissionGranted(false);
    }
  };

  useEffect(() => {
    getVideoDevices();
  }, []);

  // Start video capture
  const startCapture = async () => {
    try {
      if (!selectedDeviceId) {
        alert('Please select a camera device.');
        return;
      }

      const constraints = {
        video: {
          deviceId: { exact: selectedDeviceId },
          width: { ideal: 640 },
          height: { ideal: 480 }
        }
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      
      setIsCapturing(true);
    } catch (err) {
      console.error('Camera access error:', err);
      alert('Could not access camera. Please check permissions and try again.');
    }
  };

  // Stop video capture
  const stopCapture = () => {
    // Stop analysis if running
    stopAnalysis();
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsCapturing(false);
  };

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      stopAnalysis();
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Capture image from video
  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      
      context.drawImage(videoRef.current, 0, 0);
      
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
      setCapturedImages(prev => [...prev, {
        id: Date.now(),
        dataUrl: imageDataUrl,
        timestamp: new Date().toLocaleString()
      }]);
    }
  };

  // Remove captured image
  const removeImage = (imageId) => {
    setCapturedImages(prev => prev.filter(img => img.id !== imageId));
  };

  const analyzeFacialExpressions = () => {
    if (!isCapturing) {
      alert('Please start the camera first');
      return;
    }
    startRealTimeCapture(); // start streaming
  };

  return (
    <div className="facial-examination-container">
      <div className="facial-examination-card">
        <h2 className="facial-examination-title">📷 Facial Expression Analysis</h2>
        <hr className="facial-examination-divider" />

        {/* Camera Selection */}
        {permissionGranted && availableDevices.length > 0 && (
          <>
            <label htmlFor="cameraSelect" className="facial-examination-label">
              Select Camera:
            </label>
            <select
              id="cameraSelect"
              className="facial-camera-select"
              value={selectedDeviceId}
              onChange={(e) => setSelectedDeviceId(e.target.value)}
              disabled={isCapturing}
            >
              {availableDevices.map((device) => (
                <option key={device.deviceId} value={device.deviceId}>
                  {device.label || `Camera ${device.deviceId.substring(0, 8)}`}
                </option>
              ))}
            </select>
          </>
        )}

        {/* Video Preview */}
        <div className="video-container">
          <video
            ref={videoRef}
            className="video-preview"
            autoPlay
            muted
            playsInline
          />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>

        {/* Camera Controls */}
        <div className="camera-controls">
          {!isCapturing ? (
            <button
              onClick={startCapture}
              className="facial-examination-btn start"
              disabled={!selectedDeviceId}
            >
              📹 Start Camera
            </button>
          ) : (
            <>
              <button
                onClick={captureImage}
                className="facial-examination-btn capture"
              >
                📸 Capture Image
              </button>
              <button
                onClick={stopCapture}
                className="facial-examination-btn stop"
              >
                ⏹️ Stop Camera
              </button>
            </>
          )}
        </div>

        {/* Captured Images */}
        {capturedImages.length > 0 && (
          <div className="captured-images-section">
            <h3 className="section-title">Captured Images</h3>
            <div className="captured-images-grid">
              {capturedImages.map((image) => (
                <div key={image.id} className="captured-image-item">
                  <img src={image.dataUrl} alt="Captured" className="captured-image" />
                  <div className="image-timestamp">{image.timestamp}</div>
                  <button
                    onClick={() => removeImage(image.id)}
                    className="remove-image-btn"
                  >
                    ❌
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analysis Section */}
        <div className="analysis-section">
          <button
            onClick={analyzeFacialExpressions}
            className="facial-examination-btn analyze"
            disabled={!isCapturing || isAnalyzing}
          >
            {isAnalyzing ? '🔄 Analyzing... (30s)' : '🧠 Analyze Expressions'}
          </button>

          {isStreamingFrames && (
            <div className="analysis-status">
              <div className="streaming-indicator">
                🔴 Analyzing facial expressions... ({analysisProgress}% complete)
                <br />
                Frames captured: {frameCount} | Time remaining: {Math.max(0, 30 - Math.floor(analysisProgress * 30 / 100))}s
              </div>
              <div className="progress-bar" style={{ marginTop: '10px' }}>
                <div 
                  className="progress-fill" 
                  style={{ width: `${analysisProgress}%` }}
                ></div>
              </div>
              <button
                onClick={stopAnalysis}
                className="facial-examination-btn stop"
                style={{ marginTop: '10px' }}
              >
                ⏹️ Stop Analysis
              </button>
            </div>
          )}

          {analysisResults && (
            <div className="analysis-results">
              <h3 className="section-title">Analysis Results</h3>
              <div className="result-item">
                <strong>Overall Mood:</strong> {analysisResults}
              </div>
              
              
              <div className="emotions-breakdown">
                <h4>Emotion Breakdown:</h4>
                {Object.entries(analysisResults.emotions).map(([emotion, value]) => (
                  <div key={emotion} className="emotion-item">
                    <span className="emotion-label">{emotion.charAt(0).toUpperCase() + emotion.slice(1)}:</span>
                    <div className="emotion-bar">
                      <div 
                        className="emotion-fill" 
                        style={{ width: `${value}%` }}
                      ></div>
                    </div>
                    <span className="emotion-value">{value}%</span>
                  </div>
                ))}
              </div>

              <div className="recommendations">
                <h4>Recommendations:</h4>
                <ul>
                  {analysisResults.recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="navigation-buttons">
          <button
            onClick={() => navigate('/ai-exam')}
            className="facial-examination-btn back"
          >
            ⬅️ Back to Voice Analysis
          </button>
          <button
            onClick={() => navigate('/examination-complete')}
            className="facial-examination-btn next"
          >
            ✅ Complete Assessment
          </button>
        </div>

        {/* Permission Warning */}
        {!permissionGranted && (
          <div className="facial-examination-warning">
            Camera permission is required. Click "Start Camera" to grant permission.
          </div>
        )}
      </div>
    </div>
  );
};

export default Facial_examination;
