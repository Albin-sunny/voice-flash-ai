# core/audio.py
# This file handles microphone recording and audio playback

import sounddevice as sd
import scipy.io.wavfile as wavfile
import numpy as np
from config import RECORDING_DURATION, SAMPLE_RATE, AUDIO_DIR
import os

def record_audio(filename: str = "temp_recording.wav") -> str:
    """
    Records audio from the microphone for RECORDING_DURATION seconds.
    
    Args:
        filename: Name of the file to save (default: temp_recording.wav)
    
    Returns:
        Full path to the saved audio file
    """
    
    # Create assets/audio directory if it doesn't exist
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    file_path = os.path.join(AUDIO_DIR, filename)
    
    print(f"🎤 Recording for {RECORDING_DURATION} seconds...")
    
    try:
        # Record audio at the specified sample rate for the specified duration
        audio_data = sd.rec(
            int(SAMPLE_RATE * RECORDING_DURATION),  # number of frames to record
            samplerate=SAMPLE_RATE,
            channels=1,                              # mono audio (1 channel)
            dtype=np.int16                           # 16-bit audio quality
        )
        
        # Wait for recording to finish
        sd.wait()
        
        # Save the audio to a WAV file
        wavfile.write(file_path, SAMPLE_RATE, audio_data)
        
        print(f"✅ Recording saved to {file_path}")
        return file_path
        
    except Exception as e:
        print(f"❌ Error recording audio: {e}")
        raise


def play_audio(file_path: str) -> None:
    """
    Plays an audio file (used for gTTS text-to-speech).
    
    Args:
        file_path: Full path to the audio file to play
    """
    
    try:
        # Read the audio file
        sample_rate, audio_data = wavfile.read(file_path)
        
        print(f"🔊 Playing audio...")
        
        # Play the audio
        sd.play(audio_data, samplerate=sample_rate)
        
        # Wait for playback to finish
        sd.wait()
        
        print("✅ Playback finished")
        
    except Exception as e:
        print(f"❌ Error playing audio: {e}")
        raise


def cleanup_temp_files() -> None:
    """
    Deletes all temporary audio files from assets/audio directory.
    Call this when the quiz is done to clean up space.
    """
    
    try:
        if os.path.exists(AUDIO_DIR):
            for file in os.listdir(AUDIO_DIR):
                file_path = os.path.join(AUDIO_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            print(f"🧹 Cleaned up temporary audio files")
            
    except Exception as e:
        print(f"⚠️ Error cleaning up files: {e}")