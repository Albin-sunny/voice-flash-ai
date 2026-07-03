import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_LLM_MODEL

client = Groq(api_key=GROQ_API_KEY)


def score_answer(question, correct_answer, user_answer):
    print(f"🤔 Scoring answer...")

    prompt = f"""Grade this answer as JSON only, no other text:
{{"score": <0-100>, "feedback": "<one sentence>", "is_correct": <true/false>}}

Question: {question}
Correct: {correct_answer}
Student: {user_answer}"""

    try:
        response = client.chat.completions.create(
            model=GROQ_LLM_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.choices[0].message.content.strip()
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        result = json.loads(response_text)

        if not all(key in result for key in ['score', 'feedback', 'is_correct']):
            raise ValueError("Missing keys in response")

        print(f"✅ Score: {result['score']}/100")
        return result

    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        print(f"   Response was: {response_text}")
        raise
    except Exception as e:
        print(f"❌ Scoring error: {e}")
        raise


def score_answers_batch(flashcards, user_answers):
    if len(flashcards) != len(user_answers):
        raise ValueError("Flashcards and answers count must match")

    scores = []

    for i, (card, user_answer) in enumerate(zip(flashcards, user_answers), 1):
        print(f"\n📝 Scoring card {i}/{len(flashcards)}...")
        try:
            score = score_answer(card['question'], card['answer'], user_answer)
            score['question'] = card['question']
            score['correct_answer'] = card['answer']
            score['user_answer'] = user_answer
            scores.append(score)
        except Exception as e:
            print(f"⚠️ Error scoring card {i}: {e}")
            scores.append({
                'question': card['question'],
                'correct_answer': card['answer'],
                'user_answer': user_answer,
                'score': 0,
                'feedback': f'Scoring error: {e}',
                'is_correct': False
            })

    return scores


def calculate_overall_score(scores):
    if not scores:
        return {'total_cards': 0, 'correct_count': 0, 'average_score': 0, 'percentage': 0.0}

    total_cards = len(scores)
    correct_count = sum(1 for s in scores if s.get('is_correct', False))
    average_score = sum(s.get('score', 0) for s in scores) / total_cards
    percentage = (correct_count / total_cards * 100)

    return {
        'total_cards': total_cards,
        'correct_count': correct_count,
        'average_score': int(average_score),
        'percentage': round(percentage, 1)
    }


def format_results_for_display(scores, overall):
    result_text = "📊 QUIZ RESULTS\n" + "=" * 60 + "\n\n"
    result_text += f"Overall: {overall['percentage']}%\n"
    result_text += f"Correct: {overall['correct_count']}/{overall['total_cards']}\n"
    result_text += f"Average: {overall['average_score']}/100\n\n"

    for i, score in enumerate(scores, 1):
        result_text += f"Card {i}: {score['score']}/100 {'✅' if score['is_correct'] else '❌'}\n"
        result_text += f"Q: {score['question']}\n"
        result_text += f"Expected: {score['correct_answer']}\n"
        result_text += f"You said: {score['user_answer']}\n"
        result_text += f"Feedback: {score['feedback']}\n\n"

    return result_text