const express = require('express')
const Personnel = require('../models/Personnel')
const auth = require('../middleware/auth')
const User = require('../models/User') // Import User model

const router = express.Router()

// Get personnel by battalion (CO sees all, JSO sees only his battalion)
router.get('/battalion/:battalionId', auth, async (req, res) => {
  try {
    const { battalionId } = req.params

    // Role-based access control
    if (req.user.role === 'USER') {
      //console.log("Error in retreinveing")
      return res.status(403).json({ message: 'Access denied' })
    }

    if (req.user.role === 'JSO') {
      // JSO can only see personnel from their battalion
      const user = await User.findOne({ armyNo: req.user.armyNo })
      if (user.battalion.toString() !== battalionId) {
        return res.status(403).json({ message: 'Access denied to this battalion' })
      }
    }

    const personnel = await Personnel.find({ battalion: battalionId })
      .populate('battalion', 'name')
      .sort({ createdAt: -1 })

    res.json(personnel)
  } catch (error) {
    console.log("Error: ", error)
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

// Get personnel by army number
router.get('/army-no/:armyNo', auth, async (req, res) => {
  try {
    const { armyNo } = req.params
    
    const personnel = await Personnel.findOne({ armyNo })
      .populate('battalion', 'name')

    if (!personnel) {
      return res.status(404).json({ message: 'Personnel not found' })
    }

    // Role-based access control
    // if (req.user.role === 'USER' && personnel.armyNo !== req.user.armyNo) {
    //   return res.status(403).json({ message: 'Access denied' })
    // }

    if (req.user.role === 'JSO') {
      const user = await User.findById(req.user.userId)
      if (personnel.battalion._id.toString() !== user.battalion.toString()) {
        return res.status(403).json({ message: 'Access denied' })
      }
    }

    res.json(personnel)
  } catch (error) {
    res.status(500).json({ message: '1 Server error', error: error.message })
  }
})

// Create personnel (CO and JSO only)
router.post('/', auth, async (req, res) => {
  try {
    if (req.user.role === 'USER') {
      console.log("Here Wrong")
      return res.status(403).json({ message: 'Access denied' })
    }

    const personnelData = req.body

    // JSO can only add personnel to their battalion
    if (req.user.role === 'JSO') {
  
      const user = await User.findOne({ armyNo: req.user.armyNo }) 
      personnelData.battalion = user.battalion
    }

    const personnel = new Personnel(personnelData)
    await personnel.save()

    await personnel.populate('battalion', 'name')
    res.status(201).json(personnel)
  } catch (error) {

    console.log('Error 2 continue', error)
    res.status(500).json({ message: '2 Server error', error: error.message })
  }
})

// Update personnel (CO and JSO only)
router.put('/:id', auth, async (req, res) => {
  try {
    if (req.user.role === 'USER') {
      return res.status(403).json({ message: 'Access denied' })
    }

    const personnel = await Personnel.findById(req.params.id)
    if (!personnel) {
      return res.status(404).json({ message: 'Personnel not found' })
    }

    // JSO can only update personnel from their battalion
    if (req.user.role === 'JSO') {
      const user = await User.findById(req.user.userId)
      if (personnel.battalion.toString() !== user.battalion.toString()) {
        return res.status(403).json({ message: 'Access denied' })
      }
    }

    const updatedPersonnel = await Personnel.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true }
    ).populate('battalion', 'name')

    res.json(updatedPersonnel)
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

// Delete personnel (CO and JSO only)
router.delete('/:id', auth, async (req, res) => {
  try {
    if (req.user.role === 'USER') {
      return res.status(403).json({ message: 'Access denied' })
    }

    const personnel = await Personnel.findById(req.params.id)
    if (!personnel) {
      return res.status(404).json({ message: 'Personnel not found' })
    }

    // JSO can only delete personnel from their battalion
    if (req.user.role === 'JSO') {
      const user = await User.findById(req.user.userId)
      if (personnel.battalion.toString() !== user.battalion.toString()) {
        return res.status(403).json({ message: 'Access denied' })
      }
    }

    await Personnel.findByIdAndDelete(req.params.id)
    res.json({ message: 'Personnel deleted successfully' })
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

// Delete all personnel from battalion (CO and JSO only)
router.delete('/battalion/:battalionId', auth, async (req, res) => {
  try {
    if (req.user.role === 'USER') {
      return res.status(403).json({ message: 'Access denied' })
    }

    const { battalionId } = req.params

    // JSO can only delete from their battalion
    if (req.user.role === 'JSO') {
      const user = await User.findById(req.user.userId)
      if (user.battalion.toString() !== battalionId) {
        return res.status(403).json({ message: 'Access denied' })
      }
    }

    await Personnel.deleteMany({ battalion: battalionId })
    res.json({ message: 'All personnel deleted successfully' })
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

module.exports = router