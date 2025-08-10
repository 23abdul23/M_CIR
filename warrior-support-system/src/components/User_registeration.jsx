"use client"

import { useState, useEffect } from "react"
import { Link, useNavigate } from "react-router-dom"
import axios from "axios"
import "../styles/Register.css"

const UserRegister = ({ onRegister }) => {
  let [formData, setFormData] = useState({
      rank: '',
      name: '',
      armyNo: '',
      subBty: '',
      battalion : "",
      service: '',
      dateOfInduction: '',
      medCat: '',
      leaveAvailed: '',
      maritalStatus: 'MARRIED',
      status : 'PENDING'
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


    
    if ((formData.role === "USER") && !formData.armyNo) {
      setError("Army Number is required USER roles")
      setLoading(false)
      return
    }


    try {
      const response = await fetch("/api/personnel", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      

      onRegister(data)
      navigate("/dashboard")
    } catch (err) {
      setError("Failed to register. Please try again later.")
    } finally {
      setLoading(false)
    }
  } 

  
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

     
            <div className="form-grid">
                <div className="form-group">
                <label>RANK</label>
                    <select
                        id="rank"
                        name="rank"
                        value={formData.rank}
                        onChange={handleChange}
                    >
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
                
                <div className="form-group">
                <label>NAME</label>
                <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                />
                </div>
                
                <div className="form-group">
                <label>ARMY NO</label>
                <input
                    type="text"
                    name="armyNo"
                    value={formData.armyNo}
                    onChange={handleChange}
                    required
                />
                </div>
                
                <div className="form-group">
                <label>COY/SQN/BTY</label>
                
                <select 
                    value={formData.subBty} 
                    onChange={(e) => setFormData({ ...formData, subBty: e.target.value })}
                >
                    <option value="">SELECT Sub BN</option>
                    <option value="P Bty">P Bty</option>
                    <option value="Q Bty">Q Bty</option>
                    <option value="R Bty">R Bty</option>
                    <option value="HQ Bty">HQ Bty</option>
                </select>
                </div>
                
                <div className="form-group">
                <label>SERVICE (YEARS)</label>
                <input
                    type="text"
                    name="service"
                    value={formData.service}
                    onChange={handleChange}
                    required
                />
                </div>
                
                <div className="form-group">
                <label>DATE OF INDN</label>
                <input
                    type="date"
                    name="dateOfInduction"
                    value={formData.dateOfInduction}
                    onChange={handleChange}
                    required
                />
                </div>
                
                <div className="form-group">
                <label>MED CAT</label>
                <select
                    name="medCat"
                    value={formData.medCat}
                    onChange={handleChange}
                    required
                >
                    <option value="">MED CAT</option>
                    <option value="A1">A1</option>
                    <option value="A2">A2</option>
                    <option value="B1">B1</option>
                    <option value="B2">B2</option>
                    <option value="C1">C1</option>
                    <option value="C2">C2</option>
                </select>
                </div>
                
                <div className="form-group">
                <label>LEAVE AVAILED THIS YEAR(ACL)</label>
                <input
                    type="text"
                    name="leaveAvailed"
                    value={formData.leaveAvailed}
                    onChange={handleChange}
                    required
                />
                </div>
                
                <div className="form-group">
                <label>MARITAL STATUS</label>
                <select
                    name="maritalStatus"
                    value={formData.maritalStatus}
                    onChange={handleChange}
                    required
                >
                    <option value="MARRIED">MARRIED</option>
                    <option value="UNMARRIED">UNMARRIED</option>
                </select>
                </div>
            </div>
            
            
            
            <div className="form-group">
            <label htmlFor="battalionId">Battalion</label>
            <select id="battalion" name="battalion" value={formData.battalion} onChange={handleChange}>
                <option value="">Select Battalion</option>
                {battalions.map((battalion) => (
                <option key={battalion._id} value={battalion._id}>
                    {battalion.name}
                </option>
                ))}
            </select>
            </div>

            <button type="submit" className="register-btn" disabled={loading}>
              {loading ? "CREATING ACCOUNT..." : "CREATE ACCOUNT"}
            </button>
          </form>

          
        </div>
      </div>
    </div>
  )
}

export default UserRegister
