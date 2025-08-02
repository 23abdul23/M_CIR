#!/usr/bin/env python3
"""
GPU Voice Processing Installation Script
Installs PyTorch, Whisper, and audio dependencies with GPU support
"""

import subprocess
import sys
import logging
import platform

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_gpu_availability():
    """Check if NVIDIA GPU is available"""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ NVIDIA GPU detected")
            return True
        else:
            logger.warning("⚠️ nvidia-smi not found")
            return False
    except FileNotFoundError:
        logger.warning("⚠️ nvidia-smi not available")
        return False

def install_pytorch_gpu():
    """Install PyTorch with GPU support"""
    logger.info("📦 Installing PyTorch with GPU support...")
    
    # PyTorch installation command for CUDA
    pytorch_cmd = [
        sys.executable, "-m", "pip", "install", 
        "torch", "torchvision", "torchaudio", 
        "--index-url", "https://download.pytorch.org/whl/cu118"
    ]
    
    try:
        subprocess.check_call(pytorch_cmd)
        logger.info("✅ PyTorch with GPU support installed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install PyTorch GPU: {e}")
        
        # Fallback to CPU version
        logger.info("🔄 Installing CPU version as fallback...")
        cpu_cmd = [sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio"]
        try:
            subprocess.check_call(cpu_cmd)
            logger.info("✅ PyTorch CPU version installed")
            return True
        except subprocess.CalledProcessError as e2:
            logger.error(f"❌ Failed to install PyTorch CPU: {e2}")
            return False

def install_whisper():
    """Install OpenAI Whisper"""
    logger.info("📦 Installing OpenAI Whisper...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
        logger.info("✅ Whisper installed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install Whisper: {e}")
        return False

def install_audio_dependencies():
    """Install audio processing dependencies"""
    logger.info("📦 Installing audio dependencies...")
    
    audio_packages = [
        "sounddevice",
        "soundfile", 
        "librosa",
        "numpy",
        "scipy"
    ]
    
    success_count = 0
    for package in audio_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            logger.info(f"✅ {package} installed")
            success_count += 1
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install {package}: {e}")
    
    return success_count == len(audio_packages)

def test_gpu_installation():
    """Test if GPU installation is working"""
    logger.info("🧪 Testing GPU installation...")
    
    try:
        import torch
        logger.info(f"✅ PyTorch version: {torch.__version__}")
        
        if torch.cuda.is_available():
            logger.info(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
            logger.info(f"✅ CUDA version: {torch.version.cuda}")
            return True
        else:
            logger.warning("⚠️ CUDA not available, using CPU")
            return False
            
    except ImportError as e:
        logger.error(f"❌ PyTorch import failed: {e}")
        return False

def test_whisper_installation():
    """Test if Whisper installation is working"""
    logger.info("🧪 Testing Whisper installation...")
    
    try:
        import whisper
        logger.info("✅ Whisper imported successfully")
        
        # Test loading a small model
        model = whisper.load_model("base")
        logger.info("✅ Whisper model loaded successfully")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Whisper import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Whisper model loading failed: {e}")
        return False

def test_audio_installation():
    """Test if audio dependencies are working"""
    logger.info("🧪 Testing audio installation...")
    
    try:
        import sounddevice as sd
        import soundfile as sf
        import numpy as np
        
        logger.info("✅ Audio libraries imported successfully")
        
        # Test microphone detection
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        logger.info(f"✅ Found {len(input_devices)} input devices")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Audio libraries import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Audio test failed: {e}")
        return False

def main():
    """Main installation function"""
    logger.info("🎖️ Army Mental Health - GPU Voice Processing Installation")
    logger.info("=" * 70)
    
    # Check system
    logger.info(f"🖥️ System: {platform.system()} {platform.release()}")
    logger.info(f"🐍 Python: {sys.version}")
    
    # Check GPU
    gpu_available = check_gpu_availability()
    
    # Install components
    logger.info("\n📦 Installing components...")
    
    # 1. Install PyTorch
    pytorch_success = install_pytorch_gpu() if gpu_available else install_pytorch_gpu()
    
    # 2. Install Whisper
    whisper_success = install_whisper()
    
    # 3. Install audio dependencies
    audio_success = install_audio_dependencies()
    
    # Test installations
    logger.info("\n🧪 Testing installations...")
    
    gpu_test = test_gpu_installation()
    whisper_test = test_whisper_installation()
    audio_test = test_audio_installation()
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("📊 Installation Summary:")
    logger.info(f"   PyTorch: {'✅' if pytorch_success else '❌'}")
    logger.info(f"   GPU Support: {'✅' if gpu_test else '❌'}")
    logger.info(f"   Whisper: {'✅' if whisper_success else '❌'}")
    logger.info(f"   Audio: {'✅' if audio_success else '❌'}")
    
    if all([pytorch_success, whisper_success, audio_success]):
        logger.info("\n🎉 Installation completed successfully!")
        logger.info("🚀 GPU-powered voice processing is ready!")
        
        if gpu_test:
            logger.info("⚡ GPU acceleration enabled")
        else:
            logger.info("🔄 Using CPU (GPU not available)")
        
        logger.info("\n📝 Next steps:")
        logger.info("   1. Run: python3 run.py")
        logger.info("   2. Test voice input in the application")
        logger.info("   3. Try Hinglish voice-to-text conversion")
        
        return True
    else:
        logger.error("\n❌ Installation failed!")
        logger.error("💡 Try running with administrator privileges")
        logger.error("💡 Check internet connection")
        logger.error("💡 Ensure CUDA drivers are installed for GPU support")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
