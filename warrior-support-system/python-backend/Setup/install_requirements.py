#!/usr/bin/env python3
"""
Installation script for Army Mental Health Assessment System
Ensures all required packages are installed for facial analysis
"""

import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_package(package_name):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        logger.info(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install {package_name}: {e}")
        return False

def check_package(package_name):
    """Check if a package is already installed"""
    try:
        __import__(package_name)
        logger.info(f"✅ {package_name} is already installed")
        return True
    except ImportError:
        logger.info(f"⚠️ {package_name} is not installed")
        return False

def main():
    """Main installation function"""
    logger.info("🎖️ Army Mental Health Assessment System - Package Installation")
    logger.info("=" * 60)
    
    # Required packages for facial analysis
    required_packages = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'streamlit': 'streamlit',
        'sqlite3': None,  # Built-in
        'datetime': None,  # Built-in
        'json': None,     # Built-in
        'pathlib': None,  # Built-in
    }
    
    installation_needed = []
    
    # Check which packages need installation
    for import_name, package_name in required_packages.items():
        if package_name is None:  # Built-in packages
            continue
            
        if not check_package(import_name):
            installation_needed.append(package_name)
    
    # Install missing packages
    if installation_needed:
        logger.info(f"📦 Installing {len(installation_needed)} packages...")
        
        for package in installation_needed:
            logger.info(f"Installing {package}...")
            if not install_package(package):
                logger.error(f"❌ Failed to install {package}")
                return False
    else:
        logger.info("✅ All required packages are already installed!")
    
    # Test OpenCV installation
    logger.info("🧪 Testing OpenCV installation...")
    try:
        import cv2
        logger.info(f"✅ OpenCV version: {cv2.__version__}")
        
        # Test cascade classifiers
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if face_cascade.empty():
            logger.error("❌ OpenCV cascade classifiers not found")
            return False
        else:
            logger.info("✅ OpenCV cascade classifiers loaded successfully")
            
    except Exception as e:
        logger.error(f"❌ OpenCV test failed: {e}")
        return False
    
    logger.info("=" * 60)
    logger.info("🎉 Installation completed successfully!")
    logger.info("🚀 You can now run the Army Mental Health Assessment System")
    logger.info("📝 Run: python3 run.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
