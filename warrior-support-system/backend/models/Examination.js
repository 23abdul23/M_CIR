const mongoose = require("mongoose")

const examinationSchema = new mongoose.Schema({
  armyNo: {
    type: String,
    required: true,
  },
  answers: [
    {
      questionId: {
        type: String,
        required: true,
      },
      answer: {
        type: mongoose.Schema.Types.Mixed,
        required: true,
      },
    },
  ],
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
  // examAI_taken: {
  //   type : Boolean,
  //   default : False
  // },
  // examManual_taken: {
  //   type : Boolean,
  //   default : False
  // },
  completedAt: {
    type: Date,
    default: Date.now,
  },
  battalion: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "Battalion",
  }
})

// Index for efficient queries
examinationSchema.index({ completedAt: -1 })
examinationSchema.index({ armyNo: 1 })
examinationSchema.index({ battalion: 1 })

module.exports = mongoose.model("Examination", examinationSchema)
