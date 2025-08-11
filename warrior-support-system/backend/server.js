const express = require('express')
const mongoose = require('mongoose')
const cors = require('cors')
require('dotenv').config()

const app = express()

// Middleware
app.use(cors())
app.use(express.json({ limit: '10mb' }))
app.use(express.urlencoded({ extended: true, limit: '10mb' }))

// Routes
app.use('/api/auth', require('./routes/auth'))
app.use('/api/battalion', require('./routes/battalion'))
app.use('/api/personnel', require('./routes/personnel'))
app.use('/api/examination', require('./routes/examination'))
app.use('/api/evaluation', require('./routes/evaluation'))
app.use('/api/csv', require('./routes/csv'))
app.use('/api/questions', require('./routes/questions')) 
app.use('/api/severePersonnel', require('./routes/severePersonnel'))

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  })
})

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err)
  
  if (err.code === 11000) {
    // Duplicate key error
    const field = Object.keys(err.keyPattern)[0]
    return res.status(400).json({ 
      message: `${field} already exists. Please use a different value.` 
    })
  }
  
  if (err.name === 'ValidationError') {
    const errors = Object.values(err.errors).map(e => e.message)
    return res.status(400).json({ 
      message: 'Validation Error', 
      errors 
    })
  }
  
  if (err.name === 'CastError') {
    return res.status(400).json({ 
      message: 'Invalid ID format' 
    })
  }
  
  res.status(500).json({ 
    message: 'Internal Server Error',
    error: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  })
})

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ message: 'Route not found' })
})

// MongoDB connection with better error handling
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/warrior-support-system', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => {
  console.log('✅ MongoDB connected successfully')
  console.log(`📊 Database: ${mongoose.connection.name}`)
})
.catch(err => {
  console.error('❌ MongoDB connection error:', err)
  process.exit(1)
})

// Handle MongoDB connection events
mongoose.connection.on('error', (err) => {
  console.error('MongoDB connection error:', err)
})

mongoose.connection.on('disconnected', () => {
  console.log('MongoDB disconnected')
})

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Shutting down gracefully...')
  await mongoose.connection.close()
  console.log('✅ MongoDB connection closed')
  process.exit(0)
})

const PORT = process.env.PORT || 5000
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`)
  console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`)
  console.log(`📡 Health check: http://localhost:${PORT}/api/health`)
})