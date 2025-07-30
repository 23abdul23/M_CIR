import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Header from './Header'
import AddDataModal from './AddDataModal'
import '../styles/DataTable.css'

const DataTable = ({ selectedBattalion, currentUser, onLogout }) => {
  const [personnel, setPersonnel] = useState([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [loading, setLoading] = useState(true)
  const [editingPersonnel, setEditingPersonnel] = useState(null)
  const fileInputRef = useRef(null)
  const navigate = useNavigate()

 
  useEffect(() => {
    fetchPersonnel()
  }, [selectedBattalion])

  const fetchPersonnel = async () => {
    setLoading(true)
    try {
      const battalionId = currentUser.battalion

      
      const response = await axios.get(`/api/personnel/battalion/${battalionId._id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      setPersonnel(response.data)
    } catch (error) {
      console.error('Error fetching personnel:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('currentArmyNo')
    
    if (onLogout) {
      onLogout()
    }
    
    navigate('/login')
  }

  const handleExport = async () => {
    try {
      const battalionId = localStorage.getItem('selectedBattalion')
      const response = await axios.get(`/api/csv/export/${battalionId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `personnel_data_${Date.now()}.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error exporting data:', error)
      alert('Error exporting data. Please try again.')
    }
  }

  const handleImport = () => {
    fileInputRef.current.click()
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('csvFile', file)

    try {
      const battalionId = selectedBattalion || currentUser.battalion
      const response = await axios.post(`/api/csv/import/${battalionId}`, formData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'multipart/form-data'
        }
      })
      alert(`Import completed! ${response.data.successCount} records imported successfully.`)
      if (response.data.errors.length > 0) {
        console.log('Import errors:', response.data.errors)
      }
      fetchPersonnel()
    } catch (error) {
      console.error('Error importing data:', error)
      alert('Error importing data. Please check the file format and try again.')
    }
    // Reset file input
    event.target.value = ''
  }

  const handleEdit = (person) => {
    setEditingPersonnel(person)
    setShowAddModal(true)
  }

  const handleDelete = async (personId) => {
    if (window.confirm('Are you sure you want to delete this person?')) {
      try {
        await axios.delete(`/api/personnel/${personId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        })
        fetchPersonnel()
      } catch (error) {
        console.error('Error deleting person:', error)
      }
    }
  }

  const handleReview = (personnelId) => {
    navigate(`/peer-evaluation/${personnelId}`)
  }

  const handleSaveAll = async () => {
    console.log('Saving all data...')
    alert('All data saved successfully!')
  }

  const handleRemoveAll = async () => {
    if (window.confirm('Are you sure you want to remove all personnel data?')) {
      try {
        const battalionId = selectedBattalion || currentUser.battalion
        await axios.delete(`/api/personnel/battalion/${battalionId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        })
        setPersonnel([])
      } catch (error) {
        console.error('Error removing all personnel:', error)
      }
    }
  }

  const canManageData = ['CO', 'JSO', 'USER'].includes(currentUser.role)
  const canImportExport = ['CO', 'JSO'].includes(currentUser.role)
  const canReview = currentUser.role === 'JSO'
 
  return (
    <div className="datatable-container">
      
      <div className="datatable-content">
        <div className="datatable-header">
          <h1 className="datatable-subtitle">{currentUser.battalion.name}</h1>
        </div>

        <div className="datatable-actions">
          {canImportExport && (
            <>
              {/* <button onClick={handleImport} className="datatable-btn datatable-btn-import">
                IMPORT
              </button> */}
              <button onClick={handleExport} className="datatable-btn datatable-btn-export">
                EXPORT DATA
              </button>
            </>
          )}
          
        </div>

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileUpload}
          accept=".csv"
          style={{ display: 'none' }}
        />

        <div className="datatable-wrapper">
          {loading ? (
            <div className="datatable-loading">
              <div className="datatable-spinner"></div>
              <p>Loading personnel data...</p>
            </div>
          ) : personnel.length === 0 ? (
            <div className="datatable-empty">
              <div className="datatable-empty-icon">📋</div>
              <h3>No Personnel Data</h3>
              <p>Click "ADD NEW" to add personnel information</p>
            </div>
          ) : (
            <div className="datatable-scroll">
              <table className="datatable-table">
                <thead>
                  <tr>
                    <th>ARMY NO.</th>
                    <th>RANK</th>
                    <th>NAME</th>
                    <th>COY/SQN/BTY</th>
                    <th>SERVICE</th>
                    <th>DATE OF INDN</th>
                    <th>MED CAT</th>
                    <th>LEAVE AVAILED THIS YEAR (AL/CL)</th>
                    <th>MARITAL STATUS</th>
                    <th>SELF EVALUATION</th>
                    {canReview && <th>PEER EVALUATION</th>}
                    
                  </tr>
                </thead>
                <tbody>
                  {personnel.map((person) => (
                    <tr key={person._id}>
                      <td>{person.armyNo}</td>
                      <td>{person.rank}</td>
                      <td>{person.name}</td>
                      <td>{person.coySquadronBty}</td>
                      <td>{person.service}</td>
                      <td>{new Date(person.dateOfInduction).toLocaleDateString()}</td>
                      <td>{person.medCat}</td>
                      <td>{person.leaveAvailed || 'NIL'}</td>
                      <td>{person.maritalStatus}</td>
                      <td>
                        <span className={`datatable-status ${person.selfEvaluation?.toLowerCase().replace('_', '-')}`}>
                          {person.selfEvaluation === 'NOT_ATTEMPTED' ? 'Not Attempted' : 
                           person.selfEvaluation || 'Not Set'}
                        </span>
                      </td>
                      {canReview && (
                        <td>
                          {person.peerEvaluation?.status === 'EVALUATED' ? (
                            <span className="datatable-status evaluated">DONE</span>
                          ) : (
                            <button
                              className="datatable-btn-small datatable-btn-review"
                              onClick={() => handleReview(person._id)}
                            >
                              NOT DONE
                            </button>
                          )}
                        </td>
                      )}
                      
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="datatable-footer">
          <span className="datatable-count">
            {personnel.length} Out Of {personnel.length}
          </span>
        </div>
      </div>

      {showAddModal && (
        <AddDataModal 
          onClose={() => {
            setShowAddModal(false)
            setEditingPersonnel(null)
          }}
          onSave={fetchPersonnel}
          battalionId={selectedBattalion || currentUser.battalion}
          editData={editingPersonnel}
        />
      )}
    </div>
  )
}

export default DataTable