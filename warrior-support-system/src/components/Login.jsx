import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import '../styles/Login.css'

const Login = ({ onLogin }) => {
  const [selectedRole, setSelectedRole] = useState(null)
  const [formData, setFormData] = useState({
    username: '',
    password: '123456'
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleRoleSelect = (role) => {
    if (role === 'USER') {
      // Direct login for users without credentials
      handleDirectLogin('USER')
    } 
    else {
      setSelectedRole(role)
      setError('')
    }
  }

  const handleDirectLogin = async (role) => {
    const userCredentials = { username: 'user_army', password: '123456' }
    
    try {
      const response = await axios.post('/api/auth/login', userCredentials)
      const { user, token } = response.data
      onLogin(user, token)
      navigate('/battalion-selection')
    } catch (error) {
      setError('Login failed. Please try again.')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await axios.post('/api/auth/login', formData)
      const { user, token } = response.data
      
      onLogin(user, token)
      
      // Redirect based on user role
      switch (user.role) {
        case 'CO':
          navigate('/co-dashboard')
          break
        case 'JCO':
          navigate('/jso-dashboard')
          break
        default:
          navigate('/')
      }
    } catch (error) {
      setError(error.response?.data?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleBackToRoles = () => {
    setSelectedRole(null)
    setFormData({ username: '', password: '123456' })
    setError('')
  }

  return (
    <div className="login-container">
      <div className="login-content">
        <div className="login-header">
          <div className="logo-section">
            <div className="logo-placeholder logo1">
            </div>
            <div className="logo-placeholder logo2">
            </div>

          </div>
          <h1>SOLDIER SUPPORT SYSTEM</h1>
          <p className="login-subtitle">Secure Authentication Portal</p>
        </div>

        <div className="login-form-container">
          {!selectedRole ? (
            // Role selection cards
            <div className="role-selection">
              <h2>Select Your Role</h2>
              <p className="role-subtitle">Choose your access level to continue</p>
              
              <div className="role-cards">
                <div 
                  className="role-card co-card"
                  onClick={() => handleRoleSelect('CO')}
                >
                  <span className="role-icon">👨‍💼</span>
                  <h3>CO</h3>
                  
                </div>
                
                <div 
                  className="role-card jso-card"
                  onClick={() => handleRoleSelect('JCO')}
                >
                  <span className="role-icon">👨‍✈️</span>
                  <h3>JCO</h3>
                </div>
                
                <div 
                  className="role-card user-card"
                  onClick={() => handleRoleSelect('USER')}
                >
                  <span className="role-icon">👨</span>
                  <h3>User</h3>
                </div>
              </div>
            </div>
          ) : (
            // Login form for selected role
            <div className="login-form-section">
              <button className="back-btn" onClick={handleBackToRoles}>
                Back
              </button>
              
              <form onSubmit={handleSubmit} className="login-form">
                <h2>{selectedRole} LOGIN</h2>
                <p className="login-description">
                  {selectedRole === 'CO' ? 'Enter your administrative credentials' : 'Enter your officer credentials'}
                </p>
                
                {error && <div className="error-message">{error}</div>}
                
                <div className="form-group">
                  <label htmlFor="username">Username</label>
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    required
                    placeholder="Enter your username"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="password">Password</label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    placeholder="Enter your password"
                  />
                </div>

                <button type="submit" className="login-btn" disabled={loading}>
                  {loading ? 'LOGGING IN...' : 'LOGIN'}
                </button>
              </form>
            </div>
          )}

          <div className="login-footer">
            <div className="system-info">
              <small>SOLDIER SUPPORT SYSTEM v2.0 | Secure Military Portal</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login