import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Header from './Header'
import AddDataModal from './AddDataModal'
import '../styles/DataTable.css'

const DataTable = ({ selectedBattalion, currentUser, onLogout }) => {
  const [personnel, setPersonnel] = useState([])
  const [showAddModal, setShowAddModal] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetchPersonnel()
  }, [selectedBattalion])

  const fetchPersonnel = async () => {
    try {
      const response = await axios.get(`/api/personnel/battalion/${selectedBattalion}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      setPersonnel(response.data)
    } catch (error) {
      console.error('Error fetching personnel:', error)
    }
  }

  const handleLogout = () => {
    // Clear all stored data
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('currentArmyNo')
    
    // Call parent logout function
    if (onLogout) {
      onLogout()
    }
    
    // Redirect to login page
    navigate('/login')
  }

  const handleSaveAll = async () => {
    // Implementation for saving all data
    console.log('Saving all data...')
  }

  const handleRemoveAll = async () => {
    try {
      await axios.delete(`/api/personnel/battalion/${selectedBattalion}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      setPersonnel([])
    } catch (error) {
      console.error('Error removing all personnel:', error)
    }
  }

  return (
    <div className="data-table-container">
      <Header currentUser={currentUser} onLogout={handleLogout} />

      <div className="table-content">
        <h2>71 FD REGT</h2>
        
        <div className="table-actions">
          <button onClick={() => setShowAddModal(true)}>ADD NEW</button>
          <button onClick={handleSaveAll}>SAVE ALL</button>
          <button onClick={handleRemoveAll}>REMOVE ALL</button>
        </div>

        <table className="personnel-table">
          <thead>
            <tr>
              <th>ARMY NO.</th>
              <th>RANK</th>
              <th>NAME</th>
              <th>COY/SQN/BTY</th>
              <th>SERVICE</th>
              <th>DATE OF INDN</th>
              <th>MED CAT</th>
              <th>LEAVE AVAILED THIS YEAR(ACL)</th>
              <th>MARITAL STATUS</th>
              <th>SELF EVALUATION</th>
              <th>ACTION</th>
            </tr>
          </thead>
          <tbody>
            {personnel.map((person, index) => (
              <tr key={person._id}>
                <td>{person.armyNo}</td>
                <td>{person.rank}</td>
                <td>{person.name}</td>
                <td>{person.coySquadronBty}</td>
                <td>{person.service}</td>
                <td>{person.dateOfInduction}</td>
                <td>{person.medCat}</td>
                <td>{person.leaveAvailed}</td>
                <td>{person.maritalStatus}</td>
                <td>{person.selfEvaluation}</td>
                <td>
                  <button>Edit</button>
                  <button>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="table-footer">
          <span>0 Out Of 0</span>
        </div>
      </div>

      {showAddModal && (
        <AddDataModal 
          onClose={() => setShowAddModal(false)}
          onSave={fetchPersonnel}
          battalionId={selectedBattalion}
        />
      )}
    </div>
  )
}

export default DataTable