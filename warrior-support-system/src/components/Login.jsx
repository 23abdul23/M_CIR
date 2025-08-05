import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import '../styles/Login.css'

const Login = ({ onLogin }) => {
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
        case 'JSO':
          navigate('/jso-dashboard')
          break
        case 'USER':
          navigate('/battalion-selection')
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

  // Demo login functions for testing
  const handleDemoLogin = async (role) => {
    const demoCredentials = {
      CO: { username: 'co_admin', password: '123456' },
      JSO: { username: 'jso_allahabad', password: '123456' },
      USER: { username: 'user_army', password: '123456' }
    }

    const credentials = demoCredentials[role]
    setFormData(credentials)
    
    try {
      const response = await axios.post('/api/auth/login', credentials)
      const { user, token } = response.data
      onLogin(user, token)
      
      switch (user.role) {
        case 'CO':
          navigate('/co-dashboard')
          break
        case 'JSO':
          navigate('/jso-dashboard')
          break
        case 'USER':
          navigate('/battalion-selection')
          break
        default:
          navigate('/')
      }
    } catch (error) {
      setError('Demo login failed. Please use manual login.')
    }
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
          <h1>WARRIOR SUPPORT SYSTEM</h1>
          <p className="login-subtitle">Secure Authentication Portal</p>
        </div>

        <div className="login-form-container">
          <form onSubmit={handleSubmit} className="login-form">
            <h2>LOGIN</h2>
            
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

          <div className="demo-section">
            <h3>Demo Login Options</h3>
            <p>Quick access for testing different user roles:</p>
            
            <div className="demo-buttons">
              <button 
                onClick={() => handleDemoLogin('CO')} 
                className="demo-btn co-btn"
                disabled={loading}
              >
                <span className="role-icon">👨‍💼</span>
                <div>
                  <strong>CO (Admin)</strong>
                  <small>Full system access</small>
                </div>
              </button>
              
              <button 
                onClick={() => handleDemoLogin('JSO')} 
                className="demo-btn jso-btn"
                disabled={loading}
              >
                <span className="role-icon">👨‍✈️</span>
                <div>
                  <strong>JSO (Officer)</strong>
                  <small>Battalion management</small>
                </div>
              </button>
              
              <button 
                onClick={() => handleDemoLogin('USER')} 
                className="demo-btn user-btn"
                disabled={loading}
              >
                <span className="role-icon">👨</span>
                <div>
                  <strong>USER (Soldier)</strong>
                  <small>Basic access</small>
                </div>
              </button>
            </div>
          </div>

          <div className="login-footer">
            <div className="system-info">
              <small>Warrior Support System v2.0 | Secure Military Portal</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login