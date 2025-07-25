from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["excelina"]
seed_collection = db["questions"]
candidates_collection = db["candidates"] 