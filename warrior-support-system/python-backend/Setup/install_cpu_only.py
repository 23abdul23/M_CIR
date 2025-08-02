#!/usr/bin/env python3
"""
CPU-Only Installation Script for Army Mental Health Assessment System
This script ensures the system runs entirely on CPU without GPU dependencies
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    print("=" * 70)
    print("Army Mental Health Assessment System - CPU-Only Installation")
    print("=" * 70)
    print("This installation ensures:")
    print("✓ CPU-only operation (no GPU required)")
    print("✓ Offline capability after initial model download")
    print("✓ Fallback systems for all AI components")
    print("=" * 70)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")

def force_cpu_environment():
    """Set environment variables to force CPU usage"""
    print("\n🔧 Configuring CPU-only environment...")
    
    # Force CPU usage
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["TORCH_USE_CUDA"] = "0"
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    
    # Disable GPU for various libraries
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    os.environ["TRANSFORMERS_OFFLINE"] = "0"  # Allow initial download
    
    print("✓ Environment configured for CPU-only operation")

def install_pytorch_cpu():
    """Install PyTorch CPU version"""
    print("\n📦 Installing PyTorch (CPU-only version)...")
    
    try:
        # Install PyTorch CPU version
        cmd = [
            sys.executable, "-m", "pip", "install", 
            "torch", "torchvision", "torchaudio", 
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ PyTorch CPU version installed successfully")
            return True
        else:
            print(f"❌ Error installing PyTorch: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing PyTorch: {e}")
        return False

def install_basic_requirements():
    """Install basic requirements"""
    print("\n📦 Installing basic requirements...")
    
    basic_packages = [
        "streamlit>=1.28.0",
        "pandas>=2.0.0", 
        "numpy>=1.24.0",
        "sqlalchemy>=2.0.0",
        "python-dotenv>=1.0.0",
        "python-dateutil>=2.8.0",
        "scikit-learn>=1.3.0"
    ]
    
    for package in basic_packages:
        try:
            cmd = [sys.executable, "-m", "pip", "install", package]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Installed {package}")
            else:
                print(f"⚠ Warning: Could not install {package}")
                
        except Exception as e:
            print(f"⚠ Warning: Error installing {package}: {e}")

def install_ai_packages():
    """Install AI/ML packages"""
    print("\n🤖 Installing AI/ML packages...")
    
    ai_packages = [
        "transformers>=4.30.0",
    ]
    
    for package in ai_packages:
        try:
            cmd = [sys.executable, "-m", "pip", "install", package]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Installed {package}")
            else:
                print(f"⚠ Warning: Could not install {package} - will use fallback")
                
        except Exception as e:
            print(f"⚠ Warning: Error installing {package}: {e}")

def install_optional_packages():
    """Install optional packages"""
    print("\n🔊 Installing optional packages (audio, auth)...")
    
    optional_packages = [
        "speechrecognition",
        "openai-whisper", 
        "pydub",
        "python-jose[cryptography]",
        "passlib[bcrypt]"
    ]
    
    for package in optional_packages:
        try:
            cmd = [sys.executable, "-m", "pip", "install", package]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✓ Installed {package}")
            else:
                print(f"⚠ Optional package {package} not installed - will use fallback")
                
        except subprocess.TimeoutExpired:
            print(f"⚠ Timeout installing {package} - skipping")
        except Exception as e:
            print(f"⚠ Optional package {package} not installed: {e}")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "data",
        "data/models", 
        "data/models/whisper",
        "data/models/hindi_sentiment",
        "data/audio",
        "data/exports",
        "logs"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Error creating directory {directory}: {e}")

def test_cpu_configuration():
    """Test that everything is configured for CPU"""
    print("\n🧪 Testing CPU-only configuration...")
    
    try:
        # Test PyTorch CPU
        import torch
        if torch.cuda.is_available():
            print("⚠ Warning: CUDA is available but will be forced to CPU")
        
        # Force CPU device
        torch.set_default_device('cpu')
        device = torch.device('cpu')
        
        # Test tensor creation
        test_tensor = torch.randn(3, 3, device=device)
        print(f"✓ PyTorch configured for CPU: {test_tensor.device}")
        
    except ImportError:
        print("⚠ PyTorch not available - will use fallback systems")
    except Exception as e:
        print(f"⚠ PyTorch test failed: {e}")
    
    try:
        # Test transformers
        from transformers import pipeline
        print("✓ Transformers library available")
    except ImportError:
        print("⚠ Transformers not available - will use keyword-based analysis")

def create_cpu_config():
    """Create CPU-only configuration file"""
    print("\n⚙️ Creating CPU-only configuration...")
    
    cpu_config = '''
# CPU-Only Configuration
# This file ensures the system runs entirely on CPU

import os

# Force CPU usage - NO GPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TORCH_USE_CUDA"] = "0"
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"

# Model configuration
CPU_ONLY_MODE = True
OFFLINE_MODE = True
USE_FALLBACK_ANALYSIS = True

print("🖥️ System configured for CPU-only operation")
'''
    
    try:
        with open("cpu_config.py", "w") as f:
            f.write(cpu_config)
        print("✓ Created cpu_config.py")
    except Exception as e:
        print(f"❌ Error creating CPU configuration: {e}")

def main():
    """Main installation function"""
    print_header()
    
    # Check Python version
    check_python_version()
    
    # Force CPU environment
    force_cpu_environment()
    
    # Install packages
    pytorch_success = install_pytorch_cpu()
    install_basic_requirements()
    
    if pytorch_success:
        install_ai_packages()
    else:
        print("⚠ Skipping AI packages due to PyTorch installation failure")
    
    install_optional_packages()
    
    # Create directories
    create_directories()
    
    # Test configuration
    test_cpu_configuration()
    
    # Create CPU config
    create_cpu_config()
    
    print("\n" + "=" * 70)
    print("🎉 CPU-Only Installation Complete!")
    print("=" * 70)
    print("Next steps:")
    print("1. Run: python run.py")
    print("2. Open browser: http://localhost:8501")
    print("3. Login with: admin / admin123")
    print("")
    print("Note: First run may download models (requires internet)")
    print("After that, the system can run completely offline!")
    print("=" * 70)

if __name__ == "__main__":
    main()
