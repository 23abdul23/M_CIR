import React from 'react'
import { useNavigate } from 'react-router-dom'

const ExaminationComplete = () => {
  const navigate = useNavigate()

  const handleOk = () => {
    localStorage.removeItem('currentArmyNo')
    navigate('/main-menu')
  }

  return (
    <div className="examination-complete-container">
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

      <div className="complete-content">
        <div className="complete-modal">
          <div className="success-icon">
            <div className="checkmark">✓</div>
          </div>
          <h2>EXAMINATION<br/>COMPLETE</h2>
          <button onClick={handleOk} className="ok-btn">OKAY</button>
        </div>
      </div>
    </div>
  )
}

export default ExaminationComplete