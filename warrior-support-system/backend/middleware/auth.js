const jwt = require('jsonwebtoken')
const User = require('../models/User')

const auth = async (req, res, next) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '')
    
    if (!token) {
      return res.status(401).json({ message: 'No token, authorization denied' })
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    
    // Get user with role information
    const user = await User.findById(decoded.userId).select('-password')
    if (!user || !user.isActive) {
      return res.status(401).json({ message: 'Token is not valid' })
    }

    req.user = {
      userId: user._id,
      role: user.role,
      armyNo: user.armyNo,
      battalion: user.battalion
    }
    
    next()
  } catch (error) {
    res.status(401).json({ message: 'Token is not valid' })
  }
}

// Role-based middleware
const requireRole = (roles) => {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ message: 'Access denied' })
    }
    next()
  }
}

module.exports = auth
module.exports.requireRole = requireRole