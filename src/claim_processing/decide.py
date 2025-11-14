from claim_processing.decision_engines import DecisionEngine, DummyDecisionEngine
from claim_processing.pydantic_models import Claim, ClaimDecision


def decide_claim(claim: Claim, decision_engine: DecisionEngine = DummyDecisionEngine("APPROVE")) -> ClaimDecision:
    
    return decision_engine.decide_claim(claim)


