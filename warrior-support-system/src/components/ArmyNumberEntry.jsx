import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Header from './Header'
import '../styles/ArmyNumberEntry.css'

const ArmyNumberEntry = ({ currentUser, onLogout }) => {
  const [armyNo, setArmyNo] = useState('')
  const [error, setError] = useState('')
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

  const handleProceed = async () => {
    if (!armyNo.trim()) {
      setError('Please enter Army Number')
      return
    }

    try {
      // Verify if army number exists
      const response = await axios.get(`/api/personnel/army-no/${armyNo}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      
      if (response.data) {
        // Store army number for examination
        localStorage.setItem('currentArmyNo', armyNo)
        navigate('/instructions')
      } else {
        setError('Army Number not found')
      }
    } catch (error) {
      setError('Army Number not found')
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
      </div>
    </div>
  )
}

export default ArmyNumberEntry