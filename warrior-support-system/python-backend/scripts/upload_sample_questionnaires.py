"""
Script to upload sample questionnaires to the database
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))

try:
    from database.database import get_db, init_database
    from database.models import Questionnaire, User
    from data.sample_questionnaires import ALL_SAMPLE_QUESTIONNAIRES
except ImportError as e:
    print(f"Import error: {e}")
    # Try alternative import
    import sys
    sys.path.insert(0, '/media/adityapachauri/a93669a1-5154-48cd-91ef-105c3fceb0d7/Desktop/culture/army_mental_health/src')
    from database.database import get_db, init_database
    from database.models import Questionnaire, User
    from data.sample_questionnaires import ALL_SAMPLE_QUESTIONNAIRES

def upload_sample_questionnaires():
    """Upload all sample questionnaires to the database"""
    
    print("🎖️ Uploading Sample Questionnaires for Army Mental Health System...")
    
    try:
        # Initialize database
        init_database()
        db = next(get_db())
        
        # Get admin user (create if doesn't exist)
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("❌ Admin user not found. Please create admin user first.")
            return
        
        uploaded_count = 0
        
        for questionnaire_data in ALL_SAMPLE_QUESTIONNAIRES:
            # Check if questionnaire already exists by title
            existing = db.query(Questionnaire).filter(
                Questionnaire.title == questionnaire_data["title"]["english"]
            ).first()

            if existing:
                print(f"⚠️  Questionnaire '{questionnaire_data['title']['english']}' already exists. Updating...")
                # Update existing questionnaire
                existing.title = questionnaire_data["title"]["english"]
                existing.description = questionnaire_data["description"]["english"]
                existing.instructions = questionnaire_data["instructions"]["english"]
                existing.time_limit_minutes = questionnaire_data.get("time_limit", 30)
                existing.updated_at = datetime.now()

            else:
                # Create new questionnaire
                new_questionnaire = Questionnaire(
                    title=questionnaire_data["title"]["english"],
                    description=questionnaire_data["description"]["english"],
                    instructions=questionnaire_data["instructions"]["english"],
                    time_limit_minutes=questionnaire_data.get("time_limit", 30),
                    is_active=True,
                    created_by=admin_user.id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )

                db.add(new_questionnaire)
                db.flush()  # Get the ID

                # Add questions with bilingual support
                for i, question_data in enumerate(questionnaire_data["questions"]):
                    from database.models import Question

                    # Store bilingual question text as JSON
                    question_text_json = json.dumps(question_data["text"])

                    # Store bilingual options as JSON
                    options_json = json.dumps(question_data.get("options", {}))

                    question = Question(
                        questionnaire_id=new_questionnaire.id,
                        question_text=question_text_json,  # Store as JSON for bilingual support
                        question_type=question_data["type"],
                        order_number=i + 1,
                        is_required=True,
                        options=options_json,
                        weight=question_data.get("scoring", [1.0])[0] if question_data.get("scoring") else 1.0,
                        created_at=datetime.now()
                    )
                    db.add(question)
            
            uploaded_count += 1
            print(f"✅ Processed: {questionnaire_data['title']['english']}")
        
        # Commit all changes
        db.commit()
        
        print(f"\n🎯 Successfully processed {uploaded_count} questionnaires!")
        print("\n📋 Available Questionnaires:")
        
        # List all questionnaires
        all_questionnaires = db.query(Questionnaire).filter(Questionnaire.is_active == True).all()
        for i, q in enumerate(all_questionnaires, 1):
            print(f"{i}. {q.title} (ID: {q.id})")
            print(f"   📝 {q.description}")
            print(f"   ⏱️  Time Limit: {q.time_limit_minutes} minutes")
            print(f"   📊 Questions: {len(q.questions)}")
            print()
        
        print("🎖️ Sample questionnaires upload completed successfully!")
        
    except Exception as e:
        print(f"❌ Error uploading questionnaires: {e}")
        import traceback
        traceback.print_exc()

def create_demo_users():
    """Create demo users for testing"""
    
    print("👥 Creating demo users...")
    
    try:
        db = next(get_db())
        
        # Demo users data
        demo_users = [
            {
                "username": "admin",
                "password": "admin123",
                "full_name": "System Administrator",
                "role": "admin",
                "army_id": "ADMIN001",
                "rank": "Colonel",
                "unit": "HQ"
            },
            {
                "username": "soldier1",
                "password": "soldier123",
                "full_name": "Rajesh Kumar",
                "role": "user",
                "army_id": "SOL001",
                "rank": "Sepoy",
                "unit": "1st Battalion"
            },
            {
                "username": "soldier2",
                "password": "soldier123",
                "full_name": "Amit Singh",
                "role": "user",
                "army_id": "SOL002",
                "rank": "Lance Naik",
                "unit": "2nd Battalion"
            },
            {
                "username": "officer1",
                "password": "officer123",
                "full_name": "Captain Priya Sharma",
                "role": "user",
                "army_id": "OFF001",
                "rank": "Captain",
                "unit": "Medical Corps"
            }
        ]
        
        for user_data in demo_users:
            # Check if user exists
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            
            if not existing_user:
                from database.crud import create_user
                user = create_user(
                    db=db,
                    username=user_data["username"],
                    email=f"{user_data['username']}@army.mil",  # Add email
                    password=user_data["password"],
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    army_id=user_data["army_id"],
                    rank=user_data["rank"],
                    unit=user_data["unit"]
                )
                print(f"✅ Created user: {user_data['username']} ({user_data['full_name']})")
            else:
                print(f"⚠️  User {user_data['username']} already exists")
        
        print("👥 Demo users creation completed!")
        
    except Exception as e:
        print(f"❌ Error creating demo users: {e}")

if __name__ == "__main__":
    print("🎖️ Army Mental Health System - Database Setup")
    print("=" * 50)
    
    # Create demo users first
    create_demo_users()
    print()
    
    # Upload sample questionnaires
    upload_sample_questionnaires()
    
    print("\n🚀 Setup completed! You can now use the application with:")
    print("   Admin Login: admin / admin123")
    print("   User Login: soldier1 / soldier123")
    print("   User Login: soldier2 / soldier123")
    print("   User Login: officer1 / officer123")
