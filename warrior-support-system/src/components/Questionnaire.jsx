import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Header from './Header'
import '../styles/Questionnaire.css'

const Questionnaire = ({ currentUser, onLogout }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState({})
  const [questions, setQuestions] = useState([])
  const [personnelInfo, setPersonnelInfo] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchPersonnelInfo()
    loadQuestions()
  }, [])

  const fetchPersonnelInfo = async () => {
    const armyNo = localStorage.getItem('currentArmyNo')
    try {
      const response = await axios.get(`/api/personnel/army-no/${armyNo}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      setPersonnelInfo(response.data)
    } catch (error) {
      console.error('Error fetching personnel info:', error)
    }
  }

  const loadQuestions = () => {
    // Sample questions - in real app, these would come from backend
    const sampleQuestions = [
      {
        id: 1,
        question: "Maine paya ki main bahut chhoti-chhoti baton se pareshan ho jata hun",
        options: [
          "Yeh mujh par bilkul bhi lagu nahi hua.",
          "Kabhi-Kabhi mere saath aise hota hain.",
          "Aise mere saath aksar hota rehta hain.",
          "Aise lagbhag hamesha mere saath hota rehta hain."
        ]
      },
      {
        id: 2,
        question: "Any suggestion?",
        type: "text"
      }
    ]
    setQuestions(sampleQuestions)
  }

  const handleLogout = () => {
    // Clear all stored data
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('currentArmyNo')
    
    // Call parent logout function
    if (onLogout) {
      onLogout()
    }
    
    // Redirect to login page
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
      handleSubmitExamination()
    }
  }

  const handleSubmitExamination = async () => {
    try {
      await axios.post('/api/examination', {
        armyNo: localStorage.getItem('currentArmyNo'),
        answers: answers,
        completedAt: new Date()
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      navigate('/examination-complete')
    } catch (error) {
      console.error('Error submitting examination:', error)
    }
  }

  if (!questions.length || !personnelInfo) {
    return <div>Loading...</div>
  }

  const question = questions[currentQuestion]

  return (
    <div className="questionnaire-container">
      <Header currentUser={currentUser} onLogout={handleLogout} />

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
            <span>{personnelInfo.coySquadronBty}</span>
          </div>
        </div>

        <h2>QUESTIONNAIRE</h2>

        <div className="question-section">
          <h3>{currentQuestion + 1}. {question.question}</h3>

          {question.type === 'text' ? (
            <textarea
              value={answers[question.id] || ''}
              onChange={(e) => handleAnswerChange(question.id, e.target.value)}
              placeholder="Enter your answer here..."
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

          <button onClick={handleNext} className="next-btn">
            {currentQuestion < questions.length - 1 ? 'NEXT' : 'SUBMIT'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Questionnaire