import mongoose from 'mongoose'

const battalionSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true
  },
  postedStr: {
    type: String,
    required: false
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  }
})

export default mongoose.model('Battalion', battalionSchema)