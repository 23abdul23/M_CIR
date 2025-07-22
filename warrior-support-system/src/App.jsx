import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './components/Login'
import Register from './components/Register'
import BattalionSelection from './components/BattalionSelection'
import MainMenu from './components/MainMenu'
import DataTable from './components/DataTable'
import ArmyNumberEntry from './components/ArmyNumberEntry'
import Instructions from './components/Instructions'
import Questionnaire from './components/Questionnaire'
import ExaminationComplete from './components/ExaminationComplete'
import './styles/App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [selectedBattalion, setSelectedBattalion] = useState('')
  const [currentUser, setCurrentUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')
    
    if (token && user) {
      setIsAuthenticated(true)
      setCurrentUser(JSON.parse(user))
    }
    setLoading(false)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('currentArmyNo')
    setIsAuthenticated(false)
    setCurrentUser(null)
    setSelectedBattalion('')
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route 
            path="/login" 
            element={
              !isAuthenticated ? 
              <Login 
                setIsAuthenticated={setIsAuthenticated}
                setCurrentUser={setCurrentUser}
              /> :
              <Navigate to="/battalion-selection" />
            } 
          />
          
          <Route 
            path="/register" 
            element={
              !isAuthenticated ? 
              <Register /> :
              <Navigate to="/battalion-selection" />
            } 
          />
          
          <Route 
            path="/battalion-selection" 
            element={
              isAuthenticated ? 
              <BattalionSelection 
                selectedBattalion={selectedBattalion}
                setSelectedBattalion={setSelectedBattalion}
                currentUser={currentUser}
                onLogout={handleLogout}
              /> : 
              <Navigate to="/login" />
            } 
          />
          
          <Route 
            path="/main-menu" 
            element={
              isAuthenticated ? 
              <MainMenu 
                selectedBattalion={selectedBattalion}
                currentUser={currentUser}
                onLogout={handleLogout}
              /> : 
              <Navigate to="/login" />
            } 
          />
          
          <Route 
            path="/data-table" 
            element={
              isAuthenticated ? 
              <DataTable 
                selectedBattalion={selectedBattalion}
                currentUser={currentUser}
                onLogout={handleLogout}
              /> : 
              <Navigate to="/login" />
            } 
          />
          
          <Route 
            path="/army-number-entry" 
            element={
              isAuthenticated ? 
              <ArmyNumberEntry 
                currentUser={currentUser}
                onLogout={handleLogout}
              /> : 
              <Navigate to="/login" />
            } 
          />
          
          <Route 
            path="/instructions" 
            element={
              isAuthenticated ? 
              <Instructions 
                currentUser={currentUser}
                onLogout={handleLogout}
              /> : 
              <Navigate to="/login" />
            } 
          />
          
          <Route 
            path="/questionnaire" 
            element={
              isAuthenticated ? 
              <Questionnaire 
                currentUser={currentUser}
                onLogout={handleLogout}
              /> : 
              <Navigate to="/login" />
            } 
          />
          
          <Route 
            path="/examination-complete" 
            element={
              isAuthenticated ? 
              <ExaminationComplete 
                currentUser={currentUser}
                onLogout={handleLogout}
              /> : 
              <Navigate to="/login" />
            } 
          />
          
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App