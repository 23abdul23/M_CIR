const express = require("express")
const Personnel = require("../models/Personnel")
const Battalion = require('../models/Battalion')
const Examination = require("../models/Examination")
const auth = require("../middleware/auth")
const User = require("../models/User")
const bcrypt = require("bcrypt")

const router = express.Router()

router.get("/allUsernames", auth, async (req, res) => {
  try{
    const users = await User.find({});
    const usernames = users.map(user => ({
      username: user.username,
      armyNo: user.armyNo
    }))


    return res.status(200).json({ message: "Success", data: usernames })
  }

  catch (error){
    console.log(error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

router.post("/updateUser/:armyNo", auth, async (req, res) => {
  try {
    const user = await User.findOne({ armyNo: req.params.armyNo });
    const { newUsername, newPassword, action } = req.body;


    if (!user) {
      return res.status(404).send("User not found");
    }

    if (action === "password") {
      const user = await User.findOne({ armyNo: req.params.armyNo });
      
      user.password = newPassword;
      
      await user.save();

      return res.status(200).json({
        message: "Password updated successfully",
        data: user,
      });
    }

    if (action === "username") {
      user.username = newUsername;
      await user.save();
      return res.status(200).json({
        message: "User updated successfully",
        data: user,
      });
    }

    if (action === "delete") {
      await User.deleteOne({ armyNo: req.params.armyNo });
      return res.status(200).json({ message: "User deleted successfully" });
    }

    return res.status(400).json({ message: "Invalid action" });
  } catch (error) {
    console.log(error);
    res.status(500).json({ message: "Server error", error: error.message });
  }
})

// Get personnel by battalion (CO sees all, JSO sees only his battalion)
router.get("/battalion/:battalionId", auth, async (req, res) => {
  try {
    const { battalionId } = req.params

    // Role-based access control
    if (req.user.role === "USER") {
      return res.status(403).json({ message: "Access denied" })
    }

    if (req.user.role === "JCO") {
      // JSO can only see personnel from their battalion
      const user = await User.findOne({ armyNo: req.user.armyNo })
      if (user.battalion.toString() !== battalionId) {
        return res.status(403).json({ message: "Access denied to this battalion" })
      }
    }

    const personnel = await Personnel.find({ battalion: battalionId })
      .populate("battalion", "name")
      .sort({ createdAt: -1 })

    // Enhance personnel data with examination status and DASS scores
    const enhancedPersonnel = await Promise.all(
      personnel.map(async (person) => {
        const examination = await Examination.findOne({ armyNo: person.armyNo })
        return {
          ...person.toObject(),
          hasExamination: !!examination,
          dassScores: examination ? examination.dassScores : null,
          mode: examination ? examination.mode : null,
          examinationDate: examination ? examination.completedAt : null,
        }
      }),
    )

    res.json(enhancedPersonnel)
  } catch (error) {
    console.error("Error fetching personnel:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Get personnel by army number
router.get("/army-no/:armyNo", auth, async (req, res) => {
  try {
    const { armyNo } = req.params

    const personnel = await Personnel.findOne({ armyNo }).populate("battalion", "name")

    if (!personnel) {
      return res.status(404).json({ message: "Personnel not found" })
    }

    if (personnel.status === "PENDING"){
      return res.status(400).json({ message: "Your application is pending approval by the CO." });
    }

    // Role-based access control
    if (req.user.role === "JCO") {
      const user = await User.findOne({ armyNo: req.user.armyNo })
      if (personnel.battalion._id.toString() !== user.battalion.toString()) {
        return res.status(403).json({ message: "Access denied" })
      }
    }

    // Add examination data if exists
    const examination = await Examination.findOne({ armyNo })
    const enhancedPersonnel = {
      ...personnel.toObject(),
      hasExamination: !!examination,
      dassScores: examination ? examination.dassScores : null,
      examinationDate: examination ? examination.completedAt : null,
    }

    res.json(enhancedPersonnel)
  } catch (error) {
    console.error("Error fetching personnel by army number:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})


// Create personnel (CO)
router.post("/", auth, async (req, res) => {
  try {
    const personnelData = req.body;

    // Check if personnel with this army number already exists
    const existingPersonnel = await Personnel.findOne({ armyNo: personnelData.armyNo });
    
    if (existingPersonnel) {
      if (existingPersonnel.status === "PENDING") {
        return res.status(400).json({ message: "Your application is pending approval by the CO." });
      }
    }

    if (!personnelData.battalion) {
      delete personnelData.battalion;
    }

    const personnel = new Personnel(personnelData);
    await personnel.save();

    await personnel.populate("battalion", "name");

    return res.status(200).json({ message: "Personnel created successfully", personnel });

  } catch (error) {
    console.error("Error creating personnel:", error);
    res.status(500).json({ message: "Server error", error: error.message });
  }
})

// Update personnel (CO and JSO only)
router.put("/:id", auth, async (req, res) => {
  try {
    if (req.user.role === "USER" || req.user.role === "JCO" ) {
      return res.status(403).json({ message: "Access denied" })
    }

    const personnel = await Personnel.findById(req.params.id)
    if (!personnel) {
      return res.status(404).json({ message: "Personnel not found" })
    }

    const updatedPersonnel = await Personnel.findByIdAndUpdate(req.params.id, req.body, { new: true }).populate(
      "battalion",
      "name",
    )

    // Add examination data if exists
    const examination = await Examination.findOne({ armyNo: updatedPersonnel.armyNo })
    const enhancedPersonnel = {
      ...updatedPersonnel.toObject(),
      hasExamination: !!examination,
      dassScores: examination ? examination.dassScores : null,
      examinationDate: examination ? examination.completedAt : null,
    }

    res.json(enhancedPersonnel)
  } catch (error) {
    console.error("Error updating personnel:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Delete personnel (CO and JSO only)
router.delete("/:id", auth, async (req, res) => {
  try {
    if (req.user.role === "USER") {
      return res.status(403).json({ message: "Access denied" })
    }

    const personnel = await Personnel.findById(req.params.id)
    if (!personnel) {
      return res.status(404).json({ message: "Personnel not found" })
    }

    // JSO can only delete personnel from their battalion
    if (req.user.role === "JCO") {
      const user = await User.findOne({ armyNo: req.user.armyNo })
      if (personnel.battalion.toString() !== user.battalion.toString()) {
        return res.status(403).json({ message: "Access denied" })
      }
    }

    // Also delete associated examination if exists
    await Examination.deleteOne({ armyNo: personnel.armyNo })

    await Personnel.findByIdAndDelete(req.params.id)
    res.json({ message: "Personnel and associated examination deleted successfully" })
  } catch (error) {
    console.error("Error deleting personnel:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Delete all personnel from battalion (CO and JSO only)
router.delete("/battalion/:battalionId", auth, async (req, res) => {
  try {
    if (req.user.role === "USER") {
      return res.status(403).json({ message: "Access denied" })
    }

    const { battalionId } = req.params

    // JSO can only delete from their battalion
    if (req.user.role === "JCO") {
      const user = await User.findOne({ armyNo: req.user.armyNo })
      if (user.battalion.toString() !== battalionId) {
        return res.status(403).json({ message: "Access denied" })
      }
    }

    // Get all personnel from the battalion to delete their examinations
    const personnel = await Personnel.find({ battalion: battalionId })
    const armyNumbers = personnel.map((p) => p.armyNo)

    // Delete associated examinations
    await Examination.deleteMany({ armyNo: { $in: armyNumbers } })

    // Delete personnel
    await Personnel.deleteMany({ battalion: battalionId })

    res.json({ message: "All personnel and associated examinations deleted successfully" })
  } catch (error) {
    console.error("Error deleting battalion personnel:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Get personnel statistics for dashboard
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

    const totalPersonnel = await Personnel.countDocuments({ battalion: battalionId })
    const completedExaminations = await Examination.countDocuments({ battalion: battalionId })
    const pendingExaminations = totalPersonnel - completedExaminations

    // Get marital status breakdown
    const marriedCount = await Personnel.countDocuments({
      battalion: battalionId,
      maritalStatus: "MARRIED",
    })
    const unmarriedCount = await Personnel.countDocuments({
      battalion: battalionId,
      maritalStatus: "UNMARRIED",
    })

    // Get self-evaluation status breakdown
    const notAttempted = await Personnel.countDocuments({
      battalion: battalionId,
      selfEvaluation: "NOT_ATTEMPTED",
    })
    const examAppeared = await Personnel.countDocuments({
      battalion: battalionId,
      selfEvaluation: "EXAM_APPEARED",
    })
    const completed = await Personnel.countDocuments({
      battalion: battalionId,
      selfEvaluation: "COMPLETED",
    })

    const stats = {
      totalPersonnel,
      completedExaminations,
      pendingExaminations,
      completionRate: totalPersonnel > 0 ? Math.round((completedExaminations / totalPersonnel) * 100) : 0,
      maritalStatus: {
        married: marriedCount,
        unmarried: unmarriedCount,
      },
      selfEvaluationStatus: {
        notAttempted,
        examAppeared,
        completed,
      },
    }

    res.json(stats)
  } catch (error) {
    console.error("Error fetching personnel statistics:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Add a route for CO to approve pending users
router.put("/approve-user/:id", auth, async (req, res) => {
  try {
    if (req.user.role !== "CO") {
      return res.status(403).json({ message: "Access denied" })
    }
    const user = await Personnel.findOne({ armyNo: req.params.id })

    const status = req.body.status

    if (user.addedBattalion != '' && status == 'APPROVED'){
      const battalion = new Battalion({
        _id: user.battalion,       // use the given ObjectId
        name: user.addedBattalion, // battalion name from addedBattalion
        postedStr: user.subBty,
        status: 'APPROVED'
      });

      await battalion.save();
    }

    user.status = status
    await user.save()

    res.json({ message: "User approved successfully", user })
  } catch (error) {
    console.error("Error approving user:", error);
    res.status(500).json({ message: "Server error", error: error.message });
  }
})

// Add a route to fetch pending users
router.get("/pending", auth, async (req, res) => {
  try {
    if (req.user.role !== "CO") {
      return res.status(403).json({ message: "Access denied" })
    }

    const pendingUsers = await Personnel.find({ status: "PENDING" })
    res.json(pendingUsers)
  } catch (error) {
    console.error("Error fetching pending users:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

// Update battalion creation route to automatically approve new battalions
router.post("/battalion", auth, async (req, res) => {
  try {
    if (req.user.role !== "CO") {
      return res.status(403).json({ message: "Access denied" })
    }

    const { name, postedStr } = req.body

    const newBattalion = new Battalion({
      name,
      postedStr,
      status: "APPROVED", // Automatically approve new battalions
    })

    await newBattalion.save()

    res.status(201).json({ message: "Battalion created and approved successfully", battalion: newBattalion })
  } catch (error) {
    console.error("Error creating battalion:", error)
    res.status(500).json({ message: "Server error", error: error.message })
  }
})

module.exports = router
