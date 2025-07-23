import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'

const Login = ({ setIsAuthenticated, setCurrentUser }) => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await axios.post('/api/auth/login', credentials)
      
      // Store token and user info
      localStorage.setItem('token', response.data.token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      
      setIsAuthenticated(true)
      setCurrentUser(response.data.user)
      navigate('/battalion-selection')
    } catch (error) {
      setError(error.response?.data?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="login-container">
      <div className="login-left">
        <h1 className="system-title">WARRIOR SUPPORT SYSTEM</h1>
        <div className="logo-container">
          <div className="military-logo-placeholder"><img src="/images/logo1.png" alt="Logo 1" className="login-logo" /></div>
        </div>
        <p className="login-subtitle">Secure Military Personnel Management</p>
      </div>
      
      <div className="login-right">
        <div className="login-logos">
          <div className="login-logo-placeholder"><img src="/images/logo1.png" alt="Logo 1" className="login-logo" /></div>
          <div className="login-logo-placeholder"><img src="/images/logo2.png" alt="Logo 2" className="login-logo" /></div>
        </div>
        
        <div className="login-form-container">
          <h2>LOGIN</h2>
          
          <form onSubmit={handleSubmit} className="login-form">
            <input
              type="text"
              name="username"
              placeholder="USERNAME"
              value={credentials.username}
              onChange={handleChange}
              required
            />
            <input
              type="password"
              name="password"
              placeholder="PASSWORD"
              value={credentials.password}
              onChange={handleChange}
              required
            />
            <button type="submit" className="login-btn" disabled={loading}>
              {loading ? 'LOGGING IN...' : 'LOG IN'}
            </button>
            {error && <div className="error-message">{error}</div>}
          </form>

          <div className="register-link">
            <p>Don't have an account? <Link to="/register">Register here</Link></p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login