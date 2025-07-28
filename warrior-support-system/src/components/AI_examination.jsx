import '../styles/AI_examination.css';
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import useClipboard from 'react-use-clipboard';

const AI_assessment = () => {
  const navigate = useNavigate();
  
  const [isRecording, setIsRecording] = useState(false);
  const [audioURL, setAudioURL] = useState('');
  const [availableDevices, setAvailableDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState('');
  const [permissionGranted, setPermissionGranted] = useState(false);

  const [textToCopy, setTextToCopy] = useState('');
  const [isCopied, setCopied] = useClipboard(textToCopy, { successDuration: 1000 });

  const [backendTranscript, setBackendTranscript] = useState('');
  const [backendLoading, setBackendLoading] = useState(false);
  const [backendError, setBackendError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);

  const { transcript, browserSupportsSpeechRecognition, listening, resetTranscript } = useSpeechRecognition();

  const getAudioDevices = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      setPermissionGranted(true);

      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioInputs = devices.filter(device => device.kind === 'audioinput');
      setAvailableDevices(audioInputs);

      if (audioInputs.length > 0 && !selectedDeviceId) {
        setSelectedDeviceId(audioInputs[0].deviceId);
      }
    } catch (err) {
      console.error('Error getting audio devices:', err);
      setPermissionGranted(false);
    }
  };

  useEffect(() => {
    getAudioDevices();
  }, []);

  const startRecording = async () => {
    try {
      if (!selectedDeviceId) {
        alert('Please select a microphone device.');
        return;
      }

      setBackendTranscript('');
      setBackendError(null);

      const constraints = {
        audio: {
          deviceId: { exact: selectedDeviceId },
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false,
        },
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      let mimeType = 'audio/webm';
      const supportedTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/mp4',
        'audio/ogg;codecs=opus',
      ];
      for (const type of supportedTypes) {
        if (MediaRecorder.isTypeSupported(type)) {
          mimeType = type;
          break;
        }
      }

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
        audioBitsPerSecond: 128000,
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        if (audioChunksRef.current.length === 0) {
          console.error('No audio data recorded');
          return;
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioURL(audioUrl);

        try {
          setBackendLoading(true);
          setBackendError(null);

          const formData = new FormData();
          formData.append('audio', audioBlob, `recording.${mimeType.includes('webm') ? 'webm' : 'mp4'}`);

          const response = await axios.post('http://127.0.0.1:8000/api/translate', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });

          if (response.data && response.data.transcript) {
            setBackendTranscript(response.data.transcript);
          } else {
            setBackendTranscript('No transcription received from server.');
          }
        } catch (err) {
          console.error('Transcription API error:', err);
          setBackendError('Error occurred while transcribing audio.');
        } finally {
          setBackendLoading(false);
        }

        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
          streamRef.current = null;
        }
      };

      mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event.error);
      };

      // Start SpeechRecognition
      if (browserSupportsSpeechRecognition) {
        resetTranscript();
        SpeechRecognition.startListening({ continuous: true, language: 'en-IN' });
      }

      mediaRecorder.start(1000);
      setIsRecording(true);
    } catch (err) {
      console.error('Mic access error:', err);
      alert('Could not access microphone. Please check permissions and try again.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);

    if (browserSupportsSpeechRecognition && listening) {
      SpeechRecognition.stopListening();
    }
  };

  useEffect(() => {
    setTextToCopy(transcript);
  }, [transcript]);

  if (!browserSupportsSpeechRecognition) {
    return (
      <div className="audio-recorder-container">
        <div className="audio-recorder-card">
          <h2 className="audio-recorder-title">🧠 AI Voice Assessment</h2>
          <hr className="audio-recorder-divider" />
          <div className="audio-recorder-warning">
            Your browser does not support speech recognition.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="audio-recorder-container">
      <div className="audio-recorder-card">
        <h2 className="audio-recorder-title">🧠 AI Voice Assessment</h2>
        <hr className="audio-recorder-divider" />

        {/* Microphone selection */}
        {permissionGranted && availableDevices.length > 0 && (
          <>
            <label htmlFor="micSelect" className="audio-recorder-label">Select Microphone:</label>
            <select
              id="micSelect"
              className="audio-microphone-select"
              value={selectedDeviceId}
              onChange={(e) => setSelectedDeviceId(e.target.value)}
              disabled={isRecording}
            >
              {availableDevices.map((device) => (
                <option key={device.deviceId} value={device.deviceId}>
                  {device.label || `Microphone ${device.deviceId.substring(0, 8)}`}
                </option>
              ))}
            </select>
          </>
        )}

        {/* Backend Transcription */}
        <div style={{ marginBottom: '16px' }}>
          <label className="audio-recorder-label">Transcription from Backend:</label>
          <textarea
            className="audio-transcript-textarea"
            value={backendLoading ? 'Transcribing...' : backendTranscript}
            readOnly
            rows={5}
            placeholder="The transcription from backend will appear here after recording stops."
            style={backendError ? { borderColor: '#e74c3c' } : undefined}
          />
          {backendError && (
            <div style={{ color: '#e74c3c', fontWeight: 'bold', marginTop: 4 }}>{backendError}</div>
          )}
        </div>

        {/* Frontend Transcription (Live) */}
        <div style={{ marginBottom: '16px' }}>
          <label className="audio-recorder-label">Live Transcription (Speech Recognition):</label>
          <textarea
            className="audio-transcript-textarea"
            value={transcript}
            readOnly
            rows={5}
            placeholder="Live transcription will appear here as you speak."
          />
          <button onClick={setCopied} className="audio-recorder-btn copy">
            {isCopied ? '✅ Copied' : '📋 Copy Live Transcript'}
          </button>
        </div>

        {/* Controls */}
        <div style={{ marginBottom: '12px' }}>
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="audio-recorder-btn start"
              disabled={!selectedDeviceId}
              type="button"
              style={{ width: '100%' }}
            >
              🎙️ Start & Dictate
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="audio-recorder-btn stop"
              type="button"
              style={{ width: '100%' }}
            >
              ⏹️ Stop
            </button>
          )}
        </div>

        {isRecording && (
          <div className="audio-recorder-status">🔴 Recording & transcribing… Speak now!</div>
        )}

        {/* Audio Playback */}
        {audioURL && (
          <div className="audio-recorder-player" style={{ marginTop: '16px' }}>
            <span style={{ color: '#2c3e50', fontSize: '14px', fontWeight: 'bold' }}>Playback:</span>
            <audio src={audioURL} controls style={{ width: '100%', marginTop: '8px' }} />
          </div>
        )}

        {/* Next Button */}
        <div style={{ marginTop: '24px' }}>
          <button
            onClick={() => navigate('/facial-analysis')}
            className="audio-recorder-btn next"
            type="button"
            style={{ width: '100%' }}
          >
            ➡️ Next: Facial Analysis
          </button>
        </div>

        {!permissionGranted && (
          <div className="audio-recorder-warning" style={{ marginTop: '12px' }}>
            Microphone permission is required. Click “Start & Dictate” to grant permission.
          </div>
        )}
      </div>
    </div>
  );
};

export default AI_assessment;
