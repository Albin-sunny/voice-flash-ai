from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import shutil

from config import UPLOAD_DIR, AUDIO_DIR
from core.pdf_reader import extract_text
from core.flashcard_gen import generate_flashcards_with_retry
from core.scorer import score_answers_batch, calculate_overall_score
from core.tts import text_to_speech
from core.audio import record_audio, cleanup_temp_files
from core.transcriber import transcribe_audio
from utils.helpers import clean_text, ensure_directory_exists

# ── App Setup ─────────────────────────────────────────────
app = FastAPI(title="Voice Flashcard Quiz API")

# ── CORS ──────────────────────────────────────────────────
# Allows frontend HTML to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Ensure directories exist ──────────────────────────────
ensure_directory_exists(UPLOAD_DIR)
ensure_directory_exists(AUDIO_DIR)



@app.get("/")
def health_check():
    return {"status": "running", "message": "Voice Flashcard API is live!"}

@app.post("/upload-notes")
async def upload_notes(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Extract text
        notes = extract_text(file_path)
        notes = clean_text(notes)

        return {
            "success": True,
            "notes": notes,
            "character_count": len(notes)
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/generate-flashcards")
async def generate_flashcards(
    notes: str = Form(...),
    num_cards: int = Form(3)
):
    try:
        flashcards = generate_flashcards_with_retry(notes, num_cards=num_cards)

        return {
            "success": True,
            "flashcards": flashcards,
            "count": len(flashcards)
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/text-to-speech")
async def tts_endpoint(text: str = Form(...), filename: str = Form("question.mp3")):
    try:
        audio_path = text_to_speech(text, filename=filename, play=False)

        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            filename=filename
        )

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    try:
        # Save uploaded audio file
        audio_path = os.path.join(AUDIO_DIR, file.filename)

        with open(audio_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Transcribe
        text = transcribe_audio(audio_path)
        text = clean_text(text)

        return {
            "success": True,
            "text": text
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/score-answers")
async def score_endpoint(
    flashcards: str = Form(...),
    user_answers: str = Form(...)
):
    try:
        import json

        flashcards_list = json.loads(flashcards)
        answers_list = json.loads(user_answers)

        scores = score_answers_batch(flashcards_list, answers_list)
        overall = calculate_overall_score(scores)

        return {
            "success": True,
            "scores": scores,
            "overall": overall
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/cleanup")
def cleanup():
    try:
        cleanup_temp_files()
        return {"success": True, "message": "Temp files cleaned up"}
    except Exception as e:
        return {"success": False, "error": str(e)}