import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from './Header'
import '../styles/Instructions.css'

const Instructions = ({ currentUser, onLogout }) => {
  const [agreed, setAgreed] = useState(false)
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

  const handleProceed = () => {
    if (agreed) {
      navigate('/questionnaire')
    }
  }

  return (
    <div className="instructions-container">
      <Header currentUser={currentUser} onLogout={handleLogout} />

      <div className="instructions-content">
        <h2>INSTRUCTIONS</h2>
        
        <div className="instructions-box">
          <h3>PLEASE READ ALL INSTRUCTIONS CAREFULLY</h3>
          
          <div className="instruction-list">
            <p>1. Sabhi prashno ke vichar karke, kisi bhi dabavv ya jaldi ke bina samdhan de.</p>
            <p>2. Sabhi prashno ka uttar dena zaroori hai.</p>
            <p>3. Prashno ka jawab dene mein samay ki koi pabandi nahi hai.</p>
            <p>4. Har prashan ke char(4) vikalpon me se sahi vikalp ko chunne.</p>
            <p>5. Agar kisi prashna mein vikalpon ki jagah, TEXT BOX diya gaya hai to uska uttar subjectively keyboard se type karke de.</p>
          </div>
          
          <div className="agreement-section">
            <label className="checkbox-container">
              <input
                type="checkbox"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
              />
              MAIN SEHMAT HOON KI MAINE SABHI INSTRUCTIONS KO PADHA HAI.
            </label>
          </div>
          
          <button 
            onClick={handleProceed} 
            className="proceed-btn"
            disabled={!agreed}
          >
            PROCEED
          </button>
        </div>
      </div>
    </div>
  )
}

export default Instructions