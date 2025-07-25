import React, { useState } from 'react'
import axios from 'axios'
import '../styles/AddDataModal.css'

const AddDataModal = ({ onClose, onSave, battalionId }) => {
  const [formData, setFormData] = useState({
    rank: '',
    name: '',
    armyNo: '',
    subBty: '',
    service: '',
    dateOfInduction: '',
    medCat: '',
    leaveAvailed: '',
    maritalStatus: 'MARRIED'
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await axios.post('/api/personnel', {
        ...formData,
        battalion: battalionId
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      onSave()
      onClose()
    } catch (error) {
      console.error('Error adding personnel:', error)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>UPLOAD NEW DATA</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit}>
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
          
          <button type="submit" className="submit-btn">SUBMIT</button>
        </form>
      </div>
    </div>
  )
}

export default AddDataModal