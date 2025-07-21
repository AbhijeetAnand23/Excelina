# app/answer_engine.py

import os
import requests
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval.models.base_model import DeepEvalBaseLLM

load_dotenv()

# -------------------------------
# MongoDB Setup
# -------------------------------
client = MongoClient(os.environ["MONGO_URI"])
db = client["excelina"]
candidates_collection = db["candidates"]

# -------------------------------
# HF LLM Setup
# -------------------------------
HF_MODEL = "meta-llama/Llama-3.3-70B-Instruct:nebius"  # or any other HF chat model
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.environ["HF_TOKEN"]


# Chat LLM wrapper compatible with DeepEval & HF chat API
class HFChatRemoteModel(DeepEvalBaseLLM):
    def __init__(self, api_url, hf_token, model_id):
        super().__init__()
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }
        self.model_id = model_id

    def get_model_name(self):
        return self.model_id

    def load_model(self, *args, **kwargs):
        return self

    def generate(self, prompt: str, **kwargs) -> str:
        # Forward any unknown args from DeepEval without changing payload
        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs
        }
        resp = requests.post(self.api_url, headers=self.headers, json=payload)
        if resp.status_code != 200:
            print("❌ HF error", resp.status_code, resp.text)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    async def a_generate(self, prompt: str, **kwargs) -> str:
        return self.generate(prompt, **kwargs)



hf_llm = HFChatRemoteModel(HF_API_URL, HF_TOKEN, HF_MODEL)

# -------------------------------
# GEval Metric with HF model
# -------------------------------
g_eval = GEval(
    name="Answer Correctness",
    model=hf_llm,
    criteria="Check if the candidate's answer accurately and completely answers the question.",
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.EXPECTED_OUTPUT
    ]
)


# -------------------------------
# Evaluate Answer Function
# -------------------------------
def evaluate_answer(candidate_id: str, question_id: str, user_answer: str):
    # Get candidate document
    cand = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
    if not cand:
        print("[❌] Candidate not found.")
        return

    # Find the question in interview_progress
    question_doc = next((q for q in cand["interview_progress"] if str(q["question_id"]) == question_id), None)
    if not question_doc:
        print("[❌] Question ID not found in candidate's interview progress.")
        return
    # print(question_doc)
    # Build test case for GEval
    test_case = LLMTestCase(
        input=question_doc["generated_question"],
        actual_output=user_answer,
        expected_output=question_doc["generated_reference_answer"]
    )

    # Evaluate
    result = g_eval.measure(test_case)
    score = round(result * 10, 2)

    print("🧠 Evaluation complete:")
    print(f"Score: {score}/10")

    # Update the candidate's interview_progress with score
    candidates_collection.update_one(
        {"_id": ObjectId(candidate_id), "interview_progress._id": ObjectId(question_id)},
        {"$set": {"interview_progress.$.score": score}}
    )
    print("[✅] Score updated in DB.")
