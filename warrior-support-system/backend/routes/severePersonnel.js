const express = require("express")
const mongoose = require("mongoose")
const SeverePersonnel = require("../models/SeverePersonnel")
const auth = require("../middleware/auth")
const router = express.Router()



router.get('/:id',auth, async (req, res) => {
  try{
    const id = req.params.id;
    const severePersonnel = await SeverePersonnel.find({battalion : new mongoose.Types.ObjectId(id)});
    res.status(200).json({data: severePersonnel})
  }
  catch(error){
    console.log("Error", error)
    res.status(500)
  }
}
)

router.post("/", auth , async (req, res) => {

    try {
    // Ensure req.body is an array
    if (!Array.isArray(req.body)) {
      return res.status(400).json({ error: "Request body must be an array" });
    }

    await SeverePersonnel.deleteMany({});

    // Map incoming objects to schema-compatible format
    const personnelData = req.body.map(item => ({
      armyNo: item.armyNo,
      rank: item.rank,
      name: item.name.trim(),
      subBty: item.subBty,
      service: item.service,
      dateOfInduction: item.dateOfInduction,
      medCat: item.medCat,
      leaveAvailed: item.leaveAvailed,
      maritalStatus: item.maritalStatus,
      selfEvaluation: item.selfEvaluation,
      peerEvaluation: item.peerEvaluation,
      battalion: item.battalion?._id || undefined,  // take ID if present
      dassScores: item.dassScores,
      mode: item.mode,
      addedBattalion: item.addedBattalion,
      status: item.status,
      updatedAt: item.updatedAt,
      createdAt: item.createdAt
    }));

    // Save all docs at once
    const savedDocs = await SeverePersonnel.insertMany(personnelData, { ordered: false });

    res.status(201).json({
      message: `${savedDocs.length} personnel saved successfully`,
      data: savedDocs
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error saving personnel", details: error.message });
  }
  })

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
