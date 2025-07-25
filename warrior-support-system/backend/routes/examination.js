const express = require("express")
const Examination = require("../models/Examination")
const Personnel = require("../models/Personnel")
const User = require("../models/User")
const auth = require("../middleware/auth")

const router = express.Router()

// Submit examination
router.post("/submit", auth, async (req, res) => {
  try {
    const { armyNo, answers, dassScores } = req.body
    
    // Get personnel details to associate battalion
    const personnel = await Personnel.findOne({ armyNo }).populate("battalion")
    if (!personnel) {
      return res.status(404).json({ message: "Personnel not found" })
    }

    // Create new examination
    const examination = new Examination({
      ...req.body,
      battalion: personnel.battalion._id,
    })

    await examination.save()

    // Update personnel self-evaluation status
    await Personnel.findOneAndUpdate({ armyNo }, { selfEvaluation: "COMPLETED" })

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
router.get("/army-no/:armyNo", auth, async (req, res) => {
  try {
    const { armyNo } = req.params

    // Role-based access control
    if (req.user.role === "USER" && req.user.armyNo !== armyNo) {
      return res.status(403).json({ message: "Access denied" })
    }

    const examination = await Examination.findOne({ armyNo }).populate("battalion", "name")

    if (!examination) {
      return res.status(404).json({ message: "Examination not found" })
    }

    // JSO can only see examinations from their battalion
    if (req.user.role === "JSO") {
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
    if (req.user.role === "JSO") {
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
    if (req.user.role === "JSO") {
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

module.exports = router
