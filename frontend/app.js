// app.js
// Handles all frontend logic and API calls to FastAPI backend

const API_BASE = "http://127.0.0.1:8000";

// ── App State ─────────────────────────────────────────────
let state = {
    notes: "",
    flashcards: [],
    currentCardIndex: 0,
    userAnswers: [],
    mediaRecorder: null,
    audioChunks: [],
    recordedBlob: null,
    isRecording: false
};


// ══════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ══════════════════════════════════════════════════════════

function showLoading(message = "Loading...") {
    document.getElementById("loading-overlay").classList.remove("hidden");
    document.getElementById("loading-text").textContent = message;
}

function hideLoading() {
    document.getElementById("loading-overlay").classList.add("hidden");
}

function showSection(sectionId) {
    document.querySelectorAll("section").forEach(s => s.classList.add("hidden"));
    document.getElementById(sectionId).classList.remove("hidden");
}

function switchTab(tab) {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

    document.getElementById(`tab-${tab}`).classList.add("active");
    event.target.classList.add("active");
}


// ══════════════════════════════════════════════════════════
// STEP 1: NOTES
// ══════════════════════════════════════════════════════════

async function handleFileUpload() {
    const fileInput = document.getElementById("file-input");
    const file = fileInput.files[0];

    console.log("File selected:", file);

    if (!file) return;

    showLoading("📖 Reading your file...");

    try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_BASE}/upload-notes`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            console.log("Upload success! Data:", data);
            state.notes = data.notes;
            document.getElementById("upload-status").innerHTML =
                `<p class="success-text">✅ Extracted ${data.character_count} characters!</p>`;
            showNotesReady();
        } else {
            document.getElementById("upload-status").innerHTML =
                `<p class="error-text">❌ Error: ${data.error}</p>`;
        }

    } catch (error) {
        document.getElementById("upload-status").innerHTML =
            `<p class="error-text">❌ Error: ${error.message}</p>`;
    } finally {
        hideLoading();
    }
}


function saveTypedNotes() {
    const notes = document.getElementById("typed-notes").value.trim();

    if (!notes) {
        alert("Please type some notes first!");
        return;
    }

    state.notes = notes;
    showNotesReady();
}


function showNotesReady() {
    console.log("Notes ready! Length:", state.notes.length);
    document.getElementById("notes-char-count").textContent = state.notes.length;
    document.getElementById("notes-preview").classList.remove("hidden");
    console.log("Preview shown!");
}


function goToStep2() {
    showSection("section-flashcards");
}


// ══════════════════════════════════════════════════════════
// STEP 2: GENERATE FLASHCARDS
// ══════════════════════════════════════════════════════════

async function generateFlashcards() {
    const numCards = document.getElementById("num-cards").value;

    showLoading("🤖 AI is generating your flashcards...");

    try {
        const formData = new FormData();
        formData.append("notes", state.notes);
        formData.append("num_cards", numCards);

        const response = await fetch(`${API_BASE}/generate-flashcards`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            state.flashcards = data.flashcards;

            document.getElementById("flashcard-status").innerHTML =
                `<p class="success-text">✅ Generated ${data.count} flashcards!</p>`;

            // Show preview
            const list = document.getElementById("flashcard-list");
            list.innerHTML = "";

            data.flashcards.forEach((card, i) => {
                list.innerHTML += `
                    <div class="flashcard-item">
                        <span>Card ${i + 1}:</span> ${card.question}
                    </div>`;
            });

            document.getElementById("flashcard-preview").classList.remove("hidden");

        } else {
            document.getElementById("flashcard-status").innerHTML =
                `<p class="error-text">❌ Error: ${data.error}</p>`;
        }

    } catch (error) {
        document.getElementById("flashcard-status").innerHTML =
            `<p class="error-text">❌ Error: ${error.message}</p>`;
    } finally {
        hideLoading();
    }
}


// ══════════════════════════════════════════════════════════
// STEP 3: QUIZ
// ══════════════════════════════════════════════════════════

function startQuiz() {
    state.currentCardIndex = 0;
    state.userAnswers = [];
    showSection("section-quiz");
    loadCurrentCard();
}


function loadCurrentCard() {
    const card = state.flashcards[state.currentCardIndex];
    const total = state.flashcards.length;
    const current = state.currentCardIndex + 1;

    // Update progress
    const percent = ((current - 1) / total) * 100;
    document.getElementById("progress-bar").style.width = `${percent}%`;
    document.getElementById("progress-text").textContent = `Card ${current} of ${total}`;

    // Update question
    document.getElementById("quiz-question").textContent = `❓ ${card.question}`;

    // Reset answer section
    document.getElementById("recording-status").textContent = "";
    document.getElementById("transcribed-answer").classList.add("hidden");
    document.getElementById("answer-text").textContent = "";
    document.getElementById("question-audio").classList.add("hidden");

    // Reset buttons
    document.getElementById("btn-start").disabled = false;
    document.getElementById("btn-stop").disabled = true;

    // Reset recorded blob
    state.recordedBlob = null;
    state.audioChunks = [];
}


async function readQuestionAloud() {
    const card = state.flashcards[state.currentCardIndex];

    showLoading("🔊 Generating speech...");

    try {
        const formData = new FormData();
        formData.append("text", card.question);
        formData.append("filename", `question_${state.currentCardIndex}.mp3`);

        const response = await fetch(`${API_BASE}/text-to-speech`, {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const audioUrl = URL.createObjectURL(blob);

            const audio = document.getElementById("question-audio");
            audio.src = audioUrl;
            audio.classList.remove("hidden");
            audio.play();
        }

    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}


// ── Recording ─────────────────────────────────────────────

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        state.audioChunks = [];
        state.mediaRecorder = new MediaRecorder(stream);

        state.mediaRecorder.ondataavailable = (event) => {
            state.audioChunks.push(event.data);
        };

        state.mediaRecorder.start();
        state.isRecording = true;

        // Update UI
        document.getElementById("btn-start").disabled = true;
        document.getElementById("btn-stop").disabled = false;
        document.getElementById("recording-status").textContent = "🔴 Recording... Click Stop when done!";

    } catch (error) {
        alert("❌ Microphone access denied. Please allow microphone access.");
    }
}


async function stopRecording() {
    if (!state.mediaRecorder) return;

    state.mediaRecorder.stop();
    state.isRecording = false;

    state.mediaRecorder.onstop = async () => {
        // Stop all tracks
        state.mediaRecorder.stream.getTracks().forEach(track => track.stop());

        // Create audio blob
        state.recordedBlob = new Blob(state.audioChunks, { type: "audio/webm" });

        document.getElementById("recording-status").textContent = "✅ Recording saved! Transcribing...";

        // Transcribe immediately
        await transcribeAnswer();
    };

    // Update buttons
    document.getElementById("btn-start").disabled = false;
    document.getElementById("btn-stop").disabled = true;
}


async function transcribeAnswer() {
    if (!state.recordedBlob) return;

    showLoading("🎙️ Transcribing your answer...");

    try {
        const formData = new FormData();
        formData.append("file", state.recordedBlob, "answer.webm");

        const response = await fetch(`${API_BASE}/transcribe`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById("answer-text").textContent = data.text;
            document.getElementById("transcribed-answer").classList.remove("hidden");
            document.getElementById("recording-status").textContent = "";
        } else {
            document.getElementById("recording-status").textContent = `❌ Error: ${data.error}`;
        }

    } catch (error) {
        document.getElementById("recording-status").textContent = `❌ Error: ${error.message}`;
    } finally {
        hideLoading();
    }
}


async function submitAnswer() {
    const answer = document.getElementById("answer-text").textContent;

    if (!answer) {
        alert("No answer recorded!");
        return;
    }

    // Save answer
    state.userAnswers.push(answer);

    // Move to next card or finish
    if (state.currentCardIndex >= state.flashcards.length - 1) {
        // Last card — score everything
        await scoreAllAnswers();
    } else {
        state.currentCardIndex++;
        loadCurrentCard();
    }
}


// ══════════════════════════════════════════════════════════
// STEP 4: RESULTS
// ══════════════════════════════════════════════════════════

async function scoreAllAnswers() {
    showLoading("🤖 AI is scoring your answers...");

    try {
        const formData = new FormData();
        formData.append("flashcards", JSON.stringify(state.flashcards));
        formData.append("user_answers", JSON.stringify(state.userAnswers));

        const response = await fetch(`${API_BASE}/score-answers`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showResults(data.scores, data.overall);
        } else {
            alert(`❌ Scoring error: ${data.error}`);
        }

    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}


function showResults(scores, overall) {
    showSection("section-results");

    // Overall scores
    document.getElementById("overall-score").textContent = `${overall.average_score}/100`;
    document.getElementById("correct-count").textContent = `${overall.correct_count}/${overall.total_cards}`;
    document.getElementById("percentage").textContent = `${overall.percentage}%`;

    // Performance message
    const msgEl = document.getElementById("performance-message");
    if (overall.percentage >= 90) {
        msgEl.className = "msg-success";
        msgEl.textContent = "🌟 Outstanding! You really know your stuff!";
    } else if (overall.percentage >= 75) {
        msgEl.className = "msg-success";
        msgEl.textContent = "🎉 Great job! You did really well!";
    } else if (overall.percentage >= 60) {
        msgEl.className = "msg-warning";
        msgEl.textContent = "📚 Good effort! A bit more review would help.";
    } else {
        msgEl.className = "msg-error";
        msgEl.textContent = "💪 Keep studying! You'll get there!";
    }

    // Detailed breakdown
    const breakdown = document.getElementById("results-breakdown");
    breakdown.innerHTML = "";

    scores.forEach((score, i) => {
        breakdown.innerHTML += `
            <div class="result-card ${score.is_correct ? 'correct' : 'incorrect'}">
                <h4>Card ${i + 1}: ${score.score}/100 ${score.is_correct ? '✅' : '❌'}</h4>
                <p>❓ <span>${score.question}</span></p>
                <p>✅ Expected: <span>${score.correct_answer}</span></p>
                <p>🎤 You said: <span>${score.user_answer}</span></p>
                <p>💬 Feedback: <span>${score.feedback}</span></p>
            </div>`;
    });
}


function retakeQuiz() {
    state.currentCardIndex = 0;
    state.userAnswers = [];
    showSection("section-quiz");
    loadCurrentCard();
}


function startFresh() {
    state = {
        notes: "",
        flashcards: [],
        currentCardIndex: 0,
        userAnswers: [],
        mediaRecorder: null,
        audioChunks: [],
        recordedBlob: null,
        isRecording: false
    };

    // Reset all UI
    document.getElementById("upload-status").innerHTML = "";
    document.getElementById("flashcard-status").innerHTML = "";
    document.getElementById("notes-preview").classList.add("hidden");
    document.getElementById("flashcard-preview").classList.add("hidden");
    document.getElementById("typed-notes").value = "";

    showSection("section-upload");
}