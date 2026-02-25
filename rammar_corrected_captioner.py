import whisper
import speech_recognition as sr
import pyaudio
import threading
import time
import os
from datetime import datetime
import tempfile
import wave
import language_tool_python
import re
from collections import deque
import numpy as np

class GrammarCorrectedCaptioner:
    def __init__(self, model_size="base"):
        """
        Real-time captioner with instant grammar correction
        """
        print("🚀 Loading AI models...")
        
        # Load Whisper model
        self.model = whisper.load_model(model_size)
        print(f"✅ Whisper {model_size} model loaded!")
        
        # Load grammar correction tool
        try:
            self.grammar_tool = language_tool_python.LanguageTool('en-US')
            print("✅ Grammar correction engine loaded!")
        except Exception as e:
            print(f"❌ Grammar tool failed: {e}")
            self.grammar_tool = None
        
        self.is_running = True
        self.captions = deque(maxlen=10)  # Keep last 10 captions
        self.console_width = 80
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_duration = 4  # Process every 4 seconds
        
        # Grammar correction settings
        self.correction_enabled = True
        self.min_confidence_length = 3  # Minimum words to apply correction

    def correct_grammar_realtime(self, text):
        """
        Fast grammar correction optimized for real-time use
        """
        if not self.correction_enabled or not text.strip():
            return text
        
        if len(text.split()) < self.min_confidence_length:
            return text  # Too short for reliable correction
        
        try:
            # Quick grammar check with timeout
            matches = self.grammar_tool.check(text)
            
            if matches:
                # Apply corrections
                corrected = language_tool_python.utils.correct(text, matches)
                
                # Only return correction if it's significantly better
                if self.is_better_correction(text, corrected):
                    return corrected
            
            return text
            
        except Exception as e:
            # If grammar correction fails, return original text
            return text

    def is_better_correction(self, original, corrected):
        """
        Check if the correction is actually better
        """
        if original == corrected:
            return False
        
        # Count punctuation and capitalization as improvements
        orig_punct = len(re.findall(r'[.!?]', original))
        corr_punct = len(re.findall(r'[.!?]', corrected))
        
        # If correction adds proper punctuation, it's better
        if corr_punct > orig_punct:
            return True
        
        # If correction fixes obvious errors
        common_errors = {
            'your': 'you\'re', 'there': 'their', 'its': 'it\'s',
            'then': 'than', 'effect': 'affect', 'accept': 'except'
        }
        
        for wrong, right in common_errors.items():
            if wrong in original.lower() and right in corrected.lower():
                return True
        
        # Default: trust the correction for significant changes
        return len(corrected) > len(original) * 0.8  # Not too shortened

    def smart_capitalization(self, text):
        """
        Apply smart capitalization to sentences
        """
        if not text.strip():
            return text
        
        # Split into sentences
        sentences = re.split(r'[.!?]', text)
        corrected_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Capitalize first letter
                sentence = sentence[0].upper() + sentence[1:] if sentence else sentence
                corrected_sentences.append(sentence)
        
        # Join with proper punctuation
        result = '. '.join(corrected_sentences)
        if result and not result.endswith(('.', '!', '?')):
            result += '.'
        
        return result

    def enhance_transcription(self, text):
        """
        Apply multiple enhancement layers to transcription
        """
        if not text.strip():
            return text
        
        enhanced = text
        
        # Step 1: Grammar correction
        if self.grammar_tool:
            enhanced = self.correct_grammar_realtime(enhanced)
        
        # Step 2: Smart capitalization
        enhanced = self.smart_capitalization(enhanced)
        
        # Step 3: Remove extra spaces
        enhanced = re.sub(r'\s+', ' ', enhanced).strip()
        
        return enhanced

    def transcribe_audio(self, audio_data):
        """Transcribe audio using Whisper with enhancements"""
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(audio_data)
                
                # Transcribe with Whisper
                result = self.model.transcribe(
                    temp_file.name,
                    language='en',
                    fp16=False
                )
                
            os.unlink(temp_file.name)
            
            original_text = result["text"].strip()
            
            if original_text:
                # Apply grammar correction and enhancements
                enhanced_text = self.enhance_transcription(original_text)
                return original_text, enhanced_text
            
            return "", ""
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return "", ""

    def capture_audio_chunks(self):
        """Capture and process audio in real-time"""
        print("🎤 Starting real-time audio capture with grammar correction...")
        
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024
        )
        
        audio_buffer = b""
        chunk_size = self.sample_rate * self.chunk_duration
        
        while self.is_running:
            try:
                data = stream.read(1024, exception_on_overflow=False)
                audio_buffer += data
                
                if len(audio_buffer) >= chunk_size:
                    # Transcribe current chunk
                    original_text, corrected_text = self.transcribe_audio(audio_buffer[:chunk_size])
                    
                    if original_text:
                        caption = {
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'original': original_text,
                            'corrected': corrected_text,
                            'time': time.time(),
                            'was_corrected': original_text != corrected_text
                        }
                        
                        self.captions.append(caption)
                        
                        # Show real-time output
                        if caption['was_corrected']:
                            print(f"🔧 [{caption['timestamp']}] CORRECTED: {corrected_text}")
                            print(f"   📝 Original: {original_text}")
                        else:
                            print(f"✅ [{caption['timestamp']}] {corrected_text}")
                    
                    # Keep 50% overlap for continuity
                    audio_buffer = audio_buffer[chunk_size//2:]
                    
            except Exception as e:
                print(f"❌ Audio processing error: {e}")
                time.sleep(0.1)
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    def display_enhanced_interface(self):
        """Display with grammar correction highlights"""
        while self.is_running:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🎯 GRAMMAR-CORRECTED LIVE CAPTIONER")
            print("=" * self.console_width)
            print("🔧 Real-time Grammar Correction • Auto-Punctuation • Smart Capitalization")
            print("=" * self.console_width)
            print(f"🕒 {datetime.now().strftime('%H:%M:%S')} | 🎤 Live + Grammar Fixes")
            print("-" * self.console_width)
            
            if not self.captions:
                print("\n" * 4)
                print("🔇 Waiting for audio input...")
                print("💡 Speak naturally - grammar will be auto-corrected!")
            else:
                # Display recent captions with correction highlights
                for caption in list(self.captions)[-8:]:  # Show last 8
                    seconds_ago = time.time() - caption['time']
                    time_ago = f"{int(seconds_ago)}s ago"
                    
                    if caption['was_corrected']:
                        print(f"🔧 [{caption['timestamp']}] ({time_ago})")
                        print(f"   📝 {caption['corrected']}")
                        print(f"   ⚠️  Original: {caption['original']}")
                    else:
                        print(f"✅ [{caption['timestamp']}] ({time_ago}): {caption['corrected']}")
                    print()
            
            print("=" * self.console_width)
            print("🎛️  Controls: [C]orrection On/Off • [Q]uit • [R]eset")
            
            time.sleep(0.3)

    def transcribe_file_with_correction(self, file_path):
        """Transcribe file with advanced grammar correction"""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return
        
        print(f"📁 Transcribing with grammar correction: {file_path}")
        
        # Transcribe with Whisper
        result = self.model.transcribe(
            file_path,
            language='en',
            beam_size=5,
            best_of=3
        )
        
        original_text = result["text"]
        
        print("\n" + "="*60)
        print("📝 ORIGINAL TRANSCRIPTION:")
        print("="*60)
        print(original_text)
        
        # Apply enhanced grammar correction
        corrected_text = self.enhance_transcription(original_text)
        
        print("\n" + "="*60)
        print("🔧 GRAMMAR-CORRECTED VERSION:")
        print("="*60)
        print(corrected_text)
        print("="*60)
        
        # Save both versions
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        with open(f'{base_name}_original.txt', 'w', encoding='utf-8') as f:
            f.write(original_text)
        
        with open(f'{base_name}_corrected.txt', 'w', encoding='utf-8') as f:
            f.write(corrected_text)
        
        print(f"💾 Saved: {base_name}_original.txt")
        print(f"💾 Saved: {base_name}_corrected.txt")

    def handle_user_input(self):
        """Handle real-time user commands"""
        try:
            while self.is_running:
                try:
                    # Non-blocking input check
                    if os.name == 'nt':  # Windows
                        import msvcrt
                        if msvcrt.kbhit():
                            cmd = msvcrt.getch().decode().lower()
                            self.process_command(cmd)
                    else:  # Linux/Mac
                        import select
                        import sys
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            cmd = sys.stdin.readline().strip().lower()
                            self.process_command(cmd)
                    
                    time.sleep(0.1)
                except:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            self.is_running = False

    def process_command(self, cmd):
        """Process user commands"""
        if cmd == 'q':
            self.is_running = False
            print("\n🛑 Stopping captioner...")
        elif cmd == 'c':
            self.correction_enabled = not self.correction_enabled
            status = "ENABLED" if self.correction_enabled else "DISABLED"
            print(f"\n🔧 Grammar correction {status}")
        elif cmd == 'r':
            self.captions.clear()
            print("\n🔄 Captions cleared")

    def start_live_captioning(self):
        """Start live grammar-corrected captioning"""
        print("🎤 Starting LIVE grammar-corrected captioning...")
        print("💡 Speaking will be auto-corrected in real-time!")
        
        # Start display thread
        display_thread = threading.Thread(target=self.display_enhanced_interface)
        display_thread.daemon = True
        display_thread.start()
        
        # Start input handler thread
        input_thread = threading.Thread(target=self.handle_user_input)
        input_thread.daemon = True
        input_thread.start()
        
        try:
            # Start audio processing (blocks)
            self.capture_audio_chunks()
        except KeyboardInterrupt:
            print("\n🛑 Stopping captioner...")
        finally:
            self.is_running = False

def main():
    print("🎯 GRAMMAR-CORRECTED AI CAPTIONER")
    print("=" * 50)
    print("Choose mode:")
    print("1. 🎤 Live Microphone (Real-time Grammar Correction)")
    print("2. 📁 Transcribe File (With Grammar Fixes)")
    
    choice = input("Enter choice (1-2): ").strip()
    
    print("\nChoose model size:")
    print("1. Base (Fast, decent accuracy)")
    print("2. Small (Better accuracy)")
    print("3. Medium (High accuracy)")
    print("4. Large (Best accuracy, slow)")
    
    model_choice = input("Enter choice (1-4, default 2): ").strip() or "2"
    model_sizes = {"1": "base", "2": "small", "3": "medium", "4": "large"}
    model_size = model_sizes.get(model_choice, "small")
    
    # Install language-tool if not available
    try:
        import language_tool_python
    except ImportError:
        print("📦 Installing grammar correction engine...")
        os.system("pip install language-tool-python")
        import language_tool_python
    
    captioner = GrammarCorrectedCaptioner(model_size=model_size)
    
    if choice == "1":
        captioner.start_live_captioning()
    else:
        file_path = input("Enter audio/video file path: ").strip().strip("'")
        captioner.transcribe_file_with_correction(file_path)

if __name__ == "__main__":
    main()