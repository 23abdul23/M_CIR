import React from 'react';
import { useState , useEffect} from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import '../styles/GraphicalAnalysis.css';
import { filter } from 'lodash';
Chart.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const severityCategories = [
  'Normal',
  'Mild',
  'Moderate',
  'Severe',
  'Extremely Severe'
];


function getSeverityCounts(filteredPersonnel, results, type, mode) {
  // type: 'anxiety', 'depression', 'stress'; mode: 'MANUAL' or 'AI'
  
  const counts = {
    'Normal': 0,
    'Mild': 0,
    'Moderate': 0,
    'Severe': 0,
    'Extremely Severe': 0
  };
  filteredPersonnel.forEach(person => {
    if (person.selfEvaluation === 'COMPLETED') {
      const resultEntry = results.find(r => r?.[2] === person.armyNo && r?.[3] === mode);
      const scores = resultEntry?.[0];
      if (scores) {
        const severity = scores[type + 'Severity'];
        if (severity && counts.hasOwnProperty(severity)) {
          counts[severity]++;
        }
      }
    }
  });
  return severityCategories.map(cat => counts[cat]);
}


const GraphicalAnalysis = ({ filteredPersonnel, results }) => {
  // Manual graphs
  const [Bty, setBty] = useState([])


  useEffect(() => {
  const X = new Set(filteredPersonnel.map(p => p.subBty));
  setBty([...X]);
}, [filteredPersonnel]);

  
  const manualAnxietyData = {
    labels: severityCategories,
    datasets: [
      {
        label: 'Manual Anxiety',
        data: getSeverityCounts(filteredPersonnel, results, 'anxiety', 'MANUAL'),
        backgroundColor: '#3498db',
      },
    ],
  };
  const manualDepressionData = {
    labels: severityCategories,
    datasets: [
      {
        label: 'Manual Depression',
        data: getSeverityCounts(filteredPersonnel, results, 'depression', 'MANUAL'),
        backgroundColor: '#e74c3c',
      },
    ],
  };
  const manualStressData = {
    labels: severityCategories,
    datasets: [
      {
        label: 'Manual Stress',
        data: getSeverityCounts(filteredPersonnel, results, 'stress', 'MANUAL'),
        backgroundColor: '#f1c40f',
      },
    ],
  };
  // AI graphs
  const aiAnxietyData = {
    labels: severityCategories,
    datasets: [
      {
        label: 'AI Anxiety',
        data: getSeverityCounts(filteredPersonnel, results, 'anxiety', 'AI'),
        backgroundColor: '#2980b9',
      },
    ],
  };
  const aiDepressionData = {
    labels: severityCategories,
    datasets: [
      {
        label: 'AI Depression',
        data: getSeverityCounts(filteredPersonnel, results, 'depression', 'AI'),
        backgroundColor: '#c0392b',
      },
    ],
  };
  const aiStressData = {
    labels: severityCategories,
    datasets: [
      {
        label: 'AI Stress',
        data: getSeverityCounts(filteredPersonnel, results, 'stress', 'AI'),
        backgroundColor: '#f39c12',
      },
    ],
  };

  const allDataValues = [
  ...getSeverityCounts(filteredPersonnel, results, 'anxiety', 'MANUAL'),
  ...getSeverityCounts(filteredPersonnel, results, 'depression', 'MANUAL'),
  ...getSeverityCounts(filteredPersonnel, results, 'stress', 'MANUAL'),
  ...getSeverityCounts(filteredPersonnel, results, 'anxiety', 'AI'),
  ...getSeverityCounts(filteredPersonnel, results, 'depression', 'AI'),
  ...getSeverityCounts(filteredPersonnel, results, 'stress', 'AI')
];

  const maxValue = Math.max(...allDataValues) + 1;

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: false },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1, // Force integer steps
          callback: function (value) {
            return value; // Only show integers
          }
        },
        suggestedMax: maxValue // Go 1 above max data point
      }
    }
  };

  return (
    <div className="graph-analysis-container">
      <h1>Graphical Analysis: {(Bty.length > 1 ? "Overall Analysis": Bty[0])}</h1>
      <div className="graph-section">
        <h2 className="graph-section-title">Manual</h2>
        <div className="graph-charts-row graph-charts-row-single">
          <div className="graph-chart-box">
            <Bar data={manualDepressionData} options={options} width={480} height={320} />
            <h3 className="graph-chart-label">Depression Severity</h3>
          </div>
          <div className="graph-chart-box">
            <Bar data={manualAnxietyData} options={options} width={480} height={320}/>
            <h3 className="graph-chart-label">Anxiety Severity</h3>
          </div>
          <div className="graph-chart-box">
            <Bar data={manualStressData} options={options} width={480} height={320}/>
            <h3 className="graph-chart-label">Stress Severity</h3>
          </div>
        </div>
      </div>
      <div className="graph-section">
        <h2 className="graph-section-title">AI</h2>
        <div className="graph-charts-row graph-charts-row-single">
          <div className="graph-chart-box">
            <Bar data={aiDepressionData} options={options} width={480} height={320}/>
            <h3 className="graph-chart-label">Depression Severity</h3>
          </div>
          <div className="graph-chart-box">
            <Bar data={aiAnxietyData} options={options} width={480} height={320}/>
            <h3 className="graph-chart-label">Anxiety Severity</h3>
          </div>
          <div className="graph-chart-box">
            <Bar data={aiStressData} options={options} width={480} height={320}/>
            <h3 className="graph-chart-label">Stress Severity</h3>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GraphicalAnalysis;
