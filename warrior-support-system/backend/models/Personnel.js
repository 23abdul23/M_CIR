import mongoose from 'mongoose'

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
  coySquadronBty: {
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
    type: String,
    required: true
  },
  maritalStatus: {
    type: String,
    enum: ['MARRIED', 'UNMARRIED'],
    required: true
  },
  selfEvaluation: {
    type: String,
    required: false
  },
  battalion: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Battalion',
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
})

export default mongoose.model('Personnel', personnelSchema)