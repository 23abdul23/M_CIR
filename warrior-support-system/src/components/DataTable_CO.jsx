import React, { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import axios from 'axios'
import Header from './Header'
import AddDataModal from './AddDataModal'
import IndividualMonitoring from './IndividualMonitoring'
import '../styles/DataTable.css'
import '../styles/GraphicalAnalysis.css';
import { filter } from 'lodash'

// this is the updated one 


import GraphicalAnalysis from './GraphicalAnalysis';

const DataTable_CO = ({ selectedBattalion, currentUser, onLogout }) => {
  const [personnel, setPersonnel] = useState([])
  const [results, setResults] = useState([])
  const [jcoresults, setjcoresults] = useState([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [loading, setLoading] = useState(true)
  const [editingPersonnel, setEditingPersonnel] = useState(null)
  const [showGraph, setShowGraph] = useState(false)
  const [filters, setFilters] = useState({})
  const [uniqueValues, setUniqueValues] = useState({})
  const [selectedPersonnel, setSelectedPersonnel] = useState(null)
  const [showIndividualMonitoring, setShowIndividualMonitoring] = useState(false)
  const [filterSeverity, setFilterSeverity] = useState('')
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
      
      const n = response.data
        .map((e) => [e.dassScores, e.battalion, e.armyNo, e.mode, e.completedAt])
        .sort((a, b) => new Date(b[4]) - new Date(a[4])); // index 4 is completedAt

      setResults(n);
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

  const mapPerformance = (score) => {
  let label = "";
  let range = "";

  if (score >= 8.1 && score <= 10) {
    range = "(81 - 100)";
    label = "Outstanding";
  } else if (score >= 6.1 && score <= 8) {
    range = "(61 - 80)";
    label = "Commendable";
  } else if (score >= 4.1 && score <= 6) {
    range = "(41 - 60)";
    label = "Satisfactory";
  } else if (score >= 2.1 && score <= 4) {
    range = "(21 - 40)";
    label = "Needs Improvement";
  } else {
    label = "Unsatisfactory";
    range = "(0 - 20)";
  }

  return <span>{range} {label}</span>;
};



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

  const handleSuperFilter = () => {


    const filtered = personnel.filter((person) => {
      const resultEntry = results.find(r => r?.[2] === person.armyNo);
      const scores = resultEntry?.[0];

      if (!scores || person.selfEvaluation !== 'COMPLETED') return false;

      return (
        scores.anxietySeverity?.toLowerCase() === filterSeverity.toLowerCase() ||
        scores.depressionSeverity?.toLowerCase() === filterSeverity.toLowerCase() ||
        scores.stressSeverity?.toLowerCase() === filterSeverity.toLowerCase()
      );
    });

    setPersonnel(filtered);
  };

  useEffect(() => {
    if (filterSeverity === '') {
      fetchPersonnel();
    }
  }, [filterSeverity]);

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

  return (
    <div className="datatable-container">
      <Header currentUser={currentUser} onLogout={handleLogout} />

      <div className="datatable-content">
        <div className="datatable-header datatable-header-flex">
          <div className="datatable-header-title">
            <h2 className="datatable-title">SOLDIER SUPPORT SYSTEM</h2>
            <p className="datatable-subtitle">{ }</p>
          </div>
        </div>

        <div className="datatable-actions">
          {canImportExport && (
            <>
              {/* <button onClick={handleImport} className="datatable-btn datatable-btn-import">IMPORT</button> */}
              <button onClick={handleExport} className="datatable-btn datatable-btn-export">EXPORT</button>
              <button onClick={() => setShowGraph(true)} className="datatable-btn datatable-btn-graph">Graphical Analysis</button>
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

        <div className="datatable-super-filter">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="datatable-dropdown"
              >
                <option value="">All Data</option>
                <option value="Extremely Severe">Extremely Severe</option>
                <option value="Severe">Severe</option>
                <option value="Moderate">Moderate</option>
                <option value="Mild">Mild</option>
                <option value="Normal">Normal</option>
              </select>
              <button onClick={handleSuperFilter} className="datatable-btn datatable-btn-super-filter">
                Apply Filter
              </button>
            </div>
            <div className="datatable-legend">
              <table style={{ borderCollapse: 'collapse', marginLeft: '10px' }}>
                <tbody>
                  <tr>
                    <td style={{ padding: '2px 8px', fontWeight: 'bold', textAlign: 'right' }}></td>
                    <td style={{ padding: '2px 8px' }}><span className="legend-box legend-red"></span> Red - Extremely Severe</td>
                    <td style={{ padding: '2px 8px' }}><span className="legend-box legend-orange"></span> Orange - Severe</td>
                    <td style={{ padding: '2px 8px' }}><span className="legend-box legend-yellow"></span> Yellow - Moderate</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

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
                    <th>JCO Review</th>
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
                        {person.peerEvaluation.status === "EVALUATED"
                          ? mapPerformance(person.peerEvaluation.finalScore)
                          : <span>Not Evaluated Yet</span>
                        }
                      </td>


                      <td>
                        {person.selfEvaluation === "COMPLETED" ? (() => {
                          // Find latest manual and AI results for this person
                          const resultEntries = results.filter(r => r?.[2] === person.armyNo);
                          let manualResult = null;
                          let aiResult = null;
                          for (const r of resultEntries) {
                            if (!manualResult && r[3] === 'MANUAL') {
                              manualResult = r[0];
                            }
                            if (!aiResult && r[3] === 'AI') {
                              aiResult = r[0];
                            }
                            if (manualResult && aiResult) break; // stop early once both found
                          }
                          // Helper to get color class
                          const getSeverityClass = (severity) => {
                            if (!severity) return '';
                            if (severity === 'Extremely Severe') return 'result-red';
                            if (severity === 'Severe') return 'result-orange';
                            if (severity === 'Moderate') return 'result-yellow';
                            return '';
                          };

                          return (
                            <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                              <tbody>
                                <tr>
                                  <td style={{ fontWeight: 'bold', background: '#f5f5f5', border: '1px solid #ccc', width: '80px', verticalAlign: 'top' }}>Manual:</td>
                                  <td style={{ border: '1px solid #ccc', padding: '4px' }}>
                                    {manualResult ? (
                                      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                        <tbody>
                                          <tr>
                                            <td style={{ fontWeight: 'bold', border: '1px solid #ccc', padding: '2px 6px' }}>Depression</td>
                                            <td style={{ fontWeight: 'bold', border: '1px solid #ccc', padding: '2px 6px' }}>Anxiety</td>
                                            <td style={{ fontWeight: 'bold', border: '1px solid #ccc', padding: '2px 6px' }}>Stress</td>
                                          </tr>
                                          <tr>
                                            
                                            <td className={getSeverityClass(manualResult.depressionSeverity)} style={{ border: '1px solid #ccc', padding: '2px 6px', borderRadius: '4px' }}>
                                              {Number(manualResult.depression).toFixed(2)} ({manualResult.depressionSeverity})
                                            </td>
                                            <td className={getSeverityClass(manualResult.anxietySeverity)} style={{ border: '1px solid #ccc', padding: '2px 6px', borderRadius: '4px' }}>
                                              {Number(manualResult.anxiety).toFixed(2)} ({manualResult.anxietySeverity})
                                            </td>
                                            <td className={getSeverityClass(manualResult.stressSeverity)} style={{ border: '1px solid #ccc', padding: '2px 6px', borderRadius: '4px' }}>
                                              {Number(manualResult.stress).toFixed(2)} ({manualResult.stressSeverity})
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    ) : (
                                      <span style={{ color: '#e74c3c' }}>No manual result found</span>
                                    )}
                                  </td>
                                </tr>
                                <tr>
                                  <td style={{ fontWeight: 'bold', background: '#f5f5f5', border: '1px solid #ccc', width: '80px', verticalAlign: 'top' }}>AI:</td>
                                  <td style={{ border: '1px solid #ccc', padding: '4px' }}>
                                    {aiResult ? (
                                      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                        <tbody>
                                          <tr>
                                            <td style={{ fontWeight: 'bold', border: '1px solid #ccc', padding: '2px 6px' }}>Depression</td>
                                            <td style={{ fontWeight: 'bold', border: '1px solid #ccc', padding: '2px 6px' }}>Anxiety</td>
                                            <td style={{ fontWeight: 'bold', border: '1px solid #ccc', padding: '2px 6px' }}>Stress</td>
                                          </tr>
                                          <tr>
                                            
                                            <td className={getSeverityClass(aiResult.depressionSeverity)} style={{ border: '1px solid #ccc', padding: '2px 6px', borderRadius: '4px' }}>
                                              {Number(aiResult.depression).toFixed(2)} ({aiResult.depressionSeverity})
                                            </td>
                                            <td className={getSeverityClass(aiResult.anxietySeverity)} style={{ border: '1px solid #ccc', padding: '2px 6px', borderRadius: '4px' }}>
                                              {Number(aiResult.anxiety).toFixed(2)} ({aiResult.anxietySeverity})
                                            </td>
                                            <td className={getSeverityClass(aiResult.stressSeverity)} style={{ border: '1px solid #ccc', padding: '2px 6px', borderRadius: '4px' }}>
                                              {Number(aiResult.stress).toFixed(2)} ({aiResult.stressSeverity})
                                            </td>
                                          </tr>
                                        </tbody>
                                      </table>
                                    ) : (
                                      <span style={{ color: '#e67e22' }}>No AI result found</span>
                                    )}
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                          );
                        })() : (
                          <td>Not Completed</td>
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

      {showGraph && (
        <div className="graph-modal-overlay-ga">
          <div className="graph-modal-content-ga">
            <button
              className="graph-modal-close-ga"
              onClick={() => setShowGraph(false)}
              title="Close Graphical Analysis"
            >✖</button>
            <GraphicalAnalysis filteredPersonnel={filteredPersonnel} results={results} />
          </div>
        </div>
      )}
    </div>
  )
}

export default DataTable_CO
