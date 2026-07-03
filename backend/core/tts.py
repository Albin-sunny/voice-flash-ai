# core/tts.py
# This file handles text-to-speech using gTTS (Google Text-to-Speech)

from gtts import gTTS
import os
from config import AUDIO_DIR
from core.audio import play_audio
import subprocess

def text_to_speech(text: str, filename: str = "output_speech.mp3", play: bool = True) -> str:
    """
    Converts text to speech and saves it as an audio file.
    
    Args:
        text: The text to convert to speech
        filename: Name of the file to save (default: output_speech.mp3)
        play: Whether to play the audio after generating it (default: True)
    
    Returns:
        Full path to the saved audio file
    """
    
    # Create assets/audio directory if it doesn't exist
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    file_path = os.path.join(AUDIO_DIR, filename)
    
    print(f"🎙️ Converting text to speech...")
    
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to MP3 file
        tts.save(file_path)
        
        print(f"✅ Speech saved to {file_path}")
        
        # Play the audio if requested
        if play:
            play_audio_file(file_path)
        
        return file_path
        
    except Exception as e:
        print(f"❌ Error converting text to speech: {e}")
        raise


def play_audio_file(file_path: str) -> None:
    """
    Plays an MP3 audio file using the system's default player.
    
    Args:
        file_path: Full path to the audio file (MP3 or WAV)
    """
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    try:
        print(f"🔊 Playing audio...")
        
        # Use the system's default media player
        # For Windows
        if os.name == 'nt':
            os.startfile(file_path)
        # For macOS
        elif os.name == 'posix' and 'darwin' in os.sys.platform:
            subprocess.Popen(['afplay', file_path])
        # For Linux
        else:
            subprocess.Popen(['aplay', file_path])
        
        print("✅ Audio is playing")
        
    except Exception as e:
        print(f"⚠️ Could not play audio: {e}")
        print(f"   Saved to: {file_path}")


def batch_text_to_speech(texts: list) -> list:
    """
    Converts multiple text strings to speech files.
    Useful for generating all flashcard questions at once.
    
    Args:
        texts: List of text strings to convert
    
    Returns:
        List of file paths to the generated audio files
    """
    
    file_paths = []
    
    for i, text in enumerate(texts):
        filename = f"speech_{i}.mp3"
        
        try:
            file_path = text_to_speech(text, filename=filename, play=False)
            file_paths.append(file_path)
            
        except Exception as e:
            print(f"⚠️ Error generating speech for text {i}: {e}")
            continue
    
    print(f"✅ Generated {len(file_paths)} speech files")
    return file_paths