import React from 'react'
import { useNavigate } from 'react-router-dom'

const MainMenu = ({ selectedBattalion }) => {
  const navigate = useNavigate()

  return (
    <div className="main-menu-container">
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

      <div className="menu-content">
        <div className="menu-buttons">
          <button 
            className="menu-btn start-examination"
            onClick={() => navigate('/army-number-entry')}
          >
            START<br/>EXAMINATION
          </button>
          <button 
            className="menu-btn view-data"
            onClick={() => navigate('/data-table')}
          >
            VIEW DATA
          </button>
        </div>
      </div>
    </div>
  )
}

export default MainMenu