const mongoose = require('mongoose')


const reExamPeriodSchema = new mongoose.Schema({
  period: {
    type: Number,
    required: true,
  },
  setDate: {
    type: Date,
    default: Date.now,
  },
});



module.exports =  mongoose.model("ReExamPeriod", reExamPeriodSchema)
