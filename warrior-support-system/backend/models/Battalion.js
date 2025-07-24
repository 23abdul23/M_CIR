const mongoose = require('mongoose')

const battalionSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true
  },
  postedStr: {
    type: String
  },
  status: {
    type: String,
    enum: ['PENDING', 'APPROVED', 'REJECTED'],
    default: 'PENDING'
  },
  requestedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  approvedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  approvedAt: {
    type: Date
  }
})

module.exports = mongoose.model('Battalion', battalionSchema)