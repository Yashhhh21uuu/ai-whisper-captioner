import whisper
import speech_recognition as sr
import pyaudio
import threading
import time
import os
from datetime import datetime
import tempfile
import wave

class FreeWhisperCaptioner:
    def __init__(self, model_size="base"):
        """
        Initialize free AI captioner using OpenAI Whisper
        model_size: "tiny", "base", "small", "medium", "large"
        """
        print("🚀 Loading OpenAI Whisper model...")
        self.model = whisper.load_model(model_size)
        print(f"✅ Whisper {model_size} model loaded successfully!")
        
        self.is_running = True
        self.captions = []
        self.max_captions = 8
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_duration = 3  # Process every 3 seconds
        
        self.console_width = 80

    def transcribe_audio(self, audio_data):
        """Transcribe audio using Whisper"""
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                # Write WAV file
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(audio_data)
                
                # Transcribe with Whisper
                result = self.model.transcribe(temp_file.name)
                
            # Clean up temp file
            os.unlink(temp_file.name)
            
            return result["text"]
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return ""

    def capture_audio_chunks(self):
        """Capture audio from microphone in chunks"""
        print("🎤 Starting audio capture...")
        print("💡 Speak into your microphone for real-time transcription!")
        
        p = pyaudio.PyAudio()
        
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024
        )
        
        audio_buffer = b""
        chunk_size = self.sample_rate * self.chunk_duration  # 3 seconds of audio
        
        while self.is_running:
            try:
                # Read audio data
                data = stream.read(1024, exception_on_overflow=False)
                audio_buffer += data
                
                # Process when we have enough audio
                if len(audio_buffer) >= chunk_size:
                    # Transcribe the chunk
                    text = self.transcribe_audio(audio_buffer[:chunk_size])
                    
                    if text.strip():
                        caption = {
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'text': text,
                            'time': time.time()
                        }
                        self.captions.append(caption)
                        
                        # Keep only recent captions
                        if len(self.captions) > self.max_captions:
                            self.captions.pop(0)
                        
                        print(f"🔊 [{caption['timestamp']}] {text}")
                    
                    # Keep remaining audio for next chunk (overlap for continuity)
                    audio_buffer = audio_buffer[chunk_size//2:]  # 50% overlap
                    
            except Exception as e:
                print(f"❌ Audio capture error: {e}")
                time.sleep(0.1)
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    def display_captions(self):
        """Display captions in real-time"""
        while self.is_running:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🎯 FREE AI CAPTIONER (OpenAI Whisper)")
            print("=" * self.console_width)
            print("💰 100% FREE • No API Keys • Offline Processing")
            print("=" * self.console_width)
            print(f"🕒 {datetime.now().strftime('%H:%M:%S')} | 🎤 Live Transcription")
            print("-" * self.console_width)
            
            if not self.captions:
                print("\n" * 3)
                print("🔇 Waiting for audio input...")
                print("💡 Start speaking to see real-time captions!")
            else:
                # Show empty lines for spacing
                empty_lines = self.max_captions - len(self.captions)
                for _ in range(empty_lines):
                    print()
                
                # Display recent captions
                for caption in self.captions:
                    seconds_ago = time.time() - caption['time']
                    time_ago = f"{int(seconds_ago)}s ago"
                    
                    print(f"🎯 [{caption['timestamp']}] ({time_ago}): {caption['text']}")
            
            print("=" * self.console_width)
            print("⏹️  Press Ctrl+C to stop")
            
            time.sleep(0.5)  # Update display every 0.5 seconds

    def transcribe_file(self, file_path):
        """Transcribe an existing audio/video file"""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return
        
        print(f"📁 Transcribing file: {file_path}")
        result = self.model.transcribe(file_path)
        
        print("\n" + "=" * 60)
        print("📝 TRANSCRIPTION RESULT:")
        print("=" * 60)
        print(result["text"])
        print("=" * 60)
        
        # Save to file
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = f"{base_name}_transcription.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        
        print(f"💾 Transcription saved to: {output_file}")

    def start_live_captioning(self):
        """Start live captioning from microphone"""
        print("🎤 Starting LIVE captioning...")
        
        # Start display thread
        display_thread = threading.Thread(target=self.display_captions)
        display_thread.daemon = True
        display_thread.start()
        
        try:
            # Start audio capture (blocks)
            self.capture_audio_chunks()
        except KeyboardInterrupt:
            print("\n🛑 Stopping captioner...")
        finally:
            self.is_running = False

def main():
    print("🎯 FREE AI CAPTIONER - OpenAI Whisper")
    print("=" * 50)
    print("Choose mode:")
    print("1. 🎤 Live Microphone Captioning (Real-time)")
    print("2. 📁 Transcribe Audio/Video File")
    print("3. 🎥 Video Meeting Captioning (System Audio)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    # Model size selection
    print("\nChoose model size (larger = more accurate, slower):")
    print("1. Tiny (Fastest)")
    print("2. Base (Recommended)")
    print("3. Small")
    print("4. Medium")
    print("5. Large (Most accurate, slowest)")
    
    model_choice = input("Enter choice (1-5, default 2): ").strip() or "2"
    model_sizes = {"1": "tiny", "2": "base", "3": "small", "4": "medium", "5": "large"}
    model_size = model_sizes.get(model_choice, "base")
    
    captioner = FreeWhisperCaptioner(model_size=model_size)
    
    if choice == "1":
        captioner.start_live_captioning()
    elif choice == "2":
        file_path = input("Enter audio/video file path: ").strip().strip("'")
        captioner.transcribe_file(file_path)
    elif choice == "3":
        # For system audio capture, we need additional setup
        print("🔧 System audio capture requires virtual audio cable setup.")
        print("Running in microphone mode instead...")
        captioner.start_live_captioning()
    else:
        captioner.start_live_captioning()

if __name__ == "__main__":
    main()