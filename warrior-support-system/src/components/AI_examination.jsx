import '../styles/AI_examination.css';
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Form, useNavigate } from 'react-router-dom';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const AI_examination = ({ questionNo, question, onTranscriptUpdate, onAudioUpdate }) => {
  const navigate = useNavigate();

  const [isRecording, setIsRecording] = useState(false);
  const [audioURL, setAudioURL] = useState('');
  const [backendTranscript, setBackendTranscript] = useState('');
  const [backendLoading, setBackendLoading] = useState(false);
  const [backendError, setBackendError] = useState(null);
  const [availableDevices, setAvailableDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState('');
  const [permissionGranted, setPermissionGranted] = useState(false);
  const [manualInput, setManualInput] = useState('');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);

  const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition();

  useEffect(() => {
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

    getAudioDevices();
  }, [selectedDeviceId]);

  const startRecording = async () => {
    try {
      setBackendTranscript('');
      setBackendError(null);

      if (!selectedDeviceId) {
        console.error('No microphone device selected.');
        return;
      }

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

      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        console.log('Data available:', event.data.size);
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        console.log('Recording stopped. Chunks:', audioChunksRef.current.length);
        if (audioChunksRef.current.length > 0) {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

          const formData = new FormData();
          formData.append('audio', audioBlob);

          try{
            const response = await axios.post('http://localhost:8000/api/translate', formData, {
              headers: {
                'Content-Type': 'multipart/form-data',
              },
            });

            const transcript = response.data.transcript;
            setBackendTranscript(transcript);
            onTranscriptUpdate(transcript);
          }
          catch (error){
            console.log(error);
          }

          const audioUrl = URL.createObjectURL(audioBlob);
          setAudioURL(audioUrl);
          onAudioUpdate(audioUrl);
        } else {
          console.error('No audio data available for transcription.');
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Error starting recording:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  };

  const handleManualInputChange = (e) => {
    setManualInput(e.target.value);
    onTranscriptUpdate(e.target.value);
  };

  return (
    <div className="ai-examination-container">
      {permissionGranted && availableDevices.length > 0 && (
        <div>
          <label htmlFor="micSelect">Select Microphone:</label>
          <select
            id="micSelect"
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
        </div>
      )}

      <br></br>
      <h3>{questionNo}) {question}</h3>

      <div className="voice-input-section">
        <p>{listening ? 'Listening...' : 'Press the button and start speaking.'}</p>
        <button onClick={startRecording} disabled={isRecording}>Start</button>
        <button onClick={stopRecording} disabled={!isRecording}>Stop</button>
      </div>

      {audioURL && (
        <div>
          <audio src={audioURL} controls />
        </div>
      )}

      <div className="manual-input-section">
        <label htmlFor="manualInput">Enter your answer (manually or via transcription):</label>
        <textarea
          id="manualInput"
          value={backendLoading ? "Transcribing..." : manualInput || backendTranscript}
          onChange={handleManualInputChange}
          rows={5}
          placeholder="Type your answer here... or wait for backend transcription"
          readOnly={backendLoading}
        />
      </div>

      {backendError && <p style={{ color: 'red' }}>{backendError}</p>}
    </div>
  );
};

export default AI_examination;
