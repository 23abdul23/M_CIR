#!/usr/bin/env python3
"""
Setup script for Army Mental Health Assessment System
CPU-ONLY VERSION - No GPU dependencies
"""
import os
import sys
import subprocess
import sqlite3
from pathlib import Path

# Force CPU usage from the start - NO GPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TORCH_USE_CUDA"] = "0"
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"

print("🖥️ System configured for CPU-only operation")

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = [
        "data",
        "data/models",
        "data/audio",
        "data/exports",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def initialize_database():
    """Initialize the database"""
    print("Initializing database...")
    
    try:
        # Import after ensuring requirements are installed
        from src.database.database import init_database
        from src.database.crud import create_default_admin
        from src.database.database import get_db
        
        # Initialize database
        init_database()
        
        # Create default admin
        db = next(get_db())
        create_default_admin(db)
        
        print("✓ Database initialized successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False

def download_models():
    """Download required AI models"""
    print("Downloading AI models...")
    
    try:
        # Try to download Whisper model
        import whisper
        print("Downloading Whisper model for Hindi speech recognition...")
        model = whisper.load_model("base")
        print("✓ Whisper model downloaded successfully")
        
    except ImportError:
        print("⚠ Whisper not available, Okay will use fallback speech recognition")
    except Exception as e:
        print(f"⚠ Error downloading Whisper model: {e}")
    
    try:
        # Try to download Hindi sentiment model
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        
        print("Downloading Hindi sentiment analysis model...")
        model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        print("✓ Sentiment analysis model downloaded successfully")
        
    except ImportError:
        print("⚠ Transformers not available, will use keyword-based sentiment analysis")
    except Exception as e:
        print(f"⚠ Error downloading sentiment model: {e}")

def create_sample_data():
    """Create sample questionnaires and data"""
    print("Creating sample data...")
    
    try:
        from src.admin.questionnaire_manager import questionnaire_manager
        from src.database.database import get_db
        from src.database.crud import get_user_by_username, initialize_default_keywords, initialize_default_suggestions
        
        db = next(get_db())
        
        # Get admin user
        admin_user = get_user_by_username(db, "admin")
        if not admin_user:
            print("✗ Admin user not found")
            return False
        
        # Load sample questionnaires
        result = questionnaire_manager.load_sample_questionnaires(db, admin_user.id)
        print(f"✓ Loaded {result['successful']} sample questionnaires")
        
        # Initialize default keywords
        initialize_default_keywords(db, admin_user.id)
        print("✓ Initialized default keywords")
        
        # Initialize default suggestions
        initialize_default_suggestions(db, admin_user.id)
        print("✓ Initialized default suggestions")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        return False

def create_run_script():
    """Create run script for easy startup"""
    print("Creating run script...")
    
    run_script_content = """#!/usr/bin/env python3
\"\"\"
Run script for Army Mental Health Assessment System
\"\"\"
import subprocess
import sys
import os

def main():
    # Change to the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Starting Army Mental Health Assessment System...")
    print("Access the application at: http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Run Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "src/app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\\nApplication stopped.")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()
"""
    
    with open("run.py", "w", encoding="utf-8") as f:
        f.write(run_script_content)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod("run.py", 0o755)
    
    print("✓ Created run.py script")

def create_readme():
    """Create README file"""
    print("Creating README...")
    
    readme_content = """# सेना मानसिक स्वास्थ्य मूल्यांकन प्रणाली
# Army Mental Health Assessment System

एक व्यापक मानसिक स्वास्थ्य मूल्यांकन प्रणाली जो हिंदी भाषा में सैनिकों के लिए डिज़ाइन की गई है।

## विशेषताएं (Features)

### 🎯 मुख्य विशेषताएं
- **हिंदी प्रश्नावली**: सैनिकों के लिए विशेष रूप से डिज़ाइन की गई हिंदी प्रश्नावली
- **आवाज़ से मूल्यांकन**: हिंदी में बोलकर मानसिक स्वास्थ्य का मूल्यांकन
- **AI विश्लेषण**: उन्नत AI मॉडल का उपयोग करके भावना और कीवर्ड विश्लेषण
- **व्यापक रिपोर्टिंग**: विस्तृत मानसिक स्वास्थ्य रिपोर्ट और सुझाव

### 🔧 तकनीकी विशेषताएं
- **Streamlit UI**: उपयोगकर्ता-अनुकूल वेब इंटरफेस
- **SQLite Database**: स्थानीय डेटाबेस भंडारण
- **Hindi NLP**: हिंदी भाषा प्रसंस्करण
- **Voice Processing**: आवाज़ से टेक्स्ट रूपांतरण
- **Admin Panel**: प्रश्नावली प्रबंधन के लिए एडमिन पैनल

## स्थापना (Installation)

### आवश्यकताएं
- Python 3.8 या उससे ऊपर
- pip package manager

### स्थापना चरण

1. **Repository clone करें:**
```bash
git clone <repository-url>
cd army_mental_health
```

2. **Setup script चलाएं:**
```bash
python setup.py
```

3. **Application चलाएं:**
```bash
python run.py
```

4. **Browser में खोलें:**
   - http://localhost:8501 पर जाएं

## उपयोग (Usage)

### डिफ़ॉल्ट लॉगिन
- **Admin Login:**
  - Username: `admin`
  - Password: `admin123`

### उपयोगकर्ता के लिए
1. लॉगिन करें
2. "मूल्यांकन करें" टैब में जाएं
3. प्रश्नावली चुनें और पूरा करें
4. या "आवाज़ से मूल्यांकन" का उपयोग करें

### एडमिन के लिए
1. Admin के रूप में लॉगिन करें
2. प्रश्नावली प्रबंधन
3. उपयोगकर्ता प्रबंधन
4. रिपोर्ट्स देखें

## फ़ाइल संरचना

```
army_mental_health/
├── src/
│   ├── app.py                 # मुख्य Streamlit application
│   ├── database/              # डेटाबेस मॉड्यूल
│   ├── models/                # AI मॉडल्स
│   ├── admin/                 # एडमिन इंटरफेस
│   └── config.py              # कॉन्फ़िगरेशन
├── data/                      # डेटा फ़ाइलें
├── requirements.txt           # Python dependencies
├── setup.py                   # Setup script
└── run.py                     # Run script
```

## समस्या निवारण (Troubleshooting)

### सामान्य समस्याएं

1. **Audio processing नहीं हो रहा:**
   - PyAudio install करें: `pip install pyaudio`
   - Windows पर: Microsoft Visual C++ Build Tools install करें

2. **Hindi models download नहीं हो रहे:**
   - Internet connection check करें
   - Firewall settings check करें

3. **Database errors:**
   - `python setup.py` फिर से चलाएं
   - data/ directory की permissions check करें

## योगदान (Contributing)

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## लाइसेंस (License)

यह प्रोजेक्ट MIT License के तहत है।

## संपर्क (Contact)

तकनीकी सहायता के लिए संपर्क करें।
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✓ Created README.md")

def main():
    """Main setup function"""
    print("=" * 60)
    print("Army Mental Health Assessment System - Setup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Setup steps
    steps = [
        ("Creating directories", create_directories),
        ("Installing requirements", install_requirements),
        ("Initializing database", initialize_database),
        ("Downloading AI models", download_models),
        ("Creating sample data", create_sample_data),
        ("Creating run script", create_run_script),
        ("Creating README", create_readme)
    ]
    
    success_count = 0
    
    for step_name, step_function in steps:
        print(f"\n{step_name}...")
        try:
            if step_function():
                success_count += 1
        except Exception as e:
            print(f"✗ Error in {step_name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"Setup completed: {success_count}/{len(steps)} steps successful")
    
    if success_count == len(steps):
        print("✓ Setup completed successfully!")
        print("\nTo start the application:")
        print("  python run.py")
        print("\nThen open: http://localhost:8501")
        print("\nDefault admin login:")
        print("  Username: admin")
        print("  Password: admin123")
    else:
        print("⚠ Setup completed with some issues")
        print("Check the error messages above and try running setup again")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
