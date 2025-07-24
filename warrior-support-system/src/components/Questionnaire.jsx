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
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchPersonnelInfo()
    loadQuestionsFromDatabase()
  }, [])

  const fetchPersonnelInfo = async () => {
    const armyNo = localStorage.getItem('currentArmyNo')
    if (!armyNo) {
      setError('No Army Number found. Please start from the beginning.')
      navigate('/army-number-entry')
      return
    }

    try {
      const response = await axios.get(`/api/personnel/army-no/${armyNo}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      setPersonnelInfo(response.data)
    } catch (error) {
      console.error('Error fetching personnel info:', error)
      setError('Error fetching personnel information')
    }
  }

  const loadQuestionsFromDatabase = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/questions', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      
      console.log('Questions loaded from database:', response.data)
      setQuestions(response.data)
    } catch (error) {
      console.error('Error loading questions from database:', error)
      setError('Error loading questions. Please try again.')
      
      // Fallback to hardcoded questions if database fails
      console.log('Using fallback questions...')
      const fallbackQuestions = [
        {
          questionId: 1,
          questionText: "Maine paya ki main bahut chhoti-chhoti baton se pareshan ho jata hun",
          questionType: "MCQ",
          options: [
            { optionId: "A", optionText: "Yeh mujh par bilkul bhi lagu nahi hua." },
            { optionId: "B", optionText: "Kabhi-Kabhi mere saath aise hota hain." },
            { optionId: "C", optionText: "Aise mere saath aksar hota rehta hain." },
            { optionId: "D", optionText: "Aise lagbhag hamesha mere saath hota rehta hain." }
          ]
        },
        {
          questionId: 4,
          questionText: "Kya aap apni mental health improve karne ke liye koi suggestion dena chahenge?",
          questionType: "TEXT",
          options: []
        }
      ]
      setQuestions(fallbackQuestions)
    } finally {
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
    setError('')
  }

  const validateAnswers = () => {
    for (let question of questions) {
      if (!answers[question.questionId] || answers[question.questionId].trim() === '') {
        return `Please answer question ${question.questionId}`
      }
    }
    return null
  }

  const handleNext = () => {
    const currentQuestionObj = questions[currentQuestion]
    if (!answers[currentQuestionObj.questionId] || answers[currentQuestionObj.questionId].trim() === '') {
      setError('Please answer the current question before proceeding')
      return
    }

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
      setError('')
    } else {
      handleSubmitExamination()
    }
  }

  const handleBack = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
      setError('')
    }
  }

  const handleSubmitExamination = async () => {
    const validationError = validateAnswers()
    if (validationError) {
      setError(validationError)
      return
    }

    setIsSubmitting(true)
    setError('')

    try {
      const armyNo = localStorage.getItem('currentArmyNo')
      const token = localStorage.getItem('token')

      if (!armyNo) {
        throw new Error('Army Number not found')
      }

      if (!token) {
        throw new Error('Authentication token not found')
      }

      console.log('Submitting examination with data:', {
        armyNo,
        answers,
        completedAt: new Date()
      })

      // Format answers for backend
      const formattedAnswers = Object.keys(answers).map(questionId => ({
        questionId: questionId,
        answer: answers[questionId]
      }))

      const response = await axios.post('/api/examination', {
        armyNo: armyNo,
        answers: formattedAnswers,
        completedAt: new Date()
      }, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      console.log('Examination submitted successfully:', response.data)

      localStorage.removeItem('currentArmyNo')
      navigate('/examination-complete')

    } catch (error) {
      console.error('Error submitting examination:', error)
      
      let errorMessage = 'Error submitting examination. Please try again.'
      
      if (error.response) {
        console.error('Server error:', error.response.data)
        errorMessage = error.response.data.message || errorMessage
      } else if (error.request) {
        console.error('Network error:', error.request)
        errorMessage = 'Network error. Please check your connection.'
      } else {
        console.error('Error:', error.message)
        errorMessage = error.message
      }
      
      setError(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="questionnaire-container">
        <Header currentUser={currentUser} onLogout={handleLogout} />
        <div className="questionnaire-content">
          <div className="loading">Loading questionnaire...</div>
        </div>
      </div>
    )
  }

  if (!questions.length || !personnelInfo) {
    return (
      <div className="questionnaire-container">
        <Header currentUser={currentUser} onLogout={handleLogout} />
        <div className="questionnaire-content">
          <div className="loading">Loading questionnaire...</div>
          {error && <div className="error-message">{error}</div>}
        </div>
      </div>
    )
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
        
        {error && <div className="error-message">{error}</div>}

        <div className="question-section">
          <div className="question-progress">
            Question {currentQuestion + 1} of {questions.length}
          </div>
          
          <h3>{currentQuestion + 1}. {question.questionText}</h3>
          
          {question.questionType === 'TEXT' ? (
            <textarea
              value={answers[question.questionId] || ''}
              onChange={(e) => handleAnswerChange(question.questionId, e.target.value)}
              placeholder="Enter your answer here..."
              rows="5"
              cols="50"
              disabled={isSubmitting}
            />
          ) : (
            <div className="options">
              {question.options.map((option, index) => (
                <label key={option.optionId} className="option-label">
                  <input
                    type="radio"
                    name={`question-${question.questionId}`}
                    value={option.optionText}
                    checked={answers[question.questionId] === option.optionText}
                    onChange={(e) => handleAnswerChange(question.questionId, e.target.value)}
                    disabled={isSubmitting}
                  />
                  <span className="option-text">{option.optionId}. {option.optionText}</span>
                </label>
              ))}
            </div>
          )}
          
          <div className="navigation-buttons">
            {currentQuestion > 0 && (
              <button 
                onClick={handleBack} 
                className="back-btn"
                disabled={isSubmitting}
              >
                BACK
              </button>
            )}
            
            <button 
              onClick={handleNext} 
              className="next-btn"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'SUBMITTING...' : 
               currentQuestion < questions.length - 1 ? 'NEXT' : 'SUBMIT'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Questionnaire