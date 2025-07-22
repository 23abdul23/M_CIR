import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    role: 'user',
    fullName: '',
    email: '',
    rank: '',
    unit: ''
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long')
      return
    }

    setLoading(true)

    try {
      const response = await axios.post('/api/auth/register', {
        username: formData.username,
        password: formData.password,
        role: formData.role,
        fullName: formData.fullName,
        email: formData.email,
        rank: formData.rank,
        unit: formData.unit
      })

      setSuccess('Registration successful! You can now login.')
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } catch (error) {
      setError(error.response?.data?.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="register-container">
      <div className="register-left">
        <h1 className="system-title">WARRIOR SUPPORT SYSTEM</h1>
        <div className="logo-container">
          <div className="military-logo-placeholder">LOGO</div>
        </div>
        <p className="register-subtitle">Join the Warrior Support Network</p>
      </div>
      
      <div className="register-right">
        <div className="register-logos">
          <div className="register-logo-placeholder">LOGO 1</div>
          <div className="register-logo-placeholder">LOGO 2</div>
        </div>
        
        <div className="register-form-container">
          <h2>CREATE ACCOUNT</h2>
          
          <form onSubmit={handleSubmit} className="register-form">
            <div className="form-row">
              <input
                type="text"
                name="fullName"
                placeholder="FULL NAME"
                value={formData.fullName}
                onChange={handleChange}
                required
              />
              <input
                type="text"
                name="username"
                placeholder="USERNAME"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-row">
              <input
                type="email"
                name="email"
                placeholder="EMAIL ADDRESS"
                value={formData.email}
                onChange={handleChange}
                required
              />
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                required
              >
                <option value="user">USER</option>
                <option value="officer">OFFICER</option>
                <option value="admin">ADMIN</option>
              </select>
            </div>

            <div className="form-row">
              <input
                type="text"
                name="rank"
                placeholder="RANK"
                value={formData.rank}
                onChange={handleChange}
                required
              />
              <input
                type="text"
                name="unit"
                placeholder="UNIT/BATTALION"
                value={formData.unit}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-row">
              <input
                type="password"
                name="password"
                placeholder="PASSWORD"
                value={formData.password}
                onChange={handleChange}
                required
              />
              <input
                type="password"
                name="confirmPassword"
                placeholder="CONFIRM PASSWORD"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </div>

            <button type="submit" className="register-btn" disabled={loading}>
              {loading ? 'CREATING ACCOUNT...' : 'REGISTER'}
            </button>

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
          </form>

          <div className="login-link">
            <p>Already have an account? <Link to="/login">Login here</Link></p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Register