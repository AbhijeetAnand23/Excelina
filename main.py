from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient, errors
import os

from app.answer_engine import evaluate_answer
from app.interview_engine import assign_initial_questions, assign_next_level_if_passed
from data.db import candidates_collection
from app.candidate_engine import register_candidate as register_new_candidate
from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/register-candidate", methods=["POST"])
def register_candidate():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    role = data.get("role")

    try:
        candidate_id = register_new_candidate(name, email, role)
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

if __name__ == "__main__":
    app.run(debug=True, port=7860)
