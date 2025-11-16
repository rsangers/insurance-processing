from typing import List, Literal

from pydantic import BaseModel


class Document(BaseModel):
    name: str
    content: str
    type: str


class DocumentUpload(BaseModel):
    file_name: str
    document_bytes: bytes


class ClaimRequest(BaseModel):
    claim_id: int
    description_text: str
    supporting_documents: List[DocumentUpload]


class UploadResponse(BaseModel):
    status: int
    message: str


class AuthenticityResponse(BaseModel):
    reasoning: str
    authenticity_score: int


class Claim(BaseModel):
    claim_id: int
    description: Document
    supporting_documents: List[Document]


class ClaimDecision(BaseModel):
    reasoning: str
    decision: Literal["APPROVE", "DENY", "UNCERTAIN"]
