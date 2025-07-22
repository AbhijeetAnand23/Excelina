from app.question_engine import generate_candidate_questions
from data.db import candidates_collection
from bson.objectid import ObjectId

PASSING_SCORE_THRESHOLD = 6.0  # Out of 10

# Assign level 1 questions right after registration
def assign_initial_questions(candidate_object_id):
    candidate = candidates_collection.find_one({"_id": ObjectId(candidate_object_id)})
    if not candidate:
        raise ValueError("Candidate not found.")

    allowed_levels = candidate.get("allowed_levels", [])
    if not allowed_levels:
        raise ValueError("No allowed levels for candidate.")

    level = allowed_levels[0]  # Always start with the first allowed level
    questions = generate_candidate_questions(level, n=10)

    for q in questions:
        q.update({
            "score": None,
            "user_answer": None,
            "evaluated": False
        })

    candidates_collection.update_one(
        {"_id": ObjectId(candidate_object_id)},
        {
            "$set": {"status": "in_progress"},
            "$push": {"interview_progress": {"$each": questions}}
        }
    )

# Progress to the next level only if previous is passed
def assign_next_level_if_passed(candidate_object_id):
    candidate = candidates_collection.find_one({"_id": ObjectId(candidate_object_id)})
    if not candidate:
        raise ValueError("Candidate not found.")

    progress = candidate.get("interview_progress", [])
    allowed_levels = candidate.get("allowed_levels", [])
    eliminated = candidate.get("eliminated_at_level")

    if eliminated:
        raise ValueError("Candidate eliminated at level {eliminated}")

    # Find current level
    levels_attempted = sorted(set(q["level"] for q in progress))
    if not levels_attempted:
        raise ValueError("No level attempted yet.")

    current_level = levels_attempted[-1]
    current_level_questions = [q for q in progress if q["level"] == current_level]

    if len(current_level_questions) < 10 or any(q["score"] is None for q in current_level_questions):
        raise ValueError(f"Level {current_level} not fully answered or evaluated.")

    # Calculate average score
    avg_score = sum(q["score"] for q in current_level_questions) / 10.0
    print(f"[ℹ️] Candidate's average score at Level {current_level}: {avg_score:.2f}")

    if avg_score < PASSING_SCORE_THRESHOLD:
        candidates_collection.update_one(
            {"_id": ObjectId(candidate_object_id)},
            {"$set": {"eliminated_at_level": current_level, "status": "eliminated"}}
        )
        raise ValueError(f"Candidate eliminated at level {current_level}")

    # Assign next level
    current_index = allowed_levels.index(current_level)
    if current_index + 1 >= len(allowed_levels):
        candidates_collection.update_one(
            {"_id": ObjectId(candidate_object_id)},
            {"$set": {"status": "completed"}}
        )
        print("[🏁] Candidate completed all levels!")
        return

    next_level = allowed_levels[current_index + 1]
    new_questions = generate_candidate_questions(next_level, n=10)
    for q in new_questions:
        q.update({
            "score": None,
            "user_answer": None,
            "evaluated": False
        })

    candidates_collection.update_one(
        {"_id": ObjectId(candidate_object_id)},
        {"$push": {"interview_progress": {"$each": new_questions}}}
    )
    print(f"[✅] Assigned Level {next_level} questions to candidate {_id_str(candidate_object_id)}")


def _id_str(oid):
    return str(oid) if isinstance(oid, ObjectId) else oid
