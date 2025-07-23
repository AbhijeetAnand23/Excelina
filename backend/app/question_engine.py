import os
import requests
from dotenv import load_dotenv
from bson.objectid import ObjectId
from data.db import seed_collection

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
    "Content-Type": "application/json"
}

# Load all active questions (if needed)
def load_questions():
    return list(seed_collection.find({"status": "active"}))

# Randomly fetch N questions of a given level from MongoDB
def get_questions_by_level(level, n=10):
    return list(seed_collection.aggregate([
        {"$match": {"level": level, "status": "active"}},
        {"$sample": {"size": n}}
    ]))

# Use LLM to generate modified question + reference + follow-up
def generate_variant_with_llm(seed_question, seed_reference_answer, seed_followup):
    print("Original Question →", seed_question)
    prompt = f"""You are an AI interviewer. Slightly modify the Excel question below (same topic and difficulty). Then write an updated reference answer and a follow-up question.

Original Question: {seed_question}
Reference Answer: {seed_reference_answer}
Original Follow-Up: {seed_followup}

Respond in format:
Question: <new version>
Reference: <updated reference answer>
Followup: <updated follow-up question>
"""

    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct:nebius",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 300
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print("⚠️ LLM generation failed.", response.status_code, response.text)
        return seed_question, seed_reference_answer, seed_followup

    output = response.json()["choices"][0]["message"]["content"].strip()
    lines = output.split("\n")
    try:
        new_q = lines[0].split(":", 1)[1].strip()
        new_ref = lines[1].split(":", 1)[1].strip()
        new_followup = lines[2].split(":", 1)[1].strip()
    except:
        new_q, new_ref, new_followup = seed_question, seed_reference_answer, seed_followup

    return new_q, new_ref, new_followup

# Generate N new questions with reference answers & follow-ups for a candidate
def generate_candidate_questions(level, n=10):
    seed_questions = get_questions_by_level(level, n)
    final_questions = []

    for q in seed_questions:
        mod_q, mod_ref, mod_fol = generate_variant_with_llm(
            q["question"],
            q["reference_answer"],
            q.get("follow_up", "")
        )
        # Insert generated question back into seed pool
        seed_collection.insert_one({
            "level": level,
            "question_type": "generated",
            "topic": q.get("topic", ""),
            "question": mod_q,
            "reference_answer": mod_ref,
            "follow_up": mod_fol,
            "status": "active"
        })

        # Prepare question for candidate
        final_questions.append({
            "question_id": ObjectId(),
            "level": level,
            "question_type": "generated",
            "topic": q.get("topic", ""),
            "generated_question": mod_q,
            "generated_reference_answer": mod_ref,
            "follow_up": mod_fol
        })

    return final_questions
