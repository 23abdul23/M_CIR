const express = require('express')
const router = express.Router()
const Question = require('../models/Question')
const QuestionAI = require('../models/QuestionAI')
const QuestionPeer = require('../models/Question_peer')
const auth = require('../middleware/auth')

// Get all active questions
router.get('/', auth, async (req, res) => {
  try {
    const questions = await Question.find({ isActive: true })
      .sort({ order: 1 })
      .select('-__v')
    
    res.json(questions)
  } catch (error) {
    console.error('Error fetching questions:', error)
    res.status(500).json({ message: 'Error fetching questions' })
  }
})


router.get('/all', auth, async (req, res) => {
  try {
    const questions = await Question.find({})
    const questionsAI = await QuestionAI.find({})
    const questionsPeer = await QuestionPeer.find({})
  
    res.json({
    'daasQuestions' : questions,
    'aiQuestions' : questionsAI,
    'peerQuestions' : questionsPeer,
  })
  } catch (error) {
    console.error('Error fetching questions:', error)
    res.status(500).json({ message: 'Error fetching questions' })
  }
})

// Get all active questions
router.get('/ai', auth, async (req, res) => {
  try {
    const questions = await QuestionAI.find({ isActive: true })
      .sort({ order: 1 })
      .select('-__v')
    
    res.json(questions)
  } catch (error) {
    console.error('Error fetching questions:', error)
    res.status(500).json({ message: 'Error fetching questions' })
  }
})


//GEt all active peer questions

router.get('/peer_question', auth, async (req, res) => {
  try {
    const questions = await QuestionPeer.find({ isActive: true })
      .sort({ order: 1 })
      .select('-__v')
    
    res.json(questions)
  }
  catch (error) {
    console.log('Error:', error)
    res.status(500).json({ message: 'Error fetching peer questions' })
  }
})

// Get question by ID
router.get('/:questionId', auth, async (req, res) => {
  try {
    
    const question = await Question.findOne({ 
      questionId: req.params.questionId,
      isActive: true 
    })
    
    if (!question) {
      return res.status(404).json({ message: 'Question not found' })
    }
    
    res.json(question)
  } catch (error) {
    console.error('Error fetching question:', error)
    res.status(500).json({ message: 'Error fetching question' })
  }
})

// Create new question (CO only)
router.post('/', auth, async (req, res) => {
  try {
    // Check if user is CO
    if (req.user.role !== 'CO') {
      return res.status(403).json({ message: 'Access denied. CO role required.' })
    }

    const { questionId, questionText, questionType, options, order, targetDatabase } = req.body

    // Validate required fields
    if (!questionId || !questionText || !questionType || order === undefined) {
      return res.status(400).json({ 
        message: 'Missing required fields: questionId, questionText, questionType, order' 
      })
    }

    // Validate MCQ has options
    if (questionType === 'MCQ' && (!options || options.length === 0)) {
      return res.status(400).json({ 
        message: 'MCQ questions must have options' 
      })
    }


    if (targetDatabase == "manual"){
      const question = new Question({
        questionId,
        questionText,
        questionType,
        options: questionType === 'MCQ' ? options : [],
        order
      })
      await question.save()
    }

    else if (targetDatabase == "ai"){
      const question = new QuestionAI({
        questionId,
        questionText,
        questionType,
        options: questionType === 'MCQ' ? options : [],
        order
      })
      await question.save()
    }

    else if (targetDatabase == "peer"){
      const question = new QuestionPeer({
        questionId,
        questionText,
        questionType,
        options: questionType === 'MCQ' ? options : [],
        order
      })
      await question.save()
    }
  
    res.status(201).json("Success")
  } catch (error) {
    console.error('Error creating question:', error)
    res.status(500).json({ message: 'Error creating question' })
  }
})


// Delete question (CO only)
router.delete('/:questionId', auth, async (req, res) => {
  try {
    // Check if user is CO
    if (req.user.role !== 'CO') {
      return res.status(403).json({ message: 'Access denied. CO role required.' })
    }
    const {selectedType} = req.body;
    console.log(selectedType)

    if (selectedType == "manual"){
      const question = await Question.findOneAndDelete({ questionId: req.params.questionId })
      if (!question) {
        return res.status(404).json({ message: 'Question not found' })
      }
    }
    if (selectedType == "ai"){
      const question = await QuestionAI.findOneAndDelete({ questionId: req.params.questionId })
      if (!question) {
        return res.status(404).json({ message: 'Question not found' })
      }
    }
    if (selectedType == "peer"){
      const question = await QuestionPeer.findOneAndDelete({ questionId: req.params.questionId })
      if (!question) {
        return res.status(404).json({ message: 'Question not found' })
      }
    }

    res.json({ message: 'Question deleted successfully' })
  } catch (error) {
    console.error('Error deleting question:', error)
    res.status(500).json({ message: 'Error deleting question' })
  }
})

// Fetch text-based questions for AI examination
router.get('/ai-questions', async (req, res) => {
  try {
    const questions = await Question.find({ questionType: 'TEXT', isActive: true }).sort({ order: 1 })
    res.json(questions)
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: 'Failed to fetch AI questions.' })
  }
})

module.exports = router