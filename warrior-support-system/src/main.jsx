import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'


import './styles/global.css'
import './styles/Header.css'
import './styles/Login.css'
import './styles/Register.css'
import './styles/BattalionSelection.css'
import './styles/MainMenu.css'


ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)