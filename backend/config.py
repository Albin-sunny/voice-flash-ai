# config.py
# This file loads all environment variables and defines app-wide constants

import os
from dotenv import load_dotenv

# Load the .env file so our keys become available
load_dotenv()

# ── API Keys ──────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── Groq Model Settings ───────────────────────────────────
GROQ_LLM_MODEL = "llama-3.1-8b-instant"     # used for flashcard generation + scoring
GROQ_WHISPER_MODEL = "whisper-large-v3" # used for speech-to-text transcription

# ── Recording Settings ────────────────────────────────────
RECORDING_DURATION = 10         # seconds to record when user speaks
SAMPLE_RATE = 44100             # standard audio sample rate

# ── Flashcard Settings ────────────────────────────────────
MIN_FLASHCARDS = 3              # minimum Q&A pairs to generate
MAX_FLASHCARDS = 10             # maximum Q&A pairs to generate

# ── File Paths ────────────────────────────────────────────
AUDIO_DIR = "assets/audio"      # where temp recordings are saved
UPLOAD_DIR = "assets/uploads"   # where uploaded files are saved