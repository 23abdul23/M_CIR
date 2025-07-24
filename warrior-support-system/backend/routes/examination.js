const express = require('express')
const Examination = require('../models/Examination')
const auth = require('../middleware/auth')

const router = express.Router()

// Submit examination
router.post('/', auth, async (req, res) => {
  try {
    const examination = new Examination({
      ...req.body,
      submittedBy: req.user.userId
    })
    await examination.save()
    res.status(201).json(examination)
  } catch (error) {
    res.status(500).json({ message: 'Server error' })
  }
})

// Get examination by army number
router.get('/army-no/:armyNo', auth, async (req, res) => {
  try {
    const examination = await Examination.findOne({ armyNo: req.params.armyNo })
    res.json(examination)
  } catch (error) {
    res.status(500).json({ message: 'Server error' })
  }
})

module.exports = router