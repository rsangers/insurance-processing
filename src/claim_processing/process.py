import base64
import logging
import os
from typing import List

from fastapi import HTTPException

from claim_processing.constants import (
    AUTHENTICITY_THRESHOLD,
    CHECK_AUTHENTICITY,
    CLAIM_DIRECTORY,
    RESULTS_DIRECTORY,
    USE_OCR,
)
from claim_processing.pydantic_models import (
    ClaimDecision,
    DocumentUpload,
    UploadResponse,
)
from claim_processing.utils.decision_engines import DecisionEngine, DummyDecisionEngine
from claim_processing.utils.image_utils import (
    extract_text_from_doc,
    judge_image_authenticity,
)
from claim_processing.utils.load import load_claim

logger = logging.getLogger()


def process_claim(
    claim_id: int,
    decision_engine: DecisionEngine = DummyDecisionEngine(decision="DENY"),
    check_authenticity: bool = CHECK_AUTHENTICITY,
    use_ocr: bool = USE_OCR,
) -> ClaimDecision:
    claim = load_claim(claim_id)
    if check_authenticity:
        logger.info("Checking authenticity")
        for supporting_doc in claim.supporting_documents:
            if supporting_doc.type == "image supporting document":
                try:
                    authenticity_response = judge_image_authenticity(
                        supporting_doc.content, supporting_doc.name
                    )
                    if (
                        int(authenticity_response["authenticity_score"])
                        < AUTHENTICITY_THRESHOLD
                    ):
                        logger.info(
                            f"Claim {claim_id} was declined because of unauthenticity with score: {authenticity_response['authenticity_score']}"
                        )
                        return ClaimDecision(
                            reasoning="The claim was declined because supporting documents were deemed to be not authentic:\n"
                            + authenticity_response["reasoning"],
                            decision="DENY",
                        )
                except Exception as e:
                    print(
                        f"During authentication, faced exception {e} for claim id {claim_id}. Skipping authentication step..."
                    )

    parsed_supporting_documents = []
    logger.info("Parsing documents")
    for doc in claim.supporting_documents:
        parsed_supporting_documents.append(extract_text_from_doc(doc, use_ocr=use_ocr))
    claim.supporting_documents = parsed_supporting_documents

    logger.info("Making decision")
    decision = decision_engine.decide_claim(claim=claim)
    return decision


def process_and_upload_all_claims(
    decision_engine: DecisionEngine = DummyDecisionEngine(decision="DENY"),
    overwrite: bool = True,
    results_dir: str = RESULTS_DIRECTORY,
    check_authenticity: bool = CHECK_AUTHENTICITY,
    use_ocr: bool = USE_OCR,
):
    # available_claim_ids = list_available_claim_ids()
    available_claim_ids = [3, 4, 5, 6, 7, 8, 9]
    for claim_id in available_claim_ids:
        logger.info(f"Processing claim id {claim_id}")
        try:
            decision = process_claim(
                claim_id,
                decision_engine=decision_engine,
                check_authenticity=check_authenticity,
                use_ocr=use_ocr,
            )
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
            os.path.join(claim_dir, supporting_doc.file_name), "wb"
        ) as supporting_file:
            supporting_file.write(base64.b64decode(supporting_doc.document_bytes))

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
