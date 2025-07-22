import express from 'express'
import Personnel from '../models/Personnel.js'
import auth from '../middleware/auth.js'

const router = express.Router()

// Get all personnel for a battalion
router.get('/battalion/:battalionId', auth, async (req, res) => {
  try {
    const personnel = await Personnel.find({ battalion: req.params.battalionId })
      .populate('battalion', 'name')
    res.json(personnel)
  } catch (error) {
    res.status(500).json({ message: 'Server error' })
  }
})

// Get personnel by army number
router.get('/army-no/:armyNo', auth, async (req, res) => {
  try {
    const personnel = await Personnel.findOne({ armyNo: req.params.armyNo })
      .populate('battalion', 'name')
    
    if (!personnel) {
      return res.status(404).json({ message: 'Personnel not found' })
    }
    
    res.json(personnel)
  } catch (error) {
    res.status(500).json({ message: 'Server error' })
  }
})

// Add new personnel
router.post('/', auth, async (req, res) => {
  try {
    const personnel = new Personnel(req.body)
    await personnel.save()
    res.status(201).json(personnel)
  } catch (error) {
    if (error.code === 11000) {
      res.status(400).json({ message: 'Army number already exists' })
    } else {
      res.status(500).json({ message: 'Server error' })
    }
  }
})

// Update personnel
router.put('/:id', auth, async (req, res) => {
  try {
    const personnel = await Personnel.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true }
    )
    
    if (!personnel) {
      return res.status(404).json({ message: 'Personnel not found' })
    }
    
    res.json(personnel)
  } catch (error) {
    res.status(500).json({ message: 'Server error' })
  }
})

// Delete personnel
router.delete('/:id', auth, async (req, res) => {
  try {
    const personnel = await Personnel.findByIdAndDelete(req.params.id)
    
    if (!personnel) {
      return res.status(404).json({ message: 'Personnel not found' })
    }
    
    res.json({ message: 'Personnel deleted successfully' })
  } catch (error) {
    res.status(500).json({ message: 'Server error' })
  }
})

// Delete all personnel for a battalion
router.delete('/battalion/:battalionId', auth, async (req, res) => {
  try {
    await Personnel.deleteMany({ battalion: req.params.battalionId })
    res.json({ message: 'All personnel deleted successfully' })
  } catch (error) {
    res.status(500).json({ message: 'Server error' })
  }
})

export default router