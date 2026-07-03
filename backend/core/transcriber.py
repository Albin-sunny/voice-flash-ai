import whisper
import os

whisper_model = None


def load_whisper_model(model_size="base"):
    global whisper_model
    if whisper_model is None:
        print("Loading Whisper model...")
        whisper_model = whisper.load_model(model_size)
        print("Whisper model loaded")
    return whisper_model


def transcribe_audio(audio_file_path):
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    model = load_whisper_model("base")
    print(f"Transcribing: {audio_file_path}")
    try:
        result = model.transcribe(audio_file_path)
        text = result["text"].strip()
        print(f"Done: {text}")
        return text
    except Exception as e:
        print(f"Error: {e}")
        raise


def get_transcription_confidence(audio_file_path):
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    model = load_whisper_model("base")
    try:
        result = model.transcribe(audio_file_path)
        return {
            "text": result["text"].strip(),
            "segments": result["segments"]
        }
    except Exception as e:
        print(f"Error: {e}")
        raise