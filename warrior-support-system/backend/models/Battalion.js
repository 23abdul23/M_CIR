const mongoose = require('mongoose')

const battalionSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  postedStr: {
    type: String,
    required: true,
    unique: true
  },
  status: {
    type: String,
    enum: ['PENDING', 'APPROVED', 'REJECTED'],
    default: 'APPROVED'
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  approvedAt: {
    type: Date,
    default: Date.now
  }
})

module.exports = mongoose.model('Battalion', battalionSchema)