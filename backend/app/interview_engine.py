from app.question_engine import generate_candidate_questions
from data.db import candidates_collection
from bson.objectid import ObjectId

QUESTIONS_PER_ROUND = 6
MAXMARKS = 10 * QUESTIONS_PER_ROUND
PASSING_SCORE_THRESHOLD =  0.7 * MAXMARKS

def assign_round_questions(candidate_id, round_num, level):
    print(level)
    candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
    if not candidate:
        raise ValueError("Candidate not found.")

    allowed_levels = candidate.get("allowed_levels", [])
    if level not in allowed_levels:
        raise ValueError(f"Level {level} is not allowed for this candidate.")

    # ✅ Step 1: Collect already used topics
    used_topics = set()
    for round_data in candidate.get("interview_progress", []):
        for q in round_data.get("questions", []):
            topic = q.get("topic")  # Assuming each question has a `topic` field
            if topic:
                used_topics.add(topic)

    # ✅ Step 2: Generate a larger pool and filter out duplicates
    all_new_questions = generate_candidate_questions(level, 8)
    unique_topic_questions = []

    seen_topics = set()
    for q in all_new_questions:
        topic = q.get("topic")
        if topic and topic not in used_topics and topic not in seen_topics:
            seen_topics.add(topic)
            unique_topic_questions.append(q)
        if len(unique_topic_questions) == 6:
            break

    if len(unique_topic_questions) < 6:
        raise ValueError("Not enough unique-topic questions available for this candidate.")

    # ✅ Step 3: Add required metadata
    for q in unique_topic_questions:
        q.update({
            "score": None,
            "user_answer": None,
            "evaluated": False,
            "feedback": None,
        })

    # ✅ Step 4: Construct round data
    round_data = {
        "round": round_num,
        "level": level,
        "completed": False,
        "passed": False,
        "total_score": None,
        "questions": unique_topic_questions
    }

    # ✅ Step 5: Save to DB
    candidates_collection.update_one(
        {"_id": ObjectId(candidate_id)},
        {
            "$set": {"status": "in_progress"},
            "$push": {"interview_progress": round_data}
        }
    )

    print(f"[✅] Assigned Level {level} as Round {round_num} to candidate {str(candidate_id)}")
 # ← Declare this at the top of your file or globally

def check_and_update_round_status(candidate_id):
    candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
    if not candidate:
        raise ValueError("Candidate not found.")

    progress = candidate.get("interview_progress", [])
    allowed_levels = candidate.get("allowed_levels", [])
    eliminated_level = candidate.get("eliminated_at_level")

    if eliminated_level:
        return {
            "status": "eliminated",
            "level": eliminated_level
        }

    if not progress:
        raise ValueError("No rounds attempted yet.")

    latest_round = progress[-1]
    questions = latest_round.get("questions", [])
    level = latest_round.get("level")

    # ✅ Updated to match 6-question round logic
    if len(questions) < QUESTIONS_PER_ROUND or any(q["score"] is None for q in questions):
        raise ValueError(f"Round {latest_round['round']} not fully completed.")

    total_score = sum(q["score"] for q in questions)
    passed = total_score >= PASSING_SCORE_THRESHOLD
    completed = True

    # ✅ Update the latest round in DB
    candidates_collection.update_one(
        {
            "_id": ObjectId(candidate_id),
            "interview_progress.round": latest_round["round"]
        },
        {
            "$set": {
                "interview_progress.$.total_score": total_score,
                "interview_progress.$.completed": completed,
                "interview_progress.$.passed": passed
            }
        }
    )

    if not passed:
        candidates_collection.update_one(
            {"_id": ObjectId(candidate_id)},
            {
                "$set": {
                    "eliminated_at_level": level,
                    "status": "eliminated"
                }
            }
        )
        return {
            "status": "eliminated",
            "level": level
        }

    # ✅ Completed all levels?
    current_index = allowed_levels.index(level)
    if current_index + 1 >= len(allowed_levels):
        candidates_collection.update_one(
            {"_id": ObjectId(candidate_id)},
            {"$set": {"status": "completed"}}
        )
        print("[🏁] Candidate completed all levels!")
        return {
            "status": "completed"
        }

    print(f"[ℹ️] Round {latest_round['round']} evaluated: {'✅ Passed' if passed else '❌ Failed'} ({total_score}/{QUESTIONS_PER_ROUND * 10})")
    return {
        "status": "progressed",
        "next_level": allowed_levels[current_index + 1]
    }
