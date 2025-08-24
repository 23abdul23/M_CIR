const mongoose = require('mongoose')
const path = require('path')

require('dotenv').config({ path: path.join(__dirname, '../.env') })

async function cleanupDatabase() {
  try {
    console.log('🧹 Starting database cleanup...')
    
    // Connect to MongoDB
    const mongoUri = process.env.MONGODB_URI || 'mongodb://localhost:27017/warrior-support-system'
    await mongoose.connect(mongoUri, {
      useNewUrlParser: true,
      useUnifiedTopology: true
    })
    console.log('✅ Connected to MongoDB')

    // Get the database
    const db = mongoose.connection.db

    // Drop all collections to start fresh
    const collections = await db.listCollections().toArray()
    
    if (collections.length === 0) {
      console.log('ℹ️ No collections found to drop')
    } else {
      console.log(`🗑️ Found ${collections.length} collections to drop`)
      
      for (let collection of collections) {
        console.log(`   Dropping: ${collection.name}`)
        try {
          await db.collection(collection.name).drop()
        } catch (error) {
          if (error.code === 26) {
            console.log(`   ⚠️ Collection ${collection.name} doesn't exist (already dropped)`)
          } else {
            throw error
          }
        }
      }
    }

    console.log('✅ All collections dropped successfully')
    
    // Close connection
    await mongoose.connection.close()
    console.log('✅ Database cleanup completed')
    
  } catch (error) {
    console.error('❌ Error during cleanup:', error)
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

cleanupDatabase()