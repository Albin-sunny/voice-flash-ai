🎓 Voice Flash AI (voice-flash-ai)
An end-to-end multimodal audio learning platform that turns static study materials into interactive, voice-driven oral examinations. Powered by FastAPI, OpenAI Whisper, and Groq Llama-3.1-8b, the application extracts text from uploaded study documents, synthesizes targeted flashcard decks, reads questions aloud via text-to-speech, captures vocal student responses directly in the browser, and grades answers using an LLM-as-a-judge semantic evaluation engine.
📸 Interface & Workflow
| Deck Generation & Configuration | Interactive Voice Quiz & Evaluation |
|---|---|
|  |  |
| Document ingest, text normalization, flashcard count slider, and real-time generation preview | Audio playback, live microphone recording, Whisper transcription, and 0-100 semantic grading |
> Note: Save your application screenshots inside a frontend/assets/ directory as screenshot_flashcards.png and screenshot_quiz.png.
> 
⚙️ System Architecture
                      [ User Study Documents ]
                         (.pdf or .txt file)
                                  │
                                  ▼
                         [ FastAPI Gateway ]
                         (/upload-notes API)
                                  │
                                  ▼
                        [ Text Normalization ]
                       (PyPDF2 / clean_text)
                                  │
                                  ▼
                      [ Flashcard Synthesizer ]
                     (/generate-flashcards API)
                     (Groq Llama-3.1-8b-Instant)
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │  Interactive Oral Loop   │
                    └─────────────┬─────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         │ (Question Audio)                                │ (Answer Recording)
         ▼                                                 ▼
[ Text-to-Speech Engine ]                       [ Browser MediaRecorder API ]
    (/text-to-speech)                            (Raw Audio Stream: WebM)
   (gTTS + FileResponse)                                   │
         │                                                 ▼
         ▼                                      [ Whisper Transcription ]
[ Native Audio Playback ]                             (/transcribe API)
 (HTML5 Audio Controller)                         (Local Whisper Base ASR)
                                                           │
                                                           ▼
                                                [ Semantic Answer Text ]
                                                           │
         ┌─────────────────────────────────────────────────┘
         ▼
[ LLM Semantic Grading Engine ]
     (/score-answers API)
  (Groq Llama-3.1-8b-Instant)
- Evaluates Meaning (0–100 Scale)
- Rejects Rigid String Equality
- Produces Targeted Actionable Feedback
         │
         ▼
[ Cumulative Quiz Audit ]
- Percentage Score
- Correct / Incorrect Matrix
- Expected vs. Spoken Breakdown

🚀 Key Highlights
 * End-to-End Voice Cycle: Captures student audio directly in the browser via the native MediaRecorder API, streams binary audio payloads to FastAPI, transcribes speech with OpenAI Whisper, and delivers synthesized audio prompts using gTTS (Google Text-to-Speech).
 * Semantic Grading Engine (0–100 Rubric): Replaces rigid string comparisons with an LLM evaluation pipeline powered by Llama-3.1-8b. Spoken answers are scored on conceptual accuracy, returning an exact score, pass/fail status, and targeted feedback.
 * Automated Curriculum Ingestion: Parses text directly from .pdf and .txt files using PyPDF2, removes extraneous formatting characters, and formats content for token-efficient generation.
 * Resilient Deck Generation: Flashcard extraction enforces structured JSON array schemas with fallback retry routines to handle prompt output formatting errors automatically.
 * Lightweight Vanilla Frontend: Built using responsive HTML5, CSS3, and modern JavaScript to manage asynchronous file uploads, audio streams, progress metrics, and quiz lifecycles without heavy external frameworks.
📂 Repository Structure
voice-flash-ai/
├── backend/
│   ├── assets/
│   │   ├── audio/           # Stored temporary recording & synthesized audio files
│   │   └── uploads/         # Uploaded study notes and documents
│   ├── core/
│   │   ├── __init__.py
│   │   ├── audio.py         # Native audio recording & playback utilities
│   │   ├── flashcard_gen.py # LLM deck synthesis with retry wrappers
│   │   ├── pdf_reader.py    # PyPDF2 and raw text extraction utilities
│   │   ├── scorer.py        # 0–100 semantic grading and batch scoring engine
│   │   ├── transcriber.py   # OpenAI Whisper model loader and transcription logic
│   │   └── tts.py           # gTTS audio generation and batch speech synthesis
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py       # Text normalization, cleaning, and formatting helpers
│   ├── config.py            # App-wide constants, model IDs, and audio settings
│   ├── main.py              # FastAPI endpoints, CORS, and request handlers
│   └── requirements.txt     # Python backend dependencies
├── frontend/
│   ├── app.js               # Client API requests, MediaRecorder handling, and UI state
│   ├── index.html           # 4-step progressive quiz application interface
│   └── style.css            # Custom UI styling and responsive layouts
├── .gitattributes
├── .gitignore
└── README.md

🛠️ Installation & Setup
Prerequisites
 * Python 3.10+
 * Groq API Key (for Llama-3.1-8b inference)
 * FFmpeg installed and added to system PATH (required by OpenAI Whisper for audio file conversion)
 * Audio input (microphone) and output (speakers/headphones) devices
1. Clone & Environment Configuration
git clone https://github.com/Albin-sunny/voice-flash-ai.git
cd voice-flash-ai/backend

python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

2. Configure Environment Variables
Create a .env file inside the backend/ directory:
GROQ_API_KEY=your_groq_api_key_here

3. Start the Backend API
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

API documentation will be accessible at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
4. Launch the Frontend
Serve the frontend/ directory using Python's built-in web server or open index.html directly in your browser:
# From the project root in a second terminal:
cd frontend
python -m http.server 3000

Open [http://127.0.0.1:3000/](http://127.0.0.1:3000/) in a modern browser and allow microphone permissions when prompted.
📖 API Reference
1. Ingest Notes
Uploads a document and extracts clean text.
 * Endpoint: POST /upload-notes
 * Content-Type: multipart/form-data
 * Body: file: <binary_data> (.pdf, .txt)
2. Generate Flashcards
Generates a structured list of question-and-answer pairs.
 * Endpoint: POST /generate-flashcards
 * Content-Type: application/x-www-form-urlencoded
 * Fields: notes: string, num_cards: integer
3. Text-to-Speech
Synthesizes speech audio from written text.
 * Endpoint: POST /text-to-speech
 * Content-Type: application/x-www-form-urlencoded
 * Fields: text: string, filename: string
 * Response: Streaming audio file (audio/mpeg)
4. Speech-to-Text Transcription
Transcribes audio recordings using OpenAI Whisper.
 * Endpoint: POST /transcribe
 * Content-Type: multipart/form-data
 * Body: file: <binary_audio> (.wav, .webm, .mp3)
5. Semantic Scoring
Evaluates user answers against reference answers using semantic understanding.
 * Endpoint: POST /score-answers
 * Content-Type: application/x-www-form-urlencoded
 * Fields:
   * flashcards: Serialized JSON array of questions and target answers
   * user_answers: Serialized JSON array of transcribed answers
 * Response:
   {
  "success": true,
  "scores": [
    {
      "question": "What is an epoch in deep learning?",
      "correct_answer": "One complete pass of the entire training dataset through the model.",
      "user_answer": "It is when the whole training set goes through the algorithm once.",
      "score": 95,
      "is_correct": true,
      "feedback": "Accurate explanation demonstrating clear understanding of the full training pass concept."
    }
  ],
  "overall": {
    "total_cards": 1,
    "correct_count": 1,
    "average_score": 95,
    "percentage": 100.0
  }
}
