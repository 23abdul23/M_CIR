import React, { useState } from 'react';
import '../styles/FinancialForm.css';
import axios from 'axios';

const FinancialForm = () => { 
	const [formData, setFormData] = useState({ 
	ID_No: '', 
	Rank: '', 
	Name: '', 
	Unit: '', 
	Monthly_Income: '', 
	Additional_Income: '', 
	Outstanding_Loans: '', 
	Monthly_Loan_Repayment: '', 
	Monthly_Essentials: '', 
	Savings_Percentage: '', 
	Child_Family_Support: '', 
	Insurance_Payments: '', 
	Medical_Payments: '', 
	Future_Purchase: '', 
	Future_Savings: '', 
	Hobbies: '', 
	Dining_Luxuries: '', 
	Track_Budget: '', 
	Emergency_Fund: '', 
	Credit_Score: '', 
	Credit_History: '' 
	
});

const [result, setResult] = useState(null);

const handleChange = (e) => { 
	const { name, value } = e.target; 
	setFormData((prev) => ({ ...prev, [name]: value })); 
};

const handleSubmit = async (e) => { 
	e.preventDefault(); 
	const res = await submitForm(formData); 
	setResult(res.data); };

const submitForm = async (data) => {
  return await axios.post('http://127.0.0.1:8000/api/predict', data);
};

return ( 
	<div className="financial-form-container"> 
	<h2 className="form-title">Financial Profiling Form</h2> 
	<form onSubmit={handleSubmit} className="form-grid"> 
	<input type="text" name="ID_No" placeholder="Army No" className="form-input" onChange={handleChange} required /> 
	<select name="Rank" className="form-select" onChange={handleChange} required>
      <option value="">Select Rank</option>
      <option value="Brig">Brig</option>
      <option value="Capt">Capt</option>
      <option value="Col">Col</option>
      <option value="Gen">Gen</option>
      <option value="Lt">Lt</option>
      <option value="Maj">Maj</option>
    </select>
	<input type="text" name="Name" placeholder="Name" className="form-input" onChange={handleChange} required /> 
	<select name="Unit" className="form-select" onChange={handleChange} required>
      <option value="">Select Unit</option>
      <option value="Armoured">Armoured</option>
      <option value="Artillery">Artillery</option>
      <option value="Aviation">Aviation</option>
      <option value="Engineers">Engineers</option>
      <option value="Infantry">Infantry</option>
      <option value="Signals">Signals</option>
    </select>

<select name="Monthly_Income" className="form-select" onChange={handleChange} required>
      <option value="">Monthly Income</option>
      <option value="25000">₹25,000</option>
      <option value="50000">₹50,000</option>
      <option value="75000">₹75,000</option>
      <option value="100000">₹1,00,000</option>
    </select>

    <select name="Additional_Income" className="form-select" onChange={handleChange} required>
      <option value="">Additional Income</option>
      <option value="0">₹0</option>
      <option value="5000">₹5,000</option>
      <option value="10000">₹10,000</option>
    </select>

    <select name="Outstanding_Loans" className="form-select" onChange={handleChange} required>
      <option value="">Outstanding Loans</option>
      <option value="None">None</option>
      <option value="Home Loan">Home Loan</option>
      <option value="Car Loan">Car Loan</option>
    </select>

    <select name="Monthly_Loan_Repayment" className="form-select" onChange={handleChange} required>
      <option value="">Loan Repayment</option>
      <option value="0">0</option>
      <option value="5000">₹5,000</option>
      <option value="10000">₹10,000</option>
    </select>

    <select name="Monthly_Essentials" className="form-select" onChange={handleChange} required>
      <option value="">Monthly Essentials</option>
      <option value="10000">₹10,000</option>
      <option value="20000">₹20,000</option>
      <option value="30000">₹30,000</option>
    </select>

    <select name="Savings_Percentage" className="form-select" onChange={handleChange} required>
      <option value="">Savings (%)</option>
      <option value="10">10%</option>
      <option value="20">20%</option>
      <option value="30">30%</option>
    </select>

    <select name="Child_Family_Support" className="form-select" onChange={handleChange} required>
      <option value="">Child/Family Support</option>
      <option value="0">₹0</option>
      <option value="2000">₹2,000</option>
      <option value="5000">₹5,000</option>
    </select>

    <select name="Insurance_Payments" className="form-select" onChange={handleChange} required>
      <option value="">Insurance Payments</option>
      <option value="0">₹0</option>
      <option value="1000">₹1,000</option>
      <option value="2000">₹2,000</option>
    </select>

    <select name="Medical_Payments" className="form-select" onChange={handleChange} required>
      <option value="">Medical Payments</option>
      <option value="0">₹0</option>
      <option value="1000">₹1,000</option>
      <option value="2000">₹2,000</option>
    </select>

    <select name="Future_Purchase" className="form-select" onChange={handleChange} required>
      <option value="">Future Purchase</option>
      <option value="None">None</option>
      <option value="Car">Car</option>
      <option value="House">House</option>
    </select>

    <select name="Future_Savings" className="form-select" onChange={handleChange} required>
      <option value="">Future Savings</option>
      <option value="0">₹0</option>
      <option value="5000">₹5,000</option>
      <option value="10000">₹10,000</option>
    </select>

    <select name="Hobbies" className="form-select" onChange={handleChange} required>
      <option value="">Hobbies</option>
      <option value="None">None</option>
      <option value="Gaming">Gaming</option>
      <option value="Reading">Reading</option>
    </select>

    <select name="Dining_Luxuries" className="form-select" onChange={handleChange} required>
      <option value="">Dining Frequency</option>
      <option value="Never">Never</option>
      <option value="Monthly">Monthly</option>
      <option value="Weekly">Weekly</option>
    </select>

    <select name="Track_Budget" className="form-select" onChange={handleChange} required>
      <option value="">Track Budget</option>
      <option value="Yes">Yes</option>
      <option value="No">No</option>
    </select>

    <select name="Emergency_Fund" className="form-select" onChange={handleChange} required>
      <option value="">Emergency Fund</option>
      <option value="Yes">Yes</option>
      <option value="No">No</option>
    </select>

    <select name="Credit_Score" className="form-select" onChange={handleChange} required>
      <option value="">Credit Score</option>
      <option value="Poor">Poor</option>
      <option value="Average">Average</option>
      <option value="Good">Good</option>
	  <option value="Excellent">Excellent</option>
    </select>

    <select name="Credit_History" className="form-select" onChange={handleChange} required>
      <option value="">Credit History</option>
      <option value="Defaulted">Defaulted</option>
      <option value="Average">Average</option>
      <option value="Clean">Clean</option>
    </select>

    <div className="submit-button-container">
      <button type="submit" className="submit-button">
        Submit
      </button>
    </div>
  </form>

  {result && (
    <div className="result-container">
      <h3 className="result-title">Prediction Result</h3>
      <p className="result-item"><span className="result-label">Score:</span> {result.score}</p>
      <p className="result-item"><span className="result-label">Message:</span> {result.message}</p>
    </div>
  )}
</div>

); 

};

export default FinancialForm;