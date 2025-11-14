import fastapi
from claim_processing.process import process_claim
from claim_processing.pydantic_models import Claim, ClaimDecision
from typing import List

app = fastapi.FastAPI()

@app.get("/health")
def health():
    return {"message": "OK"}

@app.post("/claims")
def claims(claim: Claim):
    return {"message": "Claim received"}

@app.get("/claims/{claim_id}")
def get_claim_decision(claim_id: str) -> ClaimDecision:
    return process_claim(claim_id=claim_id)

@app.get("/claims")
def get_claims() -> List[str]:
    return []
