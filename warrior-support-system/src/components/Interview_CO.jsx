import React, { useState, useEffect } from "react";
import axios from "axios";
import Header from "./Header";
import '../styles/InterviewCO.css';
import '../styles/DataTable.css';

const Interview_CO = ({ selectedBattalion, currentUser, onLogout }) => {
    const [severePersonnel, setSeverePersonnel] = useState([]);
    const [loading, setLoading] = useState(true);
    const [interviewChecked, setInterviewChecked] = useState({});
    const interviewDone = async (personId) => {
        try {

            console.log(personId)
            await axios.post(`/api/severePersonnel/done/${personId}`, {}, {
                headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
            });
            fetchSeverePersonnel();
            alert('Interview marked as done!');
            setInterviewChecked((prev) => ({ ...prev, [personId]: false }));

            window.location.reload();
            
        } catch (error) {
            alert('Failed to mark interview as done.');
        }
    };

    const fetchSeverePersonnel = async () => {
        setLoading(true);
        try {
            const responce = await axios.get(`/api/severePersonnel/all`,
                {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
                }
            )
            console.log(responce.data.data)
            setSeverePersonnel(responce.data.data);
        } catch (error) {
            setSeverePersonnel([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSeverePersonnel();
    }, []);

    function getSeverityClass(severity) {
        if (!severity) return '';
        if (severity === 'Extremely Severe') return 'interview-result-red';
        if (severity === 'Severe') return 'interview-result-orange';
        if (severity === 'Moderate') return 'interview-result-yellow';
        return '';
    }

    return (
        <>
            <Header currentUser={currentUser} onLogout={onLogout} />
            <div className="interview-table-container">
                <h2 className="interview-table-title">Severe Personnel List</h2>
                <div className="interview-table-legend">
                    <span className="interview-legend-box interview-legend-red"></span> Red - Extremely Severe
                    <span className="interview-legend-box interview-legend-orange" style={{marginLeft:'16px'}}></span> Orange - Severe
                    <span className="interview-legend-box interview-legend-yellow" style={{marginLeft:'16px'}}></span> Yellow - Moderate
                </div>
                {loading ? (
                    <div className="interview-table-empty">
                        <div className="datatable-spinner"></div>
                        <p>Loading severe personnel data...</p>
                    </div>
                ) : severePersonnel.length === 0 ? (
                    <div className="interview-table-empty">
                        <div className="datatable-empty-icon">📋</div>
                        <h3>No Severe Personnel Found</h3>
                    </div>
                ) : (
                    <div style={{overflowX:'auto'}}>
                        {/* Group by subBty */}
                        {Object.entries(
                            severePersonnel.reduce((acc, person) => {
                                const key = person.subBty || 'Unknown';
                                if (!acc[key]) acc[key] = [];
                                acc[key].push(person);
                                return acc;
                            }, {})
                        ).map(([subBty, persons]) => (
                            <div key={subBty} style={{marginBottom:'32px'}}>
                                <h3 style={{margin:'16px 0', color:'#2c3e50'}}>{subBty}</h3>
                                <table className="interview-table">
                                    <thead>
                                        <tr>
                                            <th>Army No.</th>
                                            <th>Rank</th>
                                            <th>Name</th>
                                            <th>Service</th>
                                            <th>Date of Induction</th>
                                            <th>Med Cat</th>
                                            <th>Leave Availed</th>
                                            <th>Marital Status</th>
                                            <th>Self Evaluation</th>
                                            <th>JCO Review</th>
                                            <th>Results</th>
                                            <th>Interview</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {persons.map((person) => (
                                            <tr key={person._id}>
                                                <td>{person.armyNo}</td>
                                                <td>{person.rank}</td>
                                                <td>{person.name}</td>
                                                <td>{person.service}</td>
                                                <td>{new Date(person.dateOfInduction).toLocaleDateString()}</td>
                                                <td>{person.medCat}</td>
                                                <td>{person.leaveAvailed || 'NIL'}</td>
                                                <td>{person.maritalStatus}</td>
                                                <td>{person.selfEvaluation}</td>
                                                <td>{person.peerEvaluation?.status}</td>
                                                <td>
                                                    {person.dassScores ? (
                                                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                                            <tbody>
                                                                <tr>
                                                                    <td style={{ fontWeight: 'bold', border: '1px solid #ccc', padding: '2px 6px' }}>Anxiety</td>
                                                                    <td style={{ fontWeight: 'bold', border: '1px solid #ccc', padding: '2px 6px' }}>Depression</td>
                                                                    <td style={{ fontWeight: 'bold', border: '1px solid #ccc', padding: '2px 6px' }}>Stress</td>
                                                                </tr>
                                                                <tr>
                                                                    <td className={getSeverityClass(person.dassScores.anxietySeverity)} style={{ border: '1px solid #ccc', padding: '2px 6px', borderRadius: '4px' }}>
                                                                        {person.dassScores.anxiety} ({person.dassScores.anxietySeverity})
                                                                    </td>
                                                                    <td className={getSeverityClass(person.dassScores.depressionSeverity)} style={{ border: '1px solid #ccc', padding: '2px 6px', borderRadius: '4px' }}>
                                                                        {person.dassScores.depression} ({person.dassScores.depressionSeverity})
                                                                    </td>
                                                                    <td className={getSeverityClass(person.dassScores.stressSeverity)} style={{ border: '1px solid #ccc', padding: '2px 6px', borderRadius: '4px' }}>
                                                                        {person.dassScores.stress} ({person.dassScores.stressSeverity})
                                                                    </td>
                                                                </tr>
                                                            </tbody>
                                                        </table>
                                                    ) : (
                                                        <span>No Results found</span>
                                                    )}
                                                </td>
                                                <td>
                                                    <input
                                                        type="checkbox"
                                                        checked={!!interviewChecked[person._id]}
                                                        onChange={e => setInterviewChecked(prev => ({ ...prev, [person._id]: e.target.checked }))}
                                                    />
                                                    {interviewChecked[person._id] && (
                                                        <button
                                                            className="interview-done-btn"
                                                            style={{ marginLeft: '8px', padding: '4px 12px', borderRadius: '4px', background: '#4caf50', color: '#fff', border: 'none', cursor: 'pointer' }}
                                                            onClick={() => interviewDone(person.armyNo)}
                                                        >
                                                            Done
                                                        </button>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </>
    );
};

export default Interview_CO;