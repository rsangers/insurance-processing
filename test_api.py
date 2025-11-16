import requests
import base64
import time

# Submit a claim
with open("assignment/claim 1/booking confirmation 2.png", "rb") as f:
    image_bytes = base64.b64encode(f.read()).decode('utf-8')

claim_data = {
    "claim_id": 26,
    "description_text": "I was hospitalized during my trip to Spain...",
    "supporting_documents": [
        {
            "file_name": "booking confirmation 2.png",
            "document_bytes": image_bytes
        }
    ]
}

response = requests.post("http://localhost:8000/claims", json=claim_data)
print(response.json())

print("Successfully uploaded claim, waiting max 100 seconds until is processed")

# Retrieve decision (after processing completes)
decision = requests.get(f"http://localhost:8000/claims/26")
max_retries = 10
n_retries = 0
while decision.status_code == 404 and n_retries<max_retries:
    print(f"Decision is not available yet, try {n_retries+1}/{max_retries}")
    time.sleep(10)
    n_retries += 1
    decision = requests.get(f"http://localhost:8000/claims/26")

print(decision.json())