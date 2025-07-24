import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import axios from 'axios'
import Header from './Header'
import '../styles/PeerEvaluation.css'

const PeerEvaluation = ({ currentUser, onLogout }) => {
  const [personnel, setPersonnel] = useState(null)
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [loading, setLoading] = useState(true)
  const { personnelId } = useParams()
  const navigate = useNavigate()

  useEffect(() => {
    fetchPersonnelInfo()
    fetchQuestions()
  }, [personnelId])

  const fetchPersonnelInfo = async () => {
    try {
      const response = await axios.get(`/api/evaluation/personnel/${personnelId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      setPersonnel(response.data)
    } catch (error) {
      console.error('Error fetching personnel info:', error)
      navigate('/jso-dashboard')
    }
  }

  const fetchQuestions = async () => {
    try {
      const response = await axios.get('/api/evaluation/questions', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      setQuestions(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching questions:', error)
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('currentArmyNo')
    
    if (onLogout) {
      onLogout()
    }
    
    navigate('/login')
  }

  const handleAnswerChange = (questionId, answer) => {
    setAnswers({
      ...answers,
      [questionId]: answer
    })
  }

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    } else {
      handleSubmitEvaluation()
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const handleSubmitEvaluation = async () => {
    try {
      await axios.post('/api/evaluation/submit', {
        personnelId: personnelId,
        answers: Object.keys(answers).map(questionId => ({
          questionId,
          answer: answers[questionId]
        }))
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })

      alert('Peer evaluation submitted successfully!')
      navigate('/data-table')
    } catch (error) {
      console.error('Error submitting evaluation:', error)
      alert('Error submitting evaluation. Please try again.')
    }
  }

  if (loading || !personnel || !questions.length) {
    return (
      <div className="peer-evaluation-container">
        <Header currentUser={currentUser} onLogout={handleLogout} />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          Loading evaluation...
        </div>
      </div>
    )
  }

  const question = questions[currentQuestion]
  const progressPercentage = ((currentQuestion + 1) / questions.length) * 100

  return (
    <div className="peer-evaluation-container">
      <Header currentUser={currentUser} onLogout={handleLogout} />

      <div className="evaluation-content">
        <div className="personnel-info">
          <h3>Evaluating: {personnel.rank} {personnel.name}</h3>
          <div className="info-details">
            <span>Army No: {personnel.armyNo}</span>
            <span>Coy/Sqn/Bty: {personnel.coySquadronBty}</span>
          </div>
        </div>

        <div className="question-progress">
          Question {currentQuestion + 1} of {questions.length}
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>

        <h2>PEER EVALUATION</h2>

        <div className="question-section">
          <h3>{currentQuestion + 1}. {question.question}</h3>

          {question.type === 'text' ? (
            <textarea
              value={answers[question.id] || ''}
              onChange={(e) => handleAnswerChange(question.id, e.target.value)}
              placeholder="Enter your evaluation comments..."
              rows="5"
              cols="50"
            />
          ) : (
            <div className="options">
              {question.options.map((option, index) => (
                <label key={index} className="option-label">
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    value={option}
                    checked={answers[question.id] === option}
                    onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                  />
                  <span className="option-text">{String.fromCharCode(65 + index)}. {option}</span>
                </label>
              ))}
            </div>
          )}

          <div className="navigation-buttons">
            {currentQuestion > 0 && (
              <button onClick={handlePrevious} className="prev-btn">
                PREVIOUS
              </button>
            )}
            <button onClick={handleNext} className="next-btn">
              {currentQuestion < questions.length - 1 ? 'NEXT' : 'SUBMIT EVALUATION'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PeerEvaluation