import fastapi

from claim_processing.utils.decision_engines import SimpleLLMDecisionEngine
from claim_processing.process import list_available_decision_ids, process_claim, upload_claim, upload_decision
from claim_processing.pydantic_models import ClaimRequest, ClaimDecision, UploadResponse
from claim_processing.utils.load import load_claim_decision

from typing import List

app = fastapi.FastAPI()

decision_engine = SimpleLLMDecisionEngine()

@app.get("/health")
def health():
    return {"message": "OK"}

@app.post("/claims")
def claims(claim_request: ClaimRequest) -> UploadResponse:
    upload_response = upload_claim(
        claim_id=claim_request.claim_id, 
        description_text=claim_request.description_text, 
        supporting_documents=claim_request.supporting_documents,
    )
    claim_decision = process_claim(claim_id=claim_request.claim_id, decision_engine=decision_engine)
    upload_decision(claim_decision=claim_decision, claim_id=claim_request.claim_id)
    return upload_response

@app.post("/process_claim")
def post_process_claim(claim_id: int) -> ClaimDecision:
    claim_decision = process_claim(claim_id=claim_id, decision_engine=decision_engine)
    upload_decision(claim_decision=claim_decision, claim_id=claim_id)
    return claim_decision

@app.get("/claims/{claim_id}")
def get_claim_decision(claim_id: int) -> ClaimDecision:
    return load_claim_decision(claim_id)

@app.get("/claims")
def get_claims() -> List[int]:
    return list_available_decision_ids()
