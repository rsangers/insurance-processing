import os
from typing import List

from fastapi import HTTPException

from claim_processing.constants import CLAIM_DIRECTORY, RESULTS_DIRECTORY
from claim_processing.pydantic_models import (
    ClaimDecision,
    DocumentUpload,
    UploadResponse,
)
from claim_processing.utils.decision_engines import DecisionEngine, DummyDecisionEngine
from claim_processing.utils.load import load_claim


def process_claim(
    claim_id: int,
    decision_engine: DecisionEngine = DummyDecisionEngine(decision="DENY"),
) -> ClaimDecision:
    claim = load_claim(claim_id)
    decision = decision_engine.decide_claim(claim=claim)
    return decision


def process_and_upload_all_claims(
    decision_engine: DecisionEngine = DummyDecisionEngine(decision="DENY"),
    overwrite: bool = True,
    results_dir: str = RESULTS_DIRECTORY,
):
    available_claim_ids = list_available_claim_ids()
    for claim_id in available_claim_ids:
        try:
            decision = process_claim(claim_id, decision_engine=decision_engine)
            upload_decision(
                decision, claim_id, overwrite=overwrite, results_dir=results_dir
            )
        except Exception as e:
            print(f"Faced exception {e} for claim id {claim_id}. Skipping...")


def upload_claim(
    claim_id: int, description_text: str, supporting_documents: List[DocumentUpload]
) -> UploadResponse:
    claim_dir = os.path.join(CLAIM_DIRECTORY, f"claim {claim_id}")

    if os.path.exists(claim_dir):
        raise HTTPException(
            status_code=500, detail="Claim submission failed, claim id already exists"
        )
    os.makedirs(claim_dir)

    with open(os.path.join(claim_dir, "description.txt"), "w") as description_file:
        description_file.write(description_text)

    for supporting_doc in supporting_documents:
        with open(
            os.path.join(claim_dir, supporting_doc.file_name), "w"
        ) as supporting_file:
            supporting_file.write(supporting_doc.document_bytes)

    return UploadResponse(
        status=200,
        message="Successfully submitted claim, claim decision should be available soon",
    )


def upload_decision(
    claim_decision: ClaimDecision,
    claim_id: str,
    overwrite: bool = False,
    results_dir: str = RESULTS_DIRECTORY,
):
    os.makedirs(results_dir, exist_ok=True)
    claim_decision_path = os.path.join(results_dir, f"claim {claim_id} decision.json")

    if os.path.exists(claim_decision_path) and not overwrite:
        raise HTTPException(
            status_code=500,
            detail="Claim decision already exists and overwrite is set to False",
        )

    with open(claim_decision_path, "w") as decision_file:
        decision_file.write(claim_decision.model_dump_json())


def list_available_claim_ids() -> List[int]:
    available_claim_directories = os.listdir(CLAIM_DIRECTORY)
    claim_ids = [
        int(claim_dir.replace("claim ", ""))
        for claim_dir in available_claim_directories
        if os.path.isdir(os.path.join(CLAIM_DIRECTORY, claim_dir))
    ]
    return claim_ids


def list_available_decision_ids() -> List[int]:
    available_decision_files = os.listdir(RESULTS_DIRECTORY)
    decision_ids = [
        int(result_file.replace("claim ", "").replace(" decision.json"))
        for result_file in available_decision_files
    ]
    return decision_ids
