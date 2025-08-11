const mongoose = require('mongoose')

const severePersonnelSchema = new mongoose.Schema({
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
  dassScores: {
    depression: {
      type: Number,
      default: 0,
    },
    depressionSeverity: {
      type: String,
      enum: ["Normal", "Mild", "Moderate", "Severe", "Extremely Severe"],
      default: "Normal",
    },
    anxiety: {
      type: Number,
      default: 0,
    },
    anxietySeverity: {
      type: String,
      enum: ["Normal", "Mild", "Moderate", "Severe", "Extremely Severe"],
      default: "Normal",
    },
    stress: {
      type: Number,
      default: 0,
    },
    stressSeverity: {
      type: String,
      enum: ["Normal", "Mild", "Moderate", "Severe", "Extremely Severe"],
      default: "Normal",
    },
  },
  mode: {
    type: String,
    enum: ['AI', 'MANUAL'],
    default: 'MANUAL',
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
  updatedAt: {
    type: Date,
    default: Date.now
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
})

module.exports = mongoose.model('SeverePersonnel', severePersonnelSchema)