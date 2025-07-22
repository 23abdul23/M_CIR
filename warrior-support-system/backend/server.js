import express from 'express'
import mongoose from 'mongoose'
import cors from 'cors'
import dotenv from 'dotenv'

import authRoutes from './routes/auth.js'
import battalionRoutes from './routes/battalion.js'
import personnelRoutes from './routes/personnel.js'
import examinationRoutes from './routes/examination.js'

dotenv.config()

const app = express()
const PORT = process.env.PORT || 5000

// Middleware
app.use(cors())
app.use(express.json())

// Database connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/warrior-support', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})

mongoose.connection.on('connected', () => {
  console.log('Connected to MongoDB')
})

mongoose.connection.on('error', (err) => {
  console.log('MongoDB connection error:', err)
})

// Routes
app.use('/api/auth', authRoutes)
app.use('/api/battalion', battalionRoutes)
app.use('/api/personnel', personnelRoutes)
app.use('/api/examination', examinationRoutes)

app.get('/', (req, res) => {
  res.json({ message: 'Warrior Support System API' })
})

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})