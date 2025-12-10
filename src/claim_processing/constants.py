import os

from dotenv import load_dotenv

load_dotenv()

MODEL_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_API_URL = "https://openrouter.ai/api/v1"
# MODEL_NAME = "google/gemini-2.5-flash"
MODEL_NAME = "google/gemini-2.5-pro"
AUTHENTICITY_MODEL_NAME = "openai/gpt-5-image-mini"
OCR_MODEL_NAME = "qwen/qwen2.5-vl-72b-instruct"

CHECK_AUTHENTICITY = True
USE_OCR = True
AUTHENTICITY_THRESHOLD = 2  # Scores greater or equal to this are determined authentic

CLAIM_DIRECTORY = "data"
POLICY_DIRECTORY = "data"
RESULTS_DIRECTORY = os.path.join("results", "latest")
FILES_TO_EXCLUDE = ["description.txt", "answer.json"]
