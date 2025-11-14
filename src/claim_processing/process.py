from claim_processing.decide import decide_claim
from claim_processing.decision_engines import SimpleLLMDecisionEngine
from claim_processing.load import load_claim
from claim_processing.pydantic_models import ClaimDecision


def process_claim(claim_id: str) -> ClaimDecision:
    decision_engine = SimpleLLMDecisionEngine()

    claim = load_claim(claim_id)
    decision = decide_claim(claim=claim, decision_engine=decision_engine)
    return decision
