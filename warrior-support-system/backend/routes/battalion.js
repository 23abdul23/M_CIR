const express = require('express')
const Battalion = require('../models/Battalion')
const auth = require('../middleware/auth')

const router = express.Router()

// Get all battalions (CO sees all, others see only approved)
router.get('/subBty', async (req, res) => {
  try {
    

    if (req.user && req.user.role === 'CO') {
      // Only CO can see all battalions
      query = {}
    }

    const battalions = await Battalion.find()
      .sort({ createdAt: -1 })

      
    res.json(battalions)
  } catch (error) {
    console.log("Error: ", error)
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})


// Get all battalions (CO sees all, others see only approved)
router.get('/', async (req, res) => {
  try {
    let query = { status: 'APPROVED' } // default for public/unauthenticated

    if (req.user && req.user.role === 'CO') {
      // Only CO can see all battalions
      query = {}
    }

    const battalions = await Battalion.find(query)
      .sort({ createdAt: -1 })

      
    res.json(battalions)
  } catch (error) {
    console.log("Error: ", error)
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

// Get pending battalion requests (CO only)
router.get('/pending', auth, async (req, res) => {
  try {
    if (req.user.role !== 'CO') {
      return res.status(403).json({ message: 'Access denied' })
    }

    const pendingBattalions = await Battalion.find({ status: 'PENDING' })
      .populate('requestedBy', 'fullName username armyNo rank')
      .sort({ createdAt: -1 })

    res.json(pendingBattalions)
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

// Create new battalion (request)
router.post('/', auth, async (req, res) => {
  try {
    const { name, postedStr } = req.body

    // Check if battalion already exists
    const existingBattalion = await Battalion.findOne({ postedStr })
    if (existingBattalion) {
      return res.status(400).json({ message: 'SubBty already exists' })
    }

    const battalionData = {
      name,
      postedStr,
      requestedBy: req.user.userId
    }

    // CO can directly approve, others need approval
    if (req.user.role === 'CO') {
      battalionData.status = 'APPROVED'
      battalionData.approvedBy = req.user.userId
      battalionData.approvedAt = new Date()
    }

    const battalion = new Battalion(battalionData)
    await battalion.save()

    await battalion.populate('requestedBy', 'fullName username')
    await battalion.populate('approvedBy', 'fullName username')

    res.status(201).json(battalion)
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

// Approve/Reject battalion (CO only)
router.patch('/:id/status', auth, async (req, res) => {
  try {
    if (req.user.role !== 'CO') {
      return res.status(403).json({ message: 'Access denied' })
    }

    const { status } = req.body // 'APPROVED' or 'REJECTED'
    
    if (!['APPROVED', 'REJECTED'].includes(status)) {
      return res.status(400).json({ message: 'Invalid status' })
    }

    const battalion = await Battalion.findById(req.params.id)
    if (!battalion) {
      return res.status(404).json({ message: 'Battalion not found' })
    }

    battalion.status = status
    battalion.approvedBy = req.user.userId
    battalion.approvedAt = new Date()

    await battalion.save()
    await battalion.populate('requestedBy', 'fullName username')
    await battalion.populate('approvedBy', 'fullName username')

    res.json(battalion)
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

// Delete battalion (CO only)
router.delete('/:id', auth, async (req, res) => {
  try {
    if (req.user.role !== 'CO') {
      return res.status(403).json({ message: 'Access denied' })
    }

    const battalion = await Battalion.findById(req.params.id)
    if (!battalion) {
      return res.status(404).json({ message: 'Battalion not found' })
    }

    await Battalion.findByIdAndDelete(req.params.id)
    res.json({ message: 'Battalion deleted successfully' })
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

module.exports = router