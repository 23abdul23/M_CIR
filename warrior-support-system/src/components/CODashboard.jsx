import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import '../styles/CODashboard.css'
import '../styles/DashboardCommon.css'

const CODashboard = ({ currentUser, onLogout }) => {
  const [pendingBattalions, setPendingBattalions] = useState([])
  const [allBattalions, setAllBattalions] = useState([])
  const [selectedBattalion, setSelectedBattalion] = useState('')
  const [stats, setStats] = useState({
    totalBattalions: 0,
    pendingApprovals: 0,
    totalPersonnel: 0,
    activeUsers: 0
  })
  const navigate = useNavigate()

  useEffect(() => {
    fetchPendingBattalions()
    fetchAllBattalions()
    calculateStats()
  }, [])

  const fetchPendingBattalions = async () => {
    try {
      const response = await axios.get('/api/battalion/pending', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      setPendingBattalions(response.data)
    } catch (error) {
      console.error('Error fetching pending battalions:', error)
    }
  }

  const fetchAllBattalions = async () => {
    try {
      const response = await axios.get('/api/battalion', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      setAllBattalions(response.data)
    } catch (error) {
      console.error('Error fetching battalions:', error)
    }
  }

  const calculateStats = async () => {
    try {
      // You can replace this with an actual API call if you have one
      const approvedBattalions = allBattalions.filter(b => b.status === 'APPROVED').length
      const pendingBattalions = allBattalions.filter(b => b.status === 'PENDING').length
      
      // Get personnel count - this is a placeholder, replace with actual API call
      const personnelResponse = await axios.get('/api/personnel/count', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      }).catch(() => ({ data: { count: 0 }}))
      
      // Get user count - this is a placeholder, replace with actual API call
      const usersResponse = await axios.get('/api/auth/users/count', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      }).catch(() => ({ data: { count: 0 }}))
      
      setStats({
        totalBattalions: approvedBattalions,
        pendingApprovals: pendingBattalions,
        totalPersonnel: personnelResponse.data.count || 0,
        activeUsers: usersResponse.data.count || 0
      })
    } catch (error) {
      console.error('Error calculating stats:', error)
    }
  }

  const handleBattalionAction = async (battalionId, action) => {
    try {
      await axios.patch(`/api/battalion/${battalionId}/status`, 
        { status: action },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      )
      fetchPendingBattalions()
      fetchAllBattalions()
      calculateStats()
      showNotification(`Battalion ${action.toLowerCase()}d successfully`, 'success')
    } catch (error) {
      console.error('Error updating battalion status:', error)
      showNotification('Error updating battalion status', 'error')
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

  const handleViewData = () => {
    if (selectedBattalion) {
      navigate('/data-table')
    }
  }

  const showNotification = (message, type) => {
    // Simple notification implementation
    const notification = document.createElement('div')
    notification.className = `co-notification ${type}`
    notification.textContent = message
    document.body.appendChild(notification)
    
    setTimeout(() => {
      document.body.removeChild(notification)
    }, 3000)
  }

  return (
    <div className="co-dashboard">
      {/* Header */}
      <header className="co-dashboard-header">
        <div className="co-header-content">
          <div className="co-title-section">
            <div>
              <h1 className="co-title">WARRIOR SUPPORT SYSTEM</h1>
              <p className="co-subtitle">Commanding Officer Dashboard</p>
            </div>
          </div>
          <div className="co-user-info">
            <div className="co-user-details">
              <p className="co-user-name">{currentUser?.fullName || 'CO Admin'}</p>
              <p className="co-user-role">CO - Administrator</p>
            </div>
            <button className="co-logout-btn" onClick={handleLogout}>
              LOGOUT
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="co-main-content">
        {/* Statistics Grid */}
        <section className="co-stats-grid">
          <div className="co-stat-card">
            <div className="co-stat-header">
              <span className="co-stat-title">Total Battalions</span>
              <div className="co-stat-icon">🏛️</div>
            </div>
            <h2 className="co-stat-value">{stats.totalBattalions}</h2>
            <p className="co-stat-description">Approved battalions</p>
          </div>

          <div className="co-stat-card">
            <div className="co-stat-header">
              <span className="co-stat-title">Pending Approvals</span>
              <div className="co-stat-icon">⏳</div>
            </div>
            <h2 className="co-stat-value">{pendingBattalions.length}</h2>
            <p className="co-stat-description">Awaiting approval</p>
          </div>

          <div className="co-stat-card">
            <div className="co-stat-header">
              <span className="co-stat-title">Total Personnel</span>
              <div className="co-stat-icon">👥</div>
            </div>
            <h2 className="co-stat-value">{stats.totalPersonnel}</h2>
            <p className="co-stat-description">Active personnel</p>
          </div>

          <div className="co-stat-card">
            <div className="co-stat-header">
              <span className="co-stat-title">Active Users</span>
              <div className="co-stat-icon">👤</div>
            </div>
            <h2 className="co-stat-value">{stats.activeUsers}</h2>
            <p className="co-stat-description">System users</p>
          </div>
        </section>

        {/* Quick Actions */}
        <section className="co-actions-section">
          <h2 className="co-section-title">Quick Actions</h2>
          <div className="co-actions-grid">
            <div className="co-action-card">
              <h3 className="co-action-title">Start Examination</h3>
              <p className="co-action-description">
                Begin a new examination for personnel assessment
              </p>
              <button 
                className="co-action-btn"
                onClick={() => navigate('/army-number-entry')}
              >
                START EXAMINATION
              </button>
            </div>

            <div className="co-action-card">
              <h3 className="co-action-title">Add New User</h3>
              <p className="co-action-description">
                Create a new user account in the system
              </p>
              <button 
                className="co-action-btn"
                onClick={() => navigate('/register')}
              >
                ADD NEW USER
              </button>
            </div>

            <div className="co-action-card">
              <h3 className="co-action-title">View Battalion Data</h3>
              <p className="co-action-description">
                View personnel data for selected battalion
              </p>
              <select 
                value={selectedBattalion}
                onChange={(e) => setSelectedBattalion(e.target.value)}
                className="form-control mb-2"
              >
                <option value="">Select Battalion</option>
                {allBattalions.filter(b => b.status === 'APPROVED').map(battalion => (
                  <option key={battalion._id} value={battalion._id}>
                    {battalion.name}
                  </option>
                ))}
              </select>
              <button 
                className="co-action-btn"
                onClick={handleViewData}
                disabled={!selectedBattalion}
              >
                VIEW DATA
              </button>
            </div>
          </div>
        </section>

        {/* Battalion Management */}
        <section className="co-battalion-management">
          <h2 className="co-section-title">Battalion Management</h2>
          {pendingBattalions.length > 0 ? (
            <div className="co-battalion-grid">
              {pendingBattalions.map(battalion => (
                <div key={battalion._id} className="co-battalion-card">
                  <div className="co-battalion-header">
                    <h3 className="co-battalion-name">{battalion.name}</h3>
                    <span className="co-battalion-status pending">
                      PENDING
                    </span>
                  </div>
                  <div className="co-battalion-info">
                    <div>
                      <strong>Posted Strength:</strong> {battalion.postedStr}
                    </div>
                    <div>
                      <strong>Created:</strong> {new Date(battalion.createdAt).toLocaleDateString()}
                    </div>
                    <div>
                      <strong>Requested by:</strong> {battalion.requestedBy?.fullName || 'Unknown'}
                    </div>
                    <div>
                      <strong>Username:</strong> {battalion.requestedBy?.username || 'Unknown'}
                    </div>
                  </div>
                  <div className="co-battalion-actions">
                    <button 
                      className="co-btn-approve"
                      onClick={() => handleBattalionAction(battalion._id, 'APPROVED')}
                    >
                      APPROVE
                    </button>
                    <button 
                      className="co-btn-reject"
                      onClick={() => handleBattalionAction(battalion._id, 'REJECTED')}
                    >
                      REJECT
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center">No pending battalion requests</p>
          )}
        </section>

        {/* All Approved Battalions */}
        <section className="co-recent-activity">
          <h2 className="co-section-title">Approved Battalions</h2>
          <div className="co-battalion-grid">
            {allBattalions
              .filter(battalion => battalion.status === 'APPROVED')
              .map(battalion => (
                <div key={battalion._id} className="co-battalion-card">
                  <div className="co-battalion-header">
                    <h3 className="co-battalion-name">{battalion.name}</h3>
                    <span className="co-battalion-status approved">
                      APPROVED
                    </span>
                  </div>
                  <div className="co-battalion-info">
                    <div>
                      <strong>Posted Strength:</strong> {battalion.postedStr}
                    </div>
                    <div>
                      <strong>Created:</strong> {new Date(battalion.createdAt).toLocaleDateString()}
                    </div>
                    <div>
                      <strong>Approved:</strong> {battalion.approvedAt ? new Date(battalion.approvedAt).toLocaleDateString() : 'N/A'}
                    </div>
                  </div>
                  <div className="co-battalion-actions">
                    <button 
                      className="co-btn-view"
                      onClick={() => {
                        setSelectedBattalion(battalion._id);
                        navigate('/data-table');
                      }}
                    >
                      VIEW DETAILS
                    </button>
                  </div>
                </div>
              ))}
          </div>
        </section>
      </main>
    </div>
  )
}

export default CODashboard