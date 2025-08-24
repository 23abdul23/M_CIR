const { trim } = require('lodash')
const mongoose = require('mongoose')

const battalionSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim : true
  },
  postedStr: {
    type: String, 
    required: true,
    trim : true,
    uppercase: true
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