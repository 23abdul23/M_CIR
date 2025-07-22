import express from 'express'
import Battalion from '../models/Battalion.js'
import auth from '../middleware/auth.js'

const router = express.Router()

// Get all battalions
router.get('/', auth, async (req, res) => {
  try {
    const battalions = await Battalion.find().populate('createdBy', 'username')
    res.json(battalions)
  } catch (error) {
    res.status(500).json({ message: 'Server error' })
  }
})

// Create new battalion
router.post('/', auth, async (req, res) => {
  try {
    const battalion = new Battalion({
      ...req.body,
      createdBy: req.user.userId
    })
    await battalion.save()
    res.status(201).json(battalion)
  } catch (error) {
    if (error.code === 11000) {
      res.status(400).json({ message: 'Battalion name already exists' })
    } else {
      res.status(500).json({ message: 'Server error' })
    }
  }
})

// Delete battalion
router.delete('/:id', auth, async (req, res) => {
  try {
    const battalion = await Battalion.findByIdAndDelete(req.params.id)
    
    if (!battalion) {
      return res.status(404).json({ message: 'Battalion not found' })
    }
    
    res.json({ message: 'Battalion deleted successfully' })
  } catch (error) {
    res.status(500).json({ message: 'Server error' })
  }
})

export default router