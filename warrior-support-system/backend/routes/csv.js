const express = require('express')
const Personnel = require('../models/Personnel')
const auth = require('../middleware/auth')
const User = require('../models/User')
const csv = require('csv-parser')
const { Parser } = require('json2csv')
const multer = require('multer')
const fs = require('fs')

const router = express.Router()

// Configure multer for file uploads
const upload = multer({ dest: 'uploads/' })

// Export personnel data as CSV (JSO and CO only)
router.get('/export/:battalionId', auth, async (req, res) => {
  try {
    if (!['JSO', 'CO'].includes(req.user.role)) {
      return res.status(403).json({ message: 'Access denied' })
    }

    const { battalionId } = req.params

    // JSO can only export their battalion data
    if (req.user.role === 'JSO') {
      const user = await User.findById(req.user.userId)
      if (user.battalion.toString() !== battalionId) {
        return res.status(403).json({ message: 'Access denied to this battalion' })
      }
    }

    const personnel = await Personnel.find({ battalion: battalionId })
      .populate('battalion', 'name')
      .populate('peerEvaluation.evaluatedBy', 'fullName rank')

    // Prepare data for CSV export
    const csvData = personnel.map(person => ({
      'Army No': person.armyNo,
      'Rank': person.rank,
      'Name': person.name,
      'Coy/Sqn/Bty': person.coySquadronBty,
      'Service': person.service,
      'Date of Induction': person.dateOfInduction.toISOString().split('T')[0],
      'Med Cat': person.medCat,
      'Leave Availed': person.leaveAvailed || 'NIL',
      'Marital Status': person.maritalStatus,
      'Self Evaluation': person.selfEvaluation,
      'Peer Evaluation Status': person.peerEvaluation.status,
      'Evaluated By': person.peerEvaluation.evaluatedBy ? 
        `${person.peerEvaluation.evaluatedBy.rank} ${person.peerEvaluation.evaluatedBy.fullName}` : 'N/A',
      'Evaluation Date': person.peerEvaluation.evaluatedAt ? 
        person.peerEvaluation.evaluatedAt.toISOString().split('T')[0] : 'N/A'
    }))

    const fields = [
      'Army No', 'Rank', 'Name', 'Coy/Sqn/Bty', 'Service', 
      'Date of Induction', 'Med Cat', 'Leave Availed', 'Marital Status',
      'Self Evaluation', 'Peer Evaluation Status', 'Evaluated By', 'Evaluation Date'
    ]

    const json2csvParser = new Parser({ fields })
    const csv = json2csvParser.parse(csvData)

    res.header('Content-Type', 'text/csv')
    res.attachment(`personnel_data_${Date.now()}.csv`)
    res.send(csv)
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

// Import personnel data from CSV (JSO and CO only)
router.post('/import/:battalionId', auth, upload.single('csvFile'), async (req, res) => {
  try {
    if (!['JSO', 'CO'].includes(req.user.role)) {
      return res.status(403).json({ message: 'Access denied' })
    }

    const { battalionId } = req.params

    // JSO can only import to their battalion
    if (req.user.role === 'JSO') {
      const user = await User.findById(req.user.userId)
      if (user.battalion.toString() !== battalionId) {
        return res.status(403).json({ message: 'Access denied to this battalion' })
      }
    }

    if (!req.file) {
      return res.status(400).json({ message: 'No file uploaded' })
    }

    const results = []
    const errors = []

    // Read and parse CSV file
    fs.createReadStream(req.file.path)
      .pipe(csv())
      .on('data', (data) => results.push(data))
      .on('end', async () => {
        try {
          for (let i = 0; i < results.length; i++) {
            const row = results[i]
            
            try {
              // Validate required fields
              if (!row['Army No'] || !row['Rank'] || !row['Name']) {
                errors.push(`Row ${i + 1}: Missing required fields`)
                continue
              }

              // Check if personnel already exists
              const existingPersonnel = await Personnel.findOne({ armyNo: row['Army No'] })
              if (existingPersonnel) {
                errors.push(`Row ${i + 1}: Personnel with Army No ${row['Army No']} already exists`)
                continue
              }

              // Create new personnel record
              const personnelData = {
                armyNo: row['Army No'],
                rank: row['Rank'],
                name: row['Name'],
                coySquadronBty: row['Coy/Sqn/Bty'] || '',
                service: row['Service'] || '',
                dateOfInduction: new Date(row['Date of Induction']) || new Date(),
                medCat: row['Med Cat'] || '',
                leaveAvailed: row['Leave Availed'] || '',
                maritalStatus: row['Marital Status'] || 'UNMARRIED',
                battalion: battalionId
              }

              const personnel = new Personnel(personnelData)
              await personnel.save()
            } catch (rowError) {
              errors.push(`Row ${i + 1}: ${rowError.message}`)
            }
          }

          // Clean up uploaded file
          fs.unlinkSync(req.file.path)

          res.json({
            message: 'Import completed',
            totalRows: results.length,
            errors: errors,
            successCount: results.length - errors.length
          })
        } catch (error) {
          fs.unlinkSync(req.file.path)
          res.status(500).json({ message: 'Import failed', error: error.message })
        }
      })
  } catch (error) {
    if (req.file) {
      fs.unlinkSync(req.file.path)
    }
    res.status(500).json({ message: 'Server error', error: error.message })
  }
})

module.exports = router