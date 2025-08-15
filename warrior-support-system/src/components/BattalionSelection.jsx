import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Header from './Header'

const BattalionSelection = ({ selectedBattalion, setSelectedBattalion, currentUser, onLogout }) => {
  const [battalions, setBattalions] = useState([])
  const [showAddForm, setShowAddForm] = useState(false)
  const [newBattalion, setNewBattalion] = useState({ name: '', postedStr: '' })
  const [selectedSubBattalion, setSelectedSubBattalion] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    fetchBattalions()
  }, [])

  const fetchBattalions = async () => {
    try {
      const response = await axios.get('/api/battalion', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      setBattalions(response.data)
    } catch (error) {
      console.error('Error fetching battalions:', error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('currentArmyNo')
    if (onLogout) onLogout()
    navigate('/login')
  }

  const handleProceed = () => {
    if (selectedBattalion) {
      localStorage.setItem('selectedBattalion', selectedBattalion)
      navigate('/decide-assessment')
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

  const handleDeleteBattalion = async () => {
    if (selectedBattalion) {
      try {
        await axios.delete(`/api/battalion/${selectedBattalion}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        })
        fetchBattalions()
        setSelectedBattalion('')
        setSelectedSubBattalion('')
      } catch (error) {
        console.error('Error deleting battalion:', error)
      }
    }
  }

  return (
    <div className="battalion-selection-container">
      <Header currentUser={currentUser} onLogout={handleLogout} />

      <div className="selection-content">
        <div className="selection-form">
          <label>SELECT BN</label>
          <select 
            value={selectedBattalion} 
            onChange={(e) => setSelectedBattalion(e.target.value)}
          >
            <option value="">SELECT BN</option>
            {battalions.map(battalion => (
              <option key={battalion._id} value={battalion._id}>
                {battalion.name + ' (' + battalion.postedStr + ')'}
              </option>
            ))}
          </select>

          

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

          <button 
            onClick={handleProceed} 
            className="proceed-btn"
          >
            Proceed
          </button>
        </div>
      </div>
    </div>
  )
}

export default BattalionSelection
