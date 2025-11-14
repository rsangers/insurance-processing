from typing import Literal
from pydantic import BaseModel

class Document(BaseModel):
    name: str
    content: str
    type: str

class Claim(BaseModel):
    claim_id: str
    description: Document
    supporting_documents: list[Document]

class ClaimDecision(BaseModel):
    reasoning: str
    decision: Literal["APPROVE", "DENY", "UNCERTAIN"]
