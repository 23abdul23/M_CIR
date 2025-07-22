import mongoose from 'mongoose'

const examinationSchema = new mongoose.Schema({
  armyNo: {
    type: String,
    required: true
  },
  answers: {
    type: Map,
    of: String,
    required: true
  },
  completedAt: {
    type: Date,
    required: true
  },
  submittedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
})

export default mongoose.model('Examination', examinationSchema)