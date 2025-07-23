from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient, errors
import os
import jwt
import bcrypt 
from app.answer_engine import evaluate_answer
from app.interview_engine import assign_initial_questions, assign_next_level_if_passed
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

        assign_initial_questions(candidate_id)
        return jsonify({
            "message": "Candidate registered and initial questions assigned",
            "candidate_id": str(candidate_id)
        })
    except ValueError as ve:
        if "Candidate not found." in str(ve):
            return jsonify({"error": str(ve)}), 404    
        else:
            return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/submit-answer", methods=["POST"])
@token_required
def submit_answer():
    data = request.json
    candidate_id = data.get("candidate_id")
    question_id = data.get("question_id")
    user_answer = data.get("user_answer")

    try:
        score = evaluate_answer(candidate_id, question_id, user_answer)
        return jsonify({"message": "Answer evaluated", "score": score})
    except ValueError as ve:
        if "Candidate not found" in str(ve) or "Question ID not found in candidate's interview progress." in str(ve):
            return jsonify({"error": str(ve)}), 404
        else:
            return jsonify({"error": str(ve)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/next-level", methods=["POST"])
@token_required
def progress_to_next_level():
    data = request.json
    candidate_id = data.get("candidate_id")

    try:
        assign_next_level_if_passed(candidate_id)
        return jsonify({"message": "Checked and progressed candidate if passed."})
    except ValueError as ve:
        if "Candidate not found." in str(ve):
            return jsonify({"error": str(ve)}), 404    
        else:
            return jsonify({"error": str(ve)}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-questions/<candidate_id>", methods=["GET"])
def get_questions(candidate_id):
    candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    questions = candidate.get("interview_progress", [])
    for q in questions:
        q["question_id"] = str(q["question_id"])
        q["generated_question"] = str(q["generated_question"])
    return jsonify(questions)

@app.route("/candidate-status/<candidate_id>", methods=["GET"])
@token_required
def candidate_status(candidate_id):
    candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404

    progress = candidate["interview_progress"]
    allowed_levels = candidate["allowed_levels"]
    eliminated_level = candidate.get("eliminated_at_level")
    levels_attempted = sorted(set(q["level"] for q in progress))
    current_level = levels_attempted[-1] if levels_attempted else None

    current_level_questions = [q for q in progress if q["level"] == current_level]
    total_score = None
    if len(current_level_questions) == 10 and all(q["score"] is not None for q in current_level_questions):
        total_score = sum(q["score"] for q in current_level_questions)  # total out of 100

    return jsonify({
        "status": candidate["status"],
        "eliminated_at_level": eliminated_level,
        "current_level": current_level,
        "total_score": round(total_score, 2) if total_score is not None else None
    })

@app.route("/login-candidate", methods=["POST"])
def login_candidate():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    candidate = candidates_collection.find_one({"email": email})
    if not candidate:
        return jsonify({"error": "Invalid email or password."}), 401

    # 🔒 Check password hash
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
        "status": candidate["status"]
    })

if __name__ == "__main__":
    app.run(debug=True, port=7860)
