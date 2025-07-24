const mongoose = require('mongoose')

const examinationSchema = new mongoose.Schema({
  armyNo: {
    type: String,
    required: true,
    trim: true,
    uppercase: true
  },
  answers: [{
    questionId: {
      type: String,
      required: true
    },
    answer: {
      type: String,
      required: true
    }
  }],
  completedAt: {
    type: Date,
    default: Date.now
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
})

// Update the updatedAt field before saving
examinationSchema.pre('save', function(next) {
  this.updatedAt = new Date()
  next()
})

// Index for faster queries
examinationSchema.index({ armyNo: 1 })
examinationSchema.index({ completedAt: -1 })

module.exports = mongoose.model('Examination', examinationSchema)