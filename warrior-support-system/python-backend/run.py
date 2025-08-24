#!/usr/bin/env python3
"""
Run script for Army Mental Health Assessment System
"""
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
        print("\nApplication stopped.")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()
