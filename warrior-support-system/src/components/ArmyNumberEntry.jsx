import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Header from './Header'
import '../styles/ArmyNumberEntry.css'
import UserRegister from './User_registeration'

const ArmyNumberEntry = ({ currentUser, onLogout }) => {
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

  const handleLogin = async (user, token) => {
    // setCurrentUser(user)
    localStorage.getItem('token')
    localStorage.getItem('user')

    
  }

  const handleProceed = async () => {
    if (!armyNo.trim()) {
      setError('Please enter Army Number')
      return
    }

    try {
      // Fetch the CO's set date for the exam period
      const coDateResponse = await axios.get('/api/examination/co-set-date', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })

      const coSetPeriod = (coDateResponse.data.setPeriod)

      // Verify if army number exists
      const response = await axios.get(`/api/personnel/army-no/${armyNo}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })

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


      if (response.data) {

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
          navigate('/instructions');
        } 
        else if (examModes.size === 1 && examModes.has("MANUAL")) {
          setError(`You have given this test, but can give the AI test`);
        }
        else if (examModes.size == 2){
          setError(`You can't give the test until the time period is over in ${coSetPeriod -  Math.round(diffInDays+1)} Day and ${Math.round(diffInHours % 24)} Hours.}.`);
        }
      }
    } catch (error) {
      // Handle Axios error response
      if (error.response && error.response.status === 400) {
        const message = error.response.data.message
        if (message === 'Your application is pending approval by the CO.') {
          setError('Your application is pending approval by the CO.')
        } else {
          setError(message || 'An error occurred.')
          return 
        }
      } else {
        console.log(error)
        setError('Army Number Not Valid, Register First')
        setShowRegister(true) // Show the registration component
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

export default ArmyNumberEntry