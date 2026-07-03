import os
import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_LLM_MODEL, MIN_FLASHCARDS, MAX_FLASHCARDS

client = Groq(api_key=GROQ_API_KEY)

def generate_flashcards(notes, num_cards=3):
    if num_cards > MAX_FLASHCARDS:
        num_cards = MAX_FLASHCARDS

    notes = notes[:1500]

    print(f"🧠 Generating {num_cards} flashcards from notes...")

    prompt = f"""Create {num_cards} flashcards from these notes as a JSON array only, no other text:
[{{"question": "...", "answer": "..."}}]

Notes: {notes}"""

    try:
        response = client.chat.completions.create(
            model=GROQ_LLM_MODEL,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        flashcards = json.loads(response_text)

        if not isinstance(flashcards, list):
            raise ValueError("Response is not a list")

        print(f"✅ Generated {len(flashcards)} flashcards")
        return flashcards

    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        print(f"   Response: {response_text}")
        raise
    except Exception as e:
        print(f"❌ Error generating flashcards: {e}")
        raise


def generate_flashcards_with_retry(notes, num_cards=5, max_retries=3):
    for attempt in range(max_retries):
        try:
            return generate_flashcards(notes, num_cards)
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"   Retrying... ({max_retries - attempt - 1} retries left)")
            else:
                print(f"❌ Failed after {max_retries} attempts")
                raise


def format_flashcards_for_display(flashcards):
    formatted = "📚 Generated Flashcards:\n" + "=" * 50 + "\n\n"
    for i, card in enumerate(flashcards, 1):
        formatted += f"Card {i}:\n"
        formatted += f"❓ Q: {card['question']}\n"
        formatted += f"✅ A: {card['answer']}\n\n"
    return formatted