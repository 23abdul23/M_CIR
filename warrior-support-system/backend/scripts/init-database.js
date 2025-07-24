const mongoose = require('mongoose')
const path = require('path')

// Import models with correct paths
const User = require(path.join(__dirname, '../models/User'))
const Battalion = require(path.join(__dirname, '../models/Battalion'))
const Personnel = require(path.join(__dirname, '../models/Personnel'))
const Question = require(path.join(__dirname, '../models/Question'))

// Create Examination schema inline since the model file might not exist
const examinationSchema = new mongoose.Schema({
  armyNo: {
    type: String,
    required: true
  },
  answers: [{
    questionId: String,
    answer: String
  }],
  completedAt: {
    type: Date,
    default: Date.now
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
})

const Examination = mongoose.model('Examination', examinationSchema)

require('dotenv').config({ path: path.join(__dirname, '../.env') })

async function initializeDatabase() {
  try {
    console.log('🚀 Starting database initialization...')
    
    // Connect to MongoDB with updated database name
    const mongoUri = process.env.MONGODB_URI || 'mongodb://localhost:27017/questionnaire_user'
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
    console.log('✅ Cleared existing data')

    // Create Questions first
    console.log('📝 Creating questions...')
    const questions = await Question.insertMany([
      {
        questionId: 1,
        questionText: "Maine paya ki main bahut chhoti-chhoti baton se pareshan ho jata hun",
        questionType: "MCQ",
        options: [
          {
            optionId: "A",
            optionText: "Yeh mujh par bilkul bhi lagu nahi hua."
          },
          {
            optionId: "B", 
            optionText: "Kabhi-Kabhi mere saath aise hota hain."
          },
          {
            optionId: "C",
            optionText: "Aise mere saath aksar hota rehta hain."
          },
          {
            optionId: "D",
            optionText: "Aise lagbhag hamesha mere saath hota rehta hain."
          }
        ],
        order: 1,
        isActive: true
      },
      {
        questionId: 2,
        questionText: "Main apne aap ko khush aur prasann mehsus karta hun",
        questionType: "MCQ",
        options: [
          {
            optionId: "A",
            optionText: "Hamesha"
          },
          {
            optionId: "B",
            optionText: "Aksar"
          },
          {
            optionId: "C", 
            optionText: "Kabhi-kabhi"
          },
          {
            optionId: "D",
            optionText: "Bilkul nahi"
          }
        ],
        order: 2,
        isActive: true
      },
      {
        questionId: 3,
        questionText: "Main apne kaam mein concentrate kar pata hun",
        questionType: "MCQ",
        options: [
          {
            optionId: "A",
            optionText: "Hamesha kar pata hun"
          },
          {
            optionId: "B",
            optionText: "Aksar kar pata hun"
          },
          {
            optionId: "C",
            optionText: "Kabhi-kabhi mushkil hoti hai"
          },
          {
            optionId: "D",
            optionText: "Bilkul concentrate nahi kar pata"
          }
        ],
        order: 3,
        isActive: true
      },
      {
        questionId: 4,
        questionText: "Kya aap apni mental health improve karne ke liye koi suggestion dena chahenge?",
        questionType: "TEXT",
        options: [],
        order: 4,
        isActive: true
      }
    ])
    console.log(`✅ Created ${questions.length} questions`)

    // Create Battalions
    console.log('🏛️ Creating battalions...')
    const battalions = await Battalion.insertMany([
      {
        name: '71 FD REGT',
        postedStr: '450',
        status: 'APPROVED',
        createdAt: new Date('2024-01-10T10:00:00.000Z'),
        approvedAt: new Date('2024-01-10T10:05:00.000Z')
      },
      {
        name: '219 (I) Fd WKSP (Spl)',
        postedStr: '320',
        status: 'APPROVED',
        createdAt: new Date('2024-01-12T11:00:00.000Z'),
        approvedAt: new Date('2024-01-12T11:10:00.000Z')
      },
      {
        name: '15 PARA BN',
        postedStr: '800',
        status: 'PENDING',
        createdAt: new Date('2024-01-20T14:30:00.000Z')
      },
      {
        name: '3 GUARDS',
        postedStr: '650',
        status: 'APPROVED',
        createdAt: new Date('2024-01-08T09:00:00.000Z'),
        approvedAt: new Date('2024-01-08T09:15:00.000Z')
      }
    ])
    console.log(`✅ Created ${battalions.length} battalions`)

    // Create Users
    console.log('👥 Creating users...')
    const users = await User.create([
      {
        username: 'co_admin',
        password: 'admin123',
        fullName: 'Colonel Rajesh Kumar',
        role: 'CO',
        createdAt: new Date('2024-01-15T08:00:00.000Z')
      },
      {
        username: 'jso_officer',
        password: 'jso123',
        fullName: 'Major Priya Sharma',
        role: 'JSO',
        armyNo: 'JC15234M',
        rank: 'MAJ',
        battalion: battalions[0]._id,
        createdAt: new Date('2024-01-15T08:30:00.000Z')
      },
      {
        username: 'jso_officer2',
        password: 'jso123',
        fullName: 'Major Arjun Patel',
        role: 'JSO',
        armyNo: 'JC15235N',
        rank: 'MAJ',
        battalion: battalions[1]._id,
        createdAt: new Date('2024-01-15T08:45:00.000Z')
      },
      {
        username: 'user_soldier',
        password: 'user123',
        fullName: 'Sepoy Amit Singh',
        role: 'USER',
        armyNo: 'SS51782K',
        rank: 'SEP',
        battalion: battalions[0]._id,
        createdAt: new Date('2024-01-15T09:00:00.000Z')
      },
      {
        username: 'user_soldier',
        password: 'user123',
        fullName: 'Captain Karan Thakare',
        role: 'USER',
        armyNo: 'SSS1782K',
        rank: 'CAPT',
        battalion: battalions[0]._id,
        createdAt: new Date('2024-01-15T09:15:00.000Z')
      },
      {
        username: 'user_soldier',
        password: 'user123',
        fullName: 'Lieutenant Vikram Kumar',
        role: 'USER',
        armyNo: 'IC69763F',
        rank: 'LT',
        battalion: battalions[0]._id,
        createdAt: new Date('2024-01-15T09:30:00.000Z')
      },
      {
        username: 'user_soldier',
        password: 'user123',
        fullName: 'Havildar Rajesh Singh',
        role: 'USER',
        armyNo: '14570938M',
        rank: 'HAV',
        battalion: battalions[0]._id,
        createdAt: new Date('2024-01-15T09:45:00.000Z')
      }
    ])
    console.log(`✅ Created ${users.length} users`)

    // Update battalions with requestedBy and approvedBy
    console.log('🔗 Updating battalion references...')
    await Battalion.findByIdAndUpdate(battalions[0]._id, {
      requestedBy: users[0]._id,
      approvedBy: users[0]._id
    })
    await Battalion.findByIdAndUpdate(battalions[1]._id, {
      requestedBy: users[0]._id,
      approvedBy: users[0]._id
    })
    await Battalion.findByIdAndUpdate(battalions[2]._id, {
      requestedBy: users[3]._id // Requested by user_soldier
    })
    await Battalion.findByIdAndUpdate(battalions[3]._id, {
      requestedBy: users[0]._id,
      approvedBy: users[0]._id
    })

    // Create Personnel
    console.log('👨‍💼 Creating personnel records...')
    const personnel = await Personnel.insertMany([
      {
        armyNo: 'SSS1782K',
        rank: 'CAPT',
        name: 'Karan Thakare',
        coySquadronBty: '184 FD Bty',
        service: '03',
        dateOfInduction: new Date('2022-07-30'),
        medCat: 'SHAPE 1',
        leaveAvailed: '39',
        maritalStatus: 'UNMARRIED',
        selfEvaluation: 'EXAM_APPEARED',
        peerEvaluation: {
          status: 'PENDING'
        },
        battalion: battalions[0]._id,
        createdAt: new Date('2024-01-15T10:00:00.000Z')
      },
      {
        armyNo: 'IC69763F',
        rank: 'LT',
        name: 'Vikram Kumar',
        coySquadronBty: 'AWG Band Camp',
        service: '2 yrs',
        dateOfInduction: new Date('2022-01-06'),
        medCat: 'SHAPE 1',
        leaveAvailed: '05 days PAL',
        maritalStatus: 'MARRIED',
        selfEvaluation: 'EXAM_APPEARED',
        peerEvaluation: {
          status: 'EVALUATED',
          evaluatedBy: users[1]._id,
          evaluatedAt: new Date('2024-01-18T15:30:00.000Z'),
          answers: [
            {
              questionId: '1',
              answer: 'Good - Demonstrates solid leadership abilities'
            },
            {
              questionId: '2',
              answer: 'Works well with others'
            },
            {
              questionId: '3',
              answer: 'Competent in most areas'
            },
            {
              questionId: '4',
              answer: 'Shows good initiative and is reliable in duties.'
            }
          ]
        },
        battalion: battalions[0]._id,
        createdAt: new Date('2024-01-15T10:15:00.000Z')
      },
      {
        armyNo: '14570938M',
        rank: 'HAV',
        name: 'J DHARMAN',
        coySquadronBty: 'VH PL',
        service: '14 yrs',
        dateOfInduction: new Date('2022-03-04'),
        medCat: 'SHAPE 1',
        leaveAvailed: '24 DAYS',
        maritalStatus: 'MARRIED',
        selfEvaluation: 'NOT_ATTEMPTED',
        peerEvaluation: {
          status: 'PENDING'
        },
        battalion: battalions[0]._id,
        createdAt: new Date('2024-01-15T10:30:00.000Z')
      },
      {
        armyNo: '17944391P',
        rank: 'SEP',
        name: 'SAROJ SINGH',
        coySquadronBty: 'MT',
        service: '6',
        dateOfInduction: new Date('2022-03-13'),
        medCat: 'SHAPE 1',
        leaveAvailed: '30 DAYS',
        maritalStatus: 'MARRIED',
        selfEvaluation: 'EXAM_APPEARED',
        peerEvaluation: {
          status: 'PENDING'
        },
        battalion: battalions[0]._id,
        createdAt: new Date('2024-01-15T10:45:00.000Z')
      },
      {
        armyNo: '17932623W',
        rank: 'CFN',
        name: 'PANKAJ KUMAR',
        coySquadronBty: 'VH PL',
        service: '12',
        dateOfInduction: new Date('2022-11-17'),
        medCat: 'SHAPE 1',
        leaveAvailed: 'NIL',
        maritalStatus: 'MARRIED',
        selfEvaluation: 'NOT_ATTEMPTED',
        peerEvaluation: {
          status: 'PENDING'
        },
        battalion: battalions[0]._id,
        createdAt: new Date('2024-01-15T11:00:00.000Z')
      },
      {
        armyNo: '17654321X',
        rank: 'NK',
        name: 'RAVI SHANKAR',
        coySquadronBty: 'HQ PL',
        service: '8',
        dateOfInduction: new Date('2022-05-15'),
        medCat: 'SHAPE 1',
        leaveAvailed: '15 DAYS',
        maritalStatus: 'UNMARRIED',
        selfEvaluation: 'EXAM_APPEARED',
        peerEvaluation: {
          status: 'PENDING'
        },
        battalion: battalions[0]._id,
        createdAt: new Date('2024-01-15T11:15:00.000Z')
      },
      {
        armyNo: 'SS51782K',
        rank: 'SEP',
        name: 'Amit Singh',
        coySquadronBty: 'A COY',
        service: '5',
        dateOfInduction: new Date('2022-08-20'),
        medCat: 'SHAPE 1',
        leaveAvailed: '20 DAYS',
        maritalStatus: 'UNMARRIED',
        selfEvaluation: 'EXAM_APPEARED',
        peerEvaluation: {
          status: 'PENDING'
        },
        battalion: battalions[0]._id,
        createdAt: new Date('2024-01-15T11:30:00.000Z')
      },
      // Personnel for second battalion
      {
        armyNo: '18765432Y',
        rank: 'HAV',
        name: 'SURESH KUMAR',
        coySquadronBty: 'WKSP',
        service: '10',
        dateOfInduction: new Date('2021-04-10'),
        medCat: 'SHAPE 1',
        leaveAvailed: '25 DAYS',
        maritalStatus: 'MARRIED',
        selfEvaluation: 'EXAM_APPEARED',
        peerEvaluation: {
          status: 'PENDING'
        },
        battalion: battalions[1]._id,
        createdAt: new Date('2024-01-15T12:00:00.000Z')
      }
    ])
    console.log(`✅ Created ${personnel.length} personnel records`)

    // Create Examinations with answers matching the new question format
    console.log('📝 Creating examination records...')
    const examinations = await Examination.insertMany([
      {
        armyNo: 'SSS1782K',
        answers: [
          {
            questionId: '1',
            answer: 'Kabhi-Kabhi mere saath aise hota hain.'
          },
          {
            questionId: '2',
            answer: 'Aksar'
          },
          {
            questionId: '3',
            answer: 'Aksar kar pata hun'
          },
          {
            questionId: '4',
            answer: 'I feel motivated to serve my country and work with my team. Regular physical exercise and meditation help me stay focused.'
          }
        ],
        completedAt: new Date('2024-01-16T14:30:00.000Z'),
        createdAt: new Date('2024-01-16T14:30:00.000Z')
      },
      {
        armyNo: 'IC69763F',
        answers: [
          {
            questionId: '1',
            answer: 'Yeh mujh par bilkul bhi lagu nahi hua.'
          },
          {
            questionId: '2',
            answer: 'Hamesha'
          },
          {
            questionId: '3',
            answer: 'Hamesha kar pata hun'
          },
          {
            questionId: '4',
            answer: 'Focus on continuous learning and team building activities. Regular communication with family helps maintain work-life balance.'
          }
        ],
        completedAt: new Date('2024-01-17T16:45:00.000Z'),
        createdAt: new Date('2024-01-17T16:45:00.000Z')
      },
      {
        armyNo: '17944391P',
        answers: [
          {
            questionId: '1',
            answer: 'Aise mere saath aksar hota rehta hain.'
          },
          {
            questionId: '2',
            answer: 'Kabhi-kabhi'
          },
          {
            questionId: '3',
            answer: 'Kabhi-kabhi mushkil hoti hai'
          },
          {
            questionId: '4',
            answer: 'Need better work-life balance and stress management techniques. Would appreciate counseling sessions and recreational activities.'
          }
        ],
        completedAt: new Date('2024-01-18T10:20:00.000Z'),
        createdAt: new Date('2024-01-18T10:20:00.000Z')
      }
    ])
    console.log(`✅ Created ${examinations.length} examination records`)

    console.log('\n🎉 === DATABASE INITIALIZATION COMPLETED ===')
    console.log('\n📊 Summary:')
    console.log(`   Questions: ${questions.length}`)
    console.log(`   Users: ${users.length}`)
    console.log(`   Battalions: ${battalions.length}`)
    console.log(`   Personnel: ${personnel.length}`)
    console.log(`   Examinations: ${examinations.length}`)
    
    console.log('\n📝 Questions Created:')
    questions.forEach(q => {
      console.log(`   ${q.questionId}. ${q.questionText.substring(0, 50)}... (${q.questionType})`)
    })
    
    console.log('\n🔐 Demo Login Credentials:')
    console.log('   CO (Admin): username=co_admin, password=admin123')
    console.log('   JSO (Officer 1): username=jso_officer, password=jso123')
    console.log('   JSO (Officer 2): username=jso_officer2, password=jso123')
    console.log('   USER (Soldier): username=user_soldier, password=user123')
    console.log('   USER (Captain): username=user_soldier, password=user123')
    console.log('   USER (Lieutenant): username=user_soldier, password=user123')
    console.log('   USER (Havildar): username=user_soldier, password=user123')
    
    console.log('\n🏛️ Battalions:')
    console.log('   ✅ 71 FD REGT (Approved) - 7 personnel')
    console.log('   ✅ 219 (I) Fd WKSP (Spl) (Approved) - 1 personnel')
    console.log('   ✅ 3 GUARDS (Approved) - 0 personnel')
    console.log('   ⏳ 15 PARA BN (Pending approval)')
    
    console.log('\n📈 Test Data Features:')
    console.log('   • 4 Mental health questions (3 MCQ + 1 Text)')
    console.log('   • Role-based user accounts')
    console.log('   • Battalion approval workflow')
    console.log('   • Personnel with different evaluation statuses')
    console.log('   • Sample examination responses')
    console.log('   • Peer evaluation data')

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