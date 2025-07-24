import os
import requests
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval.models.base_model import DeepEvalBaseLLM
from data.db import candidates_collection
load_dotenv()


HF_MODEL = "meta-llama/Llama-3.3-70B-Instruct:nebius"
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.environ["HF_TOKEN"]


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

def evaluate_answer(candidate_id: str, question_id: str, user_answer: str):
    candidate = candidates_collection.find_one({"_id": ObjectId(candidate_id)})
    if not candidate:
        raise ValueError("Candidate not found.")

    found = False
    for i, round_data in enumerate(candidate.get("interview_progress", [])):
        for j, question in enumerate(round_data.get("questions", [])):
            if str(question.get("question_id")) == question_id:
                test_case = LLMTestCase(
                    input=question["generated_question"],
                    actual_output=user_answer,
                    expected_output=question["generated_reference_answer"]
                )

                result = g_eval.measure(test_case)
                score = round(result * 10, 2)

                # Update the nested question in-place
                update_query = {
                    "_id": ObjectId(candidate_id)
                }
                update_fields = {
                    f"interview_progress.{i}.questions.{j}.user_answer": user_answer,
                    f"interview_progress.{i}.questions.{j}.evaluated": True,
                    f"interview_progress.{i}.questions.{j}.score": score
                }

                candidates_collection.update_one(update_query, {"$set": update_fields})
                found = True
                return score

    if not found:
        raise ValueError("Question ID not found in candidate's interview progress.")

def contains_cuss_words(text: str) -> bool:
    prompt = f"""Check if the following text contains any cuss words, profanity, or inappropriate language. Just respond with "Yes" or "No".

Text: "{text}"
"""
    response = hf_llm.generate(prompt).strip().lower()
    return "yes" in response