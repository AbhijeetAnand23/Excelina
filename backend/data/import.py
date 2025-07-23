import json
from db import seed_collection

with open("data/questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# Optional: Clear existing
seed_collection.delete_many({})

# Insert
seed_collection.insert_many(questions)
print("✅ Seed questions inserted into MongoDB.")
