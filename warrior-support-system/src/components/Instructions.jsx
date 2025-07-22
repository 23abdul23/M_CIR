import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const Instructions = () => {
  const [agreed, setAgreed] = useState(false)
  const navigate = useNavigate()

  const handleProceed = () => {
    if (agreed) {
      navigate('/questionnaire')
    }
  }

  return (
    <div className="instructions-container">
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