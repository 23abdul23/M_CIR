const mongoose = require('mongoose')

const questionSchema = new mongoose.Schema({
  questionId: {
    type: Number,
    required: true,
    unique: true
  },
  questionText: {
    type: String,
    required: true,
    trim: true
  },
  questionType: {
    type: String,
    enum: ['MCQ', 'TEXT'],
    required: true
  },
  options: [{
    optionId: {
      type: String,
      required: function() { return this.questionType === 'MCQ' }
    },
    optionText: {
      type: String,
      required: function() { return this.questionType === 'MCQ' }
    }
  }],
  isActive: {
    type: Boolean,
    default: true
  },
  order: {
    type: Number,
    required: true
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
questionSchema.pre('save', function(next) {
  this.updatedAt = new Date()
  next()
})

// Index for faster queries
questionSchema.index({ order: 1 })
questionSchema.index({ isActive: 1 })
questionSchema.index({ questionId: 1 })

module.exports = mongoose.model('QuestionPeer', questionSchema)