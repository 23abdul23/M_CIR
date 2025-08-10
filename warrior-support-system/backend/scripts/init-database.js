

const mongoose = require('mongoose')
const path = require('path')
const fs = require('fs')

// Import models with correct paths
const User = require(path.join(__dirname, '../models/User'))
const Battalion = require(path.join(__dirname, '../models/Battalion'))
const Personnel = require(path.join(__dirname, '../models/Personnel'))
const Question = require(path.join(__dirname, '../models/Question'))
const QuestionPeer = require(path.join(__dirname, '../models/Question_peer'))
const Examination = require(path.join(__dirname, '../models/Examination'))
const ReExam = require(path.join(__dirname, '../models/ReExam'))


require('dotenv').config({ path: path.join(__dirname, '../.env') })

// Helper function to read JSON files
function readTestData(filename) {
  try {
    const filePath = path.join(__dirname, '../../test-data', filename)
    const data = fs.readFileSync(filePath, 'utf8')
    return JSON.parse(data)
  } catch (error) {
    console.error(`Error reading ${filename}:`, error)
    return []
  }
}

// Helper function to convert MongoDB date objects
function convertDates(obj) {
  if (obj && typeof obj === 'object') {
    if (obj.$date) {
      return new Date(obj.$date)
    }
    if (obj.$oid) {
      return new mongoose.Types.ObjectId(obj.$oid)
    }
    if (Array.isArray(obj)) {
      return obj.map(convertDates)
    }
    const converted = {}
    for (const [key, value] of Object.entries(obj)) {
      converted[key] = convertDates(value)
    }
    return converted
  }
  return obj
}

async function initializeDatabase() {
  try {
    console.log('🚀 Starting database initialization...')
    
    // Connect to MongoDB with updated database name
    const mongoUri = process.env.MONGODB_URI
    await mongoose.connect(mongoUri, {
      useNewUrlParser: true,
      useUnifiedTopology: true
    })
    console.log('✅ Connected to MongoDB')

    // Clear existing data
    console.log('🧹 Clearing existing data...')
    await User.deleteMany({})
    await Battalion.deleteMany({})
    await Personnel.deleteMany({})
    await Examination.deleteMany({})
    await Question.deleteMany({})
    await QuestionPeer.deleteMany({})
    console.log('✅ Cleared existing data')

    // Create Questions first
    console.log('📝 Creating questions...')
    const questionsData = readTestData('daas41_questions.json')
    const processedQuestions = questionsData.map(q => convertDates(q))
    const questions = await Question.insertMany(processedQuestions)
    console.log(`✅ Created ${questions.length} questions`)

    // Create Peer Questions first
    console.log('📝 Creating questions...')
    const questionsPeerData = readTestData('peer_questions.json')
    const processedPeerQuestions = questionsPeerData.map(q => convertDates(q))
    const peer_questions = await QuestionPeer.insertMany(processedPeerQuestions)
    console.log(`✅ Created ${peer_questions.length} questions`)

    // Create Battalions
    console.log('🏛️ Creating battalions...')
    const battalionsData = readTestData('battalions.json')
    const processedBattalions = battalionsData.map(b => convertDates(b))
    const battalions = await Battalion.insertMany(processedBattalions)
    console.log(`✅ Created ${battalions.length} battalions`)

    // Create Users
    console.log('👥 Creating users...')
    const usersData = readTestData('users.json')
    const processedUsers = usersData.map(u => convertDates(u))
    const users = await User.insertMany(processedUsers)
    console.log(`✅ Created ${users.length} users`)

    // Create Personnel
    console.log('👨‍💼 Creating personnel records...')
    const personnelData = readTestData('personnel.json')
    const processedPersonnel = personnelData.map(p => convertDates(p))
    const personnel = await Personnel.insertMany(processedPersonnel)
    console.log(`✅ Created ${personnel.length} personnel records`)

    // Create Examinations
    console.log('📝 Creating examination records...')
    const examinationsData = readTestData('examinations.json')
    const processedExaminations = examinationsData.map(e => convertDates(e))
    const examinations = await Examination.insertMany(processedExaminations)
    console.log(`✅ Created ${examinations.length} examination records`)

    console.log('\n🎉 === DATABASE INITIALIZATION COMPLETED ===')
    console.log('\n📊 Summary:')
    console.log(`   Questions: ${questions.length}`)
    console.log(`   Peer Questions: ${peer_questions.length}`)
    console.log(`   Users: ${users.length}`)
    console.log(`   Battalions: ${battalions.length}`)
    console.log(`   Personnel: ${personnel.length}`)
    console.log(`   Examinations: ${examinations.length}`)
    
    console.log('\n📝 Questions Created:')
    questions.forEach(q => {
      console.log(`   ${q.questionId}. ${q.questionText.substring(0, 50)}... (${q.questionType})`)
    })
    
    console.log('\n🔐 Login Credentials from imported data:')
    console.log('   Check the users.json file for username/password combinations')
    
    console.log('\n🏛️ Battalions from imported data:')
    battalions.forEach(b => {
      console.log(`   ${b.status === 'APPROVED' ? '✅' : '⏳'} ${b.name} (${b.status})`)
    })
    
    console.log('\n📈 Imported Data Features:')
    console.log(`   • ${questions.length} Questions loaded from questions.json`)
    console.log(`   • ${users.length} User accounts loaded from users.json`)
    console.log(`   • ${battalions.length} Battalions loaded from battalions.json`)
    console.log(`   • ${personnel.length} Personnel records loaded from personnel.json`)
    console.log(`   • ${examinations.length} Examination responses loaded from examinations.json`)

    // Close connection
    await mongoose.connection.close()
    console.log('\n✅ Database connection closed')
    console.log('🚀 Ready to start the application!')
    
  } catch (error) {
    console.error('❌ Error during initialization:', error)
    console.error('Stack trace:', error.stack)
    process.exit(1)
  }
}

// Handle process termination
process.on('SIGINT', async () => {
  console.log('\n⚠️ Process interrupted. Closing database connection...')
  await mongoose.connection.close()
  process.exit(0)
})

initializeDatabase()