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
  const [filters, setFilters] = useState({})
  const [uniqueValues, setUniqueValues] = useState({})

  const [interviewPersonnel, setInterviewPersonnel] = useState([])
  const [severePersonnels, setSeverePersonnels] = useState([])
  const [existingInterviewDates, setExistingInterviewDates] = useState({})
  
  const navigate = useNavigate()

  useEffect(() => {
    if (personnel.length > 0) {
      const unique = {}
      personnel.forEach((person) => {
        Object.keys(person).forEach((key) => {
          if (!unique[key]) {
            unique[key] = new Set()
          }
          unique[key].add(person[key])
        })
      })
      const uniqueValuesObj = {}
      Object.keys(unique).forEach((key) => {
        uniqueValuesObj[key] = Array.from(unique[key]).filter((val) => val !== undefined && val !== null)
      })
      setUniqueValues(uniqueValuesObj)
    }
  }, [personnel])

  const filteredPersonnel = personnel.filter((person) => {
    return Object.entries(filters).every(([column, value]) => {
      if (!value) return true;
      return person[column]?.toString().toLowerCase() === value.toLowerCase();
    });
  });

  const handleFilterChange = (column, value) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      [column]: value,
    }));
  };
  
  const fetchExistingInterviewDates = async () =>{
        try{
            const responce = await axios.get(`/api/interview/getInterview`,{
                headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
            })
            setExistingInterviewDates(responce.data)
        }
        catch(error){
            console.log(error)
        }
    }


  useEffect(() => {
    fetchPersonnel()
    fetchSeverePersonnel()
    fetchExistingInterviewDates()
  }, [selectedBattalion])

  const fetchPersonnel = async () => {
    setLoading(true)
    try {
      const battalionId = currentUser.battalion
      console.log(battalionId)
      const response = await axios.get(`/api/personnel/battalion/jco/${battalionId._id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      console.log(response.data)
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


  const canManageData = ['CO', 'JCO', 'USER'].includes(currentUser.role)
  const canImportExport = ['CO', 'JCO'].includes(currentUser.role)
  const canReview = currentUser.role === 'JCO'
  
  const fetchSeverePersonnel = async () => {
    
    try {
      const responce = await axios.get(`/api/severePersonnel/${currentUser.battalion._id}`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        }
      )
      setInterviewPersonnel(responce.data.data)
    }
    catch (error){
      console.error("Error fetching severe personnel:", error)
    }
  }

  console.log(personnel)

  return (
    <div className="datatable-container">
      
      <div className="datatable-content">
        <div className="datatable-header">
          <h1 className="datatable-subtitle">{currentUser.battalion.name +' (' + currentUser.battalion.postedStr +")"}</h1>
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
                    <th>
                      RANK
                      <select
                        onChange={(e) => handleFilterChange('rank', e.target.value)}
                        value={filters.rank || ''}
                      >
                        <option value="">All</option>
                        {uniqueValues.rank?.map((value) => (
                          <option key={value} value={value}>{value}</option>
                        ))}
                      </select>
                    </th>
                    <th>NAME</th>
                    <th>
                      COY/SQN/BTY
                      <select
                        onChange={(e) => handleFilterChange('subBty', e.target.value)}
                        value={filters.subBty || ''}
                      >
                        <option value="">All</option>
                        {uniqueValues.subBty?.map((value) => (
                          <option key={value} value={value}>{value}</option>
                        ))}
                      </select>
                    </th>
                    <th>
                      SERVICE
                      <select
                        onChange={(e) => handleFilterChange('service', e.target.value)}
                        value={filters.service || ''}
                      >
                        <option value="">All</option>
                        {uniqueValues.service?.map((value) => (
                          <option key={value} value={value}>{value}</option>
                        ))}
                      </select>
                    </th>
                    <th>
                      DATE OF INDN
                      <select
                        onChange={(e) => handleFilterChange('dateOfInduction', e.target.value)}
                        value={filters.dateOfInduction || ''}
                      >
                        <option value="">All</option>
                        {uniqueValues.dateOfInduction?.map((value) => (
                          <option key={value} value={value}>{value}</option>
                        ))}
                      </select>
                    </th>
                    <th>
                      MED CAT
                      <select
                        onChange={(e) => handleFilterChange('medCat', e.target.value)}
                        value={filters.medCat || ''}
                      >
                        <option value="">All</option>
                        {uniqueValues.medCat?.map((value) => (
                          <option key={value} value={value}>{value}</option>
                        ))}
                      </select>
                    </th>
                    <th>
                      LEAVE AVAILED
                      <select
                        onChange={(e) => handleFilterChange('leaveAvailed', e.target.value)}
                        value={filters.leaveAvailed || ''}
                      >
                        <option value="">All</option>
                        {uniqueValues.leaveAvailed?.map((value) => (
                          <option key={value} value={value}>{value}</option>
                        ))}
                      </select>
                    </th>
                    <th>
                      MARITAL STATUS
                      <select
                        onChange={(e) => handleFilterChange('maritalStatus', e.target.value)}
                        value={filters.maritalStatus || ''}
                      >
                        <option value="">All</option>
                        {uniqueValues.maritalStatus?.map((value) => (
                          <option key={value} value={value}>{value}</option>
                        ))}
                      </select>
                    </th>
                    <th>
                      SELF EVALUATION
                      <select
                        onChange={(e) => handleFilterChange('selfEvaluation', e.target.value)}
                        value={filters.selfEvaluation || ''}
                      >
                        <option value="">All</option>
                        {uniqueValues.selfEvaluation?.map((value) => (
                          <option key={value} value={value}>{value}</option>
                        ))}
                      </select>
                    </th>
                    {canReview && <th>PEER EVALUATION</th>}
                    
                    
                  </tr>
                </thead>
                <tbody>
                  {filteredPersonnel.map((person) => (
                    <tr key={person._id}>
                      <td>{person.armyNo}</td>
                      <td>{person.rank}</td>
                      <td>{person.name}</td>
                      <td>{person.subBty}</td>
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

      {/* Table for personnel being interviewed */}
      <div className="datatable-wrapper" style={{marginTop: '2rem'}}>
          <h2 className="datatable-title" style={{textAlign:'center'}}>Personnel Being Interviewed</h2>
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
                  <th>LEAVE AVAILED</th>
                  <th>MARITAL STATUS</th>
                  <th>Interview Status</th>
                  <th>Interview Date</th>
                </tr>
              </thead>
              <tbody>
                {Array.isArray(interviewPersonnel) && interviewPersonnel.length === 0 ? (
                  <tr><td colSpan={10} style={{textAlign:'center'}}>No personnel scheduled for interview</td></tr>
                ) : (
                  (Array.isArray(interviewPersonnel[0]) ? interviewPersonnel.flat() : interviewPersonnel).map((person) => (
                    <tr key={person._id || person.armyNo || Math.random()}>
                      <td>{person.armyNo}</td>
                      <td>{person.rank}</td>
                      <td>{person.name}</td>
                      <td>{person.subBty}</td>
                      <td>{person.service}</td>
                      <td>{new Date(person.dateOfInduction).toLocaleDateString()}</td>
                      <td>{person.medCat}</td>
                      <td>{person.leaveAvailed || 'NIL'}</td>
                      <td>{person.maritalStatus}</td>
                      <td>
                        <span className={`datatable-status interview`}>
                          Interview Scheduled
                        </span>
                      </td>
                      <td>{(() => {
                        if (Array.isArray(existingInterviewDates)) {
                          const interviewObj = existingInterviewDates.find(p => String(p.armyNo) === String(person.armyNo));
                          if (interviewObj && interviewObj.interviewDate) {
                            const date = new Date(interviewObj.interviewDate);
                            const options = { day: '2-digit', month: 'short', year: 'numeric' };
                            return date.toLocaleDateString('en-GB', options);
                          }
                          else {
                            return <span style={{color:'#aaa'}}>No Date Scheduled</span>;
                          }
                        }
                        return <span style={{color:'#aaa'}}>Not Set</span>;
                      })()}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
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