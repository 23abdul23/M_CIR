import React, { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import axios from 'axios'
import Header from './Header'
import AddDataModal from './AddDataModal'
import IndividualMonitoring from './IndividualMonitoring'
import '../styles/DataTable.css'

const DataTable_CO = ({ selectedBattalion, currentUser, onLogout }) => {
  const [personnel, setPersonnel] = useState([])
  const [results, setResults] = useState([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [loading, setLoading] = useState(true)
  const [editingPersonnel, setEditingPersonnel] = useState(null)
  const [filters, setFilters] = useState({})
  const [uniqueValues, setUniqueValues] = useState({})
  const [selectedPersonnel, setSelectedPersonnel] = useState(null)
  const [showIndividualMonitoring, setShowIndividualMonitoring] = useState(false)
  const fileInputRef = useRef(null)
  const navigate = useNavigate()

  const location = useLocation()
  const locationSelectedBattalion = location.state?.selectedBattalion

  useEffect(() => {
    fetchPersonnel()
    fetchResults()
  }, [selectedBattalion])

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

  const fetchResults = async () => {
    try {
      const battalionId = selectedBattalion || locationSelectedBattalion
      const response = await axios.get(`/api/examination/battalion/${battalionId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      const n = response.data.map((e) => [e.dassScores, e.battalion])
      setResults(n)
    } catch (error) {
      console.log("Error fetching results: ", error)
    }
  }

  const fetchPersonnel = async () => {
    setLoading(true)
    try {
      const battalionId = selectedBattalion || locationSelectedBattalion
      const response = await axios.get(`/api/personnel/battalion/${battalionId}`, {
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
    onLogout && onLogout()
    navigate('/login')
  }

  const handleExport = async () => {
    try {
      if (filteredPersonnel.length === 0) {
        alert('No data to export');
        return;
      }

      const filteredData = filteredPersonnel.map((person) => ({
        'Army No': person.armyNo,
        'Rank': person.rank,
        'Name': person.name,
        'SubBty': person.subBty,
        'Service': person.service,
        'Date of Induction': new Date(person.dateOfInduction).toLocaleDateString(),
        'Med Cat': person.medCat,
        'Leave Availed': person.leaveAvailed || 'NIL',
        'Marital Status': person.maritalStatus,
        'Self Evaluation': person.selfEvaluation,
      }));

      const csvContent = [
        Object.keys(filteredData[0]).join(','),
        ...filteredData.map((row) => Object.values(row).join(',')),
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `filtered_personnel_data_${Date.now()}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Error exporting data. Please try again.');
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

  const handleRowClick = (person) => {
    setSelectedPersonnel(person)
    setShowIndividualMonitoring(true)
  }

  const handleCloseMonitoring = () => {
    setShowIndividualMonitoring(false)
    setSelectedPersonnel(null)
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

  const handleFilterChange = (column, value) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      [column]: value,
    }));
  };

  const filteredPersonnel = personnel.filter((person) => {
    return Object.entries(filters).every(([column, value]) => {
      if (!value) return true;
      return person[column]?.toString().toLowerCase() === value.toLowerCase();
    });
  });

  const canManageData = ['CO'].includes(currentUser.role)
  const canImportExport = ['CO', 'JSO'].includes(currentUser.role)

  // If showing individual monitoring, render that component
  if (showIndividualMonitoring && selectedPersonnel) {
    return (
      <IndividualMonitoring 
        armyNo={selectedPersonnel.armyNo}
        currentUser={currentUser}
        onLogout={onLogout}
        onBack={handleCloseMonitoring}
      />
    )
  }
  console.log(personnel)

  return (
    <div className="datatable-container">
      <Header currentUser={currentUser} onLogout={handleLogout} />

      <div className="datatable-content">
        <div className="datatable-header">
          <h2 className="datatable-title">WARRIOR SUPPORT SYSTEM</h2>
          <p className="datatable-subtitle">{}</p>
        </div>

        <div className="datatable-actions">
          {canImportExport && (
            <>
              {/* <button onClick={handleImport} className="datatable-btn datatable-btn-import">IMPORT</button> */}
              <button onClick={handleExport} className="datatable-btn datatable-btn-export">EXPORT</button>
            </>
          )}
          {canManageData && (
            <>
              <button onClick={() => setShowAddModal(true)} className="datatable-btn datatable-btn-add">ADD NEW</button>
              <button onClick={handleRemoveAll} className="datatable-btn datatable-btn-remove">REMOVE ALL</button>
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
                    <th>
                      ARMY NO.
                      {/* <select
                        onChange={(e) => handleFilterChange('armyNo', e.target.value)}
                        value={filters.armyNo || ''}
                      >
                        <option value="">All</option>
                        {uniqueValues.armyNo?.map((value) => (
                          <option key={value} value={value}>{value}</option>
                        ))}
                      </select> */}
                    </th>
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
                    <th>
                      NAME
                      {/* <select
                        onChange={(e) => handleFilterChange('name', e.target.value)}
                        value={filters.name || ''}
                      >
                        <option value="">All</option>
                        {uniqueValues.name?.map((value) => (
                          <option key={value} value={value}>{value}</option>
                        ))}
                      </select> */}
                    </th>
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
                    <th>RESULTS</th>
                    <th>Mode</th>
                    {canManageData && <th>ACTION</th>}
                  </tr>
                </thead>
                <tbody>
                  {filteredPersonnel.map((person) => (
                    <tr 
                      key={person._id} 
                      className="clickable-row"
                      onClick={() => handleRowClick(person)}
                      title="Click to view individual monitoring"
                    >
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
                          {person.selfEvaluation === 'EXAM_APPEARED' ? 'Exam Appeared' :
                            person.selfEvaluation === 'NOT_ATTEMPTED' ? 'Not Attempted' :
                              person.selfEvaluation || 'Not Set'}
                        </span>
                      </td>
                      
                      <td>
                        {person.selfEvaluation === "COMPLETED" ? (() => {
                          const resultEntry = results.find(r => r?.[1]?._id === person.battalion?._id?.toString());
                          const scores = resultEntry?.[0];

                          return scores ? (
                            <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                              <tbody>
                                <tr>
                                  <td style={{ border: '1px solid #ccc', padding: '4px' }}>
                                    <strong>Anxiety:</strong> {scores.anxiety} ({scores.anxietySeverity})
                                  </td>
                                  <td style={{ border: '1px solid #ccc', padding: '4px' }}>
                                    <strong>Depression:</strong> {scores.depression} ({scores.depressionSeverity})
                                  </td>
                                  <td style={{ border: '1px solid #ccc', padding: '4px' }}>
                                    <strong>Stress:</strong> {scores.stress} ({scores.stressSeverity})
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                          ) : (
                            <div>No result found</div>
                          );
                        })() : (
                          <div>Not Completed</div>
                        )}
                      </td>

                      <td>{person.mode}</td>

                      {canManageData && (
                        <td onClick={(e) => e.stopPropagation()}>
                          <div className="datatable-actions-cell">
                            <button className="datatable-btn-icon datatable-btn-edit" onClick={() => handleEdit(person)} title="Edit">✏️</button>
                            <button className="datatable-btn-icon datatable-btn-delete" onClick={() => handleDelete(person._id)} title="Delete">🗑️</button>
                          </div>
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
            {filteredPersonnel.length} Out Of {personnel.length}
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
          battalionId={locationSelectedBattalion || currentUser.battalion}
          editData={editingPersonnel}
        />
      )}
    </div>
  )
}

export default DataTable_CO
