const express = require("express")
const Examination = require("../models/Examination")
const Personnel = require("../models/Personnel")
const User = require("../models/User")
const auth = require("../middleware/auth")
const ReExamPeriod= require("../models/ReExam")

const router = express.Router()

// Submit examination
router.post("/submit/:examsGiven", auth, async (req, res) => {
  try {
    const examModes = req.params.examsGiven
    const { armyNo, answers, dassScores } = req.body

    console.log(examModes)
    
    // Get personnel details to associate battalion
    const personnel = await Personnel.findOne({ armyNo }).populate("battalion")
    if (!personnel) {
      return res.status(404).json({ message: "Personnel not found" })
    }

    console.log(req.body)

    // Create new examination
    const examination = new Examination({
      ...req.body,
      battalion: personnel.battalion._id,
    })

    await examination.save()


    if (examModes == 2){
      await Personnel.findOneAndUpdate(
        { armyNo },
        {
          selfEvaluation: "COMPLETED",
          updatedAt: new Date(),
          peerEvaluation: {
            status: 'PENDING',
            finalScore: 0,
            answers: []
          }
        }
      );
    }
    else{
    await Personnel.findOneAndUpdate({ armyNo }, { selfEvaluation: "COMPLETED", updatedAt : new Date()})
    }

    
    res.status(201).json({
      message: "Examination submitted successfully",
      examination: {
        armyNo: examination.armyNo,
        dassScores: examination.dassScores,
        completedAt: examination.completedAt,
      },
    })
  } 
  
  catch (error) {
    console.error("Error submitting examination:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Get examination by army number
router.get("/all/army-no/:armyNo", auth, async (req, res) => {
  try {
    const { armyNo } = req.params

    const examination = await Examination.find({ armyNo })
  .populate("battalion", "name")
  .sort({ completedAt: -1 });

    if (!examination) {
      return res.status(404).json({ message: "Examination not found" })
    }

    // Role-based access control
    if (req.user.role === "USER" && req.user.status === 'PENDING') {
      console.log("Form here")
      return res.status(400).json({'message': "Your application is pending approval by the CO.", examination})
    }

    // JSO can only see examinations from their battalion
    if (req.user.role === "JCO") {
      const user = await User.find({ armyNo: req.user.armyNo })
      if (examination.battalion._id.toString() !== user.battalion.toString()) {
        return res.status(403).json({ message: "Access denied" })
      }
    }

    res.json(examination)
  } catch (error) {
    console.error("Error fetching examination:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Get examination by army number
router.get("/army-no/:armyNo", auth, async (req, res) => {
  try {
    const { armyNo } = req.params

    const examination = await Examination.findOne({ armyNo })
  .populate("battalion", "name")
  .sort({ completedAt: -1 });

    if (!examination) {
      return res.status(404).json({ message: "Examination not found" })
    }

    // Role-based access control
    if (req.user.role === "USER" && req.user.status === 'PENDING') {
      console.log("Form here")
      return res.status(400).json({'message': "Your application is pending approval by the CO.", examination})
    }

    // JSO can only see examinations from their battalion
    if (req.user.role === "JCO") {
      const user = await User.findOne({ armyNo: req.user.armyNo })
      if (examination.battalion._id.toString() !== user.battalion.toString()) {
        return res.status(403).json({ message: "Access denied" })
      }
    }

    res.json(examination)
  } catch (error) {
    console.error("Error fetching examination:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Get all examinations by battalion (CO and JSO only)
router.get("/battalion/:battalionId", auth, async (req, res) => {
  try {
    const { battalionId } = req.params

    if (req.user.role === "USER") {
      return res.status(403).json({ message: "Access denied" })
    }

    // JSO can only see examinations from their battalion
    if (req.user.role === "JCO") {
      const user = await User.findOne({ armyNo: req.user.armyNo })
      if (user.battalion.toString() !== battalionId) {
        return res.status(403).json({ message: "Access denied to this battalion" })
      }
    }

    const examinations = await Examination.find({ battalion: battalionId })
      .populate("battalion", "name")
      .sort({ completedAt: -1 })

    res.json(examinations)
  } catch (error) {
    console.error("Error fetching examinations:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Get examination statistics for CO dashboard
router.get("/stats/battalion/:battalionId", auth, async (req, res) => {
  try {
    const { battalionId } = req.params

    if (req.user.role === "USER") {
      return res.status(403).json({ message: "Access denied" })
    }

    // JSO can only see stats from their battalion
    if (req.user.role === "JCO") {
      const user = await User.findOne({ armyNo: req.user.armyNo })
      if (user.battalion.toString() !== battalionId) {
        return res.status(403).json({ message: "Access denied to this battalion" })
      }
    }

    const examinations = await Examination.find({ battalion: battalionId })

    // Calculate statistics
    const stats = {
      totalExaminations: examinations.length,
      depressionStats: {
        normal: 0,
        mild: 0,
        moderate: 0,
        severe: 0,
        extremelySevere: 0,
      },
      anxietyStats: {
        normal: 0,
        mild: 0,
        moderate: 0,
        severe: 0,
        extremelySevere: 0,
      },
      stressStats: {
        normal: 0,
        mild: 0,
        moderate: 0,
        severe: 0,
        extremelySevere: 0,
      },
      averageScores: {
        depression: 0,
        anxiety: 0,
        stress: 0,
      },
    }

    if (examinations.length > 0) {
      let totalDepression = 0
      let totalAnxiety = 0
      let totalStress = 0

      examinations.forEach((exam) => {
        // Count severity levels
        const depSeverity = exam.dassScores.depressionSeverity.toLowerCase().replace(" ", "")
        const anxSeverity = exam.dassScores.anxietySeverity.toLowerCase().replace(" ", "")
        const strSeverity = exam.dassScores.stressSeverity.toLowerCase().replace(" ", "")

        stats.depressionStats[depSeverity === "extremelysevere" ? "extremelySevere" : depSeverity]++
        stats.anxietyStats[anxSeverity === "extremelysevere" ? "extremelySevere" : anxSeverity]++
        stats.stressStats[strSeverity === "extremelysevere" ? "extremelySevere" : strSeverity]++

        // Sum scores for averages
        totalDepression += exam.dassScores.depression
        totalAnxiety += exam.dassScores.anxiety
        totalStress += exam.dassScores.stress
      })

      // Calculate averages
      stats.averageScores.depression = Math.round(totalDepression / examinations.length)
      stats.averageScores.anxiety = Math.round(totalAnxiety / examinations.length)
      stats.averageScores.stress = Math.round(totalStress / examinations.length)
    }

    res.json(stats)
  } catch (error) {
    console.error("Error fetching examination statistics:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Delete examination (CO only)
router.delete("/:id", auth, async (req, res) => {
  try {
    if (req.user.role !== "CO") {
      return res.status(403).json({ message: "Access denied. CO access required." })
    }

    const examination = await Examination.findById(req.params.id)
    if (!examination) {
      return res.status(404).json({ message: "Examination not found" })
    }

    // Update personnel self-evaluation status back to NOT_ATTEMPTED
    await Personnel.findOneAndUpdate({ armyNo: examination.armyNo }, { selfEvaluation: "NOT_ATTEMPTED" })

    await Examination.findByIdAndDelete(req.params.id)
    res.json({ message: "Examination deleted successfully" })
  } catch (error) {
    console.error("Error deleting examination:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Get examination history for a specific army number (CO and JSO only)
router.get("/history/:armyNo", auth, async (req, res) => {
  try {
    const { armyNo } = req.params

    if (req.user.role === "USER") {
      return res.status(403).json({ message: "Access denied" })
    }

    // JSO can only see examinations from their battalion
    if (req.user.role === "JCO") {
      const user = await User.findOne({ armyNo: req.user.armyNo })
      const personnel = await Personnel.findOne({ armyNo }).populate("battalion")
      
      if (!personnel || personnel.battalion._id.toString() !== user.battalion.toString()) {
        return res.status(403).json({ message: "Access denied to this personnel data" })
      }
    }

    const examinations = await Examination.find({ armyNo })
      .populate("battalion", "name")
      .sort({ completedAt: 1 }) // Oldest first for trend analysis

    res.json(examinations)
  } catch (error) {
    console.error("Error fetching examination history:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Get all examinations (CO only)
router.get("/all", auth, async (req, res) => {
  try {
    if (req.user.role !== "CO") {
      return res.status(403).json({ message: "Access denied. CO access required." })
    }

    const examinations = await Examination.find().populate("battalion", "name").sort({ completedAt: -1 })

    res.json(examinations)
  } catch (error) {
    console.error("Error fetching all examinations:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Add a route to fetch the CO's set date for the exam period
router.get("/co-set-date", auth, async (req, res) => {
  try {
    
    // Fetch the CO's set date from the database or configuration
    const coSetDate = await ReExamPeriod.findOne({});

    if (!coSetDate) {
      return res.status(404).json({ message: "CO set date not found." });
    }

    res.json({ setPeriod: coSetDate.period });
  } catch (error) {
    console.error("Error fetching CO set date:", error);
    res.status(500).json({ message: "Server error", error: error.message });
  }
});

// Add a route to set the CO's re-examination period
router.post("/set-reexam-period", auth, async (req, res) => {
  try {
    if (req.user.role !== "CO") {
      return res.status(403).json({ message: "Access denied. CO access required." });
    }

    const { period } = req.body;

    if ( isNaN(period) || period < 0) {
      return res.status(400).json({ message: "Valid period in days is required." });
    }

    // Save or update the re-examination period in the database
    let reExamPeriod = await ReExamPeriod.findOneAndUpdate(
      {},
      { period, setDate: new Date() },
      { new: true, upsert: true }
    );

    res.json({ message: "Re-examination period set successfully.", period: reExamPeriod.period });
  } catch (error) {
    console.error("Error setting re-examination period:", error);
    res.status(500).json({ message: "Server error", error: error.message });
  }
});

// Add a route to request re-examination approval
router.post("/request-reexam", auth, async (req, res) => {
  try {
    const { armyNo } = req.body;

    if (!armyNo) {
      return res.status(400).json({ message: "Army number is required." });
    }

    const user = await User.findOne({ armyNo });

    if (!user) {
      return res.status(404).json({ message: "User not found." });
    }

    // Create a re-examination request
    const request = new Examination({
      type: "RE_EXAM_REQUEST",
      armyNo,
      status: "PENDING",
    });

    await request.save();

    res.json({ message: "Re-examination request submitted successfully." });
  } catch (error) {
    console.error("Error submitting re-examination request:", error);
    res.status(500).json({ message: "Server error", error: error.message });
  }
});

// Add a route for CO to approve re-examination requests
router.post("/approve-reexam", auth, async (req, res) => {
  try {
    if (req.user.role !== "CO") {
      return res.status(403).json({ message: "Access denied. CO access required." });
    }

    const { requestId } = req.body;

    if (!requestId) {
      return res.status(400).json({ message: "Request ID is required." });
    }

    const request = await Examination.findById(requestId);

    if (!request) {
      return res.status(404).json({ message: "Request not found." });
    }

    request.status = "APPROVED";
    await request.save();

    res.json({ message: "Re-examination request approved successfully." });
  } catch (error) {
    console.error("Error approving re-examination request:", error);
    res.status(500).json({ message: "Server error", error: error.message });
  }
});

module.exports = router
