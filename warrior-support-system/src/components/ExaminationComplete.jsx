import React from 'react'
import { useNavigate } from 'react-router-dom'
import Header from './Header'
import '../styles/ExaminationComplete.css'

const ExaminationComplete = ({ currentUser, onLogout }) => {
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

  const handleOk = () => {
    localStorage.removeItem('currentArmyNo')
    navigate('/main-menu')
  }

  return (
    <div className="examination-complete-container">
      <Header currentUser={currentUser} onLogout={handleLogout} />

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