import json
from abc import ABC, abstractmethod
from typing import Literal

from openai import OpenAI

from claim_processing.constants import MODEL_API_KEY, MODEL_API_URL, MODEL_NAME
from claim_processing.load import load_policy
from claim_processing.prompts import CLAIM_PROMPT, SIMPLE_LLM_SYSTEM_PROMPT
from claim_processing.pydantic_models import Claim, ClaimDecision


class DecisionEngine(ABC):
    @abstractmethod
    def decide_claim(self, claim: Claim) -> ClaimDecision:
        pass


class DummyDecisionEngine(DecisionEngine):
    def __init__(self, decision: Literal["APPROVE", "DENY", "UNCERTAIN"]):
        self.decision = decision

    def decide_claim(self, claim: Claim) -> ClaimDecision:
        return ClaimDecision(
            decision=self.decision, reasoning="Policy covers the claim"
        )


class SimpleLLMDecisionEngine(DecisionEngine):
    def __init__(self):
        self.policy = load_policy()
        self.system_prompt = SIMPLE_LLM_SYSTEM_PROMPT
        self.model_name = MODEL_NAME
        self.client = OpenAI(
            base_url=MODEL_API_URL,
            api_key=MODEL_API_KEY,
        )

    def decide_claim(self, claim: Claim) -> ClaimDecision:
        response = self.client.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": CLAIM_PROMPT.format(
                        claim_description=claim.description.content,
                        claim_supporting_documents=claim.supporting_documents,
                        policy=self.policy.content,
                    ),
                },
            ],
            response_format=ClaimDecision,
        )
        response_json = json.loads(response.choices[0].message.content)
        return ClaimDecision(
            decision=response_json["decision"], reasoning=response_json["reasoning"]
        )
