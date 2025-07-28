import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import AI_examination from './AI_examination';
import '../styles/AI_Questionnaire.css';

const AI_Questionnaire = () => {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/questions', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        setQuestions(response.data);
      } catch (err) {
        console.error('Error loading questions:', err);
        setError('Error loading questions. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, []);

  const handleNext = () => {
    setCurrentQuestionIndex((prev) => prev + 1);
  };

  const handleBack = () => {
    setCurrentQuestionIndex((prev) => prev - 1);
  };

  const handleSubmit = async () => {
      navigate("/facial-analysis")
  };
  

  if (loading) return <div>Loading questions...</div>;
  if (error) return <div>{error}</div>;

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="ai-questionnaire-container">
      <AI_examination
        questionNo={currentQuestionIndex + 1}
        question={currentQuestion?.questionText || ''}
        onTranscriptUpdate={(transcript) =>
          setAnswers((prev) => ({ ...prev, [currentQuestion?.id]: transcript }))
        }
        onAudioUpdate={(audioUrl) => console.log('Audio URL:', audioUrl)}
      />

      <div className="navigation-buttons">
        {currentQuestionIndex > 0 && (
          <button onClick={handleBack} disabled={isSubmitting}>Back</button>
        )}
        {currentQuestionIndex < questions.length - 1 ? (
          <button onClick={handleNext} disabled={isSubmitting}>Next</button>
        ) : (
          <button onClick={handleSubmit} disabled={isSubmitting}>Submit</button>
        )}
      </div>
    </div>
  );
};

export default AI_Questionnaire;
