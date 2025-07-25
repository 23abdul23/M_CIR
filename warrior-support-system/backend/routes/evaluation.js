const express = require('express')
const Personnel = require('../models/Personnel')
const auth = require('../middleware/auth')
const User = require('../models/User')

const router = express.Router()

// Get peer evaluation questions
router.get('/questions', auth, async (req, res) => {
  try {
    // JSO only can access peer evaluation
    if (req.user.role !== 'JSO') {
      return res.status(403).json({ message: 'Access denied' })
    }

    // Sample peer evaluation questions - in real app, these would come from database
    const questions = [
      {
        id: 1,
        question: "How would you rate this person's leadership qualities?",
        options: [
          "Excellent - Shows exceptional leadership skills",
          "Good - Demonstrates solid leadership abilities", 
          "Average - Shows basic leadership potential",
          "Needs Improvement - Requires development in leadership"
        ]
      },
      {
        id: 2,
        question: "How well does this person work in a team environment?",
        options: [
          "Outstanding team player",
          "Works well with others",
          "Adequate team participation",
          "Struggles with teamwork"
        ]
      },
      {
        id: 3,
        question: "Rate this person's technical competence in their role:",
        options: [
          "Highly skilled and knowledgeable",
          "Competent in most areas",
          "Basic technical skills",
          "Needs significant improvement"
        ]
      },
      {
        id: 4,
        question: "Additional comments about this person's performance:",
        type: "text"
      }
    ]

    res.json(questions)
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

// Submit peer evaluation
router.post('/submit', auth, async (req, res) => {
  try {
    // JSO only can submit peer evaluation
    if (req.user.role !== 'JSO') {
      return res.status(403).json({ message: 'Access denied' })
    }

    const { personnelId, answers } = req.body

    const personnel = await Personnel.findById(personnelId)
    if (!personnel) {
      return res.status(404).json({ message: 'Personnel not found' })
    }

    // Check if JSO is from same battalion
    const user = await User.findById(req.user.userId)
    if (personnel.battalion.toString() !== user.battalion.toString()) {
      return res.status(403).json({ message: 'Access denied - different battalion' })
    }

    // Update personnel with peer evaluation
    personnel.peerEvaluation = {
      status: 'EVALUATED',
      evaluatedBy: req.user.userId,
      evaluatedAt: new Date(),
      answers: answers
    }

    await personnel.save()
    await personnel.populate('peerEvaluation.evaluatedBy', 'fullName rank')

    res.json({ message: 'Peer evaluation submitted successfully', personnel })
  } catch (error) {
    console.log('Error:', error)
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

// Get personnel for evaluation (JSO only)
router.get('/personnel/:id', auth, async (req, res) => {
  try {
    if (req.user.role !== 'JSO') {
      return res.status(403).json({ message: 'Access denied' })
    }

    const personnel = await Personnel.findById(req.params.id)
      .populate('battalion', 'name')
      .populate('peerEvaluation.evaluatedBy', 'fullName rank')

    if (!personnel) {
      return res.status(404).json({ message: 'Personnel not found' })
    }

    // Check if JSO is from same battalion
    const user = await User.findById(req.user.userId)
    if (personnel.battalion._id.toString() !== user.battalion.toString()) {
      return res.status(403).json({ message: 'Access denied - different battalion' })
    }

    res.json(personnel)
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

module.exports = router