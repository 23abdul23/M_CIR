import React from 'react'
import { useNavigate } from 'react-router-dom'
import Header from './Header'

const MainMenu = ({ selectedBattalion, currentUser, onLogout }) => {
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

  return (
    <div className="main-menu-container">
      <Header currentUser={currentUser} onLogout={handleLogout} />

      <div className="menu-content">
        <div className="menu-buttons">
          <button 
            className="menu-btn start-examination"
            onClick={() => navigate('/army-number-entry')}
          >
            Manual<br/>EXAMINATION
          </button>
          <button 
            className="menu-btn view-data"
            onClick={() => navigate('/ai-exam')}
          >
            AI<br/>Examination
          </button>
        </div>
      </div>
    </div>
  )
}

export default MainMenu