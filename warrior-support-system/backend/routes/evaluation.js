const express = require('express')
const Personnel = require('../models/Personnel')
const auth = require('../middleware/auth')
const User = require('../models/User')

const router = express.Router()



// Submit peer evaluation
router.post('/submit', auth, async (req, res) => {
  try {
    // JSO only can submit peer evaluation
    if (req.user.role !== 'JCO') {
      return res.status(403).json({ message: 'Access denied' })
    }

    console.log(req.body)
    const { personnelId, answers, finalScore} = req.body
    

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
      answers: answers,
      finalScore: finalScore
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
    if (req.user.role !== 'JCO') {
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