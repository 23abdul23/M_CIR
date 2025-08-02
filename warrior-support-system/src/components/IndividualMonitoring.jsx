import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import '../styles/IndividualMonitoring.css';

const IndividualMonitoring = ({ armyNo: propArmyNo, currentUser, onLogout, onBack }) => {
  const { armyNo: paramArmyNo } = useParams();
  const navigate = useNavigate();
  const armyNo = propArmyNo || paramArmyNo; // Use prop if available, otherwise use param
  
  const [personnelData, setPersonnelData] = useState(null);
  const [examinationHistory, setExaminationHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPersonnelData();
    fetchExaminationHistory();
  }, [armyNo]);

  const fetchPersonnelData = async () => {
    try {
      const response = await axios.get(`/api/personnel/army-no/${armyNo}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setPersonnelData(response.data);
    } catch (error) {
      console.error('Error fetching personnel data:', error);
      setError('Failed to fetch personnel data');
    }
  };

  const fetchExaminationHistory = async () => {
    try {
      const response = await axios.get(`/api/examination/history/${armyNo}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });

      
      setExaminationHistory(response.data);
    } catch (error) {
      console.error('Error fetching examination history:', error);
      setError('Failed to fetch examination history');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (onBack) {
      onBack(); // Use the passed onBack function for DataTable integration
    } else {
      navigate(-1); // Fallback for standalone usage
    }
  };

  if (loading) {
    return (
      <div className="individual-monitoring">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading individual monitoring data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="individual-monitoring">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={handleBack} className="back-btn">Go Back</button>
        </div>
      </div>
    );
  }

  // Prepare data for charts
  const chartData = examinationHistory.map((exam, index) => ({
    examination: `Exam ${index + 1}`,
    date: new Date(exam.completedAt).toLocaleDateString(),
    depression: exam.dassScores.depression,
    anxiety: exam.dassScores.anxiety,
    stress: exam.dassScores.stress,
    depressionSeverity: exam.dassScores.depressionSeverity,
    anxietySeverity: exam.dassScores.anxietySeverity,
    stressSeverity: exam.dassScores.stressSeverity
  }));

  // Latest scores for pie charts
  const latestScores = examinationHistory.length > 0 ? examinationHistory[examinationHistory.length - 1].dassScores : null;

  const pieData = latestScores ? [
    { name: 'Depression', value: latestScores.depression, color: '#FF6B6B' },
    { name: 'Anxiety', value: latestScores.anxiety, color: '#4ECDC4' },
    { name: 'Stress', value: latestScores.stress, color: '#45B7D1' }
  ] : [];

  const severityColors = {
    'Normal': '#4CAF50',
    'Mild': '#FFC107',
    'Moderate': '#FF9800',
    'Severe': '#F44336',
    'Extremely Severe': '#9C27B0'
  };

  return (
    <div className="individual-monitoring">
        
      <div className="monitoring-header">
        <button onClick={handleBack} className="back-btn">← Back</button>
        <h1>Individual Monitoring Dashboard</h1>
      </div>

      {personnelData && (
        <div className="personnel-info">
          <div className="info-card">
            <h2>Personnel Information</h2>
            <div className="info-grid">
              <div className="info-item">
                <label>Army No:</label>
                <span>{personnelData.armyNo}</span>
              </div>
              <div className="info-item">
                <label>Name:</label>
                <span>{personnelData.name}</span>
              </div>
              <div className="info-item">
                <label>Rank:</label>
                <span>{personnelData.rank}</span>
              </div>
              <div className="info-item">
                <label>Battalion:</label>
                <span>{personnelData.battalion?.name}</span>
              </div>
              <div className="info-item">
                <label>Service:</label>
                <span>{personnelData.service}</span>
              </div>
              <div className="info-item">
                <label>Self Evaluation:</label>
                <span className={`status ${personnelData.selfEvaluation?.toLowerCase().replace('_', '-')}`}>
                  {personnelData.selfEvaluation}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {examinationHistory.length > 0 ? (
        <div className="charts-container">
          <div className='same-line-charts'>
            {/* Line Chart for Score Trends */}
            <div className="chart-card">
                <h3>DASS-21 Score Trends Over Time</h3>
                <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line 
                    type="monotone" 
                    dataKey="depression" 
                    stroke="#FF6B6B" 
                    strokeWidth={3}
                    name="Depression"
                    />
                    <Line 
                    type="monotone" 
                    dataKey="anxiety" 
                    stroke="#4ECDC4" 
                    strokeWidth={3}
                    name="Anxiety"
                    />
                    <Line 
                    type="monotone" 
                    dataKey="stress" 
                    stroke="#45B7D1" 
                    strokeWidth={3}
                    name="Stress"
                    />
                </LineChart>
                </ResponsiveContainer>
            </div>

            {/* Pie Chart for Score Distribution */}
            <div className="chart-card-pie">
                <h3>Latest Score Distribution</h3>
                <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                    <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                    >
                    {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                    </Pie>
                    <Tooltip />
                </PieChart>
                </ResponsiveContainer>
            </div>

          </div>

          {/* Severity History Table */}
          <div className="chart-card-all">
            <h3>Examination History</h3>
            <div className="history-table">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Depression</th>
                    <th>Anxiety</th>
                    <th>Stress</th>
                    <th>Overall Assessment</th>
                    <th>Mode</th>
                  </tr>
                </thead>
                <tbody>
                  {examinationHistory.map((exam, index) => (
                    <tr key={index}>
                      <td>{new Date(exam.completedAt).toLocaleDateString()}</td>
                      <td>
                        <span 
                          className="severity-badge"
                          style={{ backgroundColor: severityColors[exam.dassScores.depressionSeverity] }}
                        >
                          {exam.dassScores.depression} ({exam.dassScores.depressionSeverity})
                        </span>
                      </td>
                      <td>
                        <span 
                          className="severity-badge"
                          style={{ backgroundColor: severityColors[exam.dassScores.anxietySeverity] }}
                        >
                          {exam.dassScores.anxiety} ({exam.dassScores.anxietySeverity})
                        </span>
                      </td>
                      <td>
                        <span 
                          className="severity-badge"
                          style={{ backgroundColor: severityColors[exam.dassScores.stressSeverity] }}
                        >
                          {exam.dassScores.stress} ({exam.dassScores.stressSeverity})
                        </span>
                      </td>
                      <td>
                        {exam.dassScores.depressionSeverity === 'Normal' && 
                         exam.dassScores.anxietySeverity === 'Normal' && 
                         exam.dassScores.stressSeverity === 'Normal' ? 
                         'Good' : 'Needs Attention'}
                      </td>
                      <td>
                        {exam.mode}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <div className="no-data">
          <h3>No Examination Data Available</h3>
          <p>This personnel member has not completed any examinations yet.</p>
        </div>
      )}
    </div>
  );
};

export default IndividualMonitoring;
