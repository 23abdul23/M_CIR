import React from 'react'
import { useNavigate } from 'react-router-dom'

const Header = ({ currentUser, onLogout }) => {
  const navigate = useNavigate()

  const handleLogout = () => {
    onLogout()
    navigate('/login')
  }

  return (
    <header className="app-header">
      <div className="header-left">
        <div className="header-logo-placeholder">LOGO 1</div>
        <div className="header-logo-placeholder">LOGO 2</div>
        <h1>WARRIOR SUPPORT SYSTEM</h1>
      </div>
      <div className="header-right">
        {currentUser && (
          <div className="user-info">
            <span className="user-name">{currentUser.fullName}</span>
            <span className="user-role">({currentUser.role.toUpperCase()})</span>
          </div>
        )}
        <div className="profile-logo-placeholder">PROFILE</div>
        <button className="logout-btn" onClick={handleLogout}>
          LOGOUT
        </button>
      </div>
    </header>
  )
}

export default Header