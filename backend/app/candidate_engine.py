import os
import bcrypt
from dotenv import load_dotenv
from pymongo import errors
from data.db import candidates_collection
load_dotenv()

# Enforce unique email (add an index if not already done)
try:
    candidates_collection.create_index("email", unique=True)
except errors.DuplicateKeyError:
    pass

def register_candidate(name, email, role, password):
    if role not in ["beginner", "experienced"]:
        raise ValueError("Role must be either 'beginner' or 'experienced'.")

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # Assign levels based on role
    level_range = {
        "beginner": [1, 2, 3],
        "experienced": [2, 3, 4]
    }

    candidate_doc = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": role,
        "allowed_levels": level_range[role],
        "interview_progress": [],
        "eliminated_at_level": None,
        "status": "registered"
    }

    try:
        result = candidates_collection.insert_one(candidate_doc)
        return result.inserted_id
    except errors.DuplicateKeyError:
        raise ValueError(f"A candidate with email '{email}' already exists.")
