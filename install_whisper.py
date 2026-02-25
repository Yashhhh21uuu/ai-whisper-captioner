import sys
import subprocess
import os

def install_whisper():
    """Easy installer for Whisper and dependencies"""
    print("🔧 Installing OpenAI Whisper and dependencies...")
    
    # Check if Python is available
    try:
        subprocess.check_call([sys.executable, "--version"])
    except:
        print("❌ Python not found. Please install Python 3.8+ first.")
        return False
    
    packages = [
        "openai-whisper",
        "torch",
        "speechrecognition",
        "pyaudio"
    ]
    
    for package in packages:
        print(f"📦 Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully!")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
    
    # Additional system dependencies for Linux
    if os.name == 'posix' and os.uname().sysname == 'Linux':
        print("🐧 Installing Linux audio dependencies...")
        try:
            subprocess.check_call(["sudo", "apt", "update"])
            subprocess.check_call(["sudo", "apt", "install", "portaudio19-dev", "python3-pyaudio"])
        except:
            print("⚠️  Could not install system dependencies. You may need to install them manually.")
    
    print("\n🎉 Installation complete!")
    print("🚀 Run: python whisper_captioner.py")
    return True

if __name__ == "__main__":
    install_whisper()