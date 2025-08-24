const express = require("express");
const Interview = require("../models/Interview")

const router = express.Router();

router.post("/setInterview", async (req, res) => {
    try {
        const { interviewDate, armyNo } = req.body;
        console.log(armyNo, interviewDate);

        let existingInterview = await Interview.findOne({ armyNo: armyNo });

        if (existingInterview) {
            if (existingInterview.interviewDate === interviewDate) {
                console.log("Same Date for Interview is Set");
                return res.status(400).json({ message: "Same Date for Interview is Set" });
            }
            existingInterview.interviewDate = interviewDate;
            await existingInterview.save();
            return res.status(200).json({ message: "Interview date updated" });
        } else {
            const interviewPersonnel = new Interview({
                interviewDate: interviewDate,
                armyNo: armyNo
            });
            await interviewPersonnel.save();
            return res.status(200).json({ message: "Successfully set interview" });
        }
    } catch (error) {
        console.log(error);
        res.status(500).json({ message: "Server error" });
    }
});

router.get("/getInterview", async (req,res) => {
    try{
        const existingInterviews = await Interview.find({})
        res.status(200).json(existingInterviews)
    }

    catch(error){
        console.log(error)
        res.status(500)
    }
})


module.exports = router