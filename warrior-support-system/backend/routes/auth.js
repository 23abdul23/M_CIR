const express = require('express')
const jwt = require('jsonwebtoken')
const User = require('../models/User')
const Battalion = require('../models/Battalion')
const auth = require('../middleware/auth')

const router = express.Router()

// Register

router.post('/register', async (req, res) => {
  try {
    const {
      username,
      password,
      fullName,
      role = 'USER',
      armyNo,
      rank,
      battalionId
    } = req.body

    // Check if user with same army number exists
    if (armyNo) {
      const existingUser = await User.findOne({ armyNo: armyNo.toUpperCase() })
      if (existingUser) {
        return res.status(400).json({ message: 'User with this Army Number already exists' })
      }
    }

    // Validate required fields
    if (!username || !password || !fullName) {
      return res.status(400).json({ message: 'Username, password and full name are required' })
    }

    if ((role === 'JCO' || role === 'USER') && !armyNo) {
      return res.status(400).json({ message: 'Army Number is required for JSO and USER roles' })
    }

    const newUser = new User({
      username: username.trim(),
      password,
      fullName: fullName.trim(),
      role,
      armyNo: armyNo ? armyNo.toUpperCase() : undefined,
      rank: rank ? rank.toUpperCase() : undefined,
      battalion: battalionId || undefined
    })

    await newUser.save()

    // Generate JWT token
    const token = jwt.sign(
      { userId: newUser._id, role: newUser.role },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    )

    res.status(201).json({
      token,
      user: newUser // thanks to the toJSON() method, password is excluded
    })

  } catch (error) {
    console.error('Registration error:', error)
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

// Login
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body

    const user = await User.findOne({ username }).populate('battalion')
    if (!user) {
      return res.status(400).json({ message: 'Invalid credentials' })
    }

    const isMatch = await user.comparePassword(password)
    if (!isMatch) {
      return res.status(400).json({ message: 'Invalid credentials' })
    }

    if (!user.isActive) {
      return res.status(400).json({ message: 'Account is deactivated' })
    }

    const token = jwt.sign(
      { userId: user._id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    )

    res.json({
      token,
      user: {
        id: user._id,
        username: user.username,
        fullName: user.fullName,
        role: user.role,
        armyNo: user.armyNo,
        rank: user.rank,
        battalion: user.battalion
      }
    })
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

// Get current user
router.get('/me', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.userId)
      .select('-password')
      .populate('battalion')
    
    res.json(user)
  } catch (error) {
    res.status(500).json({ message: 'Server error' })
  }
})

module.exports = router