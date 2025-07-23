from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient, errors
import os
import jwt
import bcrypt 
from app.answer_engine import evaluate_answer
from app.interview_engine import assign_round_questions, check_and_update_round_status
from data.db import candidates_collection
from app.candidate_engine import register_candidate as register_new_candidate
from bson.objectid import ObjectId
from app.utils import token_required

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/register-candidate", methods=["POST"])
def register_candidate():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    role = data.get("role")
    password = data.get("password")

    if not all([name, email, role, password]):
        return jsonify({"error": "All fields (name, email, role, password) are required."}), 400

    try:
        candidate_id = register_new_candidate(name, email, role, password)
        if candidate_id is None:
            return jsonify({"error": f"Candidate with email {email} already exists."}), 409

        return jsonify({
            "message": "Candidate registered successfully",
            "candidate_id": str(candidate_id)
        })
    except ValueError as ve:
        if "Candidate not found." in str(ve):
            return jsonify({"error": str(ve)}), 404    
        else:
            return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/start-round", methods=["POST"])
@token_required
def start_round(candidate_id):
    data = request.json
    round_num = data.get("round")
    level = data.get("level")

    if not round_num or not level:
        return jsonify({"error": "round and level are required."}), 400

    try:
        assign_round_questions(candidate_id, round_num, level)
        return jsonify({"message": f"Round {round_num} questions assigned for level {level}."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/submit-answer", methods=["POST"])
@token_required
def submit_answer(candidate_id):
    data = request.json
    question_id = data.get("question_id")
    user_answer = data.get("user_answer")

    if not question_id or not user_answer:
        return jsonify({"error": "Missing question_id or user_answer"}), 400

    try:
        candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
        if not candidate:
            raise ValueError("Candidate not found")

        found = False
        for round_data in candidate.get("interview_progress", []):
            for question in round_data.get("questions", []):
                if str(question.get("question_id")) == question_id:
                    question["user_answer"] = user_answer
                    score = evaluate_answer(candidate_id, question_id, user_answer)
                    question["evaluated"] = True
                    question["score"] = score
                    found = True
                    break
            if found:
                break

        if not found:
            raise ValueError("Question ID not found in candidate's interview progress.")

        # Save changes
        candidates_collection.update_one(
            {"_id": ObjectId(candidate_id)},
            {"$set": {"interview_progress": candidate["interview_progress"]}}
        )

        return jsonify({"message": "Answer evaluated", "score": score})

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404 if "not found" in str(ve).lower() else 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/complete-round", methods=["POST"])
@token_required
def complete_round(candidate_id):
    try:
        result = check_and_update_round_status(candidate_id)
        return jsonify(result)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-questions/<candidate_id>", methods=["GET"])
def get_questions(candidate_id):
    candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    questions = []
    for round_data in candidate.get("interview_progress", []):
        for q in round_data.get("questions", []):
            q["question_id"] = str(q.get("question_id"))
            q["generated_question"] = str(q.get("generated_question"))
            q["level"] = round_data.get("level")
            questions.append(q)

    return jsonify(questions)

@app.route("/candidate-status", methods=["GET"])
@token_required
def candidate_status(candidate_id):
    candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    progress = candidate.get("interview_progress", [])
    allowed_levels = candidate.get("allowed_levels", [])
    eliminated_level = candidate.get("eliminated_at_level")
    current_round = progress[-1] if progress else {}
    current_level = current_round.get("level")
    total_score = current_round.get("total_score")

    # NEW: detect incomplete round
    incomplete_round = False
    if current_round and not current_round.get("completed"):
        questions = current_round.get("questions", [])
        if any(q.get("score") is None for q in questions):
            incomplete_round = True

    return jsonify({
        "status": candidate.get("status"),
        "eliminated_at_level": eliminated_level,
        "current_level": current_level,
        "total_score": round(total_score, 2) if total_score is not None else None,
        "incomplete_round": incomplete_round  # 👈 add this
    })

@app.route("/login-candidate", methods=["POST"])
def login_candidate():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    candidate = candidates_collection.find_one({"email": email})
    if not candidate:
        return jsonify({"error": "Invalid email or password."}), 401

    if not bcrypt.checkpw(password.encode('utf-8'), candidate["password"]):
        return jsonify({"error": "Invalid email or password."}), 401

    token = jwt.encode(
        {"candidate_id": str(candidate["_id"])},
        os.getenv("JWT_SECRET"),
        algorithm="HS256"
    )

    return jsonify({
        "message": "Login successful",
        "candidate_id": str(candidate["_id"]),
        "status": candidate["status"],
        "token": token
    })

@app.route("/last-round-status", methods=["GET"])
@token_required
def last_round_status(candidate_id):
    candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    progress = candidate.get("interview_progress", [])
    if not progress:
        return jsonify({"passed": True})  # If no rounds, allow to start first

    last_round = progress[-1]
    return jsonify({
        "passed": last_round.get("passed", False),
        "completed": last_round.get("completed", False),
        "level": last_round.get("level"),
        "round": last_round.get("round")
    })


if __name__ == "__main__":
    app.run(debug=True, port=7860)
