import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import axios from 'axios'

// Components
import Login from './components/Login'
import Register from './components/Register'
import BattalionSelection from './components/BattalionSelection'
import MainMenu from './components/MainMenu'
import DataTable from './components/DataTable'
import ArmyNumberEntry from './components/ArmyNumberEntry'
import Instructions from './components/Instructions'
import Questionnaire from './components/Questionnaire'
import ExaminationComplete from './components/ExaminationComplete'
import CODashboard from './components/CODashboard'
import JSODashboard from './components/JSODashboard'
import PeerEvaluation from './components/PeerEvaluation'
import DataTable_CO from './components/DataTable_CO'
import DecideAsessment from './components/DecideAssessment'
import AI_Assessment from './components/AI_examination'
import Facial_examination from './components/Facial_examination'
import AI_Questionnaire from './components/AI_Questionnaire'
import FinancialForm from './components/FinancialForm'

// Styles
import './styles/App.css'

// Set axios base URL
axios.defaults.baseURL = 'http://localhost:5000'

function App() {
  const [currentUser, setCurrentUser] = useState(null)
  const [selectedBattalion, setSelectedBattalion] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')
    
    if (token && user) {
      try {
        const parsedUser = JSON.parse(user)
        setCurrentUser(parsedUser)
        
        // Verify token is still valid
        axios.get('/api/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        }).catch(() => {
          // Token invalid, clear storage
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          setCurrentUser(null)
        })
      } catch (error) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  const handleLogin = async (user, token) => {
    setCurrentUser(user)
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))

    
  }

  const handleLogout = () => {
    setCurrentUser(null)
    setSelectedBattalion('')
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('currentArmyNo')
  }

  // Role-based route protection
  const ProtectedRoute = ({ children, allowedRoles }) => {
    if (!currentUser) {
      return <Navigate to="/login" />
    }
    
    if (allowedRoles && !allowedRoles.includes(currentUser.role)) {
      return <Navigate to="/unauthorized" />
    }
    
    return children
  }

  // Role-based dashboard redirect
  const DashboardRedirect = () => {
    if (!currentUser) return <Navigate to="/login" />
    
    switch (currentUser.role) {
      case 'CO':
        return <Navigate to="/co-dashboard" />
      case 'JSO':
        return <Navigate to="/jso-dashboard" />
      case 'USER':
        return <Navigate to="/battalion-selection" />
      default:
        return <Navigate to="/login" />
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Public Routes */}
          <Route 
            path="/login" 
            element={
              currentUser ? <DashboardRedirect /> : 
              <Login onLogin={handleLogin} />
            } 
          />
          <Route 
            path="/register" 
            element={
              currentUser ? <DashboardRedirect /> : 
              <Register onRegister={handleLogin} />
            } 
          />

          {/* CO Routes */}
          <Route 
            path="/co-dashboard" 
            element={
              <ProtectedRoute allowedRoles={['CO']}>
                <CODashboard 
                  currentUser={currentUser} 
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          {/* JSO Routes */}
          <Route 
            path="/jso-dashboard" 
            element={
              <ProtectedRoute allowedRoles={['JSO']}>
                <JSODashboard 
                  currentUser={currentUser} 
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          {/* Peer Evaluation Route (JSO only) */}
          <Route 
            path="/peer-evaluation/:personnelId" 
            element={
              <ProtectedRoute allowedRoles={['JSO']}>
                <PeerEvaluation 
                  currentUser={currentUser} 
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          {/* Common Routes for JSO*/}
          <Route 
            path="/data-table-jso" 
            element={
              <ProtectedRoute allowedRoles={['JSO']}>
                <DataTable 
                  selectedBattalion={selectedBattalion}
                  currentUser={currentUser}
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/data-table-co" 
            element={
              <ProtectedRoute allowedRoles={['CO']}>
                <DataTable_CO
                  selectedBattalion={selectedBattalion}
                  currentUser={currentUser}
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          {/* User Routes */}
          <Route 
            path="/battalion-selection" 
            element={
              <ProtectedRoute allowedRoles={['USER']}>
                <BattalionSelection 
                  selectedBattalion={selectedBattalion}
                  setSelectedBattalion={setSelectedBattalion}
                  currentUser={currentUser}
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/decide-assessment" 
            element={
              <ProtectedRoute allowedRoles={['USER']}>
                <DecideAsessment 
                  selectedBattalion={selectedBattalion}
                  currentUser={currentUser}
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/main-menu" 
            element={
              <ProtectedRoute allowedRoles={['USER']}>
                <MainMenu 
                  selectedBattalion={selectedBattalion}
                  currentUser={currentUser}
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/fianancial-menu" 
            element={
              <ProtectedRoute allowedRoles={['USER']}>
                <FinancialForm/>
              </ProtectedRoute>
            } 
          />

          <Route 
          path="/ai-questionnaire" 
          element={<AI_Questionnaire />} 
          />

          {/* Examination Routes (All authenticated users) */}
          <Route 
            path="/ai-exam" 
            element={
              <ProtectedRoute>
                <AI_Assessment 
                  currentUser={currentUser}
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/facial-analysis" 
            element={
              <ProtectedRoute>
                <Facial_examination 
                  currentUser={currentUser}
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          {/* Examination Routes (All authenticated users) */}
          <Route 
            path="/army-number-entry" 
            element={
              <ProtectedRoute>
                <ArmyNumberEntry 
                  currentUser={currentUser}
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/instructions" 
            element={
              <ProtectedRoute>
                <Instructions 
                  currentUser={currentUser}
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/questionnaire" 
            element={
              <ProtectedRoute>
                <Questionnaire 
                  currentUser={currentUser}
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/examination-complete" 
            element={
              <ProtectedRoute>
                <ExaminationComplete 
                  currentUser={currentUser}
                  onLogout={handleLogout}
                />
              </ProtectedRoute>
            } 
          />

          

          {/* Default Routes */}
          <Route path="/" element={<DashboardRedirect />} />
          <Route 
            path="/unauthorized" 
            element={
              <div className="unauthorized">
                <h2>Access Denied</h2>
                <p>You don't have permission to access this page.</p>
              </div>
            } 
          />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App