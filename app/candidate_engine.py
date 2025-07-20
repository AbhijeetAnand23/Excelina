import os
from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv()

# ---------------------------
# MongoDB Connection
# ---------------------------
client = MongoClient(os.getenv("MONGO_URI"))
db = client["excelina"]
candidates_col = db["candidates"]

# Enforce unique email (add an index if not already done)
try:
    candidates_col.create_index("email", unique=True)
except errors.DuplicateKeyError:
    pass

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

    candidate_doc = {
        "name": name,
        "email": email,
        "role": role,
        "allowed_levels": level_range[role],
        "interview_progress": [],
        "eliminated_at_level": None,
        "status": "registered"
    }

    try:
        result = candidates_col.insert_one(candidate_doc)
        print(f"[✅] Candidate '{name}' registered with _id: {result.inserted_id}")
        return result.inserted_id
    except errors.DuplicateKeyError:
        print(f"[❌] A candidate with email '{email}' already exists.")
        return None
