const mongoose = require('mongoose')

const personnelSchema = new mongoose.Schema({
  armyNo: {
    type: String,
    required: true,
    unique: true
  },
  rank: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  subBty: {
    type: String,
    required: true
  },
  service: {
    type: String,
    required: true
  },
  dateOfInduction: {
    type: Date,
    required: true
  },
  medCat: {
    type: String,
    required: true
  },
  leaveAvailed: {
    type: String
  },
  maritalStatus: {
    type: String,
    enum: ['MARRIED', 'UNMARRIED'],
    required: true
  },
  selfEvaluation: {
    type: String,
    enum: ['NOT_ATTEMPTED', 'COMPLETED'],
    default: 'NOT_ATTEMPTED'
  },
  peerEvaluation: {
    status: {
      type: String,
      enum: ['PENDING', 'EVALUATED'],
      default: 'PENDING'
    },
    evaluatedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    evaluatedAt: {
      type: Date
    },
    answers: [{
      questionId: String,
      answer: String
    }],
    evaluation: {
      answer: String
    },
    finalScore: {
      type: Number,
      min: 0,
      max: 100,
      default: 0
    }

  },
  battalion: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Battalion',
    required: true,
    default: () => new mongoose.Types.ObjectId()
  },
  addedBattalion : {
    type: String,
    default: "",
    required: function () {
    return !this.battalion; // only required if no battalion selected
  }
  },
  status : {
    type: String,
    enum: ['PENDING', 'APPROVED', 'REJECTED'],
    default: 'PENDING'
  },
  interviewTaken : {
    type: Boolean,
    default : false
  },
  updatedAt: {
    type: Date,
    default: Date.now
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
})

module.exports = mongoose.model('Personnel', personnelSchema)