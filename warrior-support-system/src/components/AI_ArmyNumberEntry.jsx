import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Header from './Header'
import '../styles/ArmyNumberEntry.css'
import UserRegister from './User_registeration'

const AI_ArmyNumberEntry = ({ currentUser, onLogout }) => {
  const [armyNo, setArmyNo] = useState('SSS1782K')
  const [error, setError] = useState('')
  const [showRegister, setShowRegister] = useState(false)

  const navigate = useNavigate()

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

  const handleLogin = async (data) => {
    const registeredArmyNo = data?.personnel?.armyNo
    if (registeredArmyNo) {
      setArmyNo(registeredArmyNo)
    }
    setShowRegister(false)
    setError('Registration submitted. Your application is pending approval by the CO.')
  }

  const handleProceed = async () => {
    setError('')

    if (!armyNo.trim()) {
      setError('Please enter Army Number')
      return
    }

    try {
      // Verify if army number exists
      const response = await axios.get(`/api/personnel/army-no/${armyNo}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })

      // Fetch CO period with safe fallback so this call never triggers registration UI.
      let coSetPeriod = 0
      try {
        const coDateResponse = await axios.get('/api/examination/co-set-date', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        })
        coSetPeriod = Number(coDateResponse?.data?.setPeriod ?? 0)
      } catch (periodError) {
        coSetPeriod = 0
      }

      let examModes = new Set();

      if (response.data.selfEvaluation == "COMPLETED"){
        const ExamResults = await axios.get(`/api/examination/all/army-no/${armyNo}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        })
        if (Array.isArray(ExamResults.data)) {
          examModes = new Set(ExamResults.data.map(e => e.mode));
        } else {
          examModes = new Set([ExamResults.data.mode]);
        }
      }

      localStorage.setItem('examModes', examModes.size)


      if (response.data) {
        setShowRegister(false)

        const examTaken = response.data.selfEvaluation
        const completedAt = new Date(response.data.updatedAt).getTime();
        const currentDate = Date.now();

        // Calculate difference in days
        const diffInDays = (currentDate - completedAt) / (1000 * 60 * 60 * 24);
        const diffInHours = (currentDate - completedAt) / (1000 * 60 * 60);

        // console.log("Days difference:", Math.round(diffInDays+1));
        console.log(examModes.size)

        if (diffInDays > coSetPeriod || examTaken == "NOT_ATTEMPTED") {
          localStorage.setItem('currentArmyNo', armyNo);
          navigate('/combined-assessment');
        } 
        else if (examModes.size === 1 && examModes.has("AI")) {
          setError(`You have given this test, but can give the Manual test`);
        }
        else if (examModes.size == 2){
          setError(`You can't give the test until the time period is over in ${coSetPeriod -  Math.round(diffInDays)} Day`);
        }
        else{
          localStorage.setItem('currentArmyNo', armyNo);
          navigate('/combined-assessment');
        }
      }
    } catch (error) {
      // Handle Axios error response
      if (error.response && error.response.status === 400) {
        const message = error.response.data.message
        if (message === 'Your application is pending approval by the CO.') {
          setError('Your application is pending approval by the CO.')
          setShowRegister(false)
        } else {
          setError(message || 'An error occurred.')
          setShowRegister(false)
          return 
        }
      } else if (error.response && error.response.status === 404) {
        setError('Army Number Not Valid, Register First')
        setShowRegister(true) // Show the registration component only when army number does not exist
      } else {
        console.log(error)
        const message = error.response?.data?.message || 'Unable to verify Army Number. Please try again.'
        setError(message)
        setShowRegister(false)
      }
    }
  }

  const handleBack = () => {
    navigate('/main-menu')
  }

  return (
    <div className="army-number-container">
      <Header currentUser={currentUser} onLogout={handleLogout} />

      <div className="entry-content">
        <div className="entry-form">
          <label>ENTER ARMY NO</label>
          <input
            type="text"
            placeholder="ARMY NO"
            value={armyNo}
            onChange={(e) => setArmyNo(e.target.value)}
          />
          {error && <div className="error-message">{error}</div>}
          
          <div className="entry-buttons">
            <button onClick={handleBack} className="back-btn">BACK</button>
            <button onClick={handleProceed} className="proceed-btn">PROCEED</button>
          </div>
        </div>
        {showRegister && (
          <div className="registration-section">
            <UserRegister onRegister={handleLogin} />
          </div>
        )}
      </div>
    </div>
  )
}

export default AI_ArmyNumberEntry
