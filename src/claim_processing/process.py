from claim_processing.decide import decide_claim
from claim_processing.load import load_claim
from claim_processing.pydantic_models import ClaimDecision


def process_claim(claim_id: str) -> ClaimDecision:
    claim = load_claim(claim_id)
    decision = decide_claim(claim)
    return decision
