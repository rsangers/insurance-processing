import os

from dotenv import load_dotenv

load_dotenv()

MODEL_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_API_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "google/gemini-2.5-flash-001"

CLAIM_DIRECTORY = "assignment"
POLICY_DIRECTORY = "assignment"
