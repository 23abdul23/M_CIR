"use client"

import { useState, useEffect } from "react"
import { Link, useNavigate } from "react-router-dom"
import axios from "axios"
import "../styles/Register.css"

const UserRegister = ({ onRegister }) => {
  const [formData, setFormData] = useState({
    fullName: "",
    role: "USER",
    armyNo: "",
    rank: "",
    battalionId: "",
  })
  const [battalions, setBattalions] = useState([])
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newBattalion, setNewBattalion] = useState({ name: '', postedStr: '' })
  const [selectedSubBattalion, setSelectedSubBattalion] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    fetchBattalions()
  }, [])

  const fetchBattalions = async () => {
    try {
      const response = await axios.get("/api/battalion")
      setBattalions(response.data.filter((b) => b.status === "APPROVED"))
    } catch (error) {
      console.error("Error fetching battalions:", error)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })

    // Clear army number and rank if role is CO
    if (name === "role" && value === "CO") {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
        armyNo: "",
        rank: "",
      }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match")
      setLoading(false)
      return
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters long")
      setLoading(false)
      return
    }

    if ((formData.role === "JSO" || formData.role === "USER") && !formData.armyNo) {
      setError("Army Number is required for JSO and USER roles")
      setLoading(false)
      return
    }

    try {
      const registrationData = {
        username: formData.username,
        password: formData.password,
        fullName: formData.fullName,
        role: formData.role,
      }

      if (formData.armyNo) registrationData.armyNo = formData.armyNo
      if (formData.rank) registrationData.rank = formData.rank
      if (formData.battalionId) registrationData.battalionId = formData.battalionId

      const response = await axios.post("/api/auth/register", registrationData)
      const { user, token } = response.data

      onRegister(user, token)

      // Redirect based on user role
      switch (user.role) {
        case "CO":
          navigate("/co-dashboard")
          break
        case "JSO":
          navigate("/jso-dashboard")
          break
        case "USER":
          navigate("/battalion-selection")
          break
        default:
          navigate("/")
      }
    } catch (error) {
      setError(error.response?.data?.message || "Registration failed")
    } finally {
      setLoading(false)
    }
  }

    const handleAddBattalion = async (e) => {
    e.preventDefault()
    try {
      await axios.post('/api/battalion', newBattalion, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      fetchBattalions()
      setShowAddForm(false)
      setNewBattalion({ name: '', postedStr: '' })
    } catch (error) {
      console.error('Error adding battalion:', error)
    }
  }

  

  

  const requiresArmyNo = formData.role === "JSO" || formData.role === "USER"

  return (
    <div className="register-container">
      <div className="register-content">
        <div className="register-header">
          <div className="logo-section">
            <div className="logo-placeholder">🇮🇳</div>
            <div className="logo-placeholder">⚔️</div>
          </div>
          <h1>WARRIOR SUPPORT SYSTEM</h1>
          <p className="register-subtitle">Register YourSelf</p>
        </div>

        <div className="register-form-container">
          <form onSubmit={handleSubmit} className="register-form">
            <h2>REGISTER</h2>

            {error && <div className="error-message">{error}</div>}

            <div className="form-row">
              

              <div className="form-group">
                <label htmlFor="fullName">Full Name *</label>
                <input
                  type="text"
                  id="fullName"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleChange}
                  required
                  placeholder="Enter full name"
                />
              </div>
            </div>


            {requiresArmyNo && (
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="armyNo">Army Number *</label>
                  <input
                    type="text"
                    id="armyNo"
                    name="armyNo"
                    value={formData.armyNo}
                    onChange={handleChange}
                    required
                    placeholder="Enter army number"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="rank">Rank</label>
                  <select id="rank" name="rank" value={formData.rank} onChange={handleChange}>
                    <option value="">Select Rank</option>
                    <option value="Lt Col">Lt Col</option>
                    <option value="Maj">Maj</option>
                    <option value="Capt">Capt</option>
                    <option value="Lt">Lt</option>
                    <option value="2Lt">2Lt</option>
                    <option value="Sub">Sub</option>
                    <option value="Nb Sub">Nb Sub</option>
                    <option value="Hav">Hav</option>
                    <option value="Nk">Nk</option>
                    <option value="L/Nk">L/Nk</option>
                    <option value="Sep">Sep</option>
                    <option value="Rfn">Rfn</option>
                  </select>
                </div>
              </div>
            )}

            {( formData.role === "USER") && (
              <div className="form-group">
                <label htmlFor="battalionId">Battalion</label>
                <select id="battalionId" name="battalionId" value={formData.battalionId} onChange={handleChange}>
                  <option value="">Select Battalion</option>
                  {battalions.map((battalion) => (
                    <option key={battalion._id} value={battalion._id}>
                      {battalion.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="action-buttons">
                <button onClick={() => setShowAddForm(true)}>ADD BN</button>
            </div>

            {showAddForm && (
                <form onSubmit={handleAddBattalion} className="add-battalion-form">
                <input
                    type="text"
                    placeholder="ENTER BN/REGT NAME"
                    value={newBattalion.name}
                    onChange={(e) => setNewBattalion({...newBattalion, name: e.target.value})}
                    required
                />
                <input
                    type="text"
                    placeholder="POSTED STR"
                    value={newBattalion.postedStr}
                    onChange={(e) => setNewBattalion({...newBattalion, postedStr: e.target.value})}
                />
                <button type="submit">SUBMIT</button>
                </form>
            )}

            <button type="submit" className="register-btn" disabled={loading}>
              {loading ? "CREATING ACCOUNT..." : "CREATE ACCOUNT"}
            </button>
          </form>

          <div className="register-footer">
            <p>
              Already have an account?
              <Link to="/login" className="login-link">
                {" "}
                Login here
              </Link>
            </p>
            <div className="system-info">
              <small>Warrior Support System v2.0 | Secure Military Portal</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default UserRegister
