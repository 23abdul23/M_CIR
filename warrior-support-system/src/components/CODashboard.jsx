"use client"

import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import "../styles/CODashboard.css"
import "../styles/DashboardCommon.css"
import "../styles/QuestionModal.css"

const CODashboard = ({ currentUser, onLogout }) => {
  const [pendingBattalions, setPendingBattalions] = useState([])
  const [allBattalions, setAllBattalions] = useState([])
  const [selectedBattalion, setSelectedBattalion] = useState("")
  const [questions, setQuestions] = useState([])
  const [showQuestionModal, setShowQuestionModal] = useState(false)
  const [showQuestionsView, setShowQuestionsView] = useState(false)
  const [stats, setStats] = useState({
    totalBattalions: 0,
    pendingApprovals: 0,
    totalQuestions: 0,
  })
  const navigate = useNavigate()

  useEffect(() => {
    fetchPendingBattalions()
    fetchAllBattalions()
    fetchQuestions()
    calculateStats()
  }, [])

  const fetchPendingBattalions = async () => {
    try {
      const response = await axios.get("/api/battalion/pending", {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      })
      setPendingBattalions(response.data)
    } catch (error) {
      console.error("Error fetching pending battalions:", error)
    }
  }

  const fetchAllBattalions = async () => {
    try {
      const response = await axios.get("/api/battalion", {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      })
      setAllBattalions(response.data)
    } catch (error) {
      console.error("Error fetching battalions:", error)
    }
  }

  const fetchQuestions = async () => {
    try {
      const response = await axios.get("/api/questions", {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      })
      
      
      setQuestions(response.data)
    } catch (error) {
      console.error("Error fetching questions:", error)
      showNotification("Error fetching questions", "error")
      // Set empty array if error
      setQuestions([])
    }
  }

  const calculateStats = async () => {
    try {
      // You can replace this with an actual API call if you have one
      const responce = await axios.get(`api/battalion`,{
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      console.log(responce.data.length)
      
      const approvedBattalions = responce.data.filter((b) => b.status === "APPROVED").length
      const pendingBattalions = responce.data.filter((b) => b.status === "PENDING").length
      
      const res = await axios.get("/api/questions", {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      })
      
      setStats({
        totalBattalions: approvedBattalions,
        pendingApprovals: pendingBattalions,
        totalQuestions: res.data.length,
      })
    } catch (error) {
      console.error("Error calculating stats:", error)
    }
  }

  const handleBattalionAction = async (battalionId, action) => {
    try {
      await axios.patch(
        `/api/battalion/${battalionId}/status`,
        { status: action },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } },
      )
      fetchPendingBattalions()
      fetchAllBattalions()
      calculateStats()
      showNotification(`Battalion ${action.toLowerCase()}d successfully`, "success")
    } catch (error) {
      console.error("Error updating battalion status:", error)
      showNotification("Error updating battalion status", "error")
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    localStorage.removeItem("currentArmyNo")

    if (onLogout) {
      onLogout()
    }

    navigate("/login")
  }

  const handleViewData = () => {
    if (selectedBattalion) {
      navigate("/data-table-co", {
        state: { selectedBattalion }
      })

    }
  }

  const showNotification = (message, type) => {
    // Simple notification implementation
    const notification = document.createElement("div")
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
              <p className="co-user-name">{currentUser?.fullName || "CO Admin"}</p>
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
              <span className="co-stat-title">Total Questions</span>
              <div className="co-stat-icon">❓</div>
            </div>
            <h2 className="co-stat-value">{stats.totalQuestions}</h2>
            <p className="co-stat-description">Examination questions</p>
          </div>
        </section>

        {/* Quick Actions */}
        <section className="co-actions-section">
          <h2 className="co-section-title">Quick Actions</h2>
          <div className="co-actions-grid">
            
            <div className="co-action-card">
              <h3 className="co-action-title">Manage Questions</h3>
              <p className="co-action-description">Add, edit, or manage examination questions</p>
              <div className="co-action-buttons">
                <button className="co-action-btn co-btn-primary" onClick={() => setShowQuestionModal(true)}>
                  ADD QUESTION
                </button>
                <button className="co-action-btn co-btn-secondary" onClick={() => setShowQuestionsView(true)}>
                  VIEW QUESTIONS
                </button>
              </div>
            </div>
            <div className="co-action-card">
              <h3 className="co-action-title">View Battalion Data</h3>
              <p className="co-action-description">View personnel data for selected battalion</p>
              <select
                value={selectedBattalion}
                onChange={(e) => setSelectedBattalion(e.target.value)}
                className="form-control mb-2"
              >
                <option value="">Select Battalion</option>
                {allBattalions
                  .filter((b) => b.status === "APPROVED")
                  .map((battalion) => (
                    <option key={battalion._id} value={battalion._id}>
                      {battalion.name}
                    </option>
                  ))}
              </select>
              <button className="co-action-btn" onClick={handleViewData} disabled={!selectedBattalion}>
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
              {pendingBattalions.map((battalion) => (
                <div key={battalion._id} className="co-battalion-card">
                  <div className="co-battalion-header">
                    <h3 className="co-battalion-name">{battalion.name}</h3>
                    <span className="co-battalion-status pending">PENDING</span>
                  </div>
                  <div className="co-battalion-info">
                    <div>
                      <strong>Posted Strength:</strong> {battalion.postedStr}
                    </div>
                    <div>
                      <strong>Created:</strong> {new Date(battalion.createdAt).toLocaleDateString()}
                    </div>
                    <div>
                      <strong>Requested by:</strong> {battalion.requestedBy?.fullName || "Unknown"}
                    </div>
                    <div>
                      <strong>Username:</strong> {battalion.requestedBy?.username || "Unknown"}
                    </div>
                  </div>
                  <div className="co-battalion-actions">
                    <button className="co-btn-approve" onClick={() => handleBattalionAction(battalion._id, "APPROVED")}>
                      APPROVE
                    </button>
                    <button className="co-btn-reject" onClick={() => handleBattalionAction(battalion._id, "REJECTED")}>
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
              .filter((battalion) => battalion.status === "APPROVED")
              .map((battalion) => (
                <div key={battalion._id} className="co-battalion-card">
                  <div className="co-battalion-header">
                    <h3 className="co-battalion-name">{battalion.name}</h3>
                    <span className="co-battalion-status approved">APPROVED</span>
                  </div>
                  <div className="co-battalion-info">
                    <div>
                      <strong>Posted Strength:</strong> {battalion.postedStr}
                    </div>
                    <div>
                      <strong>Created:</strong> {new Date(battalion.createdAt).toLocaleDateString()}
                    </div>
                    <div>
                      <strong>Approved:</strong>{" "}
                      {battalion.approvedAt ? new Date(battalion.approvedAt).toLocaleDateString() : "N/A"}
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </section>
      </main>

      {/* Add Question Modal */}
      {showQuestionModal && (
        <AddQuestionModal
          onClose={() => setShowQuestionModal(false)}
          onSave={() => {
            fetchQuestions()
            calculateStats()
            setShowQuestionModal(false)
            showNotification("Question added successfully", "success")
          }}
        />
      )}

      {/* View Questions Modal */}
      {showQuestionsView && (
        <ViewQuestionsModal
          questions={questions}
          onClose={() => setShowQuestionsView(false)}
          onRefresh={() => {
            fetchQuestions()
            calculateStats()
          }}
          showNotification={showNotification}
        />
      )}
    </div>
  )
}

// Update the AddQuestionModal component
const AddQuestionModal = ({ onClose, onSave }) => {
  const [formData, setFormData] = useState({
    questionId: "",
    questionText: "",
    questionType: "MCQ",
    options: [
      { optionId: "A", optionText: "" },
      { optionId: "B", optionText: "" },
      { optionId: "C", optionText: "" },
      { optionId: "D", optionText: "" },
    ],
    order: 1,
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Generate questionId if not provided
      const questionId = formData.questionId || Date.now()

      const questionData = {
        questionId: Number.parseInt(questionId),
        questionText: formData.questionText,
        questionType: formData.questionType,
        options: formData.questionType === "MCQ" ? formData.options.filter((opt) => opt.optionText.trim()) : [],
        order: Number.parseInt(formData.order),
      }

      console.log("Submitting question:", questionData)

      await axios.post("/api/questions", questionData, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      })

      onSave()
    } catch (error) {
      console.error("Error adding question:", error)
      const errorMessage = error.response?.data?.message || "Error adding question. Please try again."
      alert(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleOptionChange = (index, value) => {
    const newOptions = [...formData.options]
    newOptions[index].optionText = value
    setFormData({ ...formData, options: newOptions })
  }

  const addTextQuestion = () => {
    setFormData({ ...formData, questionType: "TEXT", options: [] })
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content question-modal">
        <div className="modal-header">
          <h2>ADD NEW QUESTION</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className={loading ? "form-loading" : ""}>
          <div className="form-group">
            <label>Question ID (Optional)</label>
            <input
              type="number"
              value={formData.questionId}
              onChange={(e) => setFormData({ ...formData, questionId: e.target.value })}
              placeholder="Auto-generated if empty"
            />
          </div>

          <div className="form-group">
            <label>Question Text</label>
            <textarea
              value={formData.questionText}
              onChange={(e) => setFormData({ ...formData, questionText: e.target.value })}
              placeholder="Enter the question text..."
              rows={3}
              required
            />
          </div>

          <div className="form-group">
            <label>Question Type</label>
            <select
              value={formData.questionType}
              onChange={(e) => setFormData({ ...formData, questionType: e.target.value })}
            >
              <option value="MCQ">Multiple Choice (MCQ)</option>
              <option value="TEXT">Text Answer</option>
            </select>
          </div>

          <div className="form-group">
            <label>Order</label>
            <input
              type="number"
              value={formData.order}
              onChange={(e) => setFormData({ ...formData, order: e.target.value })}
              min="1"
              required
            />
          </div>

          {formData.questionType === "MCQ" && (
            <div className="options-section">
              <label>Answer Options</label>
              {formData.options.map((option, index) => (
                <div key={index} className="option-group">
                  <div className="option-input-group">
                    <span>{option.optionId}.</span>
                    <input
                      type="text"
                      value={option.optionText}
                      onChange={(e) => handleOptionChange(index, e.target.value)}
                      placeholder={`Option ${option.optionId}`}
                      required={formData.questionType === "MCQ"}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? "ADDING QUESTION..." : "ADD QUESTION"}
          </button>
        </form>
      </div>
    </div>
  )
}

// View Questions Modal Component
const ViewQuestionsModal = ({ questions, onClose, onRefresh, showNotification }) => {
  const [selectedCategory, setSelectedCategory] = useState("")
  const [searchTerm, setSearchTerm] = useState("")

  const categories = [...new Set(questions.map((q) => q.category))].filter(Boolean)

  const filteredQuestions = questions.filter((question) => {
    const matchesCategory = !selectedCategory || question.category === selectedCategory
    const matchesSearch =
      !searchTerm ||
      question.questionText.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (question.category && question.category.toLowerCase().includes(searchTerm.toLowerCase()))
    return matchesCategory && matchesSearch
  })

  const handleDeleteQuestion = async (questionId) => {
    if (window.confirm("Are you sure you want to delete this question?")) {
      try {
        await axios.delete(`/api/questions/${questionId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        })
        onRefresh()
        showNotification("Question deleted successfully", "success")
      } catch (error) {
        console.error("Error deleting question:", error)
        showNotification("Error deleting question", "error")
      }
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content questions-view-modal">
        <div className="modal-header">
          <h2>MANAGE QUESTIONS ({questions.length})</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="questions-filters">
          <div className="filter-group">
            <input
              type="text"
              placeholder="Search questions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          {categories.length > 0 && (
            <div className="filter-group">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="category-filter"
              >
                <option value="">All Categories</option>
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        <div className="questions-list">
          {filteredQuestions.length > 0 ? (
            filteredQuestions.map((question, index) => (
              <div key={question._id} className="question-item">
                <div className="question-header">
                  <span className="question-number">Q{question.questionId}</span>
                  <span className="question-category">{question.questionType}</span>
                  <span className={`question-difficulty ${question.difficulty?.toLowerCase() || "medium"}`}>
                    Order: {question.order}
                  </span>
                  <button className="delete-question-btn" onClick={() => handleDeleteQuestion(question.questionId)}>
                    🗑️
                  </button>
                </div>
                <div className="question-text">{question.questionText}</div>
                {question.questionType === "MCQ" && question.options && question.options.length > 0 && (
                  <div className="question-options">
                    {question.options.map((option, optIndex) => (
                      <div key={optIndex} className="option">
                        <span className="option-label">{option.optionId}.</span>
                        <span className="option-text">{option.optionText}</span>
                      </div>
                    ))}
                  </div>
                )}
                {question.questionType === "TEXT" && (
                  <div className="question-options">
                    <div className="option">
                      <span className="option-text">Text answer expected</span>
                    </div>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="no-questions">
              <p>No questions found matching your criteria.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CODashboard
