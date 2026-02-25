import subprocess
import sys
import os

def install_dependencies():
    """Install all required dependencies"""
    print("🔧 Installing Grammar-Corrected Captioner...")
    
    packages = [
        "openai-whisper",
        "torch",
        "speechrecognition", 
        "pyaudio",
        "language-tool-python",
        "numpy"
    ]
    
    for package in packages:
        print(f"📦 Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed!")
        except Exception as e:
            print(f"❌ Failed to install {package}: {e}")
    
    # Linux audio dependencies
    if os.name == 'posix' and os.uname().sysname == 'Linux':
        print("🐧 Installing Linux audio dependencies...")
        try:
            subprocess.check_call(["sudo", "apt", "install", "portaudio19-dev", "python3-pyaudio", "-y"])
        except:
            print("⚠️  Manual installation may be required for audio")
    
    print("\n🎉 Installation complete!")
    print("🚀 Run: python grammar_corrected_captioner.py")

if __name__ == "__main__":
    install_dependencies()