"use client"

import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import Header from "./Header"
import "../styles/Questionnaire.css"

const depressionItems = [3, 5, 10, 13, 16, 17, 21, 24, 26, 31, 34, 37, 38, 42]
const anxietyItems = [2, 4, 7, 9, 15, 19, 20, 23, 25, 28, 30, 36, 40, 41]
const stressItems = [1, 6, 8, 11, 12, 14, 18, 22, 27, 29, 32, 33, 35, 39]

function scoreDASS(answers) {
  let depression = 0,
    anxiety = 0,
    stress = 0

  depressionItems.forEach((q) => {
    depression += Number(answers[q] ?? 0)
  })
  anxietyItems.forEach((q) => {
    anxiety += Number(answers[q] ?? 0)
  })
  stressItems.forEach((q) => {
    stress += Number(answers[q] ?? 0)
  })

  // Multiply by 2 for DASS-21 scoring (since we're using 21 items instead of 42)
  depression *= 2
  anxiety *= 2
  stress *= 2

  const depressionSeverity =
    depression <= 9
      ? "Normal"
      : depression <= 13
        ? "Mild"
        : depression <= 20
          ? "Moderate"
          : depression <= 27
            ? "Severe"
            : "Extremely Severe"

  const anxietySeverity =
    anxiety <= 7
      ? "Normal"
      : anxiety <= 9
        ? "Mild"
        : anxiety <= 14
          ? "Moderate"
          : anxiety <= 19
            ? "Severe"
            : "Extremely Severe"

  const stressSeverity =
    stress <= 14
      ? "Normal"
      : stress <= 18
        ? "Mild"
        : stress <= 25
          ? "Moderate"
          : stress <= 33
            ? "Severe"
            : "Extremely Severe"

  return {
    depression,
    depressionSeverity,
    anxiety,
    anxietySeverity,
    stress,
    stressSeverity,
  }
}

const Questionnaire = ({ currentUser, onLogout }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState({})
  const [questions, setQuestions] = useState([])
  const [personnelInfo, setPersonnelInfo] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(true)
  const [showResults, setShowResults] = useState(false)
  const [finalScores, setFinalScores] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchPersonnelInfo()
    loadQuestionsFromDatabase()
  }, [])

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

  const loadQuestionsFromDatabase = async () => {
  try {
    setLoading(true)
    const response = await axios.get("/api/questions", {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    })
    setQuestions(response.data)
  } catch (error) {
    setError("Error loading questions. Please try again.")
    // Fallback questions
    setQuestions([
      {
        questionId: 1,
        questionText: "Maine paya ki main bahut chhoti-chhoti baton se pareshan ho jata hun",
        questionType: "MCQ",
        options: [
          { optionId: "0", optionText: "Yeh mujh par bilkul bhi lagu nahi hua." },
          { optionId: "1", optionText: "Kabhi-Kabhi mere saath aise hota hain." },
          { optionId: "2", optionText: "Aise mere saath aksar hota rehta hain." },
          { optionId: "3", optionText: "Aise lagbhag hamesha mere saath hota rehta hain." },
        ],
      },
    ])
  } finally {
    setLoading(false)
  }
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    localStorage.removeItem("currentArmyNo")
    if (onLogout) onLogout()
    navigate("/login")
  }

  const handleAnswerChange = (questionId, answer, questionType) => {
    setAnswers({
      ...answers,
      [questionId]: questionType === "MCQ" ? Number(answer) : answer,
    })
    setError("")
  }

  const validateAnswers = () => {
    for (const question of questions) {
      if (
        answers[question.questionId] === undefined ||
        answers[question.questionId] === null ||
        (typeof answers[question.questionId] === "string" && answers[question.questionId].trim() === "")
      ) {
        return `Please answer question ${question.questionId}`
      }
    }
    return null
  }

  const handleNext = () => {
    const currentQuestionObj = questions[currentQuestion]
    if (
      answers[currentQuestionObj.questionId] === undefined ||
      answers[currentQuestionObj.questionId] === null ||
      (typeof answers[currentQuestionObj.questionId] === "string" &&
        answers[currentQuestionObj.questionId].trim() === "")
    ) {
      setError("Please answer the current question before proceeding")
      return
    }
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
      setError("")
    } else {
      handleSubmitExamination()
    }
  }


  const handleSubmitExamination = async () => {
    const validationError = validateAnswers()
    if (validationError) {
      setError(validationError)
      return
    }
    setIsSubmitting(true)
    setError("")

    try {
      const armyNo = localStorage.getItem("currentArmyNo")

      // Calculate DASS scores
      const scores = scoreDASS(answers)

      
      // Prepare examination data with scores
      const examinationData = {
        armyNo: armyNo,
        answers: Object.keys(answers).map((questionId) => ({
          questionId,
          answer: answers[questionId],
        })),
        dassScores: {
          depression: scores.depression,
          depressionSeverity: scores.depressionSeverity,
          anxiety: scores.anxiety,
          anxietySeverity: scores.anxietySeverity,
          stress: scores.stress,
          stressSeverity: scores.stressSeverity,
        },
        battalion : localStorage.getItem('selectedBattalion'),
        completedAt: new Date(),
        
      }

      console.log(examinationData)
      
      
      // Submit to backend
      const response = await axios.post("/api/examination/submit", examinationData, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      })
      
      console.log('Examination submitted successfully:', response.data)
      

      setFinalScores(scores)
      setShowResults(true)
    } catch (error) {
      console.error("Error submitting examination:", error)
      setError("Error submitting examination. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleContinue = () => {
    localStorage.removeItem("currentArmyNo")
    navigate("/army-number-entry")
  }

  if (loading) {
    return (
      <div className="questionnaire-container">
        <Header currentUser={currentUser} onLogout={handleLogout} />
        <div className="questionnaire-content">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <span>Loading questionnaire...</span>
          </div>
        </div>
      </div>
    )
  }

  if (showResults && finalScores) {
    return (
      <div className="questionnaire-container">
        <Header currentUser={currentUser} onLogout={handleLogout} />
        <div className="questionnaire-content">
          <div className="results-container">
            <div className="results-header">
              <div className="success-icon">
                <div className="checkmark">✓</div>
              </div>
              <h2>EXAMINATION COMPLETED</h2>
              <p className="results-subtitle">Your mental health assessment results</p>
            </div>
            <div className="results-actions">
              <button onClick={handleContinue} className="continue-btn">
                CONTINUE
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!questions.length || !personnelInfo) {
    return (
      <div className="questionnaire-container">
        <Header currentUser={currentUser} onLogout={handleLogout} />
        <div className="questionnaire-content">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <span>Loading questionnaire...</span>
          </div>
          {error && <div className="error-message">{error}</div>}
        </div>
      </div>
    )
  }

  const question = questions[currentQuestion]
  const progressPercentage = ((currentQuestion + 1) / questions.length) * 100

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
            <span>{personnelInfo.subBty}</span>
          </div>
        </div>

        <h2>MENTAL HEALTH QUESTIONNAIRE</h2>
        {error && <div className="error-message">{error}</div>}

        <div className="question-section">
          <div className="question-progress">
            <span>
              Question {currentQuestion + 1} of {questions.length}
            </span>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progressPercentage}%` }}></div>
            </div>
          </div>

          <h3>
            {currentQuestion + 1}. {question.questionText}
          </h3>

          {question.questionType === "TEXT" ? (
            <textarea
              value={answers[question.questionId] || ""}
              onChange={(e) => handleAnswerChange(question.questionId, e.target.value, question.questionType)}
              placeholder="Enter your answer here..."
              rows="5"
              cols="50"
              disabled={isSubmitting}
            />
          ) : (
            <div className="options">
              {question.options.map((option) => (
                <label key={option.optionId} className="option-label">
                  <input
                    type="radio"
                    name={`question-${question.questionId}`}
                    value={option.optionId}
                    checked={answers[question.questionId] === Number(option.optionId)}
                    onChange={(e) => handleAnswerChange(question.questionId, e.target.value, question.questionType)}
                    disabled={isSubmitting}
                  />
                  <span className="option-text">
                    {option.optionId}. {option.optionText}
                  </span>
                </label>
              ))}
            </div>
          )}

          <div className="navigation-buttons">
            <button onClick={handleNext} className="next-btn" disabled={isSubmitting}>
              {isSubmitting ? "SUBMITTING..." : currentQuestion < questions.length - 1 ? "NEXT" : "SUBMIT"}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Questionnaire
