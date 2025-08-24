const express = require("express");
const Interview = require("../models/Interview")

const router = express.Router();


router.post("/setInterview", async (req, res) => {
    const {interviewDate, armyNo} = req.body;
    console.log(armyNo, interviewDate)

    const interviewPersonnel = new Interview({
        interviewDate : interviewDate,
        armyNo : armyNo
    })

    await interviewPersonnel.save()

})


module.exports = router