
const express = require("express")
const mongoose = require("mongoose")
const SeverePersonnel = require("../models/SeverePersonnel")
const Personnel = require("../models/Personnel")
const Examination = require("../models/Examination")
const Battalion = require("../models/Battalion")

const auth = require("../middleware/auth")
const router = express.Router()


router.get('/all',auth, async (req, res) => {
  try {
    const { battalionName } = req.query;

    const allBattalions = await Battalion.find({'name' : battalionName});
    const allBattalionIds = allBattalions.map(b => b._id)

    const severePersonnel = await SeverePersonnel.find({
      battalion: { $in: allBattalionIds }
    });

    return res.status(200).json({ data: severePersonnel });

  } catch (error) {
    console.log("Error", error);
    res.status(500).json({ error: "Error fetching personnel" });
  }
})

router.get('/:id',auth, async (req, res) => {
  try {
    console.log(req)
    console.log(req.user)
    // If user is CO, return all severe personnel
    if (req.user && req.user.role === 'CO') {
      const severePersonnel = await SeverePersonnel.find({});
      return res.status(200).json({ data: severePersonnel });
    }
    // Otherwise, filter by battalion
    const id = req.params.id;
    const severePersonnel = await SeverePersonnel.find({ battalion: new mongoose.Types.ObjectId(id) });
    res.status(200).json({ data: severePersonnel });
  } catch (error) {
    console.log("Error", error);
    res.status(500).json({ error: "Error fetching personnel" });
  }
})

// Post examinations for personnel with selfEvaluation COMPLETED
router.post('/all', auth, async (req, res) => {
  try {
    const personnel = await Personnel.find({ selfEvaluation: "COMPLETED"});
    // console.log(personnel)
    const armyNos = personnel.map(p => p.armyNo);
    // Find examinations for those army numbers
    const examinations = await Examination.find({ armyNo: { $in: armyNos } });

    // Combine data by armyNo
    const examMap = {};
    examinations.forEach(exam => {
      if (!examMap[exam.armyNo]) examMap[exam.armyNo] = [];
      examMap[exam.armyNo].push(exam);
    });

    const combined = personnel.map(p => ({
      ...p.toObject(),
      examinations: examMap[p.armyNo] || []
    }));

    // Filter for severe/extremely severe cases
    const severeLevels = ['Severe', 'Extremely Severe'];
    const severePersonnels = combined
      .map(person => {
        if (person.selfEvaluation !== 'COMPLETED') return null;
        // Sort all exams by completedAt descending to get the latest
        const sortedExams = [...(person.examinations || [])].sort((a, b) => new Date(b.completedAt) - new Date(a.completedAt));
        const latestExam = sortedExams[0];
        if (!latestExam || !latestExam.dassScores) return null;
        const isSevere = (scores) => {
          if (!scores) return false;
          return (
            severeLevels.includes(scores.anxietySeverity) ||
            severeLevels.includes(scores.depressionSeverity) ||
            severeLevels.includes(scores.stressSeverity)
          );
        };
        if (isSevere(latestExam.dassScores)) {
          // Overwrite dassScores with the latest
          return { ...person, dassScores: latestExam.dassScores };
        }
        return null;
      })
      .filter(Boolean);

    await SeverePersonnel.deleteMany({});

    const savedDocs = await SeverePersonnel.insertMany(severePersonnels, { ordered: false });

    res.status(200).json({ data: severePersonnels });
  } catch (error) {
    console.error("Error fetching completed examinations:", error);
    res.status(500).json({ error: "Error fetching completed examinations" });
  }
});

router.post("/done/:armyNo", auth, async (req, res) => {
  try {
    const armyNo = req.params.armyNo;

    const result = await SeverePersonnel.deleteOne({ armyNo });
    if (result.deletedCount === 0) {
      return res.status(404).json({ message: "No personnel found with this army number" });
    }

    res.status(200).json({message : "Interview is Done"})
  }
  catch (error){
    console.log("Error", error)
    res.status(500)
  }
})



module.exports = router
