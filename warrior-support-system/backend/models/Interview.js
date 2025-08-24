const mongoose = require('mongoose')

const InterviewSchema = new mongoose.Schema({
    armyNo : {
        type : String,
        required : true
    },
    interviewDate : {
        type : Date,
        required : true
    },
    interviewScheduleDate : {
        type : Date,
        required : true,
        default : Date.now()
    }
})


module.exports = mongoose.model('Interview', InterviewSchema)