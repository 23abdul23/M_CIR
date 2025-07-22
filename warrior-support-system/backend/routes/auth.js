import express from 'express'
import jwt from 'jsonwebtoken'
import User from '../models/User.js'
import auth from '../middleware/auth.js'

const router = express.Router()

// Register new user
router.post('/register', async (req, res) => {
  try {
    const { username, password, fullName, email, role, rank, unit } = req.body

    // Validation
    if (!username || !password || !fullName || !email || !rank || !unit) {
      return res.status(400).json({ message: 'All fields are required' })
    }

    if (password.length < 6) {
      return res.status(400).json({ message: 'Password must be at least 6 characters long' })
    }

    // Check if user already exists
    const existingUser = await User.findOne({
      $or: [{ username }, { email }]
    })

    if (existingUser) {
      if (existingUser.username === username) {
        return res.status(400).json({ message: 'Username already exists' })
      }
      if (existingUser.email === email) {
        return res.status(400).json({ message: 'Email already exists' })
      }
    }

    // Create new user
    const user = new User({
      username,
      password,
      fullName,
      email,
      role: role || 'user',
      rank,
      unit
    })

    await user.save()

    res.status(201).json({ 
      message: 'User registered successfully',
      user: {
        id: user._id,
        username: user.username,
        fullName: user.fullName,
        email: user.email,
        role: user.role,
        rank: user.rank,
        unit: user.unit
      }
    })
  } catch (error) {
    console.error('Registration error:', error)
    
    if (error.name === 'ValidationError') {
      const messages = Object.values(error.errors).map(err => err.message)
      return res.status(400).json({ message: messages.join(', ') })
    }
    
    res.status(500).json({ message: 'Server error during registration' })
  }
})

// Login user
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body

    if (!username || !password) {
      return res.status(400).json({ message: 'Username and password are required' })
    }

    // Check if user exists
    const user = await User.findOne({ username })
    if (!user) {
      return res.status(401).json({ message: 'Invalid credentials' })
    }

    // Check if user is active
    if (!user.isActive) {
      return res.status(401).json({ message: 'Account is deactivated' })
    }

    // Check password
    const isPasswordValid = await user.comparePassword(password)
    if (!isPasswordValid) {
      return res.status(401).json({ message: 'Invalid credentials' })
    }

    // Update last login
    user.lastLogin = new Date()
    await user.save()

    // Generate JWT token
    const token = jwt.sign(
      { 
        userId: user._id, 
        username: user.username, 
        role: user.role,
        fullName: user.fullName
      },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    )

    res.json({
      token,
      user: {
        id: user._id,
        username: user.username,
        fullName: user.fullName,
        email: user.email,
        role: user.role,
        rank: user.rank,
        unit: user.unit,
        lastLogin: user.lastLogin
      }
    })
  } catch (error) {
    console.error('Login error:', error)
    res.status(500).json({ message: 'Server error during login' })
  }
})

// Get current user profile
router.get('/profile', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.userId)
    if (!user) {
      return res.status(404).json({ message: 'User not found' })
    }
    res.json(user)
  } catch (error) {
    console.error('Profile fetch error:', error)
    res.status(500).json({ message: 'Server error' })
  }
})

// Update user profile
router.put('/profile', auth, async (req, res) => {
  try {
    const { fullName, email, rank, unit } = req.body
    
    const user = await User.findById(req.user.userId)
    if (!user) {
      return res.status(404).json({ message: 'User not found' })
    }

    // Update fields
    if (fullName) user.fullName = fullName
    if (email) user.email = email
    if (rank) user.rank = rank
    if (unit) user.unit = unit

    await user.save()
    res.json(user)
  } catch (error) {
    console.error('Profile update error:', error)
    
    if (error.code === 11000) {
      return res.status(400).json({ message: 'Email already exists' })
    }
    
    res.status(500).json({ message: 'Server error' })
  }
})

// Change password
router.put('/change-password', auth, async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body

    if (!currentPassword || !newPassword) {
      return res.status(400).json({ message: 'Current password and new password are required' })
    }

    if (newPassword.length < 6) {
      return res.status(400).json({ message: 'New password must be at least 6 characters long' })
    }

    const user = await User.findById(req.user.userId)
    if (!user) {
      return res.status(404).json({ message: 'User not found' })
    }

    // Verify current password
    const isCurrentPasswordValid = await user.comparePassword(currentPassword)
    if (!isCurrentPasswordValid) {
      return res.status(400).json({ message: 'Current password is incorrect' })
    }

    // Update password
    user.password = newPassword
    await user.save()

    res.json({ message: 'Password changed successfully' })
  } catch (error) {
    console.error('Password change error:', error)
    res.status(500).json({ message: 'Server error' })
  }
})

// Get all users (admin only)
router.get('/users', auth, async (req, res) => {
  try {
    // Check if user is admin
    if (req.user.role !== 'admin') {
      return res.status(403).json({ message: 'Access denied. Admin only.' })
    }

    const users = await User.find({})
      .select('-password')
      .sort({ createdAt: -1 })

    res.json(users)
  } catch (error) {
    console.error('Users fetch error:', error)
    res.status(500).json({ message: 'Server error' })
  }
})

// Toggle user active status (admin only)
router.put('/users/:id/toggle-status', auth, async (req, res) => {
  try {
    // Check if user is admin
    if (req.user.role !== 'admin') {
      return res.status(403).json({ message: 'Access denied. Admin only.' })
    }

    const user = await User.findById(req.params.id)
    if (!user) {
      return res.status(404).json({ message: 'User not found' })
    }

    user.isActive = !user.isActive
    await user.save()

    res.json({ 
      message: `User ${user.isActive ? 'activated' : 'deactivated'} successfully`,
      user 
    })
  } catch (error) {
    console.error('User status toggle error:', error)
    res.status(500).json({ message: 'Server error' })
  }
})

export default router