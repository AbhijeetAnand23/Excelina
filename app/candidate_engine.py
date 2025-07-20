# app/candidate_engine.py

import os
import uuid
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# ---------------------------
# MongoDB Connection
# ---------------------------
client = MongoClient(os.getenv("MONGO_URI"))
db = client["excelina"]
candidates_col = db["candidates"]

# ---------------------------
# Register a new candidate
# ---------------------------
def register_candidate(name, email, role):
    if role not in ["beginner", "experienced"]:
        raise ValueError("Role must be either 'beginner' or 'experienced'.")

    # Assign levels based on role
    level_range = {
        "beginner": [1, 2, 3],
        "experienced": [2, 3, 4]
    }

    candidate_id = str(uuid.uuid4())  # Unique ID for tracking

    candidate_doc = {
        "candidate_id": candidate_id,
        "name": name,
        "email": email,
        "role": role,
        "allowed_levels": level_range[role],
        "interview_progress": [],  # Will hold questions + scores per level
        "eliminated_at_level": None,
        "status": "registered"  # Can be: registered, in_progress, eliminated, completed
    }

    candidates_col.insert_one(candidate_doc)
    print(f"[✅] Candidate '{name}' registered with ID: {candidate_id}")
    return candidate_id
