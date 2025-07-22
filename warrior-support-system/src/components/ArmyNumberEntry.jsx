import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const ArmyNumberEntry = () => {
  const [armyNo, setArmyNo] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

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
      <header className="app-header">
        <div className="header-left">
          <img src="/images/logo1.png" alt="Logo 1" className="header-logo" />
          <img src="/images/logo2.png" alt="Logo 2" className="header-logo" />
          <h1>WARRIOR SUPPORT SYSTEM</h1>
        </div>
        <div className="header-right">
          <img src="/images/logo1.png" alt="Profile" className="profile-logo" />
          <button className="logout-btn">LOGOUT</button>
        </div>
      </header>

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