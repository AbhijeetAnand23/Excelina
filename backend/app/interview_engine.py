from app.question_engine import generate_candidate_questions
from data.db import candidates_collection
from bson.objectid import ObjectId

PASSING_SCORE_THRESHOLD = 60  # Out of 100

def assign_round_questions(candidate_id, round_num, level):
    candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
    if not candidate:
        raise ValueError("Candidate not found.")

    allowed_levels = candidate.get("allowed_levels", [])
    if level not in allowed_levels:
        raise ValueError(f"Level {level} is not allowed for this candidate.")

    questions = generate_candidate_questions(level, n=10)

    for q in questions:
        q.update({
            "score": None,
            "user_answer": None,
            "evaluated": False
        })

    round_data = {
        "round": round_num,
        "level": level,
        "completed": False,
        "passed": False,
        "total_score": None,
        "questions": questions
    }

    candidates_collection.update_one(
        {"_id": ObjectId(candidate_id)},
        {
            "$set": {"status": "in_progress"},
            "$push": {"interview_progress": round_data}
        }
    )

    print(f"[✅] Assigned Level {level} as Round {round_num} to candidate {str(candidate_id)}")

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

    if len(questions) < 10 or any(q["score"] is None for q in questions):
        raise ValueError(f"Round {latest_round['round']} not fully completed.")

    total_score = sum(q["score"] for q in questions)
    passed = total_score >= PASSING_SCORE_THRESHOLD
    completed = True

    # Update the latest round in DB
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
            {"$set": {
                "eliminated_at_level": level,
                "status": "eliminated"
            }}
        )
        return {
            "status": "eliminated",
            "level": level
        }

    # Check if this was the last level
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

    print(f"[ℹ️] Round {latest_round['round']} evaluated: {'✅ Passed' if passed else '❌ Failed'} ({total_score}/100)")
    return {
        "status": "progressed",
        "next_level": allowed_levels[current_index + 1]
    }
